#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_context.py — 滚动上下文/术语漂移报告（外部 AI 批量翻译的"既定事实"生成器）

用途：
  1) --upto N --apply  生成 项目文档/投喂上下文_第N章.md
     供 pack_external.py 塞进投喂包 02_CONTEXT.md。
  2) --drift-report [--upto N] --apply  生成 项目文档/术语漂移报告_<时间戳>.md
     扫已落地章节纯英版，报告同一中文的多种英文写法（只报告、不判罚）。

红线：只读 glossary.md / 既定事实表.md / 译文候选池.md / 章节纯英版；
      只写 项目文档/ 下的派生 md，不改译文真源、不改规则主源。
"""
import argparse
import glob
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
DOCS = BASE / "项目文档"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import chapter_lib as L  # noqa: E402
from compose_bilingual import nonempty_lines  # noqa: E402

FACTS = DOCS / "既定事实表.md"
POOL = DOCS / "译文候选池.md"
POEMS = "诗词核验记录_"


def est_tok(text):
    cjk = len(re.findall(r"[\u3400-\u9fff\uf900-\ufaff]", text))
    return int(cjk / 1.6 + (len(text) - cjk) / 4)


def parse_facts():
    """读既定事实表，返回 [{category, cn, en, first, by, date}]。"""
    if not FACTS.is_file():
        return []
    rows = []
    for ln in FACTS.read_text(encoding="utf-8-sig").splitlines():
        if not ln.startswith("|") or re.match(r"^\|[\s:\-|]+\|$", ln.strip()):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("类别", "（暂无）") or cells[1] in ("中文", ""):
            continue
        if cells[0].startswith("---"):
            continue
        rows.append({"category": cells[0], "cn": cells[1], "en": cells[2],
                     "first": cells[3] if len(cells) > 3 else "",
                     "by": cells[4] if len(cells) > 4 else "",
                     "date": cells[5] if len(cells) > 5 else ""})
    return rows


def parse_pool():
    """读译文候选池中 status=待裁 的行，返回 dict。"""
    if not POOL.is_file():
        return []
    rows = []
    for ln in POOL.read_text(encoding="utf-8-sig").splitlines():
        if not ln.startswith("|") or re.match(r"^\|[\s:\-|]+\|$", ln.strip()):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0] in ("中文", "（暂无）"):
            continue
        rows.append(cells)
    return rows


def chapter_en(n):
    """返回该章纯英段的非空行（优先译文.md，无则对照版英文块）。"""
    p = BASE / "章节原文" / f"第{n}章" / f"第{n}章译文.md"
    if p.is_file():
        lines = nonempty_lines(p)
        return lines[1:] if lines else []
    return []


def recent_chapter(n):
    """n 未译时回退到最近一个已落地章。"""
    for i in range(n, 0, -1):
        if chapter_en(i):
            return i, chapter_en(i)
    return None, []


def build_context(upto, max_terms=120, max_poems=12, prev_paras=6, max_tok=2000):
    facts = parse_facts()
    glossary = L.load_glossary()
    roles = [f for f in facts if f["category"] == "角色"]
    others = [f for f in facts if f["category"] != "角色"]
    # 按首现章节数字排序，再按类别优先
    def first_no(f):
        m = re.search(r"(\d+)", f["first"])
        return int(m.group(1)) if m else 9999
    others.sort(key=lambda f: (0 if f["category"] in ("称谓官制", "器物母题") else 1, first_no(f)))
    others = others[:max_terms]
    poems = [f for f in facts if f["category"] == "诗词"][:max_poems]

    src_ch, en_lines = recent_chapter(upto)
    tail = en_lines[-prev_paras:] if en_lines else []

    out = io.StringIO()
    out.write(f"# 既定事实（截至第{upto}章 · 供外部模型使用）\n\n")
    out.write("> 以下是已在落地译文中反复出现、经人工确认的写法。优先级高于"
              "`01_GLOSSARY.md` 的 `[建议]` 状态，但**低于忠实原文**。"
              "若与本章原文语境冲突，先按原文译并在「译法建议」提出，由人工终裁。\n\n")
    out.write("## 1. 角色（拼写唯一，禁变体）\n\n")
    out.write("| 中文 | 英文定法 | 备注 |\n|---|---|---|\n")
    for f in roles:
        out.write(f"| {f['cn']} | {f['en']} | 来源 {f['first']} |\n")
    out.write("\n## 2. 称谓官制 / 器物母题 / 度量货币\n\n")
    out.write("| 中文 | 英文定法 | 来源 |\n|---|---|---|\n")
    for f in others:
        out.write(f"| {f['cn']} | {f['en']} | {f['first']} |\n")
    out.write("\n## 3. 诗词（已核验译法）\n\n")
    if poems:
        for f in poems:
            out.write(f"- {f['cn']} → {f['en']}（{f['first']}）\n")
    else:
        out.write("（暂无已核验条目；遇诗词先查权威译本，标 `[TN:]`。）\n")
    out.write("\n## 4. 上章结尾口吻参照\n\n")
    if src_ch:
        out.write(f"（来源：第{src_ch}章末 {len(tail)} 段）\n\n")
        for p in tail:
            out.write(p + "\n\n")
    else:
        out.write("（尚无已落地章节。）\n")

    text = out.getvalue()
    # token 上限保护：超了先裁 others（不裁角色/诗词）
    if est_tok(text) > max_tok and others:
        keep = max(1, len(others) // 2)
        return build_context(upto, max_terms=keep, max_poems=max_poems,
                            prev_paras=prev_paras, max_tok=max_tok)
    return {"text": text, "tok": est_tok(text), "src_ch": src_ch,
            "roles": len(roles), "terms": len(others)}


def drift_report(upto, chapters):
    """扫 chapters 的纯英版，按 glossary 词条统计同一中文的多种英文写法。"""
    glossary = L.load_glossary()
    by_cn = {}
    for e in glossary:
        by_cn.setdefault(e["cn"], []).append(e["en"])
    hits = {}
    for n in chapters:
        text = "\n".join(chapter_en(n))
        if not text:
            continue
        low = text.lower()
        for cn, ens in by_cn.items():
            found = []
            for en in set(ens):
                if en and re.search(r"(?<![A-Za-z])" + re.escape(en) + r"(?![A-Za-z])", low, re.I):
                    found.append(en)
            if len(found) > 1:
                hits.setdefault(cn, {"variants": {}, "chapters": []})["variants"][en] = found
                hits[cn]["chapters"].append(n)

    out = io.StringIO()
    out.write(f"# 术语漂移报告（章 {chapters[0]}–{chapters[-1]} · {datetime.now():%Y-%m-%d %H:%M:%S}）\n\n")
    out.write("> 只报告、不判罚。人工每批集中看一次：决定是否写入 `既定事实表.md` 或 `译文候选池.md`。\n\n")
    out.write("| 中文 | 出现的多种英文 | 章号 |\n|---|---|---|\n")
    if not hits:
        out.write("| （无漂移） | | |\n")
    for cn, v in sorted(hits.items()):
        ens = sorted({x for xs in v["variants"].values() for x in xs})
        chs = ",".join(map(str, sorted(set(v["chapters"]))))
        out.write(f"| {cn} | {' / '.join(ens)} | {chs} |\n")
    out.write(f"\n候选池待裁条目：{len(parse_pool())} 条（见 `译文候选池.md`）。\n")
    return out.getvalue()


def main():
    ap = argparse.ArgumentParser(description="滚动上下文/术语漂移报告")
    ap.add_argument("--upto", type=int, help="截至章号（含）")
    ap.add_argument("--drift-report", action="store_true", help="生成术语漂移报告")
    ap.add_argument("--chapters", help="漂移报告限定章号区间，如 91-100")
    ap.add_argument("--apply", action="store_true", help="写盘（默认 dry-run）")
    args = ap.parse_args()

    if args.drift_report:
        if args.chapters:
            m = re.match(r"(\d+)-(\d+)$", args.chapters)
            if not m:
                print("[ERROR] --chapters 格式应为 91-100")
                return 2
            chapters = list(range(int(m.group(1)), int(m.group(2)) + 1))
        elif args.upto:
            chapters = list(range(max(1, args.upto - 9), args.upto + 1))
        else:
            chapters = sorted(int(re.search(r"第(\d+)章", p).group(1)) for p in
                              glob.glob(str(BASE / "章节原文" / "第*章")))
        text = drift_report(args.upto or (chapters[-1] if chapters else 0), chapters)
        name = f"术语漂移报告_{datetime.now():%Y%m%d_%H%M%S}.md"
        target = DOCS / name
        print(f"[DRIFT] 章 {chapters[0]}-{chapters[-1]} · 报告 {name}")
        if args.apply:
            target.write_text(text, encoding="utf-8", newline="\n")
            print(f"[OK] 已写 {target.relative_to(BASE)}")
        else:
            print("[DRY-RUN] 加 --apply 落盘")
        return 0

    if not args.upto:
        print("[ERROR] 请给 --upto N 或 --drift-report")
        return 2
    r = build_context(args.upto)
    target = DOCS / f"投喂上下文_第{args.upto}章.md"
    print(f"[CTX] 截至第{args.upto}章 · {r['tok']} tok · 角色 {r['roles']} · 词条 {r['terms']} · 口吻来源 第{r['src_ch']}章")
    if args.apply:
        target.write_text(r["text"], encoding="utf-8", newline="\n")
        print(f"[OK] 已写 {target.relative_to(BASE)}")
    else:
        print("[DRY-RUN] 加 --apply 落盘")
        print("--- 预览 ---")
        print(r["text"][:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
