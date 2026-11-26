#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_review_terms.py — 把终审意见里的高频术语一致性替换批量落地。

只做**高置信、无歧义**的术语归一（来自终审报告 Top 高频 + 既定事实表锁定项）：
Nanny Wei→Matron Wei / Qianlixun→Qianli Xun / Xia Guo→Xiaguo / Nanshuang→Nan Shuang 等。
改动只发生在对照版（唯一真源）的英文行，中文行一字不动；改完重派生纯英版。

用法：
  python tools/apply_review_terms.py            # dry-run
  python tools/apply_review_terms.py --apply    # 落盘
"""
import argparse
import re
import sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
CH = BASE / "章节原文"

# (正则, 替换, 说明) —— 全部是锁定译名/专名拼写，不会误伤普通英文
RULES = [
    (r"\bNanny Wei\b", "Matron Wei", "嬷嬷锁定译名"),
    (r"\bNanny Xiuzhen\b", "Matron Xiuzhen", "嬷嬷锁定译名"),
    (r"\bAunt Wei\b", "Matron Wei", "嬷嬷锁定译名"),
    (r"\bAuntie Wei\b", "Matron Wei", "嬷嬷锁定译名"),
    (r"\bQianlixun\b", "Qianli Xun", "女主拼写"),
    (r"\bQiānlǐxún\b", "Qianli Xun", "带调拼音归一"),
    (r"\bXia Guo\b", "Xiaguo", "夏果拼写"),
    (r"\bNanshuang\b", "Nan Shuang", "南双拼写"),
    (r"\bBaifeng\b", "Bai Feng", "白风拼写"),
    (r"\bthe Zhu residence\b", "Zhu Manor", "朱府锁定译名"),
    (r"\bthe Zhu Residence\b", "Zhu Manor", "朱府锁定译名"),
    (r"\bYoulin Villa\b", "Youlin Retreat", "幽林别居锁定译名"),
    (r"\bSecluded Forest Villa\b", "Youlin Retreat", "幽林别居锁定译名"),
    (r"\bSacred Willow\b", "Divine Willow", "神柳锁定译名"),
    (r"\bCounty Princess Jiahe\b", "Princess Jiahe", "郡主锁定译名"),
    (r"\bKu Qiao\b", "Kuqiao", "苦荞拼写"),
]


def is_zh_line(s):
    """中文行判定：含 CJK 且无 ASCII 字母（与 sync_bilingual 口径一致）。"""
    return bool(re.search(r"[一-鿿]", s)) and not re.search(r"[A-Za-z]", s)


def main():
    ap = argparse.ArgumentParser(description="批量归一终审高频术语（只改英文行）")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    total_files = 0
    total_hits = 0
    by_rule = {}
    for n in range(1, 352):
        p = CH / f"第{n}章" / f"第{n}章初译_对照.md"
        if not p.exists():
            continue
        lines = p.read_text(encoding="utf-8-sig").splitlines()
        changed = False
        fhits = 0
        for idx, ln in enumerate(lines):
            if is_zh_line(ln) or ln.strip().startswith("#"):
                continue
            new = ln
            for rx, rep, why in RULES:
                new, k = re.subn(rx, rep, new)
                if k:
                    fhits += k
                    by_rule[why] = by_rule.get(why, 0) + k
            if new != ln:
                lines[idx] = new
                changed = True
        if changed:
            total_files += 1
            total_hits += fhits
            if args.apply:
                p.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[{'APPLY' if args.apply else 'DRY'}] 涉及 {total_files} 章 · {total_hits} 处替换")
    for why, k in sorted(by_rule.items(), key=lambda x: -x[1]):
        print(f"  {k:4d}  {why}")
    if not args.apply:
        print("加 --apply 落盘；之后需重派生纯英版并复验 G8。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
