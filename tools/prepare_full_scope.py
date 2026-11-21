#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare_full_scope.py — 全书 351 章原文接入 + 连续推进台账

背景：第 91–351 章原文已切分存于 章节原文/00_原文库/（gitignore 冷库、只读），
活跃目录 章节原文/第X章/ 只有 1–90 章，门禁/槽位/进度统计因此只覆盖 90 章。
本脚本把冷库原文**复制**（不移动、不改一个字节）接入活跃目录，扩展 MD5 基线到
351 章，并生成全书翻译台账（机器真源）与人读报告。

用法（参数全 ASCII；路径由 __file__ 推导，避免 PowerShell 中文路径 GBK 乱码）：
  python tools/prepare_full_scope.py                     # dry-run
  python tools/prepare_full_scope.py --apply            # 接入 + 扩基线 + 写台账
  python tools/prepare_full_scope.py --refresh --apply  # 每批译完后只刷新台账

红线：中文原文零改动（逐字节复制 + MD5 校验）；冷库只读；默认 dry-run；
      MD5 基线只在无冲突时才写，冲突即视为原文事故，绝不覆盖基线掩盖改动。
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
CHAPTERS = BASE / "章节原文"
COLD = CHAPTERS / "00_原文库"
DOCS = BASE / "项目文档"
MD5_BASELINE = DOCS / "原文MD5基线.json"
LEDGER = DOCS / "全书翻译台账.json"
TOTAL = 351
GAP_CHAPTERS = [1, 2, 70]

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chapter_lib as L  # noqa: E402

CHAPTER_DIR_RE = L.CHAPTER_DIR_RE
ORIGIN_RE = L.ORIGIN_RE
TERM_RE = re.compile(r"^第\d+章术语与人设\.md$")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def md5(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def cold_chapters():
    """冷库章号 → 目录。"""
    out = {}
    if not COLD.is_dir():
        return out
    for d in COLD.iterdir():
        m = CHAPTER_DIR_RE.match(d.name)
        if d.is_dir() and m:
            out[int(m.group(1))] = d
    return out


def active_dir(n):
    return CHAPTERS / f"第{n}章"


def integrate(apply):
    """冷库原文 + 术语与人设 → 活跃目录；已存在则校验字节一致，绝不覆盖。"""
    cold = cold_chapters()
    done, skipped, conflicts, planned, copied = [], [], [], [], []
    for n in sorted(cold):
        src, dst = cold[n], active_dir(n)
        files = [f for f in sorted(src.iterdir())
                 if f.is_file() and (ORIGIN_RE.match(f.name) or TERM_RE.match(f.name))]
        if not any(ORIGIN_RE.match(f.name) for f in files):
            conflicts.append(f"第{n}章：冷库缺原文文件")
            continue
        todo, bad = [], False
        for f in files:
            target = dst / f.name
            if target.exists():
                if md5(target) == md5(f):
                    skipped.append(f"第{n}章/{f.name}")
                else:
                    conflicts.append(f"第{n}章/{f.name}：活跃副本与冷库字节不一致，未覆盖")
                    bad = True
                continue
            todo.append((f, target))
        if bad:
            continue  # 该章整体不写入，避免半接入状态
        planned.extend(f"第{n}章/{f.name}" for f, _ in todo)
        if apply and todo:
            dst.mkdir(parents=True, exist_ok=True)
            for f, target in todo:
                shutil.copy2(f, target)
                if md5(target) != md5(f):
                    conflicts.append(f"第{n}章/{f.name}：复制后 MD5 不一致")
                else:
                    copied.append(f"第{n}章/{f.name}")
        done.append(n)
    return {"接入章": done, "接入章数": len(done),
            "计划复制": planned, "实际复制": copied,
            "已存在且一致": skipped, "冲突": conflicts}


def refresh_md5(apply):
    """把中文原文 MD5 基线扩到全书 351 章；已有条目只校验不改写。"""
    if MD5_BASELINE.is_file():
        data = json.loads(MD5_BASELINE.read_text(encoding="utf-8-sig"))
    else:
        data = {"说明": "中文原文 MD5 基线（G1 门禁）。原文全程零改动，任何不一致即为事故。",
                "files": {}}
    files = data.setdefault("files", {})
    added, mismatched, missing = [], [], []
    for n in range(1, TOTAL + 1):
        p = active_dir(n) / f"第{n}章原文.md"
        if not p.is_file():
            missing.append(n)
            continue
        key, h = f"第{n}章/第{n}章原文.md", md5(p)
        if key in files:
            if files[key] != h:
                mismatched.append(key)
        else:
            files[key] = h
            added.append(key)
    data["最后扩展"] = now()
    data["覆盖章数"] = len(files)
    if apply and not mismatched:
        DOCS.mkdir(parents=True, exist_ok=True)
        MD5_BASELINE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
    return {"新增基线条目": added, "冲突": mismatched, "缺原文文件章": missing,
            "覆盖章数": len(files), "已写入": bool(apply and not mismatched)}


def build_ledger(apply):
    """按磁盘真源重算已译/待译章；保留已有批次与复验轮次（跨会话接续真源）。"""
    prev = {}
    if LEDGER.is_file():
        try:
            prev = json.loads(LEDGER.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            prev = {}
    translated, pending, no_origin = [], [], []
    for n in range(1, TOTAL + 1):
        d = active_dir(n)
        if not d.is_dir():
            pending.append(n)
            no_origin.append(n)
            continue
        if not (d / f"第{n}章原文.md").is_file():
            no_origin.append(n)
        bi = L.parse_bilingual(d)
        (translated if bi["pairs"] else pending).append(n)
    data = {
        "生成时间": prev.get("生成时间", now()),
        "最后刷新": now(),
        "全书章数": TOTAL,
        "已译章": translated,
        "待译章": pending,
        "已译章数": len(translated),
        "待译章数": len(pending),
        "三章缺口": [n for n in GAP_CHAPTERS if n in pending],
        "缺原文文件章": no_origin,
        "批次": prev.get("批次", []),
        "复验轮次": prev.get("复验轮次", []),
        "终止条件": {
            "全书P0": 0,
            "全书P1": 0,
            "待译章数": 0,
            "复验每轮全绿": True,
            "零占位符": True,
            "SC_E通过": True,
        },
    }
    if apply:
        DOCS.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
    return data


def write_report(apply, integration, baseline, ledger, refresh_only):
    p = DOCS / f"全书翻译批次台账_{stamp()}.md"
    lines = [
        "# 全书翻译批次台账", "",
        f"> 生成：{now()}（本机北京时间 UTC+8）· 工具 `tools/prepare_full_scope.py`",
        f"> 模式：{'只刷新台账' if refresh_only else '原文接入 + 基线扩展 + 台账'} · "
        f"{'已落盘' if apply else 'dry-run（未写任何文件）'}", "",
        "## 一、当前进度（磁盘实测，唯一真源）", "",
        "| 项 | 值 |", "|---|---|",
        f"| 全书章数 | {ledger['全书章数']} |",
        f"| 已译章（有对照版真源） | {ledger['已译章数']} |",
        f"| 待译章 | {ledger['待译章数']} |",
        f"| 三章缺口（1/2/70） | {ledger['三章缺口'] or '已补齐'} |",
        f"| 缺原文文件章 | {ledger['缺原文文件章'] or '无'} |", "",
    ]
    if not refresh_only:
        lines += [
            "## 二、原文接入", "",
            f"- 冷库 `章节原文/00_原文库/` 读出 **{integration['接入章数']}** 章",
            f"- 计划复制 {len(integration['计划复制'])} 个文件 · 实际复制 "
            f"{len(integration['实际复制'])} 个 · 已存在且字节一致 {len(integration['已存在且一致'])} 个",
            f"- 冲突：**{integration['冲突'] or '无'}**",
            "", "## 三、中文原文 MD5 基线", "",
            f"- 新增条目 {len(baseline['新增基线条目'])} 条 · 覆盖 {baseline['覆盖章数']} 章",
            f"- 冲突（原文被改动，禁止覆盖基线）：**{baseline['冲突'] or '无'}**",
            f"- 缺原文文件章：{baseline['缺原文文件章'] or '无'}",
            "",
        ]
    lines += [
        "## 四、终止条件（未全部满足不得停止）", "",
        "| 条件 | 目标值 |", "|---|---|",
    ]
    for k, v in ledger["终止条件"].items():
        lines.append(f"| {k} | {v} |")
    lines += [
        "", "## 五、连续推进约定", "",
        "- 批次之间不插入「是否继续」审批；每批译完跑 `--refresh --apply` 刷新台账。",
        "- 每批收尾跑 `session_check.py --end --apply`，下批开工跑 `--start --apply`。",
        "- 台账 `项目文档/全书翻译台账.json` 是跨会话接续的机器真源，本 md 是人读快照。",
        "- 终止闸门：待译章清零后，全书 `P0=0` 且 `P1=0`、三层复验每轮全绿、"
        "交付件与真源逐章对应、SC-E 通过，才允许停止。", "",
        "## 六、待译章清单", "",
        f"```\n{ledger['待译章']}\n```", "",
    ]
    if apply:
        DOCS.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(lines), encoding="utf-8")
    return p


def main():
    ap = argparse.ArgumentParser(description="全书 351 章原文接入与翻译台账")
    ap.add_argument("--apply", action="store_true", help="实际写文件（默认 dry-run）")
    ap.add_argument("--refresh", action="store_true", help="只刷新台账，不接入原文/不动基线")
    args = ap.parse_args()

    print("=" * 90)
    print(f"全书范围接入 · 模式={'落盘' if args.apply else 'dry-run'}"
          f" · refresh={args.refresh} · {now()}")
    print("=" * 90)

    if args.refresh:
        integration = {"接入章数": 0, "计划复制": [], "实际复制": [],
                       "已存在且一致": [], "冲突": []}
        baseline = {"新增基线条目": [], "冲突": [], "缺原文文件章": [],
                    "覆盖章数": 0, "已写入": False}
    else:
        integration = integrate(args.apply)
        print(f"[接入] 冷库读出 {integration['接入章数']} 章 · "
              f"计划复制 {len(integration['计划复制'])} 文件 · "
              f"实际复制 {len(integration['实际复制'])} 文件 · "
              f"冲突 {len(integration['冲突'])}")
        baseline = refresh_md5(args.apply)
        print(f"[基线] 新增 {len(baseline['新增基线条目'])} 条 · "
              f"覆盖 {baseline['覆盖章数']} 章 · 冲突 {len(baseline['冲突'])}")

    ledger = build_ledger(args.apply)
    print(f"[台账] 已译 {ledger['已译章数']} 章 · 待译 {ledger['待译章数']} 章 · "
          f"三章缺口 {ledger['三章缺口'] or '已补齐'}")
    report = write_report(args.apply, integration, baseline, ledger, args.refresh)
    print(f"[报告] {report.name}{'（已写入）' if args.apply else '（dry-run 未写入）'}")

    conflicts = integration["冲突"] + baseline["冲突"]
    if conflicts:
        print(f"\n[FAIL] 检测到 {len(conflicts)} 处原文冲突，须排查：{conflicts[:5]}")
        return 1
    print("\n[OK] 无原文冲突；中文原文零改动已校验。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
