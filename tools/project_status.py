#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目进度基线扫描器（Project Status Scanner）

扫描 `章节原文/` 下所有章节目录，统计每章产物完整度，输出项目真实进度基线。
用途：校正滞后的 `项目目录索引.md`，并为「补基线」任务提供缺失清单。

产物槽位（按翻译工作流顺序）：
  原文 / 术语与人设 / 初译_对照 / 译文(纯英) / 质量评估 / 审校意见 / 整合报告 / 商业审校

用法：
  python tools/project_status.py                # dry-run，打印统计与缺失摘要
  python tools/project_status.py --apply        # 写完整报告到 项目文档/项目进度基线.md

规范：仅标准库；默认 dry-run；只读源文件；路径由 __file__ 推导，避免中文路径命令行乱码。
"""
import argparse
import re
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
CHAPTERS = BASE / "章节原文"
DOCS = BASE / "项目文档"
DEFAULT_REPORT = DOCS / "项目进度基线.md"

CHAPTER_DIR_RE = re.compile(r"^第(\d+)章$")

# 槽位名 -> 匹配规则（文件名包含即命中）
SLOTS = OrderedDict([
    ("原文", lambda n: "原文" in n and "术语" not in n),
    ("术语与人设", lambda n: "术语与人设" in n),
    ("初译_对照", lambda n: "初译_对照" in n or "对照" in n),
    ("译文(纯英)", lambda n: "译文" in n or "初译_纯英文" in n),
    ("质量评估", lambda n: "质量评估" in n),
    ("审校意见", lambda n: "审校意见" in n),
    ("整合报告", lambda n: "整合报告" in n or "审校意见整合" in n),
    ("商业审校", lambda n: "商业审校" in n),
])

# 核心三件套（交付完整性门禁 G12）
CORE = ["原文", "初译_对照", "译文(纯英)"]


def scan():
    if not CHAPTERS.exists():
        print(f"[ERROR] 未找到章节目录：{CHAPTERS}")
        return None

    dirs = [d for d in CHAPTERS.iterdir() if d.is_dir() and CHAPTER_DIR_RE.match(d.name)]
    dirs.sort(key=lambda d: int(CHAPTER_DIR_RE.match(d.name).group(1)))

    rows = OrderedDict()
    for d in dirs:
        num = int(CHAPTER_DIR_RE.match(d.name).group(1))
        files = [f.name for f in d.iterdir() if f.is_file()]
        slot_state = OrderedDict()
        for slot, matcher in SLOTS.items():
            hit = [f for f in files if matcher(f)]
            slot_state[slot] = "✅" if hit else "—"
        rows[num] = {"dir": d.name, "slots": slot_state, "files": len(files)}

    return rows


def summarize(rows):
    nums = sorted(rows)
    stat = OrderedDict()
    stat["章节目录数"] = len(nums)
    stat["章号范围"] = f"第{min(nums)}章 ~ 第{max(nums)}章" if nums else "—"
    missing_nums = [n for n in range(min(nums), max(nums) + 1) if n not in nums] if nums else []
    stat["缺号章"] = ", ".join(f"第{n}章" for n in missing_nums) if missing_nums else "无"

    for slot in SLOTS:
        stat[f"有{slot}的章数"] = sum(1 for n in nums if rows[n]["slots"][slot] == "✅")

    complete = [n for n in nums if all(rows[n]["slots"][s] == "✅" for s in CORE)]
    stat["三件套齐全章数"] = len(complete)
    stat["三件套缺失章"] = ", ".join(f"第{n}章" for n in nums if n not in complete) or "无"
    return stat, complete


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="写入报告文件（默认 dry-run）")
    args = ap.parse_args()

    rows = scan()
    if rows is None:
        return 1
    stat, complete = summarize(rows)
    nums = sorted(rows)

    print("=" * 62)
    print("项目进度基线扫描" + ("（--apply）" if args.apply else "（dry-run）"))
    print("=" * 62)
    for k, v in stat.items():
        print(f"  {k:<20} {v}")
    print("-" * 62)
    print("  章节 | " + " | ".join(SLOTS.keys()))
    for n in nums[:8]:
        r = rows[n]
        print(f"  {r['dir']:<6} | " + " | ".join(r["slots"].values()))
    if len(nums) > 8:
        print(f"  ...（共 {len(nums)} 章，完整表见报告）")
    print(f"\n  报告输出：{DEFAULT_REPORT}")

    if not args.apply:
        print("\n[DRY-RUN] 加 --apply 才写报告文件。")
        return 0

    DOCS.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# 项目进度基线（自动扫描）",
        "",
        f"> 生成时间：{now}",
        f"> 扫描范围：`{CHAPTERS.relative_to(BASE)}/`",
        "> ⚠️ **本文件为项目真实进度的唯一基准**；`项目目录索引.md` 已滞后，以其为准会产生误判。",
        "> 用途：补基线任务（TODO #6）的缺失清单；术语回溯抽取的范围依据。",
        "",
        "## 一、统计",
        "",
        "| 指标 | 数值 |",
        "|---|---|",
    ]
    lines += [f"| {k} | {v} |" for k, v in stat.items()]
    lines += ["", "---", "", "## 二、章节产物完整度", "", "✅ = 存在 · — = 缺失", "",
              "| 章节 | " + " | ".join(SLOTS.keys()) + " | 文件数 |",
              "|---|" + "|".join(["---"] * (len(SLOTS) + 1)) + "|"]
    for n in nums:
        r = rows[n]
        lines.append(f"| {r['dir']} | " + " | ".join(r["slots"].values()) + f" | {r['files']} |")
    lines += ["", "---", "", "## 三、缺失清单（待补）", ""]

    for slot in SLOTS:
        miss = [n for n in nums if rows[n]["slots"][slot] != "✅"]
        if miss:
            lines.append(f"- **{slot}** 缺失 {len(miss)} 章：{', '.join(f'第{n}章' for n in miss)}")
        else:
            lines.append(f"- **{slot}**：齐全")
    lines += [
        "",
        "---",
        "",
        "## 四、结论与后续动作",
        "",
        "1. 三件套（原文 / 对照 / 纯英）不齐的章节**优先补齐**——纯英版是派生物，应由 `sync_bilingual.py` 从对照版生成。",
        "2. 术语回溯抽取范围以本文件的章节目录为准（比目录索引记录的 35 章更多）。",
        "3. 每完成一批后重跑本脚本更新基线（`--apply`）。",
        "",
    ]

    DEFAULT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[OK] 报告已写入：{DEFAULT_REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
