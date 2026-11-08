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

# G6 AI 高频词（蒸馏自 MTPE tools/lqa_scan.py + check_style.py）
AI_WORDS = [
    "delve", "leverage", "pivotal", "myriad", "tapestry", "testament",
    "navigate", "embark", "unravel", "profound", "intricate", "juxtapose",
    "beacon", "labyrinth", "cascade", "tranquil", "resilient", "robust",
    "underscore", "vibrant", "nestled", "realm", "epitome", "multifaceted",
    "in the realm of", "a testament to", "it is worth noting", "serves as",
    "functions as", "stands as a",
]
# 匹配用正则（短语按短语，整词按词边界）
AI_WORD_RES = [(w, re.compile(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", re.I))
               for w in AI_WORDS]

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
LY_ALLOW = {  # 非弱填充的 -ly 词，避免误报
    "family", "only", "reply", "apply", "supply", "ugly", "holy", "early",
    "likely", "lonely", "friendly", "lovely", "daily", "weekly", "monthly",
    "yearly", "elderly", "assembly", "anomaly", "monopoly", "ally", "jelly",
    "belly", "rally", "tally", "dolly", "holly", "polly", "gully", "telly",
}

# G7 重复用词阈值（次/章）
REPEAT_LIMITS = {"said": 3, "dark": 8, "immediately": 2, "very": 3, "quite": 3}

# G4 / G5 阈值（词数口径，非字符）
SENT_P0 = 40          # 复合句 P0 门槛（单句词数）
SENT_P1 = 40          # 长句登记门槛
SENT_P0_CONN = 3      # 连接词 ≥3 才判 P0（否则 P1，不误伤文学性长句）
PARA_P0 = 150         # 单段词数上限
EM_DASH_MAX = 2       # em dash 每章上限
TRIO_MAX = 1          # 三段式每章上限

GATE_ORDER = ["G3", "G4", "G5", "G6", "G7"]


# ---------------------------------------------------------------- 各项检查

def check_g4(paras):
    """G4 句长：单句 ≥40 词且连接词 ≥3 = P0；≥40 词但无从句堆叠 = P1。"""
    p0 = p1 = 0
    details = []
    for idx, para in enumerate(paras, 1):
        for sent in L.sentences(para):
            w = L.words(sent)
            if w < SENT_P1:
                continue
            conn = L.connectors(sent)
            if conn >= SENT_P0_CONN:
                p0 += 1
                details.append(("G4", idx, "P0",
                                f"复合句 {w} 词 + {conn} 连接词，必拆", sent))
            else:
                p1 += 1
                details.append(("G4", idx, "P1",
                                f"长句 {w} 词（连接词 {conn}），登记待裁", sent))
    return p0, p1, details


def check_g5(paras):
    """G5 段长：单段 >150 词 = P0。"""
    p0 = 0
    details = []
    for idx, para in enumerate(paras, 1):
        w = L.words(para)
        if w > PARA_P0:
            p0 += 1
            details.append(("G5", idx, "P0", f"段长 {w} 词 > {PARA_P0}", para))
    return p0, 0, details


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
    p0 = len(ai_hits)
    p1 = len(ly_hits)
    details = []
    for idx, w, para in ai_hits:
        details.append(("G6", idx, "P0", f"AI 高频词 [{w}]", para))
    for idx, w, para in ly_hits:
        details.append(("G6", idx, "P1", f"弱填充副词 [{w}] + 动词（人工判断是否可删）", para))
    if em > EM_DASH_MAX:
        p1 += 1
        details.append(("G6", 0, "P1", f"em dash {em} 处 > {EM_DASH_MAX}/章", ""))
    if trio > TRIO_MAX:
        p1 += 1
        details.append(("G6", 0, "P1", f"三段式 {trio} 处 > {TRIO_MAX}/章", ""))
    return p0, p1, details


def check_g7(paras):
    """重复用词。返回 (p0, p1, details)"""
    p0 = p1 = 0
    details = []
    for word, limit in REPEAT_LIMITS.items():
        rx = re.compile(r"(?<![A-Za-z])" + word + r"(?![A-Za-z])", re.I)
        n = sum(len(rx.findall(p)) for p in paras)
        if n > limit:
            p1 += 1
            details.append(("G7", 0, "P1",
                            f"[{word}] {n} 次/章 > {limit} 次/章", ""))
    return p0, p1, details


def check_g3(paras, glossary, coverage=False):
    """
    术语一致（默认口径，只报真问题）：
      - **锁定**词条的废弃变体残留 → 每处 P0（定译已定，残留即不一致）
      - **[建议]/[!]** 词条的变体残留 → INFO（定译未裁定，**禁止**据此判罚，
        符合红线「术语定译终裁权在用户」；这类问题应回到 glossary 裁定而非改稿）
      - 锁定词条定译零命中 → 仅 coverage=True 时计入 info。
        说明：一章未出现某词条属正常，全量统计会产出数百条噪音，
        故默认关闭；需要排查「术语表有但全项目没用上」时才开。
    返回 (p0, p1, details)；info 级问题 details 里标 "INFO" 不计 P1。
    """
    p0 = p1 = 0
    details = []
    for e in glossary:
        if e["variants"]:
            level = "P0" if e["status"] == L.STATUS_LOCKED else "INFO"
            for v in e["variants"]:
                n, hits = L.count_term(paras, v)
                if n:
                    if level == "P0":
                        p0 += n
                    details.append((("G3", 0, level,
                                     f"（{e['status']}）变体 [{e['cn']} → {v}] ×{n}"
                                     f"（首选 {e['preferred']}） 段{hits[:6]}", "")))
        elif coverage and e["status"] == L.STATUS_LOCKED:
            n, _ = L.count_term(paras, e["en"])
            if n == 0:
                details.append(("G3", 0, "INFO",
                                f"锁定词条 [{e['cn']} → {e['en']}] 本章零命中", ""))
    return p0, p1, details


# ---------------------------------------------------------------- 主流程

def scan_chapter(n, ch_dir, glossary, gates, coverage=False):
    bi = L.parse_bilingual(ch_dir)
    source, paras = L.en_paragraphs(ch_dir, prefer="对照版")
    res = {
        "章": n, "来源": source or "无", "段数": len(paras),
        "对照异常": len(bi["anomalies"]), "P0": 0, "P1": 0, "details": [],
    }
    if not paras:
        res["details"].append(("—", 0, "P1", "无英文段落（缺对照版或纯英版）", ""))
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
    for g in GATE_ORDER:
        if g not in gates:
            continue
        if g == "G3":
            a, b, d = check_g3(paras, glossary, coverage=coverage)
        elif g == "G4":
            a, b, d = check_g4(paras)
        elif g == "G5":
            a, b, d = check_g5(paras)
        elif g == "G6":
            a, b, d = check_g6(paras)
        else:
            a, b, d = check_g7(paras)
        res["P0"] += a
        res["P1"] += b
        res["details"].extend(d)
    return res


def main():
    ap = argparse.ArgumentParser(description="译文质量门禁扫描（G3-G7）")
    ap.add_argument("--chapter", default="", help="章号区间/列表，如 30-90（纯 ASCII）")
    ap.add_argument("--gates", default=",".join(GATE_ORDER), help="要跑的门禁，逗号分隔")
    ap.add_argument("--detail", action="store_true", help="打印逐条明细（默认只打按章表）")
    ap.add_argument("--g3-coverage", action="store_true",
                    help="额外统计「锁定词条本章零命中」（INFO，不计 P1；排查废词时才开）")
    ap.add_argument("--report", action="store_true", help="导出 项目文档/门禁扫描报告_<时间戳>.md")
    ap.add_argument("--fail-on", default="", choices=["", "P0"], help="出现该级别问题则退出码 1")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
