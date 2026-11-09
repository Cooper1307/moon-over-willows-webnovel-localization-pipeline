# -*- coding: utf-8 -*-
"""
token_budget.py — 任务级 token 预算闸门与优化前后对比（降本增效 · 可验证口径）

用法：
  python tools/token_budget.py --task translate --chapter 31
  python tools/token_budget.py --task review --chapter 31 --strict
  python tools/token_budget.py --task terminology --chapter 31
  python tools/token_budget.py --task gate
  python tools/token_budget.py --task bootstrap
  python tools/token_budget.py --compare --chapter 31        # 打印 before/after 差值
  python tools/token_budget.py --mirrors                    # 多平台镜像冗余体量（收敛论据）

设计：
  - token 估算口径与 glossary_slice.py 一致：CJK 字符 ÷1.6 + 非 CJK ÷4。
  - 「before」= 优化前典型加载集（含全量 glossary.md）；「after」= 优化后最小加载集（术语切片/索引）。
  - 所有数字均由本脚本复跑得出，禁止凭记忆断言。
  - 仅标准库；不修改任何项目文件（--task 仅读取与估算）。
"""
import os, re, argparse, importlib.util, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 复用 glossary_slice 的解析与估算，保证口径一致
_spec = importlib.util.spec_from_file_location("gs", os.path.join(REPO, "tools", "glossary_slice.py"))
gs = importlib.util.module_from_spec(_spec)
try:
    _spec.loader.exec_module(gs)
except Exception:
    gs = None

BASE_FILES = [
    "AGENTS.md",
    "_记忆索引.md",
    ".codebuddy/rules/project_rules.md",
    ".codebuddy/rules/novel_rules.md",
]


def est_tok(text):
    if gs:
        return gs.est_tok(text)
    cjk = len(re.findall(r'[\u3400-\u9fff\uf900-\ufaff]', text))
    return int(cjk / 1.6 + (len(text) - cjk) / 4)


def file_tok(rel):
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        return 0
    return est_tok(open(p, encoding='utf-8').read())


def read_tok(rel):
    return file_tok(rel), rel


def glossary_after(chapter, strict):
    if gs is None:
        return 0
    sections = gs.parse(os.path.join(REPO, "glossary.md"))
    text, _ = gs.emit_slice(sections, chapter, strict, False)
    return est_tok(text)


def glossary_before():
    return file_tok("glossary.md")


# 不同任务的「前/后」加载集（相对路径列表）
def load_set(task, chapter, strict):
    ch = f"第{chapter}章" if chapter else ""
    chapter_files = (
        [f"章节原文/{ch}/{ch}原文.md", f"章节原文/{ch}/{ch}初译_对照.md",
         f"章节原文/{ch}/{ch}译文.md", f"章节原文/{ch}/{ch}术语与人设.md"]
        if chapter else []
    )
    before, after = [], []
    if task == "bootstrap":
        before = list(BASE_FILES)
        after = list(BASE_FILES)  # 会话引导固定成本；优化点是 memory 标注按需
    elif task == "gate":
        before = BASE_FILES + ["glossary.md"]
        after = BASE_FILES + ["术语表/glossary_index.md"]
    elif task == "terminology":
        before = BASE_FILES + ["glossary.md"] + chapter_files
        after = BASE_FILES + ["术语表/glossary_index.md"] + chapter_files
    elif task in ("translate", "review"):
        before = BASE_FILES + ["glossary.md"] + chapter_files
        # after：术语用切片（不在列表里单独计，下面用 glossary_after 替代 glossary.md）
        after = BASE_FILES + ["__SLICE__"] + chapter_files
    else:
        raise SystemExit(f"unknown task: {task}")
    return before, after


def sum_tokens(rel_list, chapter, strict):
    total = 0
    detail = []
    for rel in rel_list:
        if rel == "__SLICE__":
            t = glossary_after(chapter, strict)
            detail.append((t, f"术语表/glossary_slice_第{chapter}章.md" + (" [strict]" if strict else "")))
        else:
            t = file_tok(rel)
            if t or os.path.exists(os.path.join(REPO, rel)):
                detail.append((t, rel))
            else:
                detail.append((0, f"(missing) {rel}"))
        total += t
    return total, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--task', default='translate', choices=['bootstrap', 'translate', 'review', 'terminology', 'gate'])
    ap.add_argument('--chapter', type=int, default=31)
    ap.add_argument('--strict', action='store_true')
    ap.add_argument('--compare', action='store_true')
    ap.add_argument('--mirrors', action='store_true')
    args = ap.parse_args()

    if args.mirrors:
        mirror_dirs = [".codebuddy", ".trae", ".qoder", ".workbuddy", ".agent"]
        total = 0
        print("=== 多平台镜像冗余体量（收敛论据；非每会话必加载，属存储/漂移成本）===")
        for d in mirror_dirs:
            dp = os.path.join(REPO, d)
            if not os.path.isdir(dp):
                continue
            kb = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(dp) for f in fs) / 1024
            total += kb
            print(f"  {d:14s} {kb:8.1f} KB")
        print(f"  合计 {total:.1f} KB；若收敛为单一主源(.codebuddy)，可减去其余 4 份 ≈ {total*4/5:.1f} KB")
        return

    before, after = load_set(args.task, args.chapter, args.strict)
    b_tok, b_det = sum_tokens(before, args.chapter, args.strict)
    a_tok, a_det = sum_tokens(after, args.chapter, args.strict)

    print(f"=== TASK: {args.task}  chapter={args.chapter}{' [strict]' if args.strict else ''} ===")
    print(f"  BEFORE (优化前, 含全量 glossary): {b_tok:,} tok")
    for t, r in b_det:
        print(f"    {t:7,}  {r}")
    print(f"  AFTER  (优化后, 术语切片/索引):    {a_tok:,} tok")
    for t, r in a_det:
        print(f"    {t:7,}  {r}")
    if b_tok:
        print(f"  SAVING: ~{b_tok - a_tok:,} tok ({(1 - a_tok/b_tok)*100:.0f}% off)")

    if args.compare:
        print("\n=== COMPARE (优化前 vs 后) 汇总 ===")
        rows = []
        for t in ['bootstrap', 'gate', 'terminology', 'translate', 'review']:
            bf, af = load_set(t, args.chapter, args.strict)
            bt, _ = sum_tokens(bf, args.chapter, args.strict)
            at, _ = sum_tokens(af, args.chapter, args.strict)
            rows.append((t, bt, at))
        print(f"  {'task':12s} {'before':>9s} {'after':>9s} {'save%':>7s}")
        for t, bt, at in rows:
            print(f"  {t:12s} {bt:9,} {at:9,} {(1-at/bt)*100:6.0f}%")


if __name__ == '__main__':
    main()
