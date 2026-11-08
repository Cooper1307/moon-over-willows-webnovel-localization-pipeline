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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chapter_lib as L  # noqa: E402

CHAPTER_DIR_RE = re.compile(r"^第(\d+)章$")

# 槽位判据统一由 chapter_lib 单点定义（2026-10-27）：历史上本文件自持一套规则，
# 与 check_slot 漂移过（"三件套齐全"出现过 64/83/86 三个数字）。
SLOTS = L.SLOTS
# 核心三件套（交付完整性门禁 G12）
CORE = L.CORE_SLOTS


def scan():
    if not CHAPTERS.exists():
        print(f"[ERROR] 未找到章节目录：{CHAPTERS}")
        return None

    dirs = [d for d in CHAPTERS.iterdir() if d.is_dir() and CHAPTER_DIR_RE.match(d.name)]
    dirs.sort(key=lambda d: int(CHAPTER_DIR_RE.match(d.name).group(1)))

    rows = OrderedDict()
    for d in dirs:
        num = int(CHAPTER_DIR_RE.match(d.name).group(1))
        # 2026-10-27：改用 chapter_lib.find_slots（顶层优先 + 回退章内 归档/ 子目录）
        slots = L.find_slots(d)
        slot_state = OrderedDict()
        archived = []
        for slot in SLOTS:
            v = slots[slot]
            if v["hit"] and v["archived"]:
                slot_state[slot] = "📦"
                archived.append(slot)
            else:
                slot_state[slot] = "✅" if v["hit"] else "—"
        files = len([f for f in d.iterdir() if f.is_file()])
        rows[num] = {"dir": d.name, "slots": slot_state, "files": files,
                     "archived": archived, "path": d}

    return rows


def summarize(rows):
    nums = sorted(rows)
    stat = OrderedDict()
    stat["章节目录数"] = len(nums)
    stat["章号范围"] = f"第{min(nums)}章 ~ 第{max(nums)}章" if nums else "—"
    missing_nums = [n for n in range(min(nums), max(nums) + 1) if n not in nums] if nums else []
    stat["缺号章"] = ", ".join(f"第{n}章" for n in missing_nums) if missing_nums else "无"

    for slot in SLOTS:
        stat[f"有{slot}的章数"] = sum(
            1 for n in nums if rows[n]["slots"][slot] in ("✅", "📦"))

    stat["其中槽位在归档子目录"] = sum(1 for n in nums if rows[n]["archived"])

    complete = [n for n in nums if all(rows[n]["slots"][s] in ("✅", "📦") for s in CORE)]
    stat["三件套齐全章数"] = len(complete)
    stat["三件套缺失章"] = ", ".join(f"第{n}章" for n in nums if n not in complete) or "无"
    return stat, complete


def collect_metrics(rows, arch):
    """数值指标（--metrics 时跑，需解析 90 章对照版，耗时数秒）。"""
    cjk_total = 0
    en_words = 0
    n_bi = 0
    for _num, r in rows.items():
        d = r["path"]
        for f in d.iterdir():
            if f.is_file() and L.ORIGIN_RE.match(f.name):
                cjk_total += len(L.CJK_RE.findall(f.read_text(encoding="utf-8-sig")))
                break
        bi = L.parse_bilingual(d)
        if bi["pairs"]:
            en_words += sum(L.words(en or "") for _zh, en, _ln in bi["pairs"])
            n_bi += 1
    total_ch = len(rows) + (arch[1] if arch else 0)
    avg = en_words / n_bi if n_bi else 0
    m = OrderedDict()
    m["原文汉字合计（活跃）"] = cjk_total
    m["对照英词合计"] = en_words
    m["有对照稿章数"] = n_bi
    m["平均英词/章"] = round(avg)
    m["全本章数（活跃+库）"] = total_ch
    m["全本投影英词"] = round(avg * total_ch)
    m["字数完成度"] = (f"{en_words / (avg * total_ch) * 100:.1f}%"
                   if avg and total_ch else "—")
    m["剩余英词"] = round(max(avg * total_ch - en_words, 0))
    return m


def scan_archive():
    """
    统计 00_ 前缀目录（第91-351 章原文库等）。
    该区约定：每章一个目录，仅存 原文(+偶有 术语与人设)，尚未翻译。
    返回 (目录名, 章数, 最小章, 最大章, 有原文章数, 有术语章数) 或 None。
    """
    if not CHAPTERS.exists():
        return None
    best = None
    for s in sorted(CHAPTERS.iterdir()):
        if not s.is_dir() or not s.name.startswith("00_"):
            continue
        dirs = [d for d in s.iterdir() if d.is_dir() and CHAPTER_DIR_RE.match(d.name)]
        if not dirs:
            continue
        dirs.sort(key=lambda d: int(CHAPTER_DIR_RE.match(d.name).group(1)))
        nums = [int(CHAPTER_DIR_RE.match(d.name).group(1)) for d in dirs]
        has_orig = sum(1 for d in dirs if any(
            f.is_file() and "原文" in f.name and "术语" not in f.name for f in d.iterdir()))
        has_term = sum(1 for d in dirs if any(
            f.is_file() and "术语" in f.name for f in d.iterdir()))
        if best is None or len(dirs) > best[1]:
            best = (s.name, len(dirs), min(nums), max(nums), has_orig, has_term)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="写入报告文件（默认 dry-run）")
    ap.add_argument("--metrics", action="store_true",
                    help="追加数值指标（汉字/英词/全本投影/完成度；需解析 90 章，耗时数秒）")
    args = ap.parse_args()

    rows = scan()
    if rows is None:
        return 1
    stat, complete = summarize(rows)
    nums = sorted(rows)
    arch = scan_archive()
    mstat = collect_metrics(rows, arch) if args.metrics else None

    print("=" * 62)
    print("项目进度基线扫描" + ("（--apply）" if args.apply else "（dry-run）"))
    print("=" * 62)
    for k, v in stat.items():
        print(f"  {k:<20} {v}")
    if arch:
        name, cnt, mn, mx, o, tm = arch
        print(f"  {'00_原文库':<20} {name}：{cnt} 章（第{mn}~{mx}章），原文 {o} · 术语 {tm}（未翻译）")
    if mstat:
        print("-" * 62)
        for k, v in mstat.items():
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
        f"> 扫描范围：`{CHAPTERS.relative_to(BASE)}/`（活跃层）+ `00_` 原文库",
        "> ⚠️ **本文件为项目真实进度的唯一基准**；`项目目录索引.md` 已滞后，以其为准会产生误判。",
        "> 用途：补基线任务的缺失清单；术语回溯抽取的范围依据。",
        "",
        "## 一、统计",
        "",
        "| 指标 | 数值 |",
        "|---|---|",
    ]
    lines += [f"| {k} | {v} |" for k, v in stat.items()]
    if arch:
        name, cnt, mn, mx, o, tm = arch
        lines += [
            f"| 原文库 {name} | {cnt} 章（第{mn}~{mx}章）· 原文 {o} · 术语 {tm} · 未翻译 |",
        ]
    if mstat:
        lines += ["", "## 一·补、数值指标（--metrics）", "", "| 指标 | 数值 |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in mstat.items()]

    lines += ["", "---", "", "## 二、章节产物完整度", "",
              "✅ = 顶层存在 · 📦 = 命中章内 `归档/` 子目录（有效，建议扶正）· — = 缺失", "",
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
