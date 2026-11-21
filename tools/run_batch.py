#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_batch.py — 连续批次编排：英文行文件 → 对照真源 → 纯英派生 → 双语校验 → 门禁 → 台账

目的：让全书补译可以「批次之间不插入审批」地连续推进，并支持跨会话断点续跑。
每章唯一需要人工/模型产出的，是逐段英文行文件；中文行一律由本编排器从磁盘原文重取，
从根上保证「中文原文零改动」与段落严格 1:1。

输入：`项目文档/待译英文行/ch<N>_en.txt`
  - 每行一段英文，行数必须等于该章原文正文段数（章题不计）
  - 可选首行 `#TITLE: <英文题名>`；缺省 `Chapter N`
  - 处理成功的章会被记入台账；失败的章留在本目录，下批自动重试

每章流水线（任一环节失败即记错并继续下一章，不中断整批）：
  1. compose_bilingual.py --apply --force   （中文取自原文，生成唯一真源）
  2. extract_pure_en.py --apply --force     （派生纯英译文）
  3. sync_bilingual.py                      （只读校验段数与 MD5）
  4. lqa_gates.py --fail-on P0              （P0 只含真源/中文/段数/工程硬红线；风格项已降 INFO/P1）
  5. prepare_full_scope.py --refresh --apply + project_status.py --apply（刷新台账与进度基线）

用法（参数全 ASCII）：
  python tools/run_batch.py                          # dry-run，列出待处理章与段数对齐情况
  python tools/run_batch.py --apply                 # 连续处理全部待处理章
  python tools/run_batch.py --apply --limit 5       # 本批最多 5 章
  python tools/run_batch.py --apply --only 91,92    # 只处理指定章

红线：不改判据阈值、不加豁免；派生物只由 extract_pure_en 生成；禁 git 操作；
      临时英文行文件放系统 Temp 并即时删除。
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
DOCS = BASE / "项目文档"
INBOX = DOCS / "待译英文行"
LEDGER = DOCS / "全书翻译台账.json"
CHAPTERS = BASE / "章节原文"
PY = sys.executable
FILE_RE = re.compile(r"ch(\d+)_en\.txt$")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def run(cmd, timeout=180):
    r = subprocess.run([PY, *cmd], cwd=str(BASE), capture_output=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def nonempty_lines(path):
    return [ln for ln in path.read_text(encoding="utf-8-sig").splitlines() if ln.strip()]


def collect(only):
    out = {}
    if not INBOX.is_dir():
        return out
    for p in sorted(INBOX.glob("ch*_en.txt")):
        m = FILE_RE.match(p.name)
        if not m:
            continue
        n = int(m.group(1))
        if only and n not in only:
            continue
        out[n] = p
    return out


def zh_paras(n):
    p = CHAPTERS / f"第{n}章" / f"第{n}章原文.md"
    if not p.is_file():
        return None
    lines = nonempty_lines(p)
    return lines[1:] if lines else []


def process(n, p):
    """处理单章，返回 (ok, steps, err)。"""
    lines = nonempty_lines(p)
    title = f"Chapter {n}"
    if lines and lines[0].startswith("#TITLE:"):
        title = lines[0][len("#TITLE:"):].strip() or title
        lines = lines[1:]

    zp = zh_paras(n)
    if zp is None:
        return False, [], f"第{n}章原文不存在"
    if len(lines) != len(zp):
        return False, [], (f"段落数不等：原文 {len(zp)} · 英文 {len(lines)}；"
                           f"补齐英文行后下批自动重试")

    tmp = Path(tempfile.gettempdir()) / f"runbatch_{n}_{stamp()}.txt"
    steps = []
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")

        for label, cmd in [
            ("compose", ["tools/compose_bilingual.py", "--chapter", str(n),
                         "--title", title, "--en", str(tmp), "--apply", "--force"]),
            ("derive", ["tools/extract_pure_en.py", "--chapter", str(n),
                        "--apply", "--force"]),
            ("sync", ["tools/sync_bilingual.py", "--chapter", str(n)]),
            ("gates", ["tools/lqa_gates.py", "--chapter", str(n), "--fail-on", "P0"]),
        ]:
            try:
                rc, out = run(cmd)
            except subprocess.TimeoutExpired:
                rc, out = 124, "TIMEOUT"
            tail = " | ".join(x.strip() for x in out.splitlines() if x.strip())[-220:]
            steps.append((label, rc, tail))
            if rc != 0:
                return False, steps, f"{label} 退出码 {rc}"
        return True, steps, ""
    finally:
        tmp.unlink(missing_ok=True)


def refresh_baselines():
    run(["tools/prepare_full_scope.py", "--refresh", "--apply"])
    run(["tools/project_status.py", "--apply"])


def update_ledger(records):
    if not LEDGER.is_file():
        return
    try:
        data = json.loads(LEDGER.read_text(encoding="utf-8-sig"))
        data.setdefault("批次", []).append({
            "时间": now(),
            "处理章数": len(records),
            "通过": [r["章"] for r in records if r["通过"]],
            "失败": [r["章"] for r in records if not r["通过"]],
        })
        LEDGER.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
    except (OSError, ValueError) as e:
        print(f"[WARN] 台账写入失败：{e}")


def write_report(records, apply):
    path = DOCS / f"批次执行报告_{stamp()}.md"
    lines = [
        "# 连续批次执行报告", "",
        f"> 生成：{now()}（本机北京时间 UTC+8）· 工具 `tools/run_batch.py`",
        f"> 模式：{'已落盘' if apply else 'dry-run'}", "",
        "| 章 | 结果 | 环节退出码 | 说明 |", "|---|---|---|---|",
    ]
    for r in records:
        codes = " ".join(f"{k}={v}" for k, v, _ in r["环节"])
        lines.append(f"| 第{r['章']}章 | {'✅ 通过' if r['通过'] else '❌ 待重试'} | "
                     f"{codes} | {r['说明'] or '—'} |")
    ok = sum(1 for r in records if r["通过"])
    lines += ["", f"**合计**：处理 {len(records)} 章 · 通过 {ok} · 待重试 {len(records) - ok}",
              "", "> 通过标准：`compose → derive → sync → gates` 四环退出码均为 0，",
              "> 其中 `--fail-on P0` 只拦截真源/中文/段数/工程硬红线；风格项（G3–G7）已降 INFO/P1 不阻断。失败章留在 `项目文档/待译英文行/`，下批自动重试。", ""]
    if apply:
        DOCS.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main():
    ap = argparse.ArgumentParser(description="全书补译连续批次编排")
    ap.add_argument("--apply", action="store_true", help="实际落盘（默认 dry-run）")
    ap.add_argument("--limit", type=int, default=0, help="本批最多处理章数，0=不限")
    ap.add_argument("--only", default="", help="只处理指定章号，逗号分隔（由脚本自行拆分）")
    args = ap.parse_args()

    only = set()
    if args.only.strip():
        for x in re.split(r"[,\s]+", args.only.strip()):
            if x.isdigit():
                only.add(int(x))

    files = collect(only)
    if args.limit > 0:
        files = dict(sorted(files.items())[:args.limit])

    print("=" * 90)
    print(f"连续批次编排 · 模式={'落盘' if args.apply else 'dry-run'} · "
          f"待处理 {len(files)} 章 · {now()}")
    print("=" * 90)
    if not files:
        print("[INFO] `项目文档/待译英文行/` 无 ch<N>_en.txt；流水线就绪，放入英文行文件即可续跑。")
        return 0

    records = []
    for n, p in sorted(files.items()):
        zp = zh_paras(n)
        en = nonempty_lines(p)
        title = en[0] if en and en[0].startswith("#TITLE:") else ""
        en_n = len(en) - (1 if title else 0)
        align = "OK" if zp is not None and len(zp) == en_n else f"MISMATCH {len(zp) if zp else 0}/{en_n}"
        print(f"  第{n}章  {p.name}  对齐={align}")
        if not args.apply:
            continue
        ok, steps, err = process(n, p)
        records.append({"章": n, "通过": ok, "环节": steps, "说明": err})
        print(f"    → {'PASS' if ok else 'RETRY'} {err}")

    if args.apply:
        update_ledger(records)
        refresh_baselines()
        rep = write_report(records, apply=True)
        ok = sum(1 for r in records if r["通过"])
        print(f"\n[OK] 通过 {ok}/{len(records)} 章 · 报告 {rep.name} · 台账与进度基线已刷新")
        return 0 if ok == len(records) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
