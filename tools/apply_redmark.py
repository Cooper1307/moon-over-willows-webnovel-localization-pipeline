#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_redmark.py — 审校红标批量落地（映射表驱动）

移植自 MTPE tools/apply_redmark.py，机制不变、与业务形态无关：
  读取 UTF-8 CSV 映射表（章号,旧英文片段,新英文行），
  在该章**对照版**中定位包含「旧英文片段」的英文段，**整段**替换为
  `<font color="red">新英文段</font>`。

  * 不会双重嵌套：已含 <font color="red"> 的段自动跳过。
  * **两种替换模式**（小说段长，默认 segment）：
      - segment（默认）：只把 old 片段替换为 new，段落其余内容原样保留；
      - line：整段替换为 new（沿用 MTPE 原行为，new 须是完整改写段）。
      ⚠ 小说单段常有 40+ 词，误用 line 模式会丢失段内未改内容，务必用 segment。
  * 目标文件固定为 `第X章初译_对照.md`（唯一真源）。纯英版是派生物，
    红标落地后用 sync_bilingual.py --apply 重新生成，禁止手改纯英版。
  * 默认 dry-run，仅打印将发生的修改；--apply 才实际写文件。

用法（参数为纯 ASCII，避免 PowerShell 中文路径 GBK 乱码；CSV 路径可含中文但
建议置于项目内、用相对项目根的路径）：
  python tools/apply_redmark.py --map 项目文档/红标映射.csv
  python tools/apply_redmark.py --map 项目文档/红标映射.csv --apply
  python tools/apply_redmark.py --make-template 项目文档/红标映射.csv --chapter 30,31
      # 生成空白模板（含每章英文段摘要），供人工/AI 填写 old / new

CSV 格式（UTF-8，首行表头）：
  章号,旧英文片段,新英文行
  30,"she held them back","she alone held them back"

安全设计（照搬工作区脚本规范）：
  - 默认 dry-run；--apply 才写。
  - 每条映射独立定位，单条失败不中断（记 [MISS]），退出码 1 提示存在未落地项。
  - 写入时保留原文件行序与分隔符形态，仅整段替换，不重排结构。
  - 拒绝对纯英版（译文.md）写入，红标只打对照版。
"""
import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chapter_lib as L  # noqa: E402

RED_OPEN = '<font color="red">'
RED_CLOSE = "</font>"


def find_target(n):
    """返回该章对照版路径；优先 章节目录/第X章初译_对照.md，否则全项目搜。"""
    d = L.CHAPTERS / f"第{n}章"
    if d.is_dir():
        for f in d.iterdir():
            if f.is_file() and L.BILINGUAL_RE.search(f.name):
                return f
    if not L.CHAPTERS.exists():
        return None
    hits = [f for f in L.CHAPTERS.rglob(f"第{n}章*.md")
            if f.is_file() and L.BILINGUAL_RE.search(f.name)]
    return hits[0] if hits else None


def load_map(path):
    """读 CSV 映射表 → [(章号, 旧片段, 新行), ...]"""
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        for r in csv.reader(fh):
            if not r or not r[0].strip():
                continue
            if r[0].strip().lower() in ("章号", "chapter", "集号", "episode"):
                continue
            if len(r) < 3:
                print("[WARN] 跳过无效行（需 3 列）：%s" % r)
                continue
            try:
                n = int(r[0].strip())
            except ValueError:
                print("[WARN] 跳过章号非数字行：%s" % r)
                continue
            old, new = r[1].strip(), r[2].strip()
            if not old or not new:
                print("[WARN] 跳过空片段/新行：%s" % r)
                continue
            rows.append((n, old, new))
    return rows


def apply_to_file(path, rows, dry_run, mode="segment"):
    """
    在单个文件内应用一批映射。
    mode='segment'（默认，推荐）：**段内替换**——只把 old 片段换成 new，
        段落其余内容原样保留。适合小说长段（往往只改一句）。
    mode='line'：整段替换为 new（沿用 MTPE 原行为，适用于 new 是完整改写段）。
    返回 (成功数, 变更列表[(行号, 旧, 新)], 未匹配列表[(旧片段)])。
    """
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    # 定位英文段所在行号（对照版：含字母、不含中文、非标题/分隔/红标）
    en_rows = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s or s in ("---", "***", "___") or s.startswith("#"):
            continue
        if RED_OPEN in s:
            continue          # 已标红，避免嵌套
        if L.is_english(s):
            en_rows.append(i)

    changed, missed = [], []
    new_lines = list(lines)
    used_rows = set()
    for _n, old, new in rows:
        rx = re.compile(re.escape(old), re.I)
        hit = False
        for i in en_rows:
            if i in used_rows:
                continue      # 一行只接受一条映射，避免叠加污染
            if rx.search(new_lines[i]):
                if mode == "line":
                    new_lines[i] = RED_OPEN + new + RED_CLOSE
                else:
                    new_lines[i] = rx.sub(lambda _m: RED_OPEN + new + RED_CLOSE,
                                           new_lines[i], count=1)
                changed.append((i, lines[i], new_lines[i]))
                used_rows.add(i)
                hit = True
                break
        if not hit:
            missed.append(old)
    if not dry_run and changed:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return len(changed), changed, missed


def make_template(path, chapters):
    """生成空白映射模板：列出每章英文段前 N 段，供人工填 old/new。"""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["章号", "旧英文片段", "新英文行"])
        for n in chapters:
            ch_dir = L.CHAPTERS / f"第{n}章"
            if not ch_dir.is_dir():
                continue
            _src, paras = L.en_paragraphs(ch_dir, prefer="对照版")
            for i, para in enumerate(paras[:60], 1):
                w.writerow([n, para[:40], ""])
    print(f"[OK] 模板已生成（{path}）：每章最多列 60 段首 40 字符，填入新英文行即可")


def main():
    ap = argparse.ArgumentParser(description="审校红标批量落地（默认 dry-run）")
    ap.add_argument("--map", help="UTF-8 CSV 映射表：章号,旧英文片段,新英文行")
    ap.add_argument("--apply", action="store_true", help="实际写对照版（默认 dry-run）")
    ap.add_argument("--mode", default="segment", choices=["segment", "line"],
                    help="segment=段内替换（默认，只换 old 片段，保留段其余内容）；"
                         "line=整段替换为 new（new 须是完整改写段）")
    ap.add_argument("--make-template", help="生成空白映射模板到指定路径")
    ap.add_argument("--chapter", default="", help="配合 --make-template：章号区间/列表")
    args = ap.parse_args()

    if args.make_template:
        lo, hi = L.parse_range(args.chapter)
        chapters = [n for n, _ in L.chapter_dirs(lo, hi)]
        if not chapters:
            print("[ERROR] 未找到章节，请检查 --chapter 范围")
            return 2
        Path(args.make_template).parent.mkdir(parents=True, exist_ok=True)
        make_template(args.make_template, chapters)
        return 0

    if not args.map:
        print("[ERROR] 需 --map <CSV> 或 --make-template <CSV>")
        return 2
    map_path = Path(args.map)
    if not map_path.is_absolute():
        map_path = L.BASE / args.map
    if not map_path.is_file():
        print("[FAIL] 映射表不存在：%s" % map_path)
        return 2

    rows = load_map(map_path)
    if not rows:
        print("[FAIL] 映射表无有效数据行")
        return 2

    dry = not args.apply
    print("=== 红标落地（%s · %s 模式） ===" % ("DRY-RUN" if dry else "APPLY", args.mode))
    print("映射行数：%d\n" % len(rows))

    by_ch = {}
    for n, old, new in rows:
        by_ch.setdefault(n, []).append((n, old, new))

    total = 0
    all_missed = []
    for n in sorted(by_ch):
        path = find_target(n)
        if not path:
            print(f"[SKIP] 第{n}章 未找到对照版")
            all_missed.append(f"第{n}章:对照版缺失")
            continue
        cnt, changed, missed = apply_to_file(path, by_ch[n], dry_run=dry, mode=args.mode)
        total += cnt
        print(f"第{n}章 {path.name}：落地 {cnt} 处" + (f"，未匹配 {len(missed)}" if missed else ""))
        for ln, before, after in changed:
            print(f"  L{ln + 1}：{before.strip()[:80]}")
            print(f"    → {after[:100]}")
        for old in missed:
            print(f"  [MISS] {old[:70]}")
            all_missed.append(f"第{n}章:{old[:40]}")

    print("")
    print(f"合计落地 {total} 处。")
    if dry and total:
        print("如需生效请加 --apply（落地后请跑 sync_bilingual.py --apply 重生成纯英版）")
    if all_missed:
        print(f"[WARN] {len(all_missed)} 条未落地（对照已变或片段不匹配，需人工核对）：")
        for m in all_missed[:20]:
            print(f"  {m}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
