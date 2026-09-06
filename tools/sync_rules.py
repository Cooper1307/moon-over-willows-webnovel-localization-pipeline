# -*- coding: utf-8 -*-
"""
sync_rules.py — 四 IDE 规则同步（.codebuddy / .trae / .qoder / .antigravity）

功能：
  递归扫描指定根目录下所有项目的 rules/ 规则文件（*.md），
  以指定主源（master）为准，向其余两个 IDE 目录单向同步：
  缺失则复制、内容不同则覆盖；仅存在于目标方的文件只报告不改动。
  同时同步 skills/、agents/ 与 memory/ 目录（递归，含子目录），
  规则：主源目录的整棵子树单向复制到目标方（缺失/差异覆盖），
  目标方多出的文件仅报告不改动。

用法：
  python tools/sync_rules.py --root <工作区根目录>
  python tools/sync_rules.py --root <工作区根目录> --scope all
  python tools/sync_rules.py --root <工作区根目录> --scope all --apply
  python tools/sync_rules.py --root <工作区根目录> --master qoder --apply
  python tools/sync_rules.py --root <工作区根目录> --master trae --targets qoder --apply

参数：
  --root     工作区/项目根目录（必填）
  --scope    root=仅根目录 / all=递归所有项目子目录（默认 root）
  --master   主源 IDE：cb / trae / qoder（默认 cb）
  --targets  同步目标，逗号分隔，默认为主源之外的其余两方
  --apply    实际写文件（默认 dry-run，只报告差异）
  --direction 已废弃的旧参数（cb2trae / trae2cb），仍可用，等价于指定
              --master 与 --targets，会被新参数覆盖。

依赖：仅标准库（os / sys / shutil / argparse）。
"""
import os
import sys
import shutil
import argparse

# Windows 控制台（PowerShell 默认 GBK）下保证中文输出不乱码
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EXCLUDE_DIRS = {".git", ".writing", "归档", "tools", "node_modules", "__pycache__"}

ALL_IDES = (".codebuddy", ".trae", ".qoder", ".antigravity", ".workbuddy")
IDE_ALIASES = {"cb": ".codebuddy", "trae": ".trae", "qoder": ".qoder", "anti": ".antigravity", "wb": ".workbuddy"}

# 兼容旧版 --direction 参数
LEGACY_DIRECTION = {
    "cb2trae": (".codebuddy", (".trae",)),
    "trae2cb": (".trae", (".codebuddy",)),
}


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def rule_files(ide_dir):
    """列出某 IDE rules/ 目录下所有 .md 规则文件名。"""
    d = os.path.join(ide_dir, "rules")
    if not os.path.isdir(d):
        return set()
    return {f for f in os.listdir(d)
            if f.endswith(".md") and os.path.isfile(os.path.join(d, f))}


def iter_rule_dirs(root, scope):
    """产出所有含 rules/*.md 的项目目录。"""
    if scope == "root":
        if any(rule_files(os.path.join(root, ide)) for ide in ALL_IDES):
            yield root
        return

    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        if any(rule_files(os.path.join(dirpath, ide)) for ide in ALL_IDES):
            yield dirpath


def tree_files(base):
    """返回目录下所有相对路径（含子目录），用于对比。"""
    if not os.path.isdir(base):
        return set()
    out = set()
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            out.add(os.path.relpath(full, base).replace("\\", "/"))
    return out


def sync_tree(proj_dir, master, targets, sub, apply):
    """单向同步 IDE 下的 skills/ 或 agents/ 或 memory/ 子树。"""
    rel = os.path.relpath(proj_dir, os.getcwd())
    m_root = os.path.join(proj_dir, master, sub)
    if not os.path.isdir(m_root):
        return  # 主源无此目录，跳过

    m_files = tree_files(m_root)
    if not m_files:
        return

    for relpath in sorted(m_files):
        src = os.path.join(m_root, relpath.replace("/", os.sep))
        for tgt in targets:
            dst = os.path.join(proj_dir, tgt, sub, relpath.replace("/", os.sep))
            if not os.path.isfile(dst):
                print("[MISS] %s：%s 缺 %s/%s，将从 %s 复制"
                      % (rel, tgt, sub, relpath, master))
                if apply:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copyfile(src, dst)
                    print("       → 已创建 %s" % os.path.relpath(dst, os.getcwd()))
                continue

            a = read_bytes(src)
            b = read_bytes(dst)
            if a == b:
                print("[OK  ] %s：%s/%s 一致（%s）" % (rel, sub, relpath, tgt))
            else:
                print("[DIFF] %s：%s/%s 不同（%s %d B ≠ %s %d B）"
                      % (rel, sub, relpath, master, len(a), tgt, len(b)))
                if apply:
                    shutil.copyfile(src, dst)
                    print("       → 已按 %s→%s 同步" % (master, tgt))

    # 目标方多出的文件：只报告
    for tgt in targets:
        extra = tree_files(os.path.join(proj_dir, tgt, sub)) - m_files
        for relpath in sorted(extra):
            print("[EXTRA] %s：%s 仅存在于目标方 %s/%s，主源无（不改动）"
                  % (rel, tgt, sub, relpath))


def sync_project(proj_dir, master, targets, apply):
    rel = os.path.relpath(proj_dir, os.getcwd())
    m_dir = os.path.join(proj_dir, master, "rules")
    m_files = rule_files(os.path.join(proj_dir, master))

    if not m_files:
        print("[SKIP] %s：主源 %s 无规则文件" % (rel, master))
        return

    for fname in sorted(m_files):
        src = os.path.join(m_dir, fname)
        for tgt in targets:
            dst = os.path.join(proj_dir, tgt, "rules", fname)
            if not os.path.isfile(dst):
                print("[MISS] %s：%s 缺 %s，将从 %s 复制" % (rel, tgt, fname, master))
                if apply:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copyfile(src, dst)
                    print("       → 已创建 %s" % os.path.relpath(dst, os.getcwd()))
                continue

            a = read_bytes(src)
            b = read_bytes(dst)
            if a == b:
                print("[OK  ] %s：%s 一致（%s）" % (rel, fname, tgt))
            else:
                print("[DIFF] %s：%s 不同（%s %d B ≠ %s %d B）"
                      % (rel, fname, master, len(a), tgt, len(b)))
                if apply:
                    shutil.copyfile(src, dst)
                    print("       → 已按 %s→%s 同步" % (master, tgt))

    # 仅存在于目标方、主源没有的文件：只报告，不改动
    extra = set()
    for tgt in targets:
        extra |= rule_files(os.path.join(proj_dir, tgt)) - m_files
    for fname in sorted(extra):
        print("[EXTRA] %s：%s 仅存在于目标方，主源 %s 无此文件（不改动）"
              % (rel, fname, master))

    # skills / agents / memory 目录同步
    for sub in ("skills", "agents", "memory"):
        sync_tree(proj_dir, master, targets, sub, apply)


def parse_args():
    ap = argparse.ArgumentParser(description="五 IDE 同步：rules 规则 + skills/agents/memory 子树（.codebuddy/.trae/.qoder/.antigravity/.workbuddy）")
    ap.add_argument("--root", required=True, help="工作区/项目根目录")
    ap.add_argument("--scope", choices=["root", "all"], default="root")
    ap.add_argument("--master", choices=sorted(IDE_ALIASES), default="cb",
                    help="主源 IDE（默认 cb）")
    ap.add_argument("--targets", default=None,
                    help="同步目标，逗号分隔（默认为主源之外的其余两方）")
    ap.add_argument("--direction", choices=sorted(LEGACY_DIRECTION), default=None,
                    help="已废弃：旧版双向参数，建议改用 --master/--targets")
    ap.add_argument("--apply", action="store_true", help="实际写文件（默认 dry-run）")
    return ap.parse_args()


def main():
    args = parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        raise SystemExit("[FAIL] 目录不存在：%s" % root)

    if args.direction:
        master, targets = LEGACY_DIRECTION[args.direction]
    else:
        master = IDE_ALIASES[args.master]
        if args.targets:
            # 允许直接传目录名（如 .agent），不局限于预设 IDE
            targets = tuple(IDE_ALIASES.get(t.strip(), t.strip())
                            for t in args.targets.split(",") if t.strip())
        else:
            targets = tuple(i for i in ALL_IDES if i != master)
    if master in targets:
        raise SystemExit("[FAIL] --targets 不能包含主源 %s" % master)

    mode = "APPLY" if args.apply else "DRY-RUN"
    print("=== sync_rules（%s） ===" % mode)
    print("根目录：%s | 范围：%s | 方向：%s→%s\n"
          % (root, args.scope, master, "/".join(targets)))

    dirs = list(iter_rule_dirs(root, args.scope))
    if not dirs:
        print("未找到任何 rules/*.md。")
        return
    for d in sorted(dirs):
        sync_project(d, master, targets, args.apply)

    print("\n完成。%s" % ("如需同步请加 --apply" if not args.apply else "已执行同步。"))


if __name__ == "__main__":
    main()
