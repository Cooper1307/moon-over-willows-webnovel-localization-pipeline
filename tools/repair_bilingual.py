#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
repair_bilingual.py — 对照版真源重建工具（EN-only 损坏章专用）

背景（2026-10-03 自 CodeBuddy 交接）：
  第 44/47 章对照版发生数据事故：中文段落整段丢失，文件名仍是 初译_对照 但内容为
  纯英文（解析器判定 EN-only，sync_bilingual G0 拦截）。需从 第X章原文.md（中文）
  + 损坏对照版（英文段）按序重建对照版。

工作流原则（用户已确立）
    对照版 = 唯一手写产物（唯一真源）
    纯英版 = 脚本派生，禁止手工编辑
  重建 = 恢复真源本身，英文段**逐字**沿用损坏文件中的现存内容，不做任何改写；
  中文段逐字取自 原文（红线：中文原文零改动、对照版中文与原文逐字一致）。

前置条件（不满足即拒绝，无 --force 逃生门）
    1. 对照版判定为 EN-only（本工具只修真源损坏，不碰健康章）
    2. 原文文件存在，且 MD5 与 原文MD5基线.json 一致（原文被改过 = 先查事故再重建）
    3. len(原文段去标题) == len(对照英文段) —— 不等即拒绝并记录疑似拆分点

安全设计
    默认 dry-run；--apply 才写文件。
    写回前：损坏对照版备份到 归档/scratch/第X章初译_对照.backup_<时间戳>.md
    写回后：重读 + parse_pairs 复验，英文段逐段全等、中文段逐段全等；
            任一不等（diff_mismatch>0）→ 立即从备份回滚。
    第 44 章实测 83≠82（原文 82 / 对照英文 83），拒绝重建，仅在报告中记录疑似拆分点
    （与纯英版段落做 SequenceMatcher 对齐 + 相邻块首词相同启发式，供人工确认）。

用法（参数纯 ASCII，规避 PowerShell 中文路径 GBK 乱码）
    python tools/repair_bilingual.py                     # 全量扫描，dry-run
    python tools/repair_bilingual.py --chapter 44,47     # 只看指定章
    python tools/repair_bilingual.py --chapter 47 --apply  # 真重建
    python tools/repair_bilingual.py --report            # 导出 项目文档/对照版重建报告_<时间戳>.md
    python tools/repair_bilingual.py --fail-on-blocked   # 有拒绝/阻断则退出码 1

规范：仅标准库；默认 dry-run；路径由 __file__ 推导；stdout 重配 UTF-8。
"""
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chapter_lib as L  # noqa: E402

ST_REBUILT = "rebuilt"                      # 已重建并复验通过（dry-run = 将重建）
ST_REJECTED_COUNT = "rejected_count_mismatch"  # 段数不等，拒绝（记录疑似拆分点）
ST_SKIPPED_HEALTHY = "skipped_not_en_only"  # 对照版非 EN-only，无需本工具
ST_BLOCKED_NO_BI = "blocked_no_bilingual"   # 无对照版文件
ST_BLOCKED_NO_ORIG = "blocked_no_original"  # 无原文文件
ST_BLOCKED_MD5 = "blocked_md5_mismatch"     # 原文 MD5 与基线不一致 / 无基线
ST_FAILED_ROLLBACK = "failed_rolled_back"   # 写回后复验失败，已回滚

BACKUP_DIR = L.BASE / "归档" / "scratch"
MD5_BASELINE = L.DOCS / "原文MD5基线.json"


def _sync():
    return L._load_sync_module()


def _orig_path(ch_dir):
    """原文文件路径（不含术语表）。找不到返回 None。"""
    for f in sorted(ch_dir.iterdir()):
        if f.is_file() and f.name.endswith(".md") \
                and "原文" in f.name and "术语" not in f.name:
            return f
    return None


def extract_en_state(bi_path, sync):
    """
    解析 EN-only 损坏对照版。
    返回 (标题行列表, en_blocks=[{text, line}], notes=[(行号, 注全文)])
    英文段**逐字**保留（含块内软换行，以 \n 连接），不做 strip_red 之外的任何改写
    —— 实际上连 strip_red 也不做：红标是后续审校资产，重建只搬运原文内容。
    """
    lines = bi_path.read_text(encoding="utf-8-sig").splitlines()
    notes = []
    blocks = sync._split_blocks(lines, notes)
    en_blocks = []
    for blk in blocks:
        en_lines = [t for _i, t in blk if not sync.has_cjk(t) and sync.ASCII_RE.search(t)]
        if en_lines:
            en_blocks.append({"text": "\n".join(en_lines), "line": blk[0][0]})
    titles = []
    for raw in lines:
        s = raw.strip()
        if s.startswith("#"):
            titles.append(s)
        elif titles and s:
            break
    return titles, en_blocks, notes


def _first_word(text):
    m = L.EN_RE.search(text)
    if not m:
        return ""
    seg = text[m.start():]
    out = ""
    for ch in seg:
        if ch.isalnum() or ch in "'’-":
            out += ch
        else:
            break
    return out.lower()


def detect_split_candidates(en_blocks, pure_paras, zh_n):
    """
    段数不等时定位疑似拆分点（结果仅供人工确认，不自动修复）。
      主策略：纯英版段数 == 原文段数 时，对照英文块与纯英段落做 SequenceMatcher 对齐，
              落在非 equal 区间的对照块 = 疑似区域。
      兜底：相邻两英文块首词相同的对（实测第 44 章 L159/L161 均以 They 开头）。
    返回 (策略名, [候选描述])；无法定位时 ([], "")。
    """
    texts = [b["text"] for b in en_blocks]
    if pure_paras and len(pure_paras) == zh_n:
        sm = SequenceMatcher(None, texts, pure_paras, autojunk=False)
        sus = set()
        for tag, i1, i2, _j1, _j2 in sm.get_opcodes():
            if tag != "equal":
                sus.update(range(i1, i2))
        if sus and len(sus) <= 8:
            desc = ["对照块#%d(L%d) 落在与纯英版对齐的非匹配区域" % (i + 1, en_blocks[i]["line"])
                    for i in sorted(sus)]
            return "SequenceMatcher 对齐纯英版", desc
    desc = []
    for i in range(len(en_blocks) - 1):
        w1 = _first_word(en_blocks[i]["text"])
        w2 = _first_word(en_blocks[i + 1]["text"])
        if w1 and w1 == w2:
            desc.append("对照块#%d(L%d) 与 #%d(L%d) 首词相同（%s…），疑为同段被拆"
                        % (i + 1, en_blocks[i]["line"], i + 2, en_blocks[i + 1]["line"], w1))
    if desc:
        return "相邻块首词启发式", desc
    return "", []


def repair(ch_dir, apply_mode, ts, sync):
    """重建单章。返回结果 dict（含 reject/blocked 明细，供报告落盘）。"""
    name = ch_dir.name
    try:
        num = int(name[1:-1])
    except (ValueError, IndexError):
        num = 0
    r = {"chapter": num, "name": name, "status": "", "reason": "",
         "zh_n": 0, "en_n": 0, "notes_n": 0, "backup": "", "verify": "",
         "md5": "—", "candidates": [], "method": "", "pure_match": ""}

    hits = [f for f in ch_dir.iterdir() if f.is_file() and L.BILINGUAL_RE.search(f.name)]
    if not hits:
        r.update(status=ST_BLOCKED_NO_BI, reason="无对照版文件")
        return r
    bi_path = ch_dir / hits[0]

    lines = bi_path.read_text(encoding="utf-8-sig").splitlines()
    kind = sync.parse_pairs(lines)[0]
    if kind != "EN-only":
        r.update(status=ST_SKIPPED_HEALTHY, reason="对照版格式 %s，非 EN-only，无需重建" % kind)
        return r

    op = _orig_path(ch_dir)
    if op is None:
        r.update(status=ST_BLOCKED_NO_ORIG, reason="无原文文件，重建无中文来源")
        return r

    baseline = None
    if MD5_BASELINE.exists():
        baseline = json.loads(MD5_BASELINE.read_text(encoding="utf-8")).get("files", {})
    cur = hashlib.md5(op.read_bytes()).hexdigest()
    rel = "%s/%s" % (name, op.name)
    if baseline is None or rel not in baseline:
        r.update(status=ST_BLOCKED_MD5, md5="无基线",
                 reason="原文无 MD5 基线，拒绝在不可证伪原状时重建")
        return r
    if baseline[rel] != cur:
        r.update(status=ST_BLOCKED_MD5, md5="变更",
                 reason="★原文 MD5 与基线不一致（中文被改动？），先查事故再重建")
        return r
    r["md5"] = "一致"

    titles, en_blocks, notes = extract_en_state(bi_path, sync)
    orig_n, zh_paras, _found = sync.read_original(ch_dir)
    r.update(zh_n=orig_n, en_n=len(en_blocks), notes_n=len(notes))
    if orig_n != len(en_blocks):
        _t, _pn, pure0 = sync.read_pure_en(ch_dir)
        method, cands = detect_split_candidates(en_blocks, pure0, orig_n)
        r.update(status=ST_REJECTED_COUNT, method=method, candidates=cands,
                 reason="段数不等：原文 %d vs 对照英文 %d，拒绝按序配对（差 %+d）"
                        % (orig_n, len(en_blocks), len(en_blocks) - orig_n))
        return r

    if notes:
        r["reason"] = "注：%d 条译者注将按原行号位置插回" % len(notes)

    _t, _n, pure = sync.read_pure_en(ch_dir)
    m = sum(1 for a, b in zip(en_blocks, pure) if a["text"] == b)
    r["pure_match"] = ("%d/%d" % (m, len(en_blocks))) if pure else "-"

    en_title = None
    # 英文标题：损坏文件里没有 → 从纯英版标题行补全（该标题本就派生自本章真源）
    if not [t for t in titles if not sync.has_cjk(t.lstrip("#"))]:
        pt = sync.read_pure_en(ch_dir)[0]
        if pt and pt.startswith("#"):
            en_title = pt.strip()

    out = list(titles)
    if en_title:
        out.append(en_title)
    out.append("")
    note_by_pos = {}
    for ln, text in notes:
        pos = sum(1 for b in en_blocks if b["line"] < ln)
        note_by_pos[pos] = text
    for i, (zh, enb) in enumerate(zip(zh_paras, en_blocks)):
        if i:
            out += ["---", ""]
        out.append(zh)
        out.append("")
        if i in note_by_pos:
            out += [note_by_pos[i], ""]
        out.append(enb["text"])
        out.append("")
    text = "\n".join(out).rstrip() + "\n"

    if not apply_mode:
        r.update(status=ST_REBUILT, reason="将重建（dry-run 未写入）")
        return r

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup = BACKUP_DIR / ("%s初译_对照.backup_%s.md" % (name, ts))
    shutil.copy2(bi_path, backup)
    r["backup"] = str(backup)

    bi_path.write_text(text, encoding="utf-8")

    # 复验：重读 → parse_pairs → 中英逐段全等，任一不等即回滚
    new_lines = bi_path.read_text(encoding="utf-8-sig").splitlines()
    _k2, pairs2, anom2, _n2 = sync.parse_pairs(new_lines)
    mismatch = 0
    if len(pairs2) != len(en_blocks):
        mismatch = abs(len(pairs2) - len(en_blocks))
    else:
        for i, (zh2, en2, _ln) in enumerate(pairs2):
            if zh2 != zh_paras[i] or en2 != en_blocks[i]["text"]:
                mismatch += 1
    if anom2 or mismatch:
        shutil.copy2(backup, bi_path)
        r.update(status=ST_FAILED_ROLLBACK,
                 reason="复验失败（diff_mismatch=%d, anomalies=%d），已从备份回滚"
                        % (mismatch, len(anom2)))
        return r

    r.update(status=ST_REBUILT, verify="PASS",
             reason="重建完成：标题 %d 行 + %d 对中英 + 注 %d 条，复验逐段全等"
                    % (len(titles) + (1 if en_title else 0), len(en_blocks), len(notes)))
    return r


def main():
    ap = argparse.ArgumentParser(description="对照版真源重建（EN-only 损坏章专用）")
    ap.add_argument("--chapter", default="", help="章号区间/列表，如 44,47 / 30-90（纯 ASCII）")
    ap.add_argument("--apply", action="store_true", help="实际重建（默认 dry-run）")
    ap.add_argument("--report", action="store_true", help="导出 项目文档/对照版重建报告_<时间戳>.md")
    ap.add_argument("--fail-on-blocked", action="store_true",
                    help="存在 rejected/blocked/rolled_back 则退出码 1")
    args = ap.parse_args()

    lo, hi = L.parse_range(args.chapter)
    dirs = L.chapter_dirs(lo, hi)
    if not dirs:
        print("[ERROR] 未找到章节目录（范围 %s-%s）" % (lo, hi))
        return 2

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sync = _sync()
    rows = [repair(d, args.apply, ts, sync) for _n, d in dirs]

    done = [r for r in rows if r["status"] == ST_REBUILT]
    rej = [r for r in rows if r["status"] == ST_REJECTED_COUNT]
    skip = [r for r in rows if r["status"] == ST_SKIPPED_HEALTHY]
    blk = [r for r in rows if r["status"] in
           (ST_BLOCKED_NO_BI, ST_BLOCKED_NO_ORIG, ST_BLOCKED_MD5)]
    fail = [r for r in rows if r["status"] == ST_FAILED_ROLLBACK]

    span = "%d-%d" % (lo, hi) if lo and hi else "全量"
    mode = "APPLY 写入" if args.apply else "DRY-RUN 只读"
    print("=" * 92)
    print("对照版重建（%s）  范围：%s  时间：%s" % (mode, span, ts))
    print("=" * 92)
    for r in rows:
        if r["status"] == ST_SKIPPED_HEALTHY:
            continue
        mark = "OK " if r["status"] == ST_REBUILT else "XX "
        print("%s第%d章 %s  原文%d/英文%d/注%d  MD5:%s  %s"
              % (mark, r["chapter"], r["status"], r["zh_n"], r["en_n"],
                 r["notes_n"], r["md5"], r["reason"]))
        if r["pure_match"] and r["pure_match"] != "-":
            print("     纯英版逐段比对（仅供参考，非闸门）：%s 相同" % r["pure_match"])
        if r["backup"]:
            print("     备份：%s" % r["backup"])
        if r["verify"]:
            print("     复验：%s" % r["verify"])
        for c in r["candidates"]:
            print("     疑似拆分点[%s]：%s" % (r["method"], c))
    print("-" * 92)
    print("  扫描 %d 章 · 重建 %d · 拒绝 %d · 跳过(健康) %d · 阻断 %d · 回滚 %d"
          % (len(rows), len(done), len(rej), len(skip), len(blk), len(fail)))
    if not args.apply:
        print("  [DRY-RUN] 加 --apply 才写；写前自动备份，写后逐段复验，失败即回滚")
    if rej:
        print("  [!] 拒绝章的拆分点需人工确认后手工修对照版，本工具不代修")

    need_report = args.report or (args.apply and (rej or fail or done))
    if need_report:
        L.DOCS.mkdir(parents=True, exist_ok=True)
        out = L.DOCS / ("对照版重建报告_%s.md" % ts)
        lines = ["# 对照版重建报告", "",
                 "- 时间：%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "- 模式：%s" % mode,
                 "- 原则：对照版=唯一真源；重建=损坏恢复，英文逐字搬运、中文逐字取原文",
                 "- 前置：原文 MD5 与基线一致 + 段数相等，任一不满足即拒绝（无 --force）", "",
                 "## 明细", "",
                 "| 章节 | 状态 | 原文段 | 对照英文 | 注 | MD5 | 说明 |",
                 "|---|---|---|---|---|---|---|"]
        for r in rows:
            reason = r["reason"].replace("|", "/")
            for c in r["candidates"]:
                reason += "；疑似拆分点[%s]：%s" % (r["method"], c.replace("|", "/"))
            if r["backup"]:
                reason += "；备份 %s" % r["backup"]
            if r["verify"]:
                reason += "；复验 %s" % r["verify"]
            lines.append("| 第%d章 | %s | %d | %d | %d | %s | %s |"
                         % (r["chapter"], r["status"], r["zh_n"], r["en_n"],
                            r["notes_n"], r["md5"], reason))
        lines.append("")
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("  [OK] 报告已写入：%s" % out)

    if args.fail_on_blocked and (rej or blk or fail):
        print("  [FAIL] 存在拒绝/阻断/回滚（--fail-on-blocked 触发，退出码 1）")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
