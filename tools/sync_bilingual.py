#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双语一致性校验器（对照版 ⇄ 纯英版 / 原文）—— **只读**

职责（对应门禁 G1 / G2 / G12）：
  G1  中文原文零改动        —— 原文文件 MD5 与基线比对
  G2  段落 1:1              —— 对照版中文块数 = 原文段数 = 纯英段数
  G12 交付完整性            —— 每章三件套（原文 / 对照 / 纯英）齐全

⚠ 2026-10-03 起本工具**只读**，不再生成或覆盖任何译文文件（--apply/--force 已移除）。
  派生职责已移交 `tools/extract_pure_en.py`（单一职责原则）：
  翻译只产出对照版（唯一手写产物），纯英版一律脚本派生，禁止手工编辑纯英版。
  本工具仅在缺纯英版时给出指向新工具的提示。

核心约定：**对照版是唯一真源，纯英版（第X章译文.md）是派生物。**

对照版格式（实测 84 章，共 4 种体制，本脚本全部支持）：
  A 分隔符式（77 章）：`# 第X章 标题` → 中文段 / 空 / 英文段 / 空 / `---` / 空 …
  B 无分隔式（4 章）  ：中文标题 / `## Chapter N: …` → 中文段 / 英文段 / 空 …
  C 显式标记式（3 章）：`## 段落 N` + `**原文**：…` + `**译文**：…`
  E 纯英式（2 章）    ：文件名为对照版但内容为纯英文，中文段落已丢失（第 44/47 章，
                       须从 `第X章原文.md` 按序重建；本脚本只识别并阻断，不自动重建）

中文块判定（2026-10-03 修正，重要）：
  旧判据「含任意中文字符」会把**英文段内嵌中文原字**误判为中文块
  （如 `wrote the character "Xun" (寻， meaning "to seek")`，中文占比仅 0.02），
  打断配对 → 报「连续两个中文块」假异常。实测第 32 章 9 处异常**全部为假**，
  真实漏译为 0 处，且该假异常被写入守卫阻断，导致纯英版一直无法生成。
  现改为**占比判定** `cjk_ratio >= 0.5`，并把 `[TN:/[POEM:/[PUNC:/[PUZZLE:`
  译者注行（实测全书 18 行，均独立成块）从配对序列中剔除，单独收集到 notes。
  副作用（正向）：纯英版派生时不再把译者注里的中文原字搬进译文.md。

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
ASCII_RE = re.compile(r"[A-Za-z]")

# ---------------------------------------------------------------- 译者注行
# 形如 `[TN: ...]` / `[POEM: ...]` / `[PUNC: ...]` / `[PUZZLE: ...]`，是译者附注，
# **不是正文段落**，不参与中英配对。实测全书 18 行，全部独立成块（前后被 `---` 包裹），
# 若参与配对会产生「连续两个中文块」假异常（2026-10-03 实测第 32 章 9 处中的 1 处即此）。
NOTE_PREFIX_RE = re.compile(r"^\*?\[(TN|POEM|PUNC|PUZZLE|NOTE|EDITOR)\s*[:：]")

# ---------------------------------------------------------------- 中文块判定
# 旧判据 `含任意中文字符` 会把「英文段内嵌中文原字」误判为中文块
# （实测第 32 章 L416 `wrote the character "Xun" (寻， meaning "to seek")`，
#   中文占比仅 0.02，却被打断配对 → 9 处假异常，真实漏译实为 0）。
# 改为占比判定：中文正文段占比 ≥ 0.5；低于 0.5 且含 ASCII 字母者视为英文段。
CJK_RATIO_MIN = 0.5

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
    ⚠ 2026-10-03 起，A/B 分支已改用块级解析（`_split_blocks`），本函数**不再被调用**，
    保留供 C 型体制改进与外部复用。原用途：多行诗（`>` 引用）续行合并。
    """
    c = cur.lstrip()
    if c.startswith(">"):
        return True
    if prev.rstrip().endswith(("*", "。", "，")) and prev.lstrip().startswith(">"):
        return True
    if "\n>" in prev:
        return True
    return False


def cjk_ratio(text):
    """中文字符占非空白字符的比例。"""
    s = text.strip()
    if not s:
        return 0.0
    return len(CJK_RE.findall(s)) / len(s)


def is_note_line(line):
    """译者注行（`[TN:` 等）：不参与配对，由调用方单独收集。"""
    return bool(NOTE_PREFIX_RE.match(line.strip()))


def has_cjk(text):
    """中文块判定（2026-10-03 由「含任意中文」改为占比 ≥ CJK_RATIO_MIN）。

    保留旧函数名以兼容既有调用方，但语义已变为「是否为中文正文段」。
    """
    return cjk_ratio(text) >= CJK_RATIO_MIN


def is_en_block(text):
    """英文段判定：非中文块，且含 ASCII 字母。"""
    return not has_cjk(text) and bool(ASCII_RE.search(text))


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


def _split_blocks(lines, notes):
    """
    按空行或 `---` 切块。**块 = 一个自然段**（可能多行，如多行诗词）。
    2026-10-03：原按行解析会把多行段落误判为「连续两个块」——
    实测第 61 章 8 处、第 57 章 10 处异常均源于此（第 91-93 行中文诗 3 行、
    第 97-101 行英文诗 5 行，被当成 3 个中文块 + 5 个英文块）。
    返回 [[(行号, 行文本), ...], ...]
    """
    blocks, cur = [], []
    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            if cur:
                blocks.append(cur)
                cur = []
            continue
        if is_sep(line) or is_heading(line) or is_title_line(line):
            if cur:
                blocks.append(cur)
                cur = []
            continue
        if is_note_line(line):
            notes.append((i, line))
            continue
        cur.append((i, line))
    if cur:
        blocks.append(cur)
    return blocks


def parse_by_blocks(lines, anomalies, notes):
    """
    块级 + 块内行级混合解析（A-sep / B-plain 通用）。

    两级结构，缺一不可（均由实测反推得出）：
      1) 先按空行 / `---` 切块 —— 解决「多行诗词被当成多个块」
         （第 61 章实测：中文诗 3 行 + 英文诗 5 行，逐行解析报 8 处假异常）。
      2) 块内再按行分中英 —— 解决「中英同块且其间无空行」
         （第 3 章实测：中文段与英文段紧邻，块级中文占比约 0.44 < 0.5，
           整块会被误判为英文块 → 59 pairs 归零）。

    配对规则：
      块内既有中文又有英文 → 块内自配对（第 3 章形态）
      块内只有中文         → 悬空，等待后续块的英文（第 61 章形态）
      块内只有英文         → 与悬空中文配对；无悬空则报「疑似原文缺失」
    """
    blocks = _split_blocks(lines, notes)
    units = []
    for blk in blocks:
        zh_lines = [l for _i, l in blk if has_cjk(l)]
        en_lines = [l for _i, l in blk if not has_cjk(l) and ASCII_RE.search(l)]
        units.append({
            "zh": "\n".join(zh_lines) if zh_lines else None,
            "en": "\n".join(en_lines) if en_lines else None,
            "line": blk[0][0],
        })

    pairs = []
    pending_zh = None          # (中文文本, 起始行号)
    for u in units:
        if u["zh"] and u["en"]:
            if pending_zh:
                anomalies.append((pending_zh[1], "中文块后无对应英文块（翻译缺失？）"))
                pending_zh = None
            pairs.append((u["zh"], u["en"], u["line"]))
        elif u["zh"]:
            if pending_zh:
                anomalies.append((pending_zh[1], "连续两个中文块（翻译缺失？）"))
            pending_zh = (u["zh"], u["line"])
        elif u["en"]:
            if pending_zh:
                pairs.append((pending_zh[0], u["en"], u["line"]))
                pending_zh = None
            else:
                anomalies.append((u["line"], "连续两个英文块（疑似原文缺失）"))
    if pending_zh:
        anomalies.append((pending_zh[1], "末尾中文块未配对（翻译缺失？）"))

    en_count = sum(1 for u in units if u["en"])
    return pairs, en_count


def parse_pairs(lines):
    """
    从对照版解析出 [(中文, 英文, 英文行号), ...]，同时返回格式类型、异常列表与译者注。

    返回 (kind, pairs, anomalies, notes)
      kind     : 'A-sep' | 'B-plain' | 'C-marked' | 'EN-only'
                 EN-only = 对照版实为纯英文（中文段落丢失，见第 44/47 章）
      pairs    : [(中文, 英文, 英文行号), ...]，**不含译者注**（保证纯英版不被中文污染）
      anomalies: 真实异常（漏译 / 顺序倒置 / 末尾未配对），**不含译者注误判**
      notes    : [(行号, 译者注全文), ...]
    """
    kind = classify(lines)
    pairs = []
    anomalies = []
    notes = []

    if kind == "C-marked":
        pending_zh = None
        pending_zh_line = 0
        for i, raw in enumerate(lines, 1):
            line = raw.strip()
            if not line or is_sep(line) or is_heading(line):
                continue
            if is_note_line(line):
                notes.append((i, line))
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
        return kind, pairs, anomalies, notes

    # A / B：块级解析（空行 / `---` 为块边界，块内多行属同一段）
    pairs, en_count = parse_by_blocks(lines, anomalies, notes)

    # EN-only：对照版实为纯英文（中文段落已丢失），非「整章未配对」。
    # 实测命中第 44/47 章（文件名是初译_对照，内容为纯英，中文字符仅标题行）。
    if not pairs and en_count >= 10:
        kind = "EN-only"
        anomalies = []      # 无中文可配对，不属翻译异常

    return kind, pairs, anomalies, notes


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
           "纯英段": 0, "译者注": 0, "MD5": "—", "问题": []}

    files = [f.name for f in ch_dir.iterdir() if f.is_file()]
    bi = [f for f in files if BILINGUAL_RE.search(f)]
    if not bi:
        row["问题"].append("无对照版")
        stats["skip"] += 1
        return row
    bi_path = ch_dir / bi[0]

    lines = bi_path.read_text(encoding="utf-8-sig").splitlines()
    kind, pairs, anomalies, notes = parse_pairs(lines)
    row["格式"] = kind
    row["对照中"] = len(pairs)
    row["对照英"] = len(pairs)
    row["译者注"] = len(notes)

    if kind == "EN-only":
        row["问题"].append("⚠ 对照版无中文（真源损坏，须从原文重建）")
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

    # 写入职责已于 2026-10-03 剥离 → 移交 tools/extract_pure_en.py（单一职责原则）。
    # 本工具自此**只读**：不生成、不覆盖任何译文文件。
    if need_write:
        if kind == "EN-only":
            row["问题"].append("⚠ EN-only（对照版无中文），须先用 repair_bilingual 重建对照版")
        elif anomalies:
            row["问题"].append("⚠ 对照存在解析异常，派生被阻断（须人工先修对照）")
        else:
            row["问题"].append("→ 缺纯英版：跑 extract_pure_en.py --chapter %d --apply" % num)

    return row


def main():
    ap = argparse.ArgumentParser(
        description="双语校验器：对照版 ⇄ 纯英版 / 原文的一致性检查（只读）")
    ap.add_argument("--init-md5", action="store_true", help="建立/重建 原文 MD5 基线（唯一写盘动作）")
    ap.add_argument("--chapter", default="", help="只处理指定章号，逗号分隔，如 37,41,42")
    ap.add_argument("--report", nargs="?", const="AUTO", default="",
                    help="导出完整表格到 项目文档/双语同步校验报告_<时间戳>.md"
                         "（不给值则自动命名；⚠ 勿传中文路径，PowerShell 会 GBK 乱码）")
    args = ap.parse_args()
    apply_mode = False      # 只读工具，保留变量以免影响 check_chapter 签名
    force_mode = False

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
        if not args.report:
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
        row = check_chapter(d, baseline, apply_mode, force_mode, stats)
        if not row["问题"]:
            stats["clean"] += 1
        rows.append(row)

    # 3) 输出
    print("=" * 96)
    print(f"双语一致性校验（只读模式 · 不写任何译文文件）"
          f"  生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 96)
    print(f"  基线状态：{'已载入 ' + str(len(baseline)) + ' 项' if baseline else '⚠ 未建立（先跑 --init-md5）'}")
    print("-" * 96)
    print(f"{'章节':<8}{'格式':<10}{'原文段':>6}{'对照块':>7}{'纯英段':>7}{'注':>4}{'MD5':>8}  问题")
    print("-" * 96)
    for r in rows:
        prob = "；".join(r["问题"]) if r["问题"] else "✔ 同步"
        print(f"{r['章']:<8}{r['格式']:<10}{r['原文段']:>6}{r['对照中']:>7}{r['纯英段']:>7}"
              f"{r['译者注']:>4}{r['MD5']:>8}  {prob[:70]}")
    print("-" * 96)
    print(f"  扫描 {stats['total']} 章 · 已同步 {stats['clean']} · 缺纯英版 {stats['missing']} · "
          f"不同步 {stats['desync']} · 解析异常 {stats['blocked']} · 无对照版 {stats['skip']}")
    print("  提示：纯英版缺失 → python tools/extract_pure_en.py --chapter <N> --apply")
    print("       纯英版体检 → python tools/extract_pure_en.py --audit")
    if not args.report:
        print("  加 --report 导出表格；加 --init-md5 建原文基线。")

    if args.report:
        if args.report == "AUTO":
            out = DOCS / f"双语同步校验报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        else:
            out = BASE / args.report
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# 双语同步校验报告", "",
                 f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                 f"> 模式：只读校验（不写译文文件；派生请用 extract_pure_en.py）",
                 "", "## 统计", "",
                 f"- 扫描章节：{stats['total']}",
                 f"- 已同步：{stats['clean']}",
                 f"- 缺纯英版：{stats['missing']}",
                 f"- 不同步：{stats['desync']}",
                 f"- 段数不符跳过：{stats['blocked']}",
                 f"- 无对照版：{stats['skip']}",
                 f"- 实际写入：0（本工具只读）",
                 "", "## 明细", "",
                 "| 章节 | 格式 | 原文段 | 对照块 | 纯英段 | 译者注 | MD5 | 问题 |",
                 "|---|---|---|---|---|---|---|---|"]
        for r in rows:
            prob = "；".join(r["问题"]).replace("|", "\\|") if r["问题"] else "✔ 同步"
            lines.append(f"| {r['章']} | {r['格式']} | {r['原文段']} | {r['对照中']} | "
                         f"{r['纯英段']} | {r['译者注']} | {r['MD5']} | {prob} |")
        lines.append("")
        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"[OK] 报告已写入：{out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
