#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_pure_en.py — 纯英版派生工具（对照版 → 第X章译文.md）

单一职责：从双语对照版提取英文段落，输出纯英版。
不做校验（校验/比对用 sync_bilingual.py），不翻译、不改写任何英文。

工作流原则（2026-10-03 用户确立）
    对照版 = 唯一手写产物
    纯英版 = 脚本派生，禁止手工编辑

行为准则（用户已定：存量纯英版含人工润色，不覆盖）
    缺失   → 生成
    已存在 → 一律跳过不动（不比对、不覆盖、不告警）
    实测 30-90 章中 54 章纯英版含对照版没有的内容（人工润色）、27 章段数不等，
    属正常资产状态而非缺陷；工具无权判定该不该覆盖。--force 为逃生门，默认关。

三道安全阀（均不可被 --force 绕过）
    1. EN-only 拒绝   对照版无中文（真源损坏）→ 派生会产出空文件并掩盖损坏
    2. anomalies 拒绝 存在漏译/顺序倒置 → 派生会把漏译固化进纯英版
    3. 无对照版拒绝   无源可派生
    --force 只作用于「覆盖已存在文件」一个维度，不绕过任何闸门。

派生处理
    1. 剥离译者注：parse_bilingual 已把 [TN: 等独立成块的注移出 pairs 放入 notes，
       故纯英版不含译者注（顺带修复历史上第33/48章译文.md 混入中文注的问题）。
       ⚠ 注意：以下两类「中文」是有意保留的正文内容，**不是污染，禁止清理**：
         · 英文段内嵌的中文原字（字形/词源解释），实测第32章 4 段，
           如 Shen Jianchen... wrote the character "Xun" (寻， meaning "to seek")
         · 引号内的中文原词/诗文引用
       判别方法：译者注一律是**独立成块**且以 [TN: 等标记开头；
       正文内嵌中文则处于英文句子中间。两者不可混为一谈。
    2. 剥离红标标签：复用 chapter_lib.strip_red()
    3. 保留原英文标题行

用法（参数纯 ASCII，规避 PowerShell 中文路径 GBK 乱码）
    python tools/extract_pure_en.py                    # 全量预演
    python tools/extract_pure_en.py --chapter 32       # 单章
    python tools/extract_pure_en.py --chapter 30-90    # 区间
    python tools/extract_pure_en.py --chapter 32 --apply   # 真写
    python tools/extract_pure_en.py --chapter 32 --force   # 覆盖已有（逃生门）
    python tools/extract_pure_en.py --report           # 导出报告
    python tools/extract_pure_en.py --fail-on-blocked  # 有阻断则退出码 1

规范：仅标准库；默认 dry-run；路径由 __file__ 推导；stdout 重配 UTF-8。
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chapter_lib as L  # noqa: E402

ST_GENERATED = "generated"
ST_SKIPPED = "skipped_exists"
ST_BLOCKED_EN_ONLY = "blocked_en_only"
ST_BLOCKED_ANOM = "blocked_anomalies"
ST_BLOCKED_NO_BI = "blocked_no_bilingual"
ST_BLOCKED_NO_PAIRS = "blocked_no_pairs"
BLOCKED = {ST_BLOCKED_EN_ONLY, ST_BLOCKED_ANOM, ST_BLOCKED_NO_BI, ST_BLOCKED_NO_PAIRS}


def _title_from(ch_dir, bi):
    """取英文标题：优先沿用已有纯英版的标题，其次从对照版头部提取。"""
    path, _ = L.read_pure_en(ch_dir)
    if path is not None:
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            s = line.strip()
            if s.startswith("#"):
                return s
            if s:
                break
    p = bi.get("path")
    if p is not None:
        for raw in p.read_text(encoding="utf-8-sig").splitlines()[:8]:
            s = raw.strip()
            if s.startswith("#") and not L.CJK_RE.search(s.lstrip("#")):
                return s
    return None


def derive(ch_dir, force=False, apply_mode=False, audit=False):
    """
    派生单章纯英版。返回
      {chapter, status, reason, paragraphs, notes_stripped, written, path}

    audit=False（默认）：只关心「要生成」的章。纯英版已存在即跳过，
        **不做闸门检查**——闸门是「派生」的前置条件，不是对存量资产的体检，
        否则输出会被无关章的阻断刷屏（实测 46 章阻断中绝大多数纯英版已存在）。
    audit=True：全量体检模式，所有章都走闸门并报告状态，不写任何文件。
        用于定期排查真源损坏（如 EN-only 章）。
    """
    name = ch_dir.name
    try:
        num = int(name[1:-1])
    except (ValueError, IndexError):
        num = 0
    res = {"chapter": num, "status": "", "reason": "", "paragraphs": 0,
           "notes_stripped": 0, "written": False, "path": None}

    bi = L.parse_bilingual(ch_dir)
    existing, _ = L.read_pure_en(ch_dir)

    # 已存在且不 force → 立即跳过（audit 模式除外，见 docstring）
    if existing is not None and not force and not audit:
        res.update(status=ST_SKIPPED, path=str(existing),
                   reason="纯英版已存在，按策略跳过（--force 可覆盖）")
        return res

    if bi["path"] is None:                                   # 闸门 3
        res.update(status=ST_BLOCKED_NO_BI, reason="无对照版文件")
        return res
    if bi["kind"] == "EN-only":                             # 闸门 1
        res.update(status=ST_BLOCKED_EN_ONLY,
                   reason="对照版无中文（真源损坏，须先重建对照版）")
        return res
    if bi["anomalies"]:                                     # 闸门 2
        a0 = bi["anomalies"][0]
        more = f"（另有 {len(bi['anomalies']) - 1} 处）" if len(bi["anomalies"]) > 1 else ""
        res.update(status=ST_BLOCKED_ANOM,
                   reason=f"配对异常 {len(bi['anomalies'])} 处：L{a0[0]} {a0[1]}{more}")
        return res
    if not bi["pairs"]:
        res.update(status=ST_BLOCKED_NO_PAIRS, reason="解析不出任何中英配对")
        return res

    res["paragraphs"] = len(bi["pairs"])
    res["notes_stripped"] = len(bi["notes"])

    if existing is not None and not force:
        # 仅 audit 模式会走到这里：已存在但对照版有阻断项
        res.update(status=ST_SKIPPED, path=str(existing),
                   reason="纯英版已存在（体检模式：对照版有阻断项，未覆盖）")
        return res

    title = _title_from(ch_dir, bi) or f"# Chapter {num}"
    if not title.startswith("#"):
        title = "# " + title
    out = [title, ""]
    for _zh, en, _ln in bi["pairs"]:
        out.append(L.strip_red(en))
        out.append("")

    res["path"] = str(ch_dir / f"{name}译文.md")
    if apply_mode and not audit:          # audit 模式绝不写文件（双重保险）
        (ch_dir / f"{name}译文.md").write_text(
            "\n".join(out).rstrip() + "\n", encoding="utf-8")
        res.update(written=True, status=ST_GENERATED,
                   reason=("覆盖已存在纯英版（--force）" if existing else "新建纯英版"))
    else:
        res.update(status=ST_GENERATED,
                   reason=("体检模式：对照版可派生（未写）" if audit else
                           ("将覆盖（--force，dry-run 未写入）" if existing
                            else "将生成（dry-run 未写入）")))
    return res


def main():
    ap = argparse.ArgumentParser(description="纯英版派生工具（对照版 → 译文.md）")
    ap.add_argument("--chapter", default="", help="章号区间/列表，如 32 / 30-90（纯 ASCII）")
    ap.add_argument("--apply", action="store_true", help="实际写文件（默认 dry-run）")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的纯英版（逃生门）")
    ap.add_argument("--report", action="store_true", help="导出 纯英版派生报告_<时间戳>.md")
    ap.add_argument("--audit", action="store_true",
                    help="全量体检模式：所有章都跑闸门并报告（含已存在章），不写文件。"
                         "用于定期排查真源损坏；默认模式只关心「要生成」的章")
    ap.add_argument("--fail-on-blocked", action="store_true", help="有阻断项则退出码 1")
    args = ap.parse_args()

    lo, hi = L.parse_range(args.chapter)
    dirs = L.chapter_dirs(lo, hi)
    if not dirs:
        print("[ERROR] 未找到章节目录（范围 %s-%s）" % (lo, hi))
        return 2

    rows = [derive(d, force=args.force, apply_mode=args.apply, audit=args.audit)
            for _n, d in dirs]
    gen = [r for r in rows if r["status"] == ST_GENERATED]
    skip = [r for r in rows if r["status"] == ST_SKIPPED]
    blk = [r for r in rows if r["status"] in BLOCKED]

    span = f"{lo}-{hi}" if lo and hi else (f"{lo}-90" if lo else "全量")
    mode = "体检 AUDIT（不写）" if args.audit else (
        "APPLY 写入" if args.apply else "DRY-RUN 只读")
    print("=" * 88)
    print(f"纯英版派生（{mode}{' +force' if args.force else ''}）"
          f"  范围：{span}"
          f"  时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 88)
    for r in rows:
        if r["status"] == ST_SKIPPED and not args.audit:
            continue
        mark = "OK " if r["status"] == ST_GENERATED else (
            "-- " if r["status"] == ST_SKIPPED else "XX ")
        print(f"{mark}第{r['chapter']}章 {r['status']:<20} 段{r['paragraphs']:>4}"
              f"  注剥离{r['notes_stripped']:>3}  {r['reason']}")
    print("-" * 88)
    print(f"  扫描 {len(rows)} 章 · 将生成 {len(gen)} · 已存在跳过 {len(skip)} · 阻断 {len(blk)}")
    if blk and not args.audit:
        print("  阻断：" + "；".join(f"第{r['chapter']}章 {r['status']}" for r in blk))
    if args.audit:
        print("  [AUDIT] 体检模式，未写任何文件")
    elif not args.apply:
        print("  [DRY-RUN] 加 --apply 才写；已存在的一律跳过（--force 才覆盖）")

    if args.report:
        L.DOCS.mkdir(parents=True, exist_ok=True)
        out = L.DOCS / ("纯英版派生报告_%s.md" % datetime.now().strftime("%Y%m%d_%H%M%S"))
        lines = ["# 纯英版派生报告", "",
                 "- 时间：%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "- 模式：%s%s" % ("APPLY（已写入）" if args.apply else "dry-run（只读）",
                                   " +force" if args.force else ""),
                 "- 原则：对照版=唯一手写产物，纯英版=脚本派生；已存在一律跳过（保护人工润色）",
                 "", "## 统计", "",
                 "- 扫描章节：%d" % len(rows),
                 "- 将生成：%d" % len(gen),
                 "- 已存在跳过：%d" % len(skip),
                 "- 阻断：%d" % len(blk), "", "## 明细", "",
                 "| 章节 | 状态 | 段数 | 注剥离 | 说明 |", "|---|---|---|---|---|"]
        for r in rows:
            lines.append("| 第%d章 | %s | %d | %d | %s |"
                         % (r["chapter"], r["status"], r["paragraphs"],
                            r["notes_stripped"], r["reason"].replace("|", "/")))
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("  [OK] 报告已写入：%s" % out)

    if args.fail_on_blocked and blk:
        print("  [FAIL] 存在 %d 项阻断（--fail-on-blocked 触发，退出码 1）" % len(blk))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
