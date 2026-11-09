# -*- coding: utf-8 -*-
"""
session_check.py — 会话起止闸门（工程约束 §⑤ SC-S* / SC-E* 的自动化执行）

用法（见《工程约束与会话规程.md》§⑤）：
  python tools/session_check.py --start --apply    # 开工闸门：SC-S1~S6，写基线快照
  python tools/session_check.py --end --apply      # 收尾闸门：SC-E1~E5，对比基线
  缺 --apply 时只打印不落盘（dry-run）；--start/--end 必选其一。

检查项：
  --start: SC-S1 git 本地=远端 | SC-S2 真源完好(P0=0) | SC-S3 垃圾文件 | SC-S4 冻结镜像漂移抽查
           SC-S5 交付 docx 笔名抽样审计(20个) | SC-S6 基线快照(P0/P1/完成度/docx数)
  --end:   SC-E1 docx 作者全量复审 | SC-E2 基线对比 | SC-E3 临时文件清理
           SC-E4 四件套最后更新提醒 | SC-E5 未提交清单+push核对（SC-E6 交接更新为人工项，报告内提醒）

工程规范：仅标准库；复用 chapter_lib（chapter_dirs/cn_source_check）与既有脚本 subprocess 调用；
默认 dry-run；中文路径由 __file__ 推导；stdout 重配 UTF-8；逐项 try/except 汇总。
退出码：0 通过；1 硬失败（须排查后才能开工/提交）；告警不改变退出码。
"""
import os
import re
import sys
import json
import glob
import subprocess
import zipfile
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent
DOCS = REPO / "项目文档"
BASELINE = DOCS / "会话基线.json"
BJ = timezone(timedelta(hours=8))
AUTHOR = "CooperChen"
FORBIDDEN_META = ["审校CooperChen", "审校", "CodeBuddy", "python-docx", "Co-Author", "co-author", "协作者"]
SAMPLE_LIMIT = 20

sys.path.insert(0, str(TOOLS))
import chapter_lib  # noqa: E402


def now_bj():
    return datetime.now(timezone.utc).astimezone(BJ)


def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class Gate:
    def __init__(self):
        self.rows = []      # (id, name, status PASS/WARN/FAIL/INFO, detail)
        self.hard_fail = False

    def add(self, cid, name, status, detail=""):
        self.rows.append((cid, name, status, detail))
        if status == "FAIL":
            self.hard_fail = True

    def print(self):
        for cid, name, status, detail in self.rows:
            print("  [%-4s] %-6s %s%s" % (status, cid, name, ("　— " + detail) if detail else ""))

    def to_md(self, phase):
        lines = ["# 会话%s检查报告" % ("开工" if phase == "start" else "收尾"), "",
                 "> 生成：%s（北京时间 UTC+8）· 工具 `tools/session_check.py --%s`" % (
                     now_bj().strftime("%Y-%m-%d %H:%M:%S"), phase), "",
                 "| # | 检查项 | 结果 | 说明 |", "|---|---|---|---|"]
        for cid, name, status, detail in self.rows:
            lines.append("| %s | %s | %s | %s |" % (cid, name, status, detail or "—"))
        n_fail = sum(1 for r in self.rows if r[2] == "FAIL")
        n_warn = sum(1 for r in self.rows if r[2] == "WARN")
        lines += ["", "**结论**：%s（FAIL %d · WARN %d）" % (
            "❌ 硬失败，须排查" if self.hard_fail else "✅ 通过", n_fail, n_warn)]
        if phase == "end":
            lines += ["", "> SC-E6（人工项）：任务边界有变化时，更新 `交接_新对话.md` 遗留清单与首要指令。"]
        return "\n".join(lines) + "\n"


def git(*args):
    return subprocess.run(["git", *args], cwd=str(REPO), capture_output=True,
                          encoding="utf-8", errors="replace")


# ---------------------------------------------------------------- 共用检查件
def check_git_sync(g):
    r = git("rev-parse", "HEAD")
    local = (r.stdout or "").strip()
    r2 = git("ls-remote", "origin", "refs/heads/master")
    remote = (r2.stdout or "").split()[0] if (r2.stdout or "").strip() else ""
    if not local or not remote:
        g.add("S1/E5", "git 本地=远端", "WARN", "无法取得 HEAD 或远端（网络/仓库异常：%s）" % (r2.stderr or "")[-80:])
        return local, remote
    ok = local == remote
    g.add("S1/E5", "git 本地=远端", "PASS" if ok else "WARN",
          ("一致 %s" % local[:10]) if ok else "本地 %s ≠ 远端 %s（存在未推送提交）" % (local[:10], remote[:10]))
    return local, remote


def junk_scan():
    """(硬失败清单, 告警清单, 信息清单)。只扫活跃工作态；归档/ 冷存储内的历史件属设计如此，不判。"""
    hard, warn, info = [], [], []
    for path in REPO.rglob("*"):
        name = path.name
        rel = path.relative_to(REPO).as_posix()
        if rel.startswith(".git/") or path.is_dir():
            continue
        if rel.startswith("归档/") or rel.startswith("章节原文/00_原文库/"):
            continue  # 冷存储：内容不受活跃区清理规则约束
        if name.endswith(".bak") or name.endswith(".tmp_scrub"):
            hard.append(rel)
        elif name.endswith(".baiduyun.uploading.cfg"):
            warn.append(rel)
        elif path.suffix == ".pyc" or name == "__pycache__":
            info.append(rel)
    return hard, warn, info


def docx_meta(path):
    """读取 docx 作者字段与修订作者（只读）。"""
    out = {"creator": None, "lastModifiedBy": None, "modified": None, "rev_authors": [], "meta_dirty": []}
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            if "docProps/core.xml" in names:
                core = z.read("docProps/core.xml").decode("utf-8", "replace")
                m = re.search(r"<dc:creator\b[^>]*>(.*?)</dc:creator>", core, re.S)
                out["creator"] = m.group(1).strip() if m else None
                m = re.search(r"<cp:lastModifiedBy\b[^>]*>(.*?)</cp:lastModifiedBy>", core, re.S)
                out["lastModifiedBy"] = m.group(1).strip() if m else None
                m = re.search(r"<dcterms:modified\b[^>]*>(.*?)</dcterms:modified>", core, re.S)
                out["modified"] = m.group(1).strip() if m else None
                for bad in FORBIDDEN_META:
                    if bad in core:
                        out["meta_dirty"].append(bad)
            if "docProps/app.xml" in names:
                app = z.read("docProps/app.xml").decode("utf-8", "replace")
                for bad in FORBIDDEN_META:
                    if bad in app:
                        out["meta_dirty"].append(bad)
            if "word/document.xml" in names:
                doc = z.read("word/document.xml").decode("utf-8", "replace")
                out["rev_authors"] = sorted(set(re.findall(r'w:author="([^"]*)"', doc)))
    except Exception as e:  # noqa: BLE001
        out["meta_dirty"].append("READ_ERR:%s" % e)
    return out


def check_docx(g, cid, sample_only):
    files = sorted((REPO / "交付版").glob("*.docx")) + sorted((REPO / "docx交付").rglob("*.docx"))
    files = sorted(set(files))
    if sample_only:
        files = files[:SAMPLE_LIMIT]
    bad = []
    for p in files:
        meta = docx_meta(p)
        errs = []
        if meta["creator"] != AUTHOR:
            errs.append("creator=%r" % meta["creator"])
        if meta["lastModifiedBy"] not in (AUTHOR, None):
            errs.append("lastModifiedBy=%r" % meta["lastModifiedBy"])
        for a in meta["rev_authors"]:
            if a != AUTHOR:
                errs.append("w:author=%r" % a)
        errs += ["元数据残留%r" % b for b in meta["meta_dirty"]]
        if errs:
            bad.append("%s: %s" % (p.name, "; ".join(errs[:3])))
    scope = "抽样%d" % min(SAMPLE_LIMIT, len(files)) if sample_only else "全量%d" % len(files)
    if bad:
        g.add(cid, "docx 作者审计（%s）" % scope, "FAIL", "%d 个不合规，首例 %s" % (len(bad), bad[0][:90]))
    else:
        g.add(cid, "docx 作者审计（%s）" % scope, "PASS", "%d 个均唯一 %s" % (len(files), AUTHOR))
    return len(files), bad


def check_source(g):
    p0, p1, ok = [], [], 0
    try:
        for n, d in chapter_lib.chapter_dirs(1, 90):
            info = chapter_lib.cn_source_check(d)
            if info["level"] == "P0":
                p0.append(n)
            elif info["level"] == "P1":
                p1.append(n)
            else:
                ok += 1
        detail = "OK %d · P0 %d %s · P1 %d %s" % (
            ok, len(p0), p0[:4], len(p1), p1[:4])
        known_gap = set(p1) <= {1, 2, 70}
        if p0:
            g.add("S2", "真源完好", "FAIL", "真源 P0≠0：%s" % p0[:6])
        elif p1 and not known_gap:
            g.add("S2", "真源完好", "WARN", "出现基线外 P1：%s" % p1[:6])
        else:
            g.add("S2", "真源完好", "PASS", detail + "（P1 限已知缺口 1/2/70）")
        return {"source_ok": ok, "p0": len(p0), "p1": len(p1), "p1_chapters": p1}
    except Exception as e:  # noqa: BLE001
        g.add("S2", "真源完好", "WARN", "chapter_lib 调用异常：%s" % e)
        return None


def check_mirrors(g):
    canon = REPO / ".codebuddy" / "rules" / "project_rules.md"
    drifted, missing = [], []
    if not canon.exists():
        g.add("S4", "冻结镜像漂移抽查", "WARN", "主源 project_rules.md 不存在")
        return
    import hashlib
    ref = hashlib.sha1(canon.read_bytes()).hexdigest()[:10]
    for d in (".trae", ".qoder", ".workbuddy", ".agent"):
        f = REPO / d / "rules" / "project_rules.md"
        if not f.exists():
            missing.append(d)
            continue
        if hashlib.sha1(f.read_bytes()).hexdigest()[:10] != ref:
            drifted.append(d)
    g.add("S4", "冻结镜像漂移抽查", "INFO",
          "漂移 %s · 缺失 %s（冻结镜像属预期；仅用户在该平台工作时按 MIRRORS.md 重同步）" % (drifted or "无", missing or "无"))


def run_metrics():
    """subprocess 复用既有脚本，解析 P0/P1/完成度/对照章数/docx 数。"""
    out = {}
    try:
        r = subprocess.run([sys.executable, str(TOOLS / "lqa_gates.py")], cwd=str(REPO),
                           capture_output=True, encoding="utf-8", errors="replace", timeout=300)
        m = re.search(r"P0 合计 (\d+)", r.stdout or "")
        n = re.search(r"P1 合计 (\d+)", r.stdout or "")
        out["p0"], out["p1"] = (int(m.group(1)) if m else None), (int(n.group(1)) if n else None)
    except Exception as e:  # noqa: BLE001
        out["p0"] = out["p1"] = None
        out["_lqa_err"] = str(e)[:80]
    try:
        r = subprocess.run([sys.executable, str(TOOLS / "project_status.py"), "--metrics"], cwd=str(REPO),
                           capture_output=True, encoding="utf-8", errors="replace", timeout=300)
        m = re.search(r"字数完成度\s+([\d.]+)%", r.stdout or "")
        n = re.search(r"有初译_对照的章数\s+(\d+)", r.stdout or "")
        out["pct"] = float(m.group(1)) if m else None
        out["duizhao"] = int(n.group(1)) if n else None
    except Exception as e:  # noqa: BLE001
        out["pct"] = out["duizhao"] = None
        out["_ps_err"] = str(e)[:80]
    out["docx_delivery"] = len(list((REPO / "交付版").glob("*.docx")))
    out["docx_review"] = len(list((REPO / "docx交付").rglob("*.docx")))
    return out


# ---------------------------------------------------------------- 开工闸门
def do_start(apply):
    g = Gate()
    print("=== 会话开工闸门（SC-S1~S6）===")
    check_git_sync(g)

    src = check_source(g)

    hard, warn, info = junk_scan()
    if hard:
        g.add("S3", "垃圾文件扫描", "FAIL", "%d 个硬失败（.bak/.tmp_scrub）：%s" % (len(hard), hard[:5]))
    elif warn:
        g.add("S3", "垃圾文件扫描", "WARN", "%d 个百度云同步残留（可清理）：%s" % (len(warn), warn[:3]))
    else:
        g.add("S3", "垃圾文件扫描", "PASS", "无 .bak/.tmp_scrub/.baiduyun 残留（__pycache__ %d 处属未跟踪缓存）" % len(info))

    check_mirrors(g)
    check_docx(g, "S5", sample_only=True)

    metrics = run_metrics()
    g.add("S6", "基线快照", "INFO",
          "P0 %s · P1 %s · 完成度 %s%% · 对照 %s 章 · docx 交付 %s/核验 %s" % (
              metrics.get("p0"), metrics.get("p1"), metrics.get("pct"),
              metrics.get("duizhao"), metrics.get("docx_delivery"), metrics.get("docx_review")))

    g.print()
    if apply and not g.hard_fail:
        DOCS.mkdir(exist_ok=True)
        snap = dict(metrics)
        if src:  # 真源检查与门禁指标同名键（p0/p1），分名空间防覆盖
            snap["source_ok_chapters"] = src.get("source_ok")
            snap["source_p0"] = src.get("p0")
            snap["source_p1"] = src.get("p1")
        BASELINE.write_text(json.dumps({"ts": now_bj().strftime("%Y-%m-%d %H:%M:%S"),
                                        "phase": "start", **snap},
                                       ensure_ascii=False, indent=2), encoding="utf-8")
        rep = DOCS / ("会话检查_%s.md" % ts())
        rep.write_text(g.to_md("start"), encoding="utf-8")
        print("[OK] 基线快照 → %s" % BASELINE.name)
        print("[OK] 报告 → %s" % rep.name)
    elif apply and g.hard_fail:
        print("[STOP] 存在硬失败，未写基线；排查后方可开工。")
    return 1 if g.hard_fail else 0


# ---------------------------------------------------------------- 收尾闸门
def do_end(apply):
    g = Gate()
    print("=== 会话收尾闸门（SC-E1~E5）===")
    check_docx(g, "E1", sample_only=False)

    baseline = {}
    if BASELINE.exists():
        try:
            baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        except Exception:
            baseline = {}
    metrics = run_metrics()
    if baseline:
        d0 = (metrics.get("p0") or 0) - (baseline.get("p0") or 0)
        d1 = (metrics.get("p1") or 0) - (baseline.get("p1") or 0)
        dch = (metrics.get("duizhao") or 0) - (baseline.get("duizhao") or 0)
        if dch > 0:
            g.add("E2", "基线对比", "INFO",
                  "新增对照 %d 章 → P0%+d / P1%+d 属正常增量（P0 %s→%s，P1 %s→%s）" % (
                      dch, d0, d1, baseline.get("p0"), metrics.get("p0"), baseline.get("p1"), metrics.get("p1")))
        elif d0 > 0:
            g.add("E2", "基线对比", "FAIL", "无新增章但 P0 +%d（%s→%s）→ 须排查后方可提交" % (
                d0, baseline.get("p0"), metrics.get("p0")))
        else:
            g.add("E2", "基线对比", "PASS", "P0 %s→%s · P1 %s→%s · 完成度 %s%%→%s%%" % (
                baseline.get("p0"), metrics.get("p0"), baseline.get("p1"), metrics.get("p1"),
                baseline.get("pct"), metrics.get("pct")))
    else:
        g.add("E2", "基线对比", "WARN", "无开工基线（未跑 --start --apply），仅记录当前值：P0 %s · P1 %s" % (
            metrics.get("p0"), metrics.get("p1")))

    hard, warn, info = junk_scan()
    if hard:
        g.add("E3", "临时文件清理", "FAIL", "%d 个残留（.bak/.tmp_scrub）：%s" % (len(hard), hard[:5]))
    elif warn:
        g.add("E3", "临时文件清理", "WARN", "%d 个百度云同步残留（可清理）" % len(warn))
    else:
        g.add("E3", "临时文件清理", "PASS", "工作区无临时残留（__pycache__ %d 处属未跟踪缓存）" % len(info))

    four = ["TODO.md", "implementation.md", "_记忆索引.md"]
    logs = sorted((REPO / "项目日志").glob("项目日志_*.md"))
    if logs:
        four.append(logs[-1].name)
    stale = []
    for f in four:
        p = REPO / f
        if p.exists():
            age_h = (datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)).total_seconds() / 3600
            if age_h > 12:
                stale.append("%s(%.0f小时未更新)" % (f, age_h))
    g.add("E4", "四件套同步", "WARN" if stale else "PASS",
          ("超 12 小时未更新：%s（按规程 SC-E4 补记）" % stale) if stale else "TODO/implementation/日志/记忆索引均为当日内更新")

    r = git("status", "--porcelain")
    lines = [x for x in (r.stdout or "").splitlines() if x.strip()]
    check_git_sync(g)
    g.add("E5b", "未提交变更", "INFO" if lines else "PASS",
          "%d 项待提交（样例：%s）→ 明确路径 add，禁 -A" % (len(lines), "；".join(lines[:3])) if lines else "工作区干净")

    g.print()
    if apply:
        rep = DOCS / ("会话检查_%s.md" % ts())
        rep.write_text(g.to_md("end"), encoding="utf-8")
        print("[OK] 报告 → %s" % rep.name)
    return 1 if g.hard_fail else 0


def main():
    ap = argparse.ArgumentParser(description="会话起止闸门（工程约束 §⑤）")
    ap.add_argument("--start", action="store_true")
    ap.add_argument("--end", action="store_true")
    ap.add_argument("--apply", action="store_true", help="落盘报告（start 另写基线快照）；缺省 dry-run")
    a = ap.parse_args()
    if a.start == a.end:
        raise SystemExit("必须且只能选 --start 或 --end")
    rc = do_start(a.apply) if a.start else do_end(a.apply)
    sys.exit(rc)


if __name__ == "__main__":
    main()
