#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文标点规范化扫描器

背景（2026-09-06 实测）：第31/32章对照版中，中文文本存在半角标点
（`,`、`?`、`"` 等），与原文的全角标点（，？“”）不一致 —— 对照版
是"唯一真源"，其中文行本应与原文逐字一致（中文零改动红线）。

扫描对象：各章 `第X章初译_对照.md` 中的中文行。
判定：中文行（含 CJK）内若出现「半角标点后紧跟 CJK 字符」即记为可疑半角行。
只读，默认 dry-run 打印统计；加 --report 文件 写明细报告。

用法：
  python tools/scan_halfwidth_zh.py
  python tools/scan_halfwidth_zh.py --report            # 报告自动命名
规范：仅标准库；默认只读；stdout UTF-8；路径由 __file__ 推导。
"""
import re
import sys
from datetime import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
CHAPTERS = BASE / "章节原文"
DOCS = BASE / "项目文档"
CHAPTER_DIR_RE = re.compile(r"^第(\d+)章$")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
# 高置信规则（只报几乎必然有误的写法）：
#   A. ASCII 双引号紧贴汉字（中文对白用了半角引号，应为 “ ”）
#   B. ASCII 逗号/句点/问号/叹号 后直接跟汉字（应为全角标点）
HALF_PATTERNS = [
    (re.compile(r'[\u4e00-\u9fff]"|"[\u4e00-\u9fff]'), "中文对白用ASCII引号"),
    (re.compile(r'[,;][\u4e00-\u9fff]'), "半角逗号/分号后接汉字"),
    (re.compile(r'[?!][\u4e00-\u9fff]'), "半角问号/叹号后接汉字"),
    (re.compile(r'\.[\u4e00-\u9fff]'), "半角句点后接汉字"),
]


def scan():
    rows = []
    for ch in sorted(CHAPTERS.iterdir(), key=lambda p: p.name):
        if not CHAPTER_DIR_RE.match(ch.name):
            continue
        bis = [f for f in ch.iterdir() if "初译_对照" in f.name and f.suffix == ".md"]
        if not bis:
            continue
        text = bis[0].read_text(encoding="utf-8-sig")
        half_lines = []
        zh_lines = 0
        for ln, raw in enumerate(text.splitlines(), 1):
            if not CJK_RE.search(raw):
                continue
            zh_lines += 1
            hits = []
            for pat, name in HALF_PATTERNS:
                if pat.search(raw):
                    hits.append(name)
            if hits:
                half_lines.append((ln, raw.strip()[:60], hits))
        if half_lines:
            rows.append((ch.name, zh_lines, half_lines))
    return rows


def main():
    args = [a for a in sys.argv[1:] if a == "--report"]
    report = bool(args)
    rows = scan()
    print("=" * 70)
    print("中文半角标点扫描（对照版中文行）" + ("  --report" if report else "  dry-run"))
    print("=" * 70)
    if not rows:
        print("  干净：未发现对照版中文行使用半角标点。")
        return 0
    total = sum(len(h) for _, _, h in rows)
    print(f"  命中章节 {len(rows)} · 可疑半角标点行 {total}")
    print("-" * 70)
    for name, zl, half in rows:
        print(f"  {name:<7} 中文行 {zl:>3} · 可疑 {len(half):>3}")
    if not report:
        print("\n[DRY-RUN] 加 --report 写明细（含行号与命中类型）。")
        return 0

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = DOCS / f"中文标点扫描报告_{now}.md"
    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 中文标点扫描报告（对照版半角标点）",
        "",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 命中章节 {len(rows)} · 可疑半角标点行 {total}",
        "",
        "| 章节 | 中文行 | 可疑行 | 行号 | 类型 | 片段 |",
        "|---|---|---|---|---|---|",
    ]
    for name, zl, half in rows:
        for ln, snippet, hits in half:
            esc = snippet.replace("|", "\\|")
            lines.append(f"| {name} | {zl} | {len(half)} | L{ln} | {'、'.join(hits)} | {esc} |")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[OK] 报告已写入：{out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
