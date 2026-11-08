#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chapter_lib.py — 章节层共享库（门禁脚本共用底座）

职责：
  - 路径推导（BASE / CHAPTERS / DOCS / GLOSSARY），路径全部由 __file__ 推导，
    **不接受命令行中文路径参数**（PowerShell GBK 乱码坑，见工作区 memory）。
  - 章节目录发现与章号区间筛选（--chapter 30-90 这类纯 ASCII 参数可用）。
  - 对照版解析：直接复用 sync_bilingual.parse_pairs（已实测支持 A/B/C 三种体制），
    **不重复实现**，避免两套解析逻辑漂移。
  - glossary.md 术语表解析：状态列 + 候选变体 + 推荐首选。
  - 英文文本度量：词数 / 句子切分 / 去红标标签。

被 tools/lqa_gates.py、tools/apply_redmark.py 引用。
仅标准库。默认只读（本模块本身不写任何文件）。
"""
import re
import sys
from collections import OrderedDict
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
CHAPTERS = BASE / "章节原文"
DOCS = BASE / "项目文档"
GLOSSARY = BASE / "glossary.md"

CHAPTER_DIR_RE = re.compile(r"^第(\d+)章$")
BILINGUAL_RE = re.compile(r"初译_对照")
PURE_EN_RE = re.compile(r"^第\d+章译文\.md$")

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
EN_RE = re.compile(r"[A-Za-z]")
RED_TAG_RE = re.compile(r"</?font[^>]*>")

# 中文块判定阈值（与 sync_bilingual.CJK_RATIO_MIN 保持一致）
CJK_RATIO_MIN = 0.5
NOTE_PREFIX_RE = re.compile(r"^\*?\[(TN|POEM|PUNC|PUZZLE|NOTE|EDITOR)\s*[:：]")

# 从 docsstring 借用的对白/连接词判定
CONNECTOR_RE = re.compile(
    r"\b(and|but|or|so|yet|for|because|since|although|though|while|when|where|which|who|whom|that|if|unless|until|after|before)\b",
    re.I,
)
SENT_SPLIT_RE = re.compile(r"(?<=[.!?])[”\"']?\s+|\s*\.\.\.\s*")


# ------------------------------------------------------------------ 同步器复用

def _load_sync_module():
    """导入同目录的 sync_bilingual，取其已验证的对照版解析函数。"""
    import importlib.util
    p = Path(__file__).resolve().parent / "sync_bilingual.py"
    spec = importlib.util.spec_from_file_location("_sync_bilingual", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_bilingual_file(path):
    """解析指定的对照版文件（2026-10-27 抽出，供归档回退场景复用）。"""
    sync = _load_sync_module()
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    kind, pairs, anomalies, notes = sync.parse_pairs(lines)
    return {"kind": kind, "pairs": pairs, "anomalies": anomalies,
            "notes": notes, "path": Path(path)}


def parse_bilingual(ch_dir):
    """
    解析某章对照版（顶层优先；顶层没有时回退章内 归档/ 子目录）。
    返回 dict: {kind, pairs:[(zh,en,line)], anomalies:[(line,reason)], notes:[(line,text)], path}
      kind: 'A-sep' | 'B-plain' | 'C-marked' | 'EN-only'
        EN-only = 对照版实为纯英文，中文段落已丢失（真源损坏，须重建）
      pairs 不含译者注 → 纯英版不会被中文污染
      anomalies 仅含真实异常（漏译/顺序倒置/末尾未配对），不含译者注误判
    找不到对照版时 pairs 为空、path 为 None。
    """
    hits = [f for f in ch_dir.iterdir() if f.is_file() and BILINGUAL_RE.search(f.name)]
    if not hits:                       # 顶层没有 → 回退章内归档子目录（一层）
        for sub_name in ARCHIVE_DIRNAMES:
            sub = ch_dir / sub_name
            if sub.is_dir():
                hits = [f for f in sub.rglob("*")
                        if f.is_file() and BILINGUAL_RE.search(f.name)]
                if hits:
                    break
    if not hits:
        return {"kind": "-", "pairs": [], "anomalies": [], "notes": [], "path": None}
    hits.sort(key=lambda f: len(f.name))
    return parse_bilingual_file(hits[0])


def read_pure_en(ch_dir):
    """读取纯英版：返回 (path or None, [英文段...])。"""
    for f in ch_dir.iterdir():
        if f.is_file() and PURE_EN_RE.match(f.name):
            paras = []
            for line in f.read_text(encoding="utf-8-sig").splitlines():
                s = line.strip()
                if not s or s in ("---", "***", "___") or s.startswith("#"):
                    continue
                paras.append(s)
            return f, paras
    return None, []


def chapter_dirs(lo=None, hi=None):
    """返回按章号排序的章节目录列表；lo/hi 为闭区间章号。"""
    if not CHAPTERS.exists():
        return []
    out = []
    for d in CHAPTERS.iterdir():
        if not d.is_dir():
            continue
        m = CHAPTER_DIR_RE.match(d.name)
        if not m:
            continue
        n = int(m.group(1))
        if lo is not None and n < lo:
            continue
        if hi is not None and n > hi:
            continue
        out.append((n, d))
    out.sort(key=lambda x: x[0])
    return out


def parse_range(spec):
    """
    解析 --chapter 参数，支持 "30-90" / "37,41,42" / "30-" / "50"（纯 ASCII）。
    返回 (lo, hi)；spec 为空返回 (None, None)。
    """
    spec = (spec or "").strip()
    if not spec:
        return None, None
    if "-" in spec:
        a, _, b = spec.partition("-")
        lo = int(a) if a.strip() else None
        hi = int(b) if b.strip() else None
        return lo, hi
    nums = [int(x) for x in re.split(r"[,\s]+", spec) if x.strip().isdigit()]
    if not nums:
        return None, None
    return min(nums), max(nums)


# ------------------------------------------------------------------ 英文度量

def strip_red(text):
    """剥离红标 HTML 标签，避免 <font color="red"> 干扰词数与句长统计。"""
    return RED_TAG_RE.sub("", text)


def is_english(text):
    """英文段判定：中文占比 < 0.5 且含 ASCII 字母。

    2026-10-03 由「不含中文」改为占比判定：英文段内嵌中文原字
    （如 `(寻， meaning "to seek")`，占比 0.02）仍应判为英文段。
    """
    if not EN_RE.search(text):
        return False
    s = text.strip()
    return (len(CJK_RE.findall(s)) / len(s)) < CJK_RATIO_MIN


def is_note_line(line):
    """译者注行（`[TN:` 等），不计入段落。"""
    return bool(NOTE_PREFIX_RE.match(line.strip()))


def words(text):
    """英文词数：字母数字+撇号+连字符 记 1 词。"""
    return len(re.findall(r"[A-Za-z][A-Za-z'’-]*", text))


def sentences(text):
    """句子切分（句末标点 + 可选引号后切），只保留含字母的片段。"""
    parts = [p.strip() for p in SENT_SPLIT_RE.split(text) if p and p.strip()]
    return [p for p in parts if EN_RE.search(p)]


def max_sentence_words(text):
    sents = sentences(text)
    return max((words(s) for s in sents), default=0)


def connectors(text):
    return len(CONNECTOR_RE.findall(text))


def en_paragraphs(ch_dir, prefer="对照版"):
    """
    取该章英文段落列表。prefer='对照版'（默认，真源）→ 回退纯英版。
    返回 (来源, [英文段...])，来源为 '对照版' / '纯英版' / None。
    """
    if prefer == "对照版":
        bi = parse_bilingual(ch_dir)
        if bi["pairs"]:
            return "对照版", [strip_red(en) for _zh, en, _ln in bi["pairs"]]
    path, paras = read_pure_en(ch_dir)
    if path is not None:
        return "纯英版", [strip_red(p) for p in paras]
    return None, []


# ------------------------------------------------------------------ 术语表

# glossary.md 状态列取值
STATUS_LOCKED = "锁定"
STATUS_SUGGEST = "[建议]"
STATUS_DISPUTE = "[!]待裁定"

_CAND_RE = re.compile(r"候选[：:]\s*([^（(（]+)")
_PREFER_RE = re.compile(r"推荐\s*`([^`]+)`")


def _parse_variants(note):
    """
    从备注的"候选：A / B / C（…推荐 `A`…）"中解析 (首选, [废弃变体…])。
    无"候选"或无"推荐"时返回 (None, [])。
    """
    if not note:
        return None, []
    cm = _CAND_RE.search(note)
    pm = _PREFER_RE.search(note)
    if not cm:
        return None, []
    cand = [x.strip().strip("`") for x in cm.group(1).split("/")]
    cand = [x for x in cand if x]
    if not cand:
        return None, []
    preferred = pm.group(1).strip() if pm else cand[0]
    variants = [x for x in cand if x.lower() != preferred.lower()]
    return preferred, variants


def load_glossary(path=None):
    """
    解析 glossary.md，返回 [entry...]，每条：
      {section, cn, en, status, first, note, preferred, variants}
    仅取数据表行（跳过表头分隔行与「使用规则」等非表格内容）。
    """
    p = Path(path) if path else GLOSSARY
    if not p.is_file():
        return []
    section = ""
    entries = []
    for line in p.read_text(encoding="utf-8-sig").splitlines():
        s = line.strip()
        if s.startswith("## "):
            section = s.lstrip("# ").strip()
            continue
        if not s.startswith("|"):
            continue
        if re.match(r"^\|[\s:\-|]+\|$", s):   # 表头分隔行
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 3:
            continue
        cn, en, status = cells[0], cells[1], cells[2]
        if not cn or not en:
            continue
        if not EN_RE.search(en):        # 非英文列（如同音字/说明行）跳过
            continue
        first = cells[3] if len(cells) > 3 else ""
        note = cells[4] if len(cells) > 4 else ""
        preferred, variants = _parse_variants(note)
        entries.append({"section": section, "cn": cn, "en": en, "status": status,
                        "first": first, "note": note,
                        "preferred": preferred or en, "variants": variants})
    return entries


def count_term(paras, term):
    """统计 term 在段落中的出现次数（词边界），返回 (次数, [段序号])。"""
    if not term:
        return 0, []
    rx = re.compile(r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])")
    total, hits = 0, []
    for i, para in enumerate(paras, 1):
        c = len(rx.findall(para))
        if c:
            total += c
            hits.append(i)
    return total, hits


# ------------------------------------------------------------------ 产物槽位（2026-10-27 新增）
#
# 为什么放在共享库：project_status（进度统计）与 check_slot（槽位核验）必须用同一套
# 判据，否则两份口径会漂移（历史上"三件套齐全"出现过 64/83/86 三个数字）。
#
# 关键差异（对历史 bug 的修正）：
#   * 旧 project_status 只扫章目录**顶层** `d.iterdir()`，产物若落在章的 `归档/`
#     子目录里会被判为缺失 —— 曾据此误报"第 1–9 章未翻译"。
#   * 新逻辑：顶层优先，找不到再回退到章内 `归档/`（一层），并标记来源。

SLOTS = OrderedDict([
    ("原文",       lambda n: "原文" in n and "术语" not in n),
    ("术语与人设",  lambda n: "术语与人设" in n),
    # 严格判据（2026-10-27 收紧）：只认标准名 `初译_对照`。
    # 反例：第2章归档里有 `审校草稿中英对照版.md`（历史草稿），宽判据会把它
    # 误当成唯一真源，而 parse_bilingual 用严格名解析 → 两边口径打架。
    ("初译_对照",   lambda n: "初译_对照" in n),
    ("译文",       lambda n: ("译文" in n or "初译_纯英文" in n) and "译文对比" not in n),
    ("质量评估",    lambda n: "质量评估" in n),
    ("审校意见",    lambda n: "审校意见" in n),
    ("整合报告",    lambda n: "整合报告" in n or "审校意见整合" in n),
    ("商业审校",    lambda n: "商业审校" in n),
    ("其他报告",    lambda n: ("报告" in n and "商业审校" not in n and "质量评估" not in n
                              and "整合" not in n) or "审计" in n or "润色" in n),
])

# 交付完整性门禁 G12 的三件套
CORE_SLOTS = ["原文", "初译_对照", "译文"]

# 章内可回退查找的归档类子目录名（一层）
ARCHIVE_DIRNAMES = ("归档", "archive", "Archive", "_archive", "旧版")


def _slot_files(ch_dir):
    """返回 [(name, path, archived)]：顶层文件 + 章内归档子目录（一层）下的文件。"""
    out = []
    try:
        for f in ch_dir.iterdir():
            if f.is_file():
                out.append((f.name, f, False))
    except (FileNotFoundError, NotADirectoryError):
        return out
    for sub_name in ARCHIVE_DIRNAMES:
        sub = ch_dir / sub_name
        if not sub.is_dir():
            continue
        for f in sub.rglob("*"):
            if f.is_file():
                out.append((f.name, f, True))
    return out


def find_slots(ch_dir):
    """
    核验该章九槽位。
    返回 OrderedDict: {slot: {"hit": bool, "name": str|None, "archived": bool, "path": Path|None}}
    顶层命中优先于归档命中；同一槽位多个文件时取文件名最短者（通常是主件）。
    """
    files = _slot_files(ch_dir)
    result = OrderedDict()
    for slot, matcher in SLOTS.items():
        hits = [(n, p, a) for (n, p, a) in files if matcher(n)]
        if not hits:
            result[slot] = {"hit": False, "name": None, "archived": False, "path": None}
            continue
        hits.sort(key=lambda x: (x[2], len(x[0])))   # 顶层优先，其次名短
        name, path, archived = hits[0]
        result[slot] = {"hit": True, "name": name, "archived": archived, "path": path}
    return result


def core_complete(slots):
    """三件套是否齐全。"""
    return all(slots[s]["hit"] for s in CORE_SLOTS)


# ------------------------------------------------------------------ 真源守卫（G0 强化）

ORIGIN_RE = re.compile(r"^第\d+章原文\.md$")
G0_MIN_CJK = 50          # 与 lqa_gates.G0 保持一致
PARA_ALIGN_TOL = 0.10    # 中文段数与原文段数允许偏差（超过判 P1）


def _count_paras_origin(path):
    """按空行分段统计原文段落数（连续非空行 = 一段，忽略标题行）。"""
    n = 0
    in_para = False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        s = line.strip()
        if not s:
            in_para = False
            continue
        if s.startswith("#"):
            continue
        if not in_para:
            n += 1
            in_para = True
    return n


def cn_source_check(ch_dir):
    """
    真源健康检查（比 lqa_gates.G0 的"中文字符数 ≥50"更严：加段数对齐）。

    返回 dict:
      kind          对照版体制（A-sep/B-plain/C-marked/EN-only/-）
      bi_path       对照版路径
      cjk           对照版中文字符总数
      cn_paras      对照版中的中文段数（pairs 里 zh 非空）
      origin_paras  原文段落数（无原文文件时 None）
      level         "OK" | "P0" | "P1"
      reason        说明
    """
    info = {"kind": "-", "bi_path": None, "cjk": 0, "cn_paras": 0,
            "origin_paras": None, "level": "OK", "reason": ""}

    origin = None
    for f in ch_dir.iterdir() if ch_dir.exists() else []:
        if f.is_file() and ORIGIN_RE.match(f.name):
            origin = f
            break
    if origin is not None:
        info["origin_paras"] = _count_paras_origin(origin)

    bi = parse_bilingual(ch_dir)
    info["kind"] = bi["kind"]
    info["bi_path"] = bi["path"]
    if bi["path"] is None:
        info["level"] = "P1"
        info["reason"] = "缺对照版（唯一真源不存在）"
        return info

    pairs = bi["pairs"]
    info["cn_paras"] = sum(1 for zh, _en, _ln in pairs if zh and zh.strip())
    info["cjk"] = sum(len(CJK_RE.findall(zh or "")) for zh, _e, _l in pairs)

    if bi["kind"] == "EN-only" or info["cjk"] < G0_MIN_CJK:
        info["level"] = "P0"
        info["reason"] = f"真源中文丢失（kind={bi['kind']}，中文字符仅 {info['cjk']}）"
        return info

    op = info["origin_paras"]
    if op:
        deviation = abs(info["cn_paras"] - op) / max(op, 1)
        if deviation > PARA_ALIGN_TOL:
            info["level"] = "P1"
            info["reason"] = (f"段落不对齐：中文段 {info['cn_paras']} vs 原文段 {op}"
                             f"（偏差 {deviation:.0%}）")
            return info
    return info
