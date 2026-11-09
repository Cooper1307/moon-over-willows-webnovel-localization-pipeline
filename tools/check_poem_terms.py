# -*- coding: utf-8 -*-
"""
check_poem_terms.py — 诗词/典籍类术语「定译 vs 译文实际落地」一致性核对

用途（配合 skill `poem_web_verify`）：
  把 glossary 中诗词/典籍类词条的定译，与已译章节译文里**实际落地**的译法逐条对齐，
  自动挑出三类问题，避免"改了表没改稿"或"同一词条多种译法"：
    ① 定译与译文实际译法不一致
    ② 已译章内该词条完全未落地（可能未引用，或译法与定译完全对不上）
    ③ 同一中文术语在译文中出现多种译法（AI 痕迹 / 术语漂移）

用法：
  python tools/check_poem_terms.py                 # 全量对表（默认只打印）
  python tools/check_poem_terms.py --section 6      # 只查第六节「诗词与典故」
  python tools/check_poem_terms.py --apply          # 报告落盘到 项目文档/诗词术语落地核对_<时间戳>.md
  python tools/check_poem_terms.py --chapter 79      # 只看某章

工程规范：仅标准库；默认 dry-run（--apply 才写文件）；CLI 只收 ASCII 参数；
中文路径由 __file__ 推导；stdout 重配 UTF-8。
红线：只读 glossary 与译文 md，不修改任何译文或术语真源。
"""
import os
import re
import sys
import glob
import argparse
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTION_NAMES = {
    1: "角色人名", 2: "称谓与官制", 3: "地理与机构", 4: "世界观与武功",
    5: "衣食器物与文化项", 6: "诗词与典故", 7: "金句与口头禅锁定表",
}


def parse_glossary(path):
    """解析 glossary.md → [{section_no, title, zh, en, status, chapter, note}]"""
    text = open(path, encoding="utf-8").read()
    out = []
    cur_no, cur_title = None, None
    for ln in text.split("\n"):
        s = ln.strip()
        m = re.match(r"^##\s+([〇一二三四五六七八九])\s+(\S.*)$", s)
        if m:
            cn_no = "〇一二三四五六七八九".index(m.group(1))
            cur_no = 0 if m.group(1) == "〇" else cn_no
            cur_title = m.group(2).strip()
            continue
        if not s.startswith("|") or s.startswith("|---"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4:
            continue
        zh, en, status, chap = cells[0], cells[1], cells[2], cells[3]
        if zh in ("中文", "") or "英文" in cells[:2]:
            continue
        out.append({"no": cur_no, "title": cur_title, "zh": zh, "en": en,
                    "status": status, "chapter": chap,
                    "note": cells[4] if len(cells) > 4 else ""})
    return out


def en_core(en):
    """取英文定译主干：先剥尾部括注，再去引号，取第一个候选。"""
    e = en.strip()
    e = re.sub(r"\s*\([^)]*\)\s*$", "", e).strip()
    e = e.strip('"').strip()
    e = e.split("/")[0].strip()
    return e.strip('"').strip()


def load_bilingual():
    """{章号: 对照版全文}（用于判断中文词条是否真被引用）"""
    out = {}
    for md in glob.glob(os.path.join(REPO, "章节原文", "第*章", "第*章初译_对照.md")):
        m = re.search(r"第(\d+)章", md)
        if not m:
            continue
        try:
            out[int(m.group(1))] = open(md, encoding="utf-8").read()
        except Exception:
            pass
    return out


def load_translations():
    """{章号: 译文全文}"""
    out = {}
    for md in glob.glob(os.path.join(REPO, "章节原文", "第*章", "第*章译文.md")):
        m = re.search(r"第(\d+)章", md)
        if not m:
            continue
        try:
            out[int(m.group(1))] = open(md, encoding="utf-8").read()
        except Exception:
            pass
    return out


def find_variants(zh, texts):
    """在译文中找该中文词条的英文落地译法（取所在英文句片段）。"""
    variants = {}
    for ch, t in texts.items():
        if zh not in t:
            continue
        for m in re.finditer(r"[^\n]{0,120}" + re.escape(zh) + r"[^\n]{0,120}", t):
            frag = m.group(0)
            # 提取中文词两侧的英文（译文里中文词常被译名替换）
            idx = frag.find(zh)
            left = frag[max(0, idx - 90):idx]
            right = frag[idx + len(zh): idx + len(zh) + 90]
            left = re.findall(r"[A-Za-z][A-Za-z'’\-\.\* ]{3,}", left)
            right = re.findall(r"[A-Za-z][A-Za-z'’\-\.\* ]{3,}", right)
            cand = " ".join(left[-3:] + right[:3]).strip()
            if cand:
                variants.setdefault(cand[:70], set()).add(ch)
    return variants


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", type=int, default=None, help="只查某一节（1-7）")
    ap.add_argument("--chapter", type=int, default=None, help="只看某章")
    ap.add_argument("--apply", action="store_true", help="报告落盘（缺省只打印）")
    args = ap.parse_args()

    gpath = os.path.join(REPO, "glossary.md")
    terms = parse_glossary(gpath)
    if args.section:
        terms = [t for t in terms if t["no"] == args.section]
    texts = load_translations()
    biling = load_bilingual()
    max_ch = max(texts) if texts else 0

    rows = []
    for t in terms:
        core = en_core(t["en"])
        if not core or len(core) < 3:
            continue
        hit_ch = [ch for ch, tx in texts.items() if core in tx]
        # 中文词条在对照版里是否被引用（引用了但没按定译落地 = 真不一致）
        cited_ch = [ch for ch, tx in biling.items() if t["zh"] in tx]
        variants = find_variants(t["zh"], texts)
        issue = []
        if hit_ch:
            if len(variants) > 1:
                issue.append("译文中出现多种译法")
        elif cited_ch:
            issue.append("已引用但未按定译落地（译法不一致）")
        else:
            m = re.search(r"第(\d+)章", t["chapter"])
            first = int(m.group(1)) if m else 9999
            issue.append("尚未译到" if first > max_ch else "已译区内未引用")
        rows.append({"term": t, "core": core, "hit": hit_ch, "cited": cited_ch,
                     "variants": variants, "issue": issue})

    def fmt(t):
        z = t["zh"]
        return z if z.startswith("《") else "《%s》" % z

    print("=" * 78)
    print("诗词/典籍类术语落地一致性核对")
    print("=" * 78)
    print("glossary 词条 %d · 已译章 %d（1~%d）· 待查 %d" % (len(terms), len(texts), max_ch, len(rows)))

    n_ok = n_issue = 0
    lines = []
    for r in rows:
        t = r["term"]
        tag = "OK " if not r["issue"] else "!! "
        if r["issue"]:
            n_issue += 1
        else:
            n_ok += 1
        head = "%s%-18s 定译=%-30s %s" % (tag, fmt(t)[:18], r["core"][:30], t["status"])
        print(head)
        if r["issue"]:
            print("      问题: " + " / ".join(r["issue"]))
            print("      落地章: %s" % (r["hit"][:8] if r["hit"] else "无"))
            for v, chs in list(r["variants"].items())[:3]:
                print("      实际译法: %s  (章 %s)" % (v, sorted(chs)[:5]))
            lines.append((head, r))
    print("-" * 78)
    print("一致 %d · 需核 %d" % (n_ok, n_issue))

    if args.apply:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = os.path.join(REPO, "项目文档", "诗词术语落地核对_%s.md" % ts)
        body = ["# 诗词/典籍类术语落地一致性核对", "",
                "> 生成：%s · 工具 `tools/check_poem_terms.py`（只读检查，不改译文与术语真源）" % ts,
                "> 已译章：1~%d · glossary 词条 %d · 一致 %d · 需核 %d" % (max_ch, len(terms), n_ok, n_issue), "",
                "| 词条 | 定译 | 状态 | 落地章 | 问题 | 实际译法样本 |",
                "|---|---|---|---|---|---|"]
        for head, r in lines:
            t = r["term"]
            vs = "；".join(list(r["variants"].keys())[:2]) or "—"
            body.append("| %s | %s | %s | %s | %s | %s |" % (
                fmt(t), r["core"], t["status"],
                ",".join(str(x) for x in r["hit"][:8]) or "无",
                " / ".join(r["issue"]), vs))
        body.append("")
        body.append("> 处置：以上均为 `[建议]`，是否统一及采用哪个译名由用户裁定（见 skill `poem_web_verify`）。")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write("\n".join(body) + "\n")
        print("[OK] 报告 → %s" % out)
    else:
        print("[提示] 加 --apply 才落盘报告。")


if __name__ == "__main__":
    main()
