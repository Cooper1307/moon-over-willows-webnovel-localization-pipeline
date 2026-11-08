#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_slot.py — 章节产物槽位核验 + 真源守卫（可验证性层）

解决的三个历史问题
------------------
1. **扫描盲区**：旧 `project_status.py` 只扫章目录顶层，产物落在章内 `归档/`
   子目录时被判缺失 → 曾误报"第 1–9 章未翻译"（实为产物在归档里）。
   本脚本顶层优先、**自动回退到章内归档子目录**，并标注来源。
2. **真源损坏不能及时发现**：第 44/47 章曾整份变纯英文（唯一真源失效）。
   本脚本对每章跑 G0+（中文字符数 + 中文段数与原文段数对齐）。
3. **槽位口径漂移**："三件套齐全"历史上出现过 64/83/86 三个数字。
   槽位判据统一由 `chapter_lib.SLOTS` 单点定义。

九槽位
------
原文 · 术语与人设 · 初译_对照(真源) · 译文(派生物) · 质量评估 · 审校意见 ·
整合报告 · 商业审校 · 其他报告（润色/审计类）
核心三件套（G12）：原文 · 初译_对照 · 译文

用法（参数纯 ASCII，避免 PowerShell 中文乱码）
---------------------------------------------
  python tools/check_slot.py                      # 全量，打印摘要 + 问题清单
  python tools/check_slot.py --chapter 1-30       # 指定范围
  python tools/check_slot.py --chapter 1-30 --table   # 追加按章表
  python tools/check_slot.py --report             # 写 项目文档/槽位核验报告_<ts>.md
  python tools/check_slot.py --fail-on P0         # 存在 P0 时退出码 1（可接 CI）

规范：仅标准库；默认只读；不修改任何章节文件；路径由 __file__ 推导。
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chapter_lib as L  # noqa: E402

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def scan(lo=None, hi=None):
    """返回 [ {num, dir, slots, core_ok, src} ... ] 与 problems 列表。"""
    rows, problems = [], []
    for num, ch_dir in L.chapter_dirs(lo, hi):
        slots = L.find_slots(ch_dir)
        core_ok = L.core_complete(slots)
        src = L.cn_source_check(ch_dir)

        archived_slots = [s for s, v in slots.items() if v["hit"] and v["archived"]]
        if archived_slots:
            problems.append({
                "level": "INFO", "num": num, "kind": "槽位在归档子目录",
                "detail": f"{len(archived_slots)} 个槽位命中章内归档：{', '.join(archived_slots)}",
            })

        if src["level"] in ("P0", "P1"):
            problems.append({"level": src["level"], "num": num,
                             "kind": "真源", "detail": src["reason"]})

        if not core_ok:
            miss = [s for s in L.CORE_SLOTS if not slots[s]["hit"]]
            problems.append({"level": "P1", "num": num, "kind": "三件套缺失",
                             "detail": f"缺 {', '.join(miss)}"})

        rows.append({"num": num, "dir": ch_dir.name, "slots": slots,
                     "core_ok": core_ok, "src": src, "archived": archived_slots})
    return rows, problems


def summarize(rows):
    st = {}
    st["章节目录数"] = len(rows)
    st["三件套齐全"] = sum(1 for r in rows if r["core_ok"])
    for slot in L.SLOTS:
        st[slot] = sum(1 for r in rows if r["slots"][slot]["hit"])
    st["真源 OK"] = sum(1 for r in rows if r["src"]["level"] == "OK")
    st["槽位在归档"] = sum(1 for r in rows if r["archived"])
    return st


def build_report(rows, probs, st, scope):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    p0 = [p for p in probs if p["level"] == "P0"]
    p1 = [p for p in probs if p["level"] == "P1"]
    info = [p for p in probs if p["level"] == "INFO"]

    out = [
        "# 章节槽位核验报告（自动生成）",
        "",
        f"> 生成时间：{now}　|　范围：{scope}",
        "> 生成工具：`python tools/check_slot.py --report`（只读；不修改任何章节文件）",
        "> 槽位判据：`tools/chapter_lib.py` 的 `SLOTS`（单点定义，避免口径漂移）",
        "",
        "## 一、汇总",
        "",
        "| 指标 | 数值 |",
        "|---|---|",
    ]
    out += [f"| {k} | {v} |" for k, v in st.items()]
    out += [
        "",
        "> 九槽位按工作流顺序：原文 → 术语与人设 → 初译_对照(真源) → 译文(派生) → "
        "质量评估 → 审校意见 → 整合报告 → 商业审校 → 其他报告。",
        "",
        "## 二、问题清单",
        "",
    ]
    if not (p0 or p1 or info):
        out.append("✅ 未发现问题。")
    if p0:
        out += [f"### P0（{len(p0)}）", ""]
        out += [f"- **第{p['num']}章** · {p['kind']}：{p['detail']}" for p in p0]
        out.append("")
    if p1:
        out += [f"### P1（{len(p1)}）", ""]
        out += [f"- **第{p['num']}章** · {p['kind']}：{p['detail']}" for p in p1]
        out.append("")
    if info:
        out += [f"### INFO（{len(info)}，归档回退命中）", ""]
        out += [f"- 第{p['num']}章：{p['detail']}" for p in info]
        out.append("")

    out += ["## 三、按章明细", "",
            "✅=顶层命中　📦=归档子目录命中　—=缺失", "",
            "| 章节 | " + " | ".join(L.SLOTS.keys()) + " | 真源 |",
            "|---|" + "|".join(["---"] * len(L.SLOTS)) + "|---|"]
    for r in rows:
        cells = []
        for s in L.SLOTS:
            v = r["slots"][s]
            cells.append("📦" if (v["hit"] and v["archived"]) else ("✅" if v["hit"] else "—"))
        out.append(f"| {r['dir']} | " + " | ".join(cells) + f" | {r['src']['level']} |")

    out += ["", "---", "", "## 四、判据说明", "",
            "- **真源 P0**：对照版中文字符 < 50 或解析体制为 `EN-only`（真源中文丢失）。",
            "- **真源 P1**：缺对照版；或中文段数与原文段数偏差 > 10%（段落对齐存疑）。",
            "- **三件套 P1**：原文 / 初译_对照 / 译文 缺任一项（G12 交付完整性）。",
            "- **INFO**：槽位命中章内 `归档/` 子目录——文件有效，但建议扶正到标准位。",
            ""]
    return "\n".join(out), p0, p1


def main():
    ap = argparse.ArgumentParser(description="章节产物槽位核验 + 真源守卫（只读）")
    ap.add_argument("--chapter", default="", help="章号范围，如 1-90 / 30- / 37,41")
    ap.add_argument("--table", action="store_true", help="终端打印按章明细表")
    ap.add_argument("--report", action="store_true", help="写报告到 项目文档/")
    ap.add_argument("--fail-on", choices=["P0", "P1"], help="存在该级别问题时退出码 1")
    args = ap.parse_args()

    lo, hi = L.parse_range(args.chapter)
    scope = f"E{lo or 1}-E{hi or 'last'}" if (lo or hi) else "全量活跃章"
    rows, probs = scan(lo, hi)
    if not rows:
        print("[ERROR] 未发现章节目录")
        return 1
    st = summarize(rows)
    p0 = [p for p in probs if p["level"] == "P0"]
    p1 = [p for p in probs if p["level"] == "P1"]
    info = [p for p in probs if p["level"] == "INFO"]

    print("=" * 66)
    print(f"章节槽位核验 · {scope}")
    print("=" * 66)
    for k, v in st.items():
        print(f"  {k:<12} {v}")
    print("-" * 66)
    print(f"  P0 {len(p0)} · P1 {len(p1)} · INFO（归档回退）{len(info)}")

    if p0:
        print("\n[P0] 真源损坏 —— 禁止据此审校/交付：")
        for p in p0:
            print(f"  第{p['num']}章：{p['detail']}")
    if p1:
        print("\n[P1] 待补：")
        for p in p1[:15]:
            print(f"  第{p['num']}章 · {p['kind']}：{p['detail']}")
        if len(p1) > 15:
            print(f"  ...另有 {len(p1) - 15} 条")
    if info:
        print(f"\n[INFO] {len(info)} 章有槽位在归档子目录（有效，建议扶正）：")
        for p in info[:8]:
            print(f"  第{p['num']}章：{p['detail']}")
        if len(info) > 8:
            print(f"  ...另有 {len(info) - 8} 章")

    if args.table:
        print("\n" + "-" * 66)
        print("章节 | " + " | ".join(L.SLOTS.keys()) + " | 真源")
        for r in rows:
            cells = []
            for s in L.SLOTS:
                v = r["slots"][s]
                cells.append("📦" if (v["hit"] and v["archived"]) else ("✅" if v["hit"] else "—"))
            print(f"{r['dir']:<6} | " + " | ".join(cells) + f" | {r['src']['level']}")

    if args.report:
        text, _, _ = build_report(rows, probs, st, scope)
        L.DOCS.mkdir(parents=True, exist_ok=True)
        out = L.DOCS / f"槽位核验报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        out.write_text(text, encoding="utf-8")
        print(f"\n[OK] 报告已写入：{out}")

    if args.fail_on == "P0" and p0:
        return 1
    if args.fail_on == "P1" and (p0 or p1):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
