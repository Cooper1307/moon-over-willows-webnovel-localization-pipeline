#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双语同步器（Bilingual Sync）

职责（对应门禁 G1 / G2 / G12）：
  G1  中文原文零改动        —— 原文文件 MD5 与基线比对
  G2  段落 1:1              —— 对照版中文块数 = 原文段数 = 纯英段数
  G12 交付完整性            —— 每章三件套（原文 / 对照 / 纯英）齐全

核心约定：**对照版是唯一真源，纯英版（第X章译文.md）是派生物。**
本脚本从对照版提取英文生成纯英版，禁止手工编辑纯英版。

对照版格式（实测 84 章，共 3 种体制，本脚本全部支持）：
  A 分隔符式（77 章）：`# 第X章 标题` → 中文段 / 空 / 英文段 / 空 / `---` / 空 …
  B 无分隔式（4 章）  ：中文标题 / `## Chapter N: …` → 中文段 / 英文段 / 空 …
  C 显式标记式（3 章）：`## 段落 N` + `**原文**：…` + `**译文**：…`

用法：
  python tools/sync_bilingual.py                    # dry-run：全量校验，只报告不写文件
  python tools/sync_bilingual.py --chapter 37        # 只处理指定章（可逗号分隔：37,41,42）
  python tools/sync_bilingual.py --apply             # 生成/更新 第X章译文.md
  python tools/sync_bilingual.py --init-md5          # 建立/重建 原文 MD5 基线
  python tools/sync_bilingual.py --apply --report 项目文档/双语同步报告.md

安全设计：
  - 默认 dry-run，必须显式 --apply / --init-md5 / --report 才写文件；
  - **已存在的 第X章译文.md 保留其原有标题行**（英文标题可能不在对照版中，禁止覆盖丢失）；
  - 写入守卫：对照存在**解析异常**（漏译/顺序倒置等）或 对照块数与原文段数差 **>5** 时跳过；正常拆分导致的 ±1-2 段差允许生成（如第31章）。

规范：仅标准库；默认只读；stdout 重配 UTF-8；路径由 __file__ 推导，避免中文路径命令行乱码。
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
CHAPTERS = BASE / "章节原文"
DOCS = BASE / "项目文档"
MD5_BASELINE = DOCS / "原文MD5基线.json"

CHAPTER_DIR_RE = re.compile(r"^第(\d+)章$")
BILINGUAL_RE = re.compile(r"初译_对照")
ORIGINAL_RE = re.compile(r"原文")
PURE_EN_RE = re.compile(r"^第\d+章译文\.md$")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")

MARK_ZH = "**原文**"
MARK_EN = "**译文**"
# 冒号在全角/半角间不统一（第8章实测出现 `**译文**:`），故用正则容错
MARK_ZH_RE = re.compile(r"^\*\*原文\*\*\s*[：:]\s*")
MARK_EN_RE = re.compile(r"^\*\*译文\*\*\s*[：:]\s*")


# ---------------------------------------------------------------- 解析层

TITLE_RE = re.compile(r"^\ufeff?第\d+章[\s　:：]")


def is_heading(line):
    return line.startswith("#")


def is_sep(line):
    return line.strip() in ("---", "***", "___")


def is_title_line(line):
    """章节标题行（无 `#` 前缀的旧体制），如 `第6章 穿越成为赵仪王`。"""
    s = line.strip()
    if not TITLE_RE.match(s):
        return False
    return len(s) < 60 and not s.endswith(("。", "！", "？", "…", '"', "”", "）", ")"))


def is_continuation(prev, cur):
    """
    判断 cur 是否为 prev 的续行（同一段落内的软换行）。
    实测场景：诗词译文中以 `>` 引用的多行诗（第37章 L169-176），
    它们属于上一个英文块，不是新段落。
    """
    c = cur.lstrip()
    if c.startswith(">"):
        return True
    if prev.rstrip().endswith(("*", "。", "，")) and prev.lstrip().startswith(">"):
        return True
    if "\n>" in prev:
        return True
    return False


def has_cjk(text):
    return bool(CJK_RE.search(text))


def classify(lines):
    """判定对照版体制：A-sep / B-plain / C-marked"""
    marked = sum(1 for x in lines if MARK_ZH_RE.match(x) or MARK_EN_RE.match(x))
    if marked > 10:
        return "C-marked"
    sep = sum(1 for x in lines if is_sep(x))
    if sep > 10:
        return "A-sep"
    return "B-plain"


def strip_mark(line, mark_re):
    m = mark_re.match(line)
    return line[m.end():].strip() if m else None


def parse_pairs(lines):
    """
    从对照版解析出 [(中文, 英文), ...]，同时返回格式类型与异常列表。
    异常：连续两个中文块 / 连续两个英文块 / 单块无法配对。
    """
    kind = classify(lines)
    pairs = []
    anomalies = []

    if kind == "C-marked":
        pending_zh = None
        pending_zh_line = 0
        for i, raw in enumerate(lines, 1):
            line = raw.strip()
            if not line or is_sep(line) or is_heading(line):
                continue
            zh = strip_mark(line, MARK_ZH_RE)
            en = strip_mark(line, MARK_EN_RE)
            if zh is not None:
                if pending_zh is not None:
                    anomalies.append((pending_zh_line, "连续的**原文**块，缺少对应**译文**"))
                pending_zh, pending_zh_line = zh, i
            elif en is not None:
                if pending_zh is None:
                    anomalies.append((i, "**译文**块前缺少**原文**块"))
                else:
                    pairs.append((pending_zh, en, i))
                    pending_zh = None
            else:
                anomalies.append((i, "C型体制下的非标记内容行"))
        if pending_zh is not None:
            anomalies.append((pending_zh_line, "**原文**块缺少对应**译文**"))
        return kind, pairs, anomalies

    # A / B：按「中文块 → 英文块」交替配对
    seq = []
    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or is_sep(line) or is_heading(line) or is_title_line(line):
            continue
        seq.append((i, line))

    pending = None
    for i, line in seq:
        zh = has_cjk(line)
        if pending is None:
            # 已完成一对后紧随的续行（如多行诗），应追加到上一对的英文，而非开新块
            if pairs and not zh and is_continuation(pairs[-1][1], line):
                z, e, ln = pairs[-1]
                pairs[-1] = (z, e + "\n" + line, ln)
                continue
            pending = (i, line, zh)
            continue
        p_i, p_line, p_zh = pending
        if p_zh != zh:  # 中→英 构成一对
            if p_zh:
                pairs.append((p_line, line, i))
                pending = None
                continue
            # 英文在前、中文在后：若上一行是英文且当前是中文，
            # 多数情况是上一对缺少中文（原文缺失）→ 登记异常并丢弃该英文块
            anomalies.append((i, "顺序倒置：英文块在前、中文块在后（疑似原文缺失）"))
            pending = (i, line, zh)
        elif is_continuation(p_line, line):
            pending = (p_i, p_line + "\n" + line, zh)  # 续行合并（诗词/引用）
        else:
            reason = "连续两个中文块（翻译缺失？）" if p_zh and zh else "连续两个英文块（疑似原文缺失）"
            anomalies.append((p_i, reason))
            pending = (i, line, zh)
    if pending is not None:
        anomalies.append((pending[0], "末尾块未配对（" + ("中文" if pending[2] else "英文") + "）"))

    return kind, pairs, anomalies


def extract_en_title(lines):
    """尽力从对照版标题行提取英文标题；取不到返回 None。"""
    for raw in lines[:6]:
        line = raw.strip()
        if not line.startswith("#"):
            continue
        body = line.lstrip("#").strip()
        if " / " in body:
            parts = [p.strip() for p in body.split(" / ")]
            en = [p for p in parts if not has_cjk(p)]
            if en:
                return en[0]
        elif not has_cjk(body) and body.lower().startswith("chapter"):
            return body
    return None


def read_original(ch_dir):
    """读取原文：返回 (段数, 段落列表, 是否找到)。标题行（第X章 …）不计入段数。"""
    hits = [f for f in ch_dir.iterdir() if f.is_file() and f.name.endswith(".md")
            and ORIGINAL_RE.search(f.name) and "术语" not in f.name]
    if not hits:
        return 0, [], False
    text = hits[0].read_text(encoding="utf-8-sig")
    paras = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if not paras and re.match(r"^\ufeff?第\d+章", s):
            continue  # 标题行
        paras.append(s)
    return len(paras), paras, True


def read_pure_en(ch_dir):
    """读取已有纯英版：返回 (标题行 or None, 英文段数, 段落列表)。"""
    hits = [f for f in ch_dir.iterdir() if f.is_file() and PURE_EN_RE.match(f.name)]
    if not hits:
        return None, 0, []
    text = hits[0].read_text(encoding="utf-8-sig")
    title = None
    paras = []
    for line in text.splitlines():
        s = line.strip()
        if not s or is_sep(s):      # 分隔行（---）不计入段落
            continue
        if s.startswith("#"):
            if title is None:
                title = s
            continue
        paras.append(s)
    return title, len(paras), paras


def md5_of(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- 校验层

def check_chapter(ch_dir, baseline, apply_mode, force_mode, stats):
    name = ch_dir.name
    num = int(CHAPTER_DIR_RE.match(name).group(1))
    row = {"章": name, "格式": "-", "原文段": 0, "对照中": 0, "对照英": 0,
           "纯英段": 0, "MD5": "—", "问题": []}

    files = [f.name for f in ch_dir.iterdir() if f.is_file()]
    bi = [f for f in files if BILINGUAL_RE.search(f)]
    if not bi:
        row["问题"].append("无对照版")
        stats["skip"] += 1
        return row
    bi_path = ch_dir / bi[0]

    lines = bi_path.read_text(encoding="utf-8-sig").splitlines()
    kind, pairs, anomalies = parse_pairs(lines)
    row["格式"] = kind
    row["对照中"] = len(pairs)
    row["对照英"] = len(pairs)

    for ln, reason in anomalies[:5]:
        row["问题"].append(f"L{ln} {reason}")
    if len(anomalies) > 5:
        row["问题"].append(f"（另有 {len(anomalies) - 5} 处配对异常）")

    # 原文：段数 + MD5（G1 / G2）
    orig_n, _paras, has_orig = read_original(ch_dir)
    row["原文段"] = orig_n
    if has_orig:
        op = [f for f in files if f.endswith(".md") and ORIGINAL_RE.search(f) and "术语" not in f][0]
        rel = f"{name}/{op}"
        cur = md5_of(ch_dir / op)
        if baseline is None:
            row["MD5"] = "未建基线"
        elif rel not in baseline:
            row["MD5"] = "基线缺项"
            row["问题"].append("原文未登记 MD5 基线")
        elif baseline[rel] != cur:
            row["MD5"] = "变更"
            row["问题"].append("★原文 MD5 与基线不一致（中文被改动？）")
        else:
            row["MD5"] = "一致"
        if orig_n and orig_n != len(pairs):
            row["问题"].append(f"段数不符：原文 {orig_n} vs 对照 {len(pairs)}")
    else:
        row["MD5"] = "无原文"
        row["问题"].append("无原文文件（无法校验 G1/G2）")

    # 纯英版
    en_title, en_n, en_paras = read_pure_en(ch_dir)
    row["纯英段"] = en_n
    pure_path = None
    for f in files:
        if PURE_EN_RE.match(f):
            pure_path = ch_dir / f
            break

    need_write = False
    if pure_path is None:
        row["问题"].append("无纯英版（待生成）")
        need_write = True
        stats["missing"] += 1
    elif en_n != len(pairs):
        row["问题"].append(f"纯英段数 {en_n} ≠ 对照英文块数 {len(pairs)}（不同步）")
        if force_mode:
            need_write = True
        else:
            row["问题"].append("⚠ 覆盖需 --force")
        stats["desync"] += 1
    else:
        # 段数一致时仍抽查内容是否逐段相同
        diff = sum(1 for a, b in zip(en_paras, [p[1] for p in pairs]) if a != b)
        if diff:
            row["问题"].append(f"内容差异 {diff} 段（纯英版落后于对照版）")
            if force_mode:
                need_write = True
            else:
                row["问题"].append("⚠ 覆盖需 --force")
            stats["desync"] += 1

    # 写入（仅 --apply；守卫：解析异常 或 对照块数与原文段数差 >5 才阻断）
    # 说明：个别章会把原文一段拆成两个中英小块（如第31章 L42+L48），此时配对无错，
    # 只是段数与原文差 1-2，不影响生成 → 允许写入。
    if apply_mode and need_write:
        if anomalies:
            row["问题"].append("⚠ 对照存在解析异常，跳过写入（需人工先修对照）")
            stats["blocked"] += 1
        elif has_orig and orig_n and abs(orig_n - len(pairs)) > 5:
            row["问题"].append(f"⚠ 对照块数 {len(pairs)} 与原文段数 {orig_n} 差超过 5，跳过写入")
            stats["blocked"] += 1
        else:
            if en_title is None:
                en_title = extract_en_title(lines) or f"Chapter {num}"
            if not en_title.startswith("#"):
                en_title = "# " + en_title
            out = [en_title, ""]
            for _zh, en, _ln in pairs:
                out.append(en)
                out.append("")
            target = pure_path or (ch_dir / f"{name}译文.md")
            target.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
            row["问题"].append(f"✔ 已写入 {target.name}（保留原标题行）")
            stats["written"] += 1

    return row


def main():
    ap = argparse.ArgumentParser(description="双语同步器：对照版 ⇄ 纯英版生成与校验")
    ap.add_argument("--apply", action="store_true", help="写入 第X章译文.md（默认 dry-run）")
    ap.add_argument("--init-md5", action="store_true", help="建立/重建 原文 MD5 基线")
    ap.add_argument("--force", action="store_true",
                    help="允许覆盖已存在但不同步的 第X章译文.md（默认只补缺失，不覆盖）")
    ap.add_argument("--chapter", default="", help="只处理指定章号，逗号分隔，如 37,41,42")
    ap.add_argument("--report", nargs="?", const="AUTO", default="",
                    help="导出完整表格到 项目文档/双语同步校验报告_<时间戳>.md"
                         "（不给值则自动命名；⚠ 勿传中文路径，PowerShell 会 GBK 乱码）")
    args = ap.parse_args()

    if not CHAPTERS.exists():
        print(f"[ERROR] 未找到章节目录：{CHAPTERS}")
        return 1

    # 1) 建基线
    if args.init_md5:
        base = {}
        dirs = [d for d in CHAPTERS.iterdir() if d.is_dir() and CHAPTER_DIR_RE.match(d.name)]
        for d in sorted(dirs, key=lambda x: int(CHAPTER_DIR_RE.match(x.name).group(1))):
            for f in d.iterdir():
                if f.is_file() and f.name.endswith(".md") and ORIGINAL_RE.search(f.name) \
                        and "术语" not in f.name:
                    base[f"{d.name}/{f.name}"] = md5_of(f)
        DOCS.mkdir(parents=True, exist_ok=True)
        MD5_BASELINE.write_text(
            json.dumps({"生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "说明": "中文原文 MD5 基线（G1 门禁）。原文全程零改动，任何不一致即为事故。",
                        "files": base}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        print(f"[OK] 原文 MD5 基线已写入：{MD5_BASELINE}（{len(base)} 个文件）")
        if not args.apply and not args.report:
            return 0

    baseline = None
    if MD5_BASELINE.exists():
        baseline = json.loads(MD5_BASELINE.read_text(encoding="utf-8")).get("files", {})

    # 2) 全量校验
    dirs = [d for d in CHAPTERS.iterdir() if d.is_dir() and CHAPTER_DIR_RE.match(d.name)]
    dirs.sort(key=lambda x: int(CHAPTER_DIR_RE.match(x.name).group(1)))
    if args.chapter:
        want = {int(x) for x in re.split(r"[,\s]+", args.chapter.strip()) if x.strip().isdigit()}
        dirs = [d for d in dirs if int(CHAPTER_DIR_RE.match(d.name).group(1)) in want]

    stats = {"total": len(dirs), "written": 0, "missing": 0, "desync": 0,
             "blocked": 0, "skip": 0, "clean": 0}
    rows = []
    for d in dirs:
        row = check_chapter(d, baseline, args.apply, args.force, stats)
        if not row["问题"]:
            stats["clean"] += 1
        rows.append(row)

    # 3) 输出
    print("=" * 96)
    print(f"双语同步校验（{'--apply 写入模式' if args.apply else 'DRY-RUN 只读模式'}）"
          f"  生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 96)
    print(f"  基线状态：{'已载入 ' + str(len(baseline)) + ' 项' if baseline else '⚠ 未建立（先跑 --init-md5）'}")
    print("-" * 96)
    print(f"{'章节':<8}{'格式':<10}{'原文段':>6}{'对照块':>7}{'纯英段':>7}{'MD5':>8}  问题")
    print("-" * 96)
    for r in rows:
        prob = "；".join(r["问题"]) if r["问题"] else "✔ 同步"
        print(f"{r['章']:<8}{r['格式']:<10}{r['原文段']:>6}{r['对照中']:>7}{r['纯英段']:>7}{r['MD5']:>8}  {prob[:80]}")
    print("-" * 96)
    print(f"  扫描 {stats['total']} 章 · 已同步 {stats['clean']} · 缺纯英版 {stats['missing']} · "
          f"不同步 {stats['desync']} · 段数不符跳过 {stats['blocked']} · 无对照版 {stats['skip']}")
    if args.apply:
        print(f"  实际写入：{stats['written']} 章")
    else:
        print("\n[DRY-RUN] 加 --apply 才写 第X章译文.md；加 --init-md5 建原文基线；加 --report 文件 导出表格。")

    if args.report:
        if args.report == "AUTO":
            out = DOCS / f"双语同步校验报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        else:
            out = BASE / args.report
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# 双语同步校验报告", "",
                 f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                 f"> 模式：{'--apply（已写入）' if args.apply else 'dry-run（只读）'}",
                 "", "## 统计", "",
                 f"- 扫描章节：{stats['total']}",
                 f"- 已同步：{stats['clean']}",
                 f"- 缺纯英版：{stats['missing']}",
                 f"- 不同步：{stats['desync']}",
                 f"- 段数不符跳过：{stats['blocked']}",
                 f"- 无对照版：{stats['skip']}",
                 f"- 实际写入：{stats['written'] if args.apply else 0}",
                 "", "## 明细", "",
                 "| 章节 | 格式 | 原文段 | 对照块 | 纯英段 | MD5 | 问题 |",
                 "|---|---|---|---|---|---|---|"]
        for r in rows:
            prob = "；".join(r["问题"]).replace("|", "\\|") if r["问题"] else "✔ 同步"
            lines.append(f"| {r['章']} | {r['格式']} | {r['原文段']} | {r['对照中']} | "
                         f"{r['纯英段']} | {r['MD5']} | {prob} |")
        lines.append("")
        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"[OK] 报告已写入：{out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
