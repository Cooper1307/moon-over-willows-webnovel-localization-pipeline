#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_handoff.py — 自动生成会话入口的「当前状态速览」块（降冷启动成本）

背景
----
`_记忆索引.md` 第二节「当前状态速览」原为手工维护，最后一次更新是 2026-09-06，
到 2026-10-27 已过期 7 周；而新会话必须先读它定位状态 —— 手工维护 + 易过期 =
每次开场都要重新核对（历史实测 10–30 分钟）。

本脚本把该块改为**数据驱动、可重复生成**：
  数据源：project_status（章数/槽位/数值指标）+ check_slot（真源等级）+ glossary（术语状态）
  幂等：同一份数据重复生成，输出逐字相同（不写实时时间戳）

用法
----
  python tools/gen_handoff.py                # 打印将要写入的块（dry-run）
  python tools/gen_handoff.py --diff         # 只打印与现有文件的差异概要
  python tools/gen_handoff.py --apply        # 写回 _记忆索引.md（先备份 .bak）
  python tools/gen_handoff.py --no-src-check # 跳过真源扫描（更快）

规范：仅标准库；默认 dry-run；`--apply` 前自动备份；不触碰 `## 二、` 以外的任何章节。
"""
import argparse
import importlib.util
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
INDEX = BASE / "_记忆索引.md"
TOOLS = Path(__file__).resolve().parent

sys.path.insert(0, str(TOOLS))
import chapter_lib as L  # noqa: E402

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SECTION_PREFIX = "## 二、"
MAX_BACKUP = 3


def load_status():
    """导入 project_status.py（复用其扫描逻辑，避免两套口径）。"""
    p = TOOLS / "project_status.py"
    spec = importlib.util.spec_from_file_location("_proj_status", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def collect(fast=False):
    ps = load_status()
    rows = ps.scan() or {}
    stat, complete = ps.summarize(rows)
    arch = ps.scan_archive()
    mstat = ps.collect_metrics(rows, arch)

    missing_core = [n for n in sorted(rows) if n not in complete]
    archived = [(n, rows[n]["archived"]) for n in sorted(rows) if rows[n]["archived"]]

    # 术语状态
    entries = L.load_glossary()
    locked = sum(1 for e in entries if e["status"] == L.STATUS_LOCKED)
    suggest = sum(1 for e in entries if e["status"] == L.STATUS_SUGGEST)
    dispute = sum(1 for e in entries if e["status"] == L.STATUS_DISPUTE)

    # 真源等级
    p0, p1 = [], []
    if not fast:
        for n, ch_dir in L.chapter_dirs():
            c = L.cn_source_check(ch_dir)
            if c["level"] == "P0":
                p0.append((n, c["reason"]))
            elif c["level"] == "P1":
                p1.append((n, c["reason"]))

    return {"rows": rows, "stat": stat, "arch": arch, "mstat": mstat,
            "missing_core": missing_core, "archived": archived,
            "term": (len(entries), locked, suggest, dispute),
            "p0": p0, "p1": p1, "src_checked": not fast}


def fmt_nums(nums, limit=12):
    if not nums:
        return "无"
    s = ", ".join(f"第{n}章" for n in nums[:limit])
    return s + (f" …共 {len(nums)} 章" if len(nums) > limit else "")


def build_block(d):
    st, m = d["stat"], d["mstat"]
    total, locked, suggest, dispute = d["term"]
    arch = d["arch"]
    lib = f"{arch[1]} 章（第{arch[2]}~{arch[3]}）" if arch else "—"

    out = [
        "## 二、当前状态速览（自动生成）",
        "",
        "> 本块由 `python tools/gen_handoff.py --apply` 从 `project_status` + `check_slot` + "
        "`glossary` 生成，**请勿手工编辑**（下次生成会覆盖）。",
        "> 权威数据：`python tools/project_status.py --metrics`（进度）· "
        "`python tools/check_slot.py --report`（槽位与真源）。",
        "",
        f"- **全书 {m['全本章数（活跃+库）']} 章**：活跃 **{st['章节目录数']}** 章"
        f"（第1~{st['章节目录数']}）；原文库 {lib}（已切分，未翻译）。",
        f"- 活跃章产物：对照 **{st['有初译_对照的章数']}** · 译文 **{st['有译文的章数']}** · "
        f"术语与人设 **{st['有术语与人设的章数']}** · 质量评估 **{st['有质量评估的章数']}** · "
        f"审校意见 **{st['有审校意见的章数']}** · 商业审校 **{st['有商业审校的章数']}** · "
        f"整合报告 **{st['有整合报告的章数']}**；**三件套齐全 {st['三件套齐全章数']}**。",
        f"- 三件套缺口：{fmt_nums(d['missing_core'])}。",
        f"- 数值：原文 **{m['原文汉字合计（活跃）']:,}** 汉字 · 对照 **{m['对照英词合计']:,}** 英词 · "
        f"均 **{m['平均英词/章']:,}** 词/章；全本投影 **{m['全本投影英词']:,}** 英词，"
        f"完成度 **{m['字数完成度']}**，剩余 **{m['剩余英词']:,}** 英词。",
        f"- 术语：{total} 词条（锁定 {locked} · `[建议]` **{suggest}** · `[!]`待裁定 {dispute}）。",
    ]
    if d["archived"]:
        names = ", ".join(f"第{n}章" for n, _ in d["archived"])
        out.append(f"- 槽位在章内 `归档/`：{names}（有效，建议扶正到标准位）。")
    if not d.get("src_checked", True):
        out.append("- 真源状态：**未检测**（本次用 `--no-src-check`；跑 `python tools/check_slot.py` 复核）。")
    elif d["p0"] or d["p1"]:
        out.append(f"- **真源状态：P0 {len(d['p0'])} 章 · P1 {len(d['p1'])} 章**"
                   + ("（P0 禁止据此审校/交付）" if d["p0"] else "") + "。")
        for n, why in (d["p0"] + d["p1"])[:5]:
            out.append(f"  - 第{n}章：{why}")
    else:
        out.append("- 真源状态：全部 OK（无 P0/P1）。")
    out.append("")
    return "\n".join(out)


def replace_section(text, block):
    lines = text.split("\n")
    start = next((i for i, ln in enumerate(lines)
                  if ln.strip().startswith(SECTION_PREFIX)), None)
    if start is None:
        raise SystemExit(f"[ERROR] 未找到 `{SECTION_PREFIX}` 小节，拒绝改写（避免误伤）")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].strip().startswith("## "):
            end = j
            break
    old_block = "\n".join(lines[start:end]).rstrip()
    return "\n".join(lines[:start]) + "\n" + block + "\n" + "\n".join(lines[end:]), old_block


def main():
    ap = argparse.ArgumentParser(description="生成 _记忆索引.md 的当前状态块（默认 dry-run）")
    ap.add_argument("--apply", action="store_true", help="写回文件（先备份 .bak）")
    ap.add_argument("--diff", action="store_true", help="只打印差异概要")
    ap.add_argument("--no-src-check", action="store_true", help="跳过真源扫描（更快）")
    args = ap.parse_args()

    if not INDEX.is_file():
        print(f"[ERROR] 未找到 {INDEX}")
        return 1

    d = collect(fast=args.no_src_check)
    block = build_block(d)
    text = INDEX.read_text(encoding="utf-8-sig")
    new_text, old_block = replace_section(text, block)

    if args.diff:
        changed = old_block.strip() != block.strip()
        print(f"状态块：{'有变化' if changed else '无变化（幂等）'}")
        print(f"  原块 {len(old_block.splitlines())} 行 → 新块 {len(block.splitlines())} 行")
        return 0

    print("=" * 66)
    print("将写入 _记忆索引.md 的「当前状态速览」块：")
    print("=" * 66)
    print(block)

    if not args.apply:
        print("[DRY-RUN] 加 --apply 才写回。")
        return 0

    # 备份（只留最近 3 份）
    bak = INDEX.with_suffix(".md.bak")
    shutil.copy2(INDEX, bak)
    old_baks = sorted(INDEX.parent.glob("_记忆索引.md.bak*"))
    for extra in old_baks[:-MAX_BACKUP]:
        extra.unlink(missing_ok=True)

    INDEX.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"[OK] 已写入：{INDEX}（备份：{bak.name}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
