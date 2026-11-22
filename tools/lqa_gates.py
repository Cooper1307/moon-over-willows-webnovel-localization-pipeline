#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lqa_gates.py — 译文质量门禁扫描器（门禁 G3 / G4 / G5 / G6 / G7）

对每章英文译文跑 5 组机器可判定的门禁，输出「按章量化表 + 明细」，
供 novel-lqa-reviewer 在审校前/审校后各跑一次（落地前后必复跑）。

门禁定义（对齐 工程化改造方案_借鉴剧本MTPE.md §3.6）：
  G0 真源完好   —— 对照版中文字符数 ≥50（P0：真源中文丢失，禁止据此审校）
                  ⚠ 实测已命中 第44/47 章：对照版文件整份为纯英文，中文段落丢失
  G3 术语一致   —— **锁定**词条的废弃变体出现次数 = 0（P0）
                  [建议]/[!] 词条的变体 → INFO（定译未裁定，禁止据此判罚）
                  锁定词条零命中统计 → 仅 --g3-coverage 开启
  G4 句长       —— 单句 ≥40 词 且 同句连接词 ≥3 = P0（必拆）
                  单句 ≥40 词但无从句堆叠 = P1（登记待裁，不误伤文学性长句）
  G5 段长       —— 单段 >150 词 = P0
  G6 去 AI 痕迹  —— AI 高频词命中 = 0（P0）；**副词 + 动词**连用的 -ly 填充副词
                  （P1，人工判断）；em dash ≤2/章（P1）；三段式 a, b, and c ≤1/章（P1）
  G7 重复用词    —— said >3/章 · dark >8/章 · immediately >2/章 · very/quite >3/章（P1）

用法（全部参数为纯 ASCII，避免 PowerShell 中文路径 GBK 乱码）：
  python tools/lqa_gates.py                      # 扫全量 90 章
  python tools/lqa_gates.py --chapter 30-90       # 只扫 30~90 章
  python tools/lqa_gates.py --chapter 30-90 --detail
  python tools/lqa_gates.py --chapter 30-90 --gates G4,G5
  python tools/lqa_gates.py --report              # 导出 项目文档/门禁扫描报告_<时间戳>.md
  python tools/lqa_gates.py --chapter 30-90 --fail-on P0   # 有 P0 时退出码 1（可接 CI）

设计约束（照搬工作区脚本规范）：
  默认只读（dry-run）；本脚本**永不修改译文**，只报告。
  仅标准库；路径由 __file__ 推导；stdout 重配 UTF-8。
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chapter_lib as L  # noqa: E402

# ---------------------------------------------------------------- 词表

# G6 AI 高频词（2026-11-21 古装适配：从 MTPE 短剧词表拆两组）
# AI_HARD = 在中文网文英译里几乎无合法用例 → P1（风格提醒，不再阻断落地）
# AI_GENRE_OK = 古装/仙侠合法常用词（"境界"=realm 等）→ 完全不报
AI_HARD = [
    "delve", "leverage", "pivotal", "myriad", "tapestry", "testament",
    "juxtapose", "epitome", "multifaceted",
    "in the realm of", "a testament to", "it is worth noting", "serves as",
    "functions as", "stands as a",
]
AI_GENRE_OK = [
    "navigate", "embark", "unravel", "profound", "intricate", "beacon",
    "labyrinth", "cascade", "tranquil", "resilient", "robust", "underscore",
    "vibrant", "nestled", "realm",
]
AI_WORDS = AI_HARD + AI_GENRE_OK  # 兼容旧引用
# 匹配用正则（短语按短语，整词按词边界）
AI_WORD_RES = [(w, re.compile(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", re.I))
               for w in AI_HARD]

# G6 三段式：句内 "A, B, and C"（两个逗号 + and/或）
TRIO_RE = re.compile(r"[^,.;:]{3,},\s*[^,.;:]{3,},\s*(?:and|or|以及|还有)\s+[^,.;:]{3,}", re.I)

# G6 -ly 弱填充副词（白名单排除非副词用法）
LY_FILLER = [
    "slowly", "quietly", "softly", "gently", "firmly", "deeply", "truly",
    "simply", "clearly", "easily", "quickly", "carefully", "heavily",
    "sharply", "merely", "purely", "slightly", "partly", "mostly", "largely",
    "commonly", "typically", "generally", "basically", "actually",
    "essentially", "relatively", "somewhat", "swiftly", "silently",
    "tightly", "warmly", "coldly", "brightly", "dimly", "steadily",
]
LY_RES = [(w, re.compile(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", re.I))
          for w in LY_FILLER]
LY_ALLOW = {  # 用户 MEMORY.md L17 明确允许 + 非副词词形
    "family", "only", "reply", "apply", "supply", "ugly", "holy", "early",
    "likely", "lonely", "friendly", "lovely", "daily", "weekly", "monthly",
    "yearly", "elderly", "assembly", "anomaly", "monopoly", "ally", "jelly",
    "belly", "rally", "tally", "dolly", "holly", "polly", "gully", "telly",
    "truly", "perfectly", "really", "entirely", "miraculously", "actually",
    "essentially", "relatively", "somewhat", "merely", "purely",
}

# G7 重复用词（2026-11-21：said 是对话正常标签，全部降 INFO，只报告不判罚）
REPEAT_LIMITS = {"said": 12, "dark": 20, "immediately": 6, "very": 8, "quite": 6}
REPEAT_LEVEL = "INFO"

# G4 / G5 阈值（2026-11-21：风格类退出 P0；段长与 1:1 红线冲突，只报告）
SENT_P0 = 60          # ≥60 词且连接词 ≥6 → P1
SENT_P1 = 40          # ≥40 词登记 INFO
SENT_P0_CONN = 6
PARA_P0 = 200         # >200 词 → INFO（段落由中文决定，译者无权合并）
EM_DASH_MAX = 20
TRIO_MAX = 5

# G4 专用严格连接词表（不动 chapter_lib 的共享正则，避免影响其它脚本）
CONNECTOR_STRICT = {
    "and", "but", "or", "yet", "because", "although", "though", "while",
    "when", "where", "which", "who", "whom", "if", "unless", "until",
    "after", "before",
}

GATE_ORDER = ["G3", "G4", "G5", "G6", "G7", "G8"]


# ---------------------------------------------------------------- 各项检查

def _strict_connectors(sent):
    """G4 专用连接词计数：去掉 that/for/so/since 的混计。"""
    words = re.findall(r"[A-Za-z]+", sent.lower())
    return sum(1 for w in words if w in CONNECTOR_STRICT)


def check_g4(paras):
    """G4 句长（2026-11-21）：≥60 词且严格连接词 ≥6 → P1；40–59 → INFO；无 P0。"""
    p0 = 0
    p1 = 0
    infos = []
    details = []
    for idx, para in enumerate(paras, 1):
        for sent in L.sentences(para):
            w = L.words(sent)
            if w < SENT_P1:
                continue
            conn = _strict_connectors(sent)
            if w >= SENT_P0 and conn >= SENT_P0_CONN:
                p1 += 1
                details.append(("G4", idx, "P1",
                                f"超长复合句 {w} 词 + {conn} 连接词（人工判断是否可拆）", sent))
            else:
                infos.append((idx, f"长句 {w} 词（连接词 {conn}）"))
    return p0, p1, details, infos


def check_g5(paras):
    """G5 段长（2026-11-21）：>200 词 → INFO；段落切分由中文决定，不判罚。"""
    infos = []
    for idx, para in enumerate(paras, 1):
        w = L.words(para)
        if w > PARA_P0:
            infos.append((idx, f"段长 {w} 词 > {PARA_P0}（中文原文决定段界，仅提示）"))
    return 0, 0, [], infos


def check_g6(paras):
    """
    去 AI 痕迹。返回 (p0, p1, details)

    P0 只收「确凿的 AI 腔词」（delve / tapestry / pivotal 等）——
       这类词在中文网文英译里几乎无合法用例。
    P1 收「需人工判断」的弱填充副词：**只看 副词 + 动词 连用**（如 quickly walked），
       单独的 quickly / truly / actually 是正常文学用词，不报。
       （实测早期版本把全部 -ly 词当 P0，误报 570 处，已修正。）
    """
    ai_hits = []      # (段号, 词, 原文)
    ly_hits = []      # (段号, 副词, 原文)
    em = 0
    trio = 0
    for idx, para in enumerate(paras, 1):
        for w, rx in AI_WORD_RES:
            if rx.search(para):
                ai_hits.append((idx, w, para))
        for w, rx in LY_RES:
            for m in rx.finditer(para):
                if m.group(0).lower() in LY_ALLOW:
                    continue
                # 仅当 -ly 副词后紧跟动词形态（ed/ing/s）才算填充副词
                tail = para[m.end():m.end() + 18]
                if re.match(r"\s+\w+(?:ed|ing|s)\b", tail):
                    ly_hits.append((idx, m.group(0), para))
        em += para.count("—") + para.count("–")
        trio += len(TRIO_RE.findall(para))
    p0 = 0  # AI 词表已全部降级：AI_HARD→P1，AI_GENRE_OK→不报
    p1 = len(ai_hits) + len(ly_hits)
    infos = []
    details = []
    for idx, w, para in ai_hits:
        details.append(("G6", idx, "P1", f"AI 高频词 [{w}]（人工判断）", para))
    for idx, w, para in ly_hits:
        details.append(("G6", idx, "P1", f"弱填充副词 [{w}] + 动词（人工判断是否可删）", para))
    if em > EM_DASH_MAX:
        p1 += 1
        details.append(("G6", 0, "P1", f"em dash {em} 处 > {EM_DASH_MAX}/章", ""))
    if trio > TRIO_MAX:
        p1 += 1
        details.append(("G6", 0, "P1", f"三段式 {trio} 处 > {TRIO_MAX}/章", ""))
    return p0, p1, details, infos


def check_g7(paras):
    """重复用词（2026-11-21）：全部降 INFO，只报告，不判罚。"""
    infos = []
    for word, limit in REPEAT_LIMITS.items():
        rx = re.compile(r"(?<![A-Za-z])" + word + r"(?![A-Za-z])", re.I)
        n = sum(len(rx.findall(p)) for p in paras)
        if n > limit:
            infos.append((0, f"[{word}] {n} 次/章 > {limit} 次/章（仅提示）"))
    return 0, 0, [], infos


def check_g3(paras, glossary, coverage=False):
    """
    术语一致（2026-11-21：全部降 INFO，只报告、不判罚）：
      465 条"锁定"多为脚本按频次自动升级、非人工裁定；变体从备注列自然语言正则抠出，
      历史误伤严重（曾 7168 处）。改由 build_context.py --drift-report 在批次末集中人工看。
    返回 (p0, p1, details, infos)；p0/p1 恒 0。
    """
    details = []
    infos = []
    for e in glossary:
        if e["variants"]:
            for v in e["variants"]:
                n, hits = L.count_term(paras, v)
                if n:
                    infos.append((0, f"（{e['status']}）变体 [{e['cn']} → {v}] ×{n}"
                                     f"（首选 {e['preferred']}） 段{hits[:6]}"))
        elif coverage and e["status"] == L.STATUS_LOCKED:
            n, _ = L.count_term(paras, e["en"])
            if n == 0:
                infos.append((0, f"锁定词条 [{e['cn']} → {e['en']}] 本章零命中"))
    return 0, 0, [], infos


# ---------------------------------------------------------------- 主流程

def scan_chapter(n, ch_dir, glossary, gates, coverage=False):
    bi = L.parse_bilingual(ch_dir)
    source, paras = L.en_paragraphs(ch_dir, prefer="对照版")
    res = {
        "章": n, "来源": source or "无", "段数": len(paras),
        "对照异常": len(bi["anomalies"]), "P0": 0, "P1": 0, "details": [],
    }
    if not paras:
        # 2026-11-10：整章无译文属「遗漏」，必须计入 P1。
        # 旧实现只写 details 不加计数，会把空章误列入「全清」，与零遗漏验收冲突。
        res["P1"] += 1
        res["details"].append(("—", 0, "P1", "整章无英文段落（缺对照版或纯英版）＝待译遗漏", ""))
        return res
    # 真源损坏：对照版存在却几乎无中文 = 中文段落丢失，唯一真源已失效
    if bi["path"] is not None:
        cn = len(L.CJK_RE.findall(bi["path"].read_text(encoding="utf-8-sig")))
        if cn < 50:
            res["P0"] += 1
            res["details"].append((
                "G0", 0, "P0",
                f"对照版中文缺失（全文仅 {cn} 个中文字符）——唯一真源已损坏，"
                f"不得据此审校；需从 第X章原文.md 重建", ""))
    # G8 译文密度：英文段数 ÷ 中文段数。外部模型偶发「整章压成几段」的摘要式输出，
    # 中文覆盖与配对检查只看中文侧，抓不到它（2026-11-22 实测 78 章漏网，
    # 如第301章 103 中文段只配 8 英文段）。比率 < 0.35 判 P0，0.35–0.5 判 P1。
    if "G8" in gates and ch_dir is not None:
        try:
            origin = next((f for f in ch_dir.glob("*原文.md")), None)
            if origin is not None:
                cn_paras = max(len([l for l in origin.read_text(encoding="utf-8-sig").splitlines()
                                    if l.strip()]) - 1, 1)
                en_paras = max(len([p for p in paras if p.strip()]), 1)
                ratio = en_paras / cn_paras
                if ratio < 0.35:
                    res["P0"] += 1
                    res["details"].append((
                        "G8", 0, "P0",
                        f"疑似摘要式输出：英文 {en_paras} 段 ÷ 中文 {cn_paras} 段 = {ratio:.2f}"
                        f"（<0.35），需整章重译", ""))
                elif ratio < 0.5:
                    res["P1"] += 1
                    res["details"].append((
                        "G8", 0, "P1",
                        f"译文偏薄：英文 {en_paras} 段 ÷ 中文 {cn_paras} 段 = {ratio:.2f}（人工抽查）", ""))
        except Exception:
            pass
    for g in GATE_ORDER:
        if g not in gates:
            continue
        if g == "G8":
            continue  # G8 已在上方按密度单独计算
        if g == "G3":
            a, b, d, inf = check_g3(paras, glossary, coverage=coverage)
        elif g == "G4":
            a, b, d, inf = check_g4(paras)
        elif g == "G5":
            a, b, d, inf = check_g5(paras)
        elif g == "G6":
            a, b, d, inf = check_g6(paras)
        else:
            a, b, d, inf = check_g7(paras)
        res["P0"] += a
        res["P1"] += b
        res["details"].extend(d)
        res["details"].extend(("G" + g[1:], 0, "INFO", msg, "") for _, msg in inf)
    return res


def main():
    ap = argparse.ArgumentParser(description="译文质量门禁扫描（G3-G7）")
    ap.add_argument("--chapter", default="", help="章号区间/列表，如 30-90（纯 ASCII）")
    ap.add_argument("--gates", default=",".join(GATE_ORDER), help="要跑的门禁，逗号分隔")
    ap.add_argument("--detail", action="store_true", help="打印逐条明细（默认只打按章表）")
    ap.add_argument("--g3-coverage", action="store_true",
                    help="额外统计「锁定词条本章零命中」（INFO，不计 P1；排查废词时才开）")
    ap.add_argument("--report", action="store_true", help="导出 项目文档/门禁扫描报告_<时间戳>.md")
    ap.add_argument("--fail-on", default="", choices=["", "P0", "P1"],
                    help="出现该级别问题则退出码 1；P1 表示要求 P0 与 P1 同时为 0")
    args = ap.parse_args()

    lo, hi = L.parse_range(args.chapter)
    gates = {g.strip().upper() for g in args.gates.split(",") if g.strip().upper() in GATE_ORDER}
    if not gates:
        print("[ERROR] 未指定有效门禁，可选：%s" % ",".join(GATE_ORDER))
        return 2

    glossary = L.load_glossary()
    dirs = L.chapter_dirs(lo, hi)
    if not dirs:
        print("[ERROR] 未找到章节目录（范围 %s-%s）" % (lo, hi))
        return 2

    rows = []
    for n, d in dirs:
        rows.append(scan_chapter(n, d, glossary, gates, coverage=args.g3_coverage))

    total_p0 = sum(r["P0"] for r in rows)
    total_p1 = sum(r["P1"] for r in rows)
    total_info = sum(1 for r in rows for d in r["details"] if d[2] == "INFO")
    span = f"{lo}~{hi}" if lo or hi else "全量"
    clean = [r for r in rows if r["P0"] == 0 and r["P1"] == 0]

    print("=" * 100)
    print(f"译文质量门禁扫描（{' '.join(sorted(gates))}）  范围：{span}  "
          f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print(f"{'章节':<8}{'来源':<8}{'段数':>6}{'异常':>6}{'P0':>6}{'P1':>7}  首要问题")
    print("-" * 100)
    for r in rows:
        d0 = [d for d in r["details"] if d[2] == "P0"]
        first = d0[0][3] if d0 else (r["details"][0][3] if r["details"] else "✔ 通过")
        print(f"第{r['章']}章{'':<3}{r['来源']:<8}{r['段数']:>6}{r['对照异常']:>6}"
              f"{r['P0']:>6}{r['P1']:>7}  {first[:44]}")
    print("-" * 100)
    print(f"  扫描 {len(rows)} 章 · 全清 {len(clean)} 章 · P0 合计 {total_p0} · P1 合计 {total_p1}")

    if args.detail:
        print("\n" + "=" * 100)
        print("逐条明细")
        print("=" * 100)
        for r in rows:
            for g, idx, lvl, msg, snippet in r["details"]:
                loc = f"第{r['章']}章" + (f" 段{idx}" if idx else "")
                print(f"[{g}][{lvl}] {loc} {msg}")
                if snippet:
                    print(f"        > {snippet[:110]}")

    if args.report:
        L.DOCS.mkdir(parents=True, exist_ok=True)
        out = L.DOCS / f"门禁扫描报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        lines = ["# 译文质量门禁扫描报告", "",
                 f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                 f"> 门禁：{', '.join(sorted(gates))} · 范围：{span} · 术语表 {len(glossary)} 词条",
                 f"> 模式：只读扫描，未修改任何译文", "",
                 "## 统计", "",
                 f"- 扫描章节：{len(rows)}",
                 f"- 全清章节：{len(clean)}",
                 f"- P0 合计：{total_p0}",
                 f"- P1 合计：{total_p1}", "", "## 按章汇总", "",
                 "| 章节 | 来源 | 段数 | 对照异常 | P0 | P1 | 首要问题 |",
                 "|---|---|---|---|---|---|---|"]
        for r in rows:
            d0 = [d for d in r["details"] if d[2] == "P0"]
            first = d0[0][3] if d0 else (r["details"][0][3] if r["details"] else "✔ 通过")
            lines.append(f"| 第{r['章']}章 | {r['来源']} | {r['段数']} | {r['对照异常']} | "
                         f"{r['P0']} | {r['P1']} | {first.replace('|', '/')} |")
        lines += ["", "## 明细", "", "| 级别 | 门禁 | 位置 | 说明 |",
                  "|---|---|---|---|"]
        for r in rows:
            for g, idx, lvl, msg, snippet in r["details"]:
                loc = f"第{r['章']}章" + (f" 段{idx}" if idx else "")
                lines.append(f"| {lvl} | {g} | {loc} | {msg.replace('|', '/')} |")
        lines.append("")
        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n[OK] 报告已写入：{out}")

    if args.fail_on == "P0" and total_p0 > 0:
        print(f"\n[FAIL] P0 = {total_p0}（--fail-on P0 触发，退出码 1）")
        return 1
    if args.fail_on == "P1" and (total_p0 > 0 or total_p1 > 0):
        print(f"\n[FAIL] P0 = {total_p0} · P1 = {total_p1}"
              f"（--fail-on P1 要求两者同时为 0，退出码 1）")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
