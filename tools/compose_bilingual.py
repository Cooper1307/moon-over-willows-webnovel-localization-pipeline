#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compose_bilingual.py — 由「原文中文行 + 逐段英文行」组装对照版唯一真源

背景：新译 264 章时，手写对照版容易在中文行里打错字或改标点，违反
「中文原文零改动／逐字一致」红线。本工具把中文行**直接取自磁盘原文**，
译者只需提供等量的英文行（每行一段），从根上消除中文被改动的可能。

格式对齐 `章节原文/第3章/第3章初译_对照.md`：
  第1行  中文章题（原样取自原文）
  第2行  ## Chapter N: <英文题名>
  空行
  中文段 / 英文段 / 空行  …… 逐段成对

用法（参数全 ASCII；中文路径由 __file__ 推导）：
  python tools/compose_bilingual.py --chapter 1 --title "A Web Novelist Meets the Online Mob" --en C:/Temp/ch1_en.txt
  python tools/compose_bilingual.py --chapter 1 --title "..." --en C:/Temp/ch1_en.txt --apply

约束：默认 dry-run；段落数不等即报错退出，不写文件；
      写盘强制 LF（避免 Windows write_text 把整文件翻成 CRLF 造成全量 diff）；
      不修改原文、不修改译文.md（派生物由 extract_pure_en.py 生成）。
"""
import argparse
import sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
CHAPTERS = BASE / "章节原文"


def nonempty_lines(path):
    """保留行内原样内容（含首尾空白），只过滤纯空行。"""
    return [ln for ln in path.read_text(encoding="utf-8-sig").splitlines() if ln.strip()]


def main():
    ap = argparse.ArgumentParser(description="组装中英对照真源（中文行取自原文，零改动）")
    ap.add_argument("--chapter", required=True, help="章号，纯 ASCII 数字")
    ap.add_argument("--title", required=True, help="英文题名，ASCII 或 UTF-8 均可")
    ap.add_argument("--en", required=True, help="英文逐行文件绝对路径（每行一段，无内嵌换行）")
    ap.add_argument("--apply", action="store_true", help="写盘（默认 dry-run）")
    ap.add_argument("--force", action="store_true",
                    help="覆盖已存在的对照真源（用于译文修订后重建；中文行仍取自原文，不丢内容）")
    args = ap.parse_args()

    try:
        n = int(args.chapter)
    except ValueError:
        print("[ERROR] --chapter 必须是数字")
        return 2

    ch_dir = CHAPTERS / f"第{n}章"
    origin = ch_dir / f"第{n}章原文.md"
    en_path = Path(args.en)
    target = ch_dir / f"第{n}章初译_对照.md"

    if not origin.is_file():
        print(f"[ERROR] 原文不存在：{origin}")
        return 2
    if not en_path.is_file():
        print(f"[ERROR] 英文行文件不存在：{en_path}")
        return 2
    if target.exists() and not args.force:
        print(f"[ERROR] 真源已存在，拒绝覆盖：{target}；译文修订后重建请加 --force")
        return 2

    zh = nonempty_lines(origin)
    en = nonempty_lines(en_path)
    if not zh:
        print("[ERROR] 原文无非空行")
        return 2

    title_zh, paras_zh = zh[0], zh[1:]
    print(f"章题：{title_zh}")
    print(f"原文正文段 {len(paras_zh)} · 英文段 {len(en)}")
    if len(paras_zh) != len(en):
        print(f"[ERROR] 段落数不等（{len(paras_zh)} vs {len(en)}），拒绝组装。"
              f" 请补齐英文行后再跑；不写任何文件。")
        for i, z in enumerate(paras_zh[:3], 1):
            print(f"  原文段{i}: {z[:50]}")
        return 1

    out = [title_zh, f"## Chapter {n}: {args.title}", ""]
    for z, e in zip(paras_zh, en):
        out += [z, e, ""]
    text = "\n".join(out).rstrip() + "\n"

    if args.apply:
        with open(target, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"[OK] 已写 {target}（{len(paras_zh)} 段成对，中文行逐字取自原文，LF 行尾）")
    else:
        print(f"[DRY-RUN] 将写 {target}（{len(paras_zh)} 段成对）；加 --apply 落盘")
        print("  预览前 6 行：")
        for ln in text.splitlines()[:6]:
            print("   ", ln[:100])
    return 0


if __name__ == "__main__":
    sys.exit(main())
