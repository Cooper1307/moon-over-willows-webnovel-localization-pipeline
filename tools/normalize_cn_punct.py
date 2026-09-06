#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文标点归一化（对照版专用）

背景（Q11，2026-09-06）：对照版中文行长期使用 ASCII 引号/半角标点
（`说:"我要更衣。"`），而原文与总底稿为全角（`说：“我要更衣。”`）。
已溯源确认半角是制作对照版时引入 → 按"对照中文与原文逐字一致"红线归一。

只处理 `第X章初译_对照.md` 的**中文行**（含 CJK），英文行零改动。
转换规则（字符级）：
  - ASCII 双引号 `"`：仅当行内成对（偶数）时交替转 “ ”；
  - ASCII `:` 前一字符为 CJK → `：`；`,;?!` 后紧跟 CJK → 全角对应；
  - ASCII `.` 前一字符为 CJK → `。`。
其余一律保留。

用法：
  python tools/normalize_cn_punct.py            # dry-run：只报告各章改动行数
  python tools/normalize_cn_punct.py --chapter 31,32   # 只处理指定章
  python tools/normalize_cn_punct.py --apply    # 写盘（git 有回滚点）
规范：仅标准库；默认只读；UTF-8；路径由 __file__ 推导。
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
CJK = re.compile(r"[\u4e00-\u9fff\u2014\u201c\u201d\u2018\u2019\u3001\uff0c\uff1a\uff1b\uff1f\uff01\u3002]")

FULL = {",": "，", ";": "；", "?": "？", "!": "！", ":": "：", ".": "。"}


def norm_zh_line(line):
    """归一中文行标点，返回 (new, changed)。"""
    chars = list(line)
    changed = False
    n = len(chars)
    # 先处理成对 ASCII 双引号
    qidx = [i for i, c in enumerate(chars) if c == '"']
    if qidx and len(qidx) % 2 == 0:
        for k in range(0, len(qidx), 2):
            chars[qidx[k]] = "\u201c"   # “
            chars[qidx[k + 1]] = "\u201d"  # ”
        changed = True
    # 标点
    for i, c in enumerate(chars):
        if c in FULL:
            prev = chars[i - 1] if i > 0 else ""
            nxt = chars[i + 1] if i + 1 < n else ""
            if c in ":.":
                if CJK.match(prev):
                    chars[i] = FULL[c]
                    changed = True
            else:  # , ; ? !
                if CJK.match(nxt) or CJK.match(prev):
                    chars[i] = FULL[c]
                    changed = True
    return "".join(chars), changed


def process_file(path, apply):
    """返回 (改变行数, 总行数)。"""
    text = path.read_text(encoding="utf-8-sig")
    out = []
    changed_lines = 0
    total = 0
    for ln in text.splitlines():
        if not CJK.search(ln):
            out.append(ln)
            continue
        total += 1
        new, ch = norm_zh_line(ln)
        if ch:
            changed_lines += 1
        out.append(new if ch else ln)
    if apply and changed_lines:
        path.write_text("\n".join(out), encoding="utf-8-sig")
    return changed_lines, total


def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    sel = []
    if "--chapter" in args:
        i = args.index("--chapter")
        sel = [int(x) for x in args[i + 1].split(",") if x.strip().isdigit()]
    rows = []
    total_files = total_lines = 0
    for ch in sorted(CHAPTERS.iterdir(), key=lambda p: p.name):
        if not CHAPTER_DIR_RE.match(ch.name):
            continue
        if sel and int(CHAPTER_DIR_RE.match(ch.name).group(1)) not in sel:
            continue
        for f in sorted(ch.iterdir()):
            if "初译_对照" in f.name and f.suffix == ".md":
                cl, tl = process_file(f, apply)
                if cl:
                    rows.append((ch.name, f.name, cl, tl))
                    total_files += 1
                    total_lines += cl
                break
    print("=" * 66)
    print("中文标点归一" + ("（--apply 已写盘）" if apply else "（dry-run 只读）"))
    print("=" * 66)
    if not rows:
        print("  无改动。")
        return 0
    for name, fname, cl, tl in rows[:80]:
        print(f"  {name:<7} 改 {cl:>3}/{tl:<3} 行  {fname}")
    if len(rows) > 80:
        print(f"  …（共 {len(rows)} 章）")
    print("-" * 66)
    print(f"  章节 {len(rows)} · 改动行 {total_lines}")
    if not apply:
        print("\n[DRY-RUN] 加 --apply 写盘。改动仅作用于中文行；英文行零改动。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
