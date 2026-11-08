#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
review_batch.py — 审校底稿生成器（TODO build-workflow / 支撑 T8 逐章逐段审校）

为一批章节（默认 5 章/批，Q4 校准口径）生成一份「审校底稿」落 项目文档/，
供 novel-reviewer 按批内审校流程使用：
  机器门禁发现（G0/G3-G7 + 对照异常）预填成审校清单，
  逐段中英对照（段号 + 行号锚点）供逐段精读，
  报告/落地表骨架 + 批内完成门（复跑门禁）勾选项。

底稿是时点快照：落地 Edit 会移动行号，落地前必须以中文行为锚重新定位
（novel-reviewer 红线）；审校修改一律落在对照版，本工具只读不写章节文件。

用法（全部参数为纯 ASCII，避免 PowerShell 中文路径 GBK 乱码）：
  python tools/review_batch.py --chapter 41-45          # 批次预览（stdout，dry-run）
  python tools/review_batch.py --chapter 41-45 --emit   # 写底稿 项目文档/审校底稿_第41-45章_<时间戳>.md
  python tools/review_batch.py --chapter 41,42,44       # 非连续章号也可（取 min-max 范围内实际存在的章）
  python tools/review_batch.py                          # 全量总览预览（不 emit，底稿须按批指定 --chapter）

设计约束（照搬工作区脚本规范）：
  默认 dry-run（不写任何文件）；仅标准库；路径由 __file__ 推导；stdout 重配 UTF-8。
  门禁发现复用 lqa_gates.scan_chapter，不重复实现判定逻辑。
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chapter_lib as L        # noqa: E402
import lqa_gates as G          # noqa: E402

# 纯英版含人工润色/补写的章节（交接红线 5）：禁 extract_pure_en --force / sync --force 覆盖
POLISHED_PURE_EN = {44, 47}


def cell(text, limit=160):
    """表格单元格安全化：去换行、转义竖线、超长截断。"""
    s = (text or "").replace("\n", " ").replace("|", "/").strip()
    return s[:limit] + ("…" if len(s) > limit else "")


def rel(path):
    """章节文件在底稿中的显示路径（相对项目根）。"""
    try:
        return Path(path).resolve().relative_to(L.BASE).as_posix()
    except (ValueError, TypeError):
        return str(path)


def chapter_assets(ch_dir):
    """收集该章现有产物文件（对照版/译文/术语与人设/质量评估），返回 [(标签, 相对路径 or None)]。"""
    tags = [("对照版（唯一真源）", L.BILINGUAL_RE), ("译文（派生物）", None),
            ("术语与人设", None), ("翻译质量评估（旧）", None)]
    out = []
    files = [f.name for f in ch_dir.iterdir() if f.is_file()]
    bilingual = next((f for f in files if L.BILINGUAL_RE.search(f)), None)
    pure_en = next((f for f in files if L.PURE_EN_RE.match(f)), None)
    roles = next((f for f in files if "术语与人设" in f), None)
    quality = next((f for f in files if "质量评估" in f), None)
    out.append((tags[0][0], f"{ch_dir.name}/{bilingual}" if bilingual else None))
    out.append((tags[1][0], f"{ch_dir.name}/{pure_en}" if pure_en else None))
    out.append((tags[2][0], f"{ch_dir.name}/{roles}" if roles else None))
    out.append((tags[3][0], f"{ch_dir.name}/{quality}" if quality else None))
    return out


def scan_batch(lo, hi, glossary, gates):
    """对范围内实际存在的章逐章跑门禁扫描。

    返回 [(章号, 目录, bi, scan_res, 原文段数)]；
    原文段数复用 sync_bilingual.read_original（与门禁同口径，标题行不计）。
    """
    sync = L._load_sync_module()
    out = []
    for n, d in L.chapter_dirs(lo, hi):
        bi = L.parse_bilingual(d)
        orig_n, _paras, _has = sync.read_original(d)
        res = G.scan_chapter(n, d, glossary, gates)
        out.append((n, d, bi, res, orig_n))
    return out


def build_draft(rows, lo, hi, glossary):
    """生成底稿全文（list[str]）。rows = scan_batch 结果。"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    n_lock = sum(1 for e in glossary if e["status"] == L.STATUS_LOCKED)
    n_disp = sum(1 for e in glossary if e["status"] == L.STATUS_DISPUTE)
    n_sug = sum(1 for e in glossary if e["status"] == L.STATUS_SUGGEST)
    total_pairs = sum(len(bi["pairs"]) for _n, _d, bi, _r, _o in rows)
    total_p0 = sum(r["P0"] for _n, _d, _bi, r, _o in rows)
    total_p1 = sum(r["P1"] for _n, _d, _bi, r, _o in rows)
    span = f"第{lo}-{hi}章" if lo or hi else "全量"

    md = []
    md.append(f"# 审校底稿：{span}")
    md.append("")
    md.append(f"> 生成：`tools/review_batch.py` @ {ts} · 只读生成，未改动任何章节文件")
    md.append(f"> 消费者：novel-reviewer 批内审校流程（基线 → 逐章审校 → 用户确认后落地 → 复跑门禁）")
    md.append(f"> ⚠ 行号/段号为生成时点快照；落地 Edit 前必须以中文行为锚重新定位真实行号")
    md.append(f"> 术语表：glossary.md 共 {len(glossary)} 词条"
              f"（锁定 {n_lock} · [!]待裁定 {n_disp} · [建议] {n_sug}）")
    md.append("> 前置门（TODO T8）：Q11 半角标点口径与术语裁定未定前，**只出报告不落地红标**"
              "（Q11 已溯源、建议 A 归一全角，待用户批准；状态详见 TODO.md Q 清单）")
    md.append(f"> 工作量：逐段对照 {total_pairs} 组 · 机器发现 P0 {total_p0} / P1 {total_p1}"
              f"（供 Q4 批次大小校准）")
    md.append("")

    # 一、批次总览
    md.append("## 一、批次总览")
    md.append("")
    md.append("| 章节 | 格式 | 原文段 | 对照段 | 对照异常 | P0 | P1 | 术语与人设 | 备注 |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for n, _d, bi, r, orig_n in rows:
        roles = (p for t, p in chapter_assets(_d) if t == "术语与人设")
        has_roles = next(roles, None) is not None
        notes = []
        if orig_n and orig_n != len(bi["pairs"]):
            notes.append(f"⚠ 段数不符：原文 {orig_n} ≠ 对照 {len(bi['pairs'])}（疑似漏译，见发现清单）")
        if n in POLISHED_PURE_EN:
            notes.append("纯英版含人工润色，禁 --force 重派生")
        if not has_roles:
            notes.append("缺术语与人设（基线不齐，流程第 1 步先补读）")
        if bi["kind"] == "EN-only":
            notes.append("⚠ 真源损坏（EN-only），禁止据此审校")
        md.append(f"| 第{n}章 | {bi['kind']} | {orig_n} | {len(bi['pairs'])} | {len(bi['anomalies'])} "
                  f"| {r['P0']} | {r['P1']} | {'✔' if has_roles else '✘'} | {'；'.join(notes) or '—'} |")
    md.append("")

    # 二、机器门禁发现
    md.append("## 二、机器门禁发现（审校清单，人工逐条给结论）")
    md.append("")
    md.append("> 机器判定只是线索：P1 需人工判断，反向护栏照旧（不把正确但陌生的表达判错）。")
    md.append("")
    for n, _d, bi, r, _orig_n in rows:
        md.append(f"### 第{n}章")
        md.append("")
        items = []
        for ln, reason in bi["anomalies"]:
            items.append(("P0?", "异常", f"L{ln} {reason}", ""))
        for g, idx, lvl, msg, snippet in r["details"]:
            loc = f"段{idx}" if idx else ""
            items.append((lvl, g, f"{loc} {msg}".strip(), snippet))
        if not items:
            md.append("机器门禁零命中，无对照异常。")
        else:
            md.append("| # | 级别 | 来源 | 说明 | 片段 | 审校结论（填） |")
            md.append("|---|---|---|---|---|---|")
            for i, (lvl, src, msg, snippet) in enumerate(items, 1):
                md.append(f"| {i} | {lvl} | {src} | {cell(msg)} | {cell(snippet, 90)} | |")
        md.append("")

    # 三、逐章审校工作区
    md.append("## 三、逐章审校工作区")
    md.append("")
    md.append("> 【中】= 原文锚点（禁改）；【英】= 现译（审校对象，改这里落对照版）。"
              "含 `<font>` 红标的段 = 已落地存量红标，与本次新增建议区分。")
    md.append("")
    for n, d, bi, r, _orig_n in rows:
        md.append(f"### 第{n}章")
        md.append("")
        for tag, p in chapter_assets(d):
            md.append(f"- {tag}：{p if p else '—缺—'}")
        md.append("")
        if bi["path"] is None:
            md.append("无对照版，审校不可进行（先补真源）。")
            md.append("")
            continue
        if not bi["pairs"]:
            md.append("对照版无可配对段落（EN-only 真源损坏态），禁止据此审校。")
            md.append("")
            continue
        md.append("#### 逐段对照")
        md.append("")
        for i, (zh, en, line) in enumerate(bi["pairs"], 1):
            md.append(f"**段 {i}**（L{line}）")
            md.append("")
            md.append("【中】" + zh.replace("\n", " "))
            md.append("")
            md.append("【英】" + en.replace("\n", " "))
            md.append("")
        md.append("#### 审校记录（人工填写）")
        md.append("")
        md.append("**总评**：")
        md.append("")
        md.append("**发现明细**（定位填段号；级别 P0 致命 / P1 严重 / P2 流畅 / P3 润色）：")
        md.append("")
        md.append("| 定位 | 中文摘录 | 现译摘录 | 建议译法 | 理由 | 级别 | 保留判定 |")
        md.append("|---|---|---|---|---|---|---|")
        md.append("|  |  |  |  |  |  |  |")
        md.append("")
        md.append("**落地记录**（用户确认后逐条回填）：")
        md.append("")
        md.append("| 定位 | 落地方式（手动 Edit / apply_redmark） | 状态 |")
        md.append("|---|---|---|")
        md.append("|  |  |  |")
        md.append("")

    # 四、批内完成门
    ch_list = ",".join(str(n) for n, _d, _bi, _r, _o in rows)
    span_spec = f"{lo}-{hi}" if lo is not None and hi is not None else ch_list
    md.append("## 四、批内完成门（宣布完成前逐项复跑勾选）")
    md.append("")
    md.append(f"- [ ] `python tools/lqa_gates.py --chapter {span_spec}` → P0 = 0")
    md.append(f"- [ ] `python tools/sync_bilingual.py --chapter {ch_list}` → 解析异常 0"
              f"（sync 的 --chapter 只认逗号列表，不认区间）")
    pending = [(n, o, bi) for n, _d, bi, _r, o in rows if o and o != len(bi["pairs"])]
    if pending:
        md.append("- [ ] 本批疑似漏译复核项清零（审校中逐条裁定，裁定前不计完成）：")
        for n, o, bi in pending:
            locs = " / ".join(f"L{ln}" for ln, _why in bi["anomalies"]) or "见发现清单"
            md.append(f"  - 第{n}章：原文 {o} ≠ 对照 {len(bi['pairs'])}（{locs} 疑似漏译）")
    md.append("- [ ] 原文 MD5 与 `项目文档/原文MD5基线.json` 一致（中文零改动复核）")
    md.append("- [ ] 纯英版与对照版的存量内容差异属预期状态，留待审校整合阶段人工裁定；"
              "第 44/47 章纯英版含人工润色，**禁 --force 覆盖**")
    md.append("- [ ] 红标落地前置门状态：Q11 口径 = ____ ；术语裁定 = ____"
              "（未定则本批只交报告）")
    md.append("")
    return md


def main():
    ap = argparse.ArgumentParser(description="审校底稿生成器（按批，默认 5 章/批）")
    ap.add_argument("--chapter", default="", help="章号区间/列表，如 41-45（纯 ASCII）")
    ap.add_argument("--gates", default=",".join(G.GATE_ORDER), help="门禁子集，逗号分隔（默认全部）")
    ap.add_argument("--emit", action="store_true", help="写底稿到 项目文档/（默认仅 stdout 预览）")
    args = ap.parse_args()

    lo, hi = L.parse_range(args.chapter)
    gates = {g.strip().upper() for g in args.gates.split(",") if g.strip().upper() in G.GATE_ORDER}
    if not gates:
        print("[ERROR] 未指定有效门禁，可选：%s" % ",".join(G.GATE_ORDER))
        return 2

    if args.emit and lo is None and hi is None:
        print("[ERROR] 底稿按批生成：--emit 需配合 --chapter（建议 5 章/批，Q4 校准口径）")
        return 2

    glossary = L.load_glossary()
    rows = scan_batch(lo, hi, glossary, gates)
    if not rows:
        print("[ERROR] 未找到章节目录（范围 %s-%s）" % (lo, hi))
        return 2

    # stdout 批次预览（dry-run 摘要，与 lqa_gates 风格一致）
    span = f"{lo}~{hi}" if lo or hi else "全量"
    print("=" * 100)
    print(f"审校底稿预览  范围：{span}  生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
          f"  （{'--emit 将写底稿文件' if args.emit else 'dry-run：加 --emit 写底稿文件'}）")
    print("=" * 100)
    print(f"{'章节':<8}{'格式':<10}{'对照段':>6}{'异常':>6}{'P0':>6}{'P1':>7}  备注")
    print("-" * 100)
    for n, d, bi, r, orig_n in rows:
        notes = []
        if orig_n and orig_n != len(bi["pairs"]):
            notes.append(f"原文{orig_n}≠对照{len(bi['pairs'])}")
        if n in POLISHED_PURE_EN:
            notes.append("纯英版含人工润色，禁--force")
        if not any(t == "术语与人设" and p for t, p in chapter_assets(d)):
            notes.append("缺术语与人设")
        first = next((x[3] for x in r["details"] if x[2] == "P0"), "")
        if first:
            notes.append(first[:36])
        print(f"第{n}章{'':<4}{bi['kind']:<10}{len(bi['pairs']):>6}{len(bi['anomalies']):>6}"
              f"{r['P0']:>6}{r['P1']:>7}  {'；'.join(notes)}")
    print("-" * 100)
    print(f"  批内 {len(rows)} 章 · 逐段对照 {sum(len(bi['pairs']) for _n, _d, bi, _r, _o in rows)} 组"
          f" · P0 合计 {sum(r['P0'] for _n, _d, _bi, r, _o in rows)}"
          f" · P1 合计 {sum(r['P1'] for _n, _d, _bi, r, _o in rows)}")

    if not args.emit:
        return 0

    md = build_draft(rows, lo, hi, glossary)
    L.DOCS.mkdir(parents=True, exist_ok=True)
    out = L.DOCS / f"审校底稿_第{lo}-{hi}章_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"\n[OK] 底稿已写入：{out.relative_to(L.BASE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
