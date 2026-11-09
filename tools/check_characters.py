# -*- coding: utf-8 -*-
"""
check_characters.py — 角色与世界观设定一致性闸门（工程约束 §④）

分两级，不做伪自动判定：
  ① 自动级（可机检）：
     - 档案缺失  对照版中文出现的角色名/章内人设标题，在 .agent/knowledge/characters/ 无档案
     - 词条缺失  对照版中文出现的角色名，在 glossary 第一节「角色人名」无词条
     - 档案沉睡  档案文件在 1-90 章从未被引用（防档案漂移）
     - 术语变体  glossary 角色名条目的 [建议]/候选 状态汇总（交 lqa_gates G3 做正文判罚）
  ② 审校级（需语义判断）：对检出差异的章节输出「一致性五问检查单」，
     交 novel-reviewer / 人工审校环节，**不自动判罚、不改译文**。

用法：
  python tools/check_characters.py                  # dry-run，打印
  python tools/check_characters.py --apply         # 报告落 项目文档/角色一致性核对_<时间戳>.md
  python tools/check_characters.py --chapter 31    # 单章细查
  python tools/check_characters.py --lo 1 --hi 90  # 区间

工程规范：仅标准库；复用 chapter_lib（chapter_dirs/parse_bilingual/find_slots）；
默认 dry-run；CLI 只收 ASCII 参数；中文路径由 __file__ 推导；stdout 重配 UTF-8。
红线：只读，不修改任何译文、术语真源或角色档案。
"""
import os
import re
import sys
import glob
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent
DOCS = REPO / "项目文档"
CHARDIR = REPO / ".agent" / "knowledge" / "characters"
GLOSSARY = REPO / "glossary.md"

sys.path.insert(0, str(TOOLS))
import chapter_lib  # noqa: E402


def load_glossary_names():
    """glossary 第一节「角色人名」词条 → [(中文, 英文, 状态, 首现章节)]"""
    text = GLOSSARY.read_text(encoding="utf-8")
    sec = text.split("## 一 角色人名", 1)[-1].split("\n## ", 1)[0]
    out = []
    for ln in sec.split("\n"):
        s = ln.strip()
        if not s.startswith("|") or s.startswith("|---") or "中文" in s:
            continue
        c = [x.strip() for x in s.strip("|").split("|")]
        if len(c) >= 4 and c[0]:
            out.append((c[0], c[1], c[2], c[3]))
    return out


def load_all_glossary_terms():
    """glossary 全节中文词条（称谓/官制/器物同样有定译，不算「无词条」）"""
    text = GLOSSARY.read_text(encoding="utf-8")
    out = set()
    for ln in text.split("\n"):
        s = ln.strip()
        if not s.startswith("|") or s.startswith("|---"):
            continue
        c = [x.strip() for x in s.strip("|").split("|")]
        if c and c[0] and c[0] not in ("中文", "#"):
            out.add(c[0])
    return out


# 称谓/职务/事物词尾：不是「角色名」，不进档案/词条缺失判罚（避免伪自动判定）
NON_NAME_SUFFIX = (
    "老爷", "大人", "公子", "姑娘", "小姐", "夫人", "嬷嬷", "管家", "伯父", "三叔",
    "二爷", "大爷", "女词人", "词人", "居士", "知府", "尚书", "王爷", "娘娘", "贵妃",
    "母夜叉", "亲家", "一家", "丫鬟们", "公子们", "侍卫", "内侍", "村长", "艺人",
)
NON_NAME_CONTAINS = ("诗词", "注意事项", "剧情", "本章", "银杏", "一家", "与丫鬟", "温柔")
# 术语提取节的分类标题（非人名），不得当角色
CATEGORY_WORDS = {
    "官职", "时代", "身份", "景观", "时间", "地点", "称谓", "典故", "婚姻", "娱乐",
    "书法", "美食", "器物", "地理", "财产", "招式", "心理", "动作", "人名", "人物",
    "文化", "习俗", "建筑", "服饰", "饮食", "植物", "动物", "宗教", "节庆", "医药",
    "本章术语提取", "本章角色人设", "本章翻译注意事项", "其他", "备注", "分类",
}


def is_probable_name(s):
    if not (2 <= len(s) <= 8):
        return False
    if s in CATEGORY_WORDS or s.startswith(("《", "(")):
        return False
    if re.match(r"^[\d.]+", s):
        return False
    if any(s.endswith(x) for x in NON_NAME_SUFFIX):
        return False
    if any(x in s for x in NON_NAME_CONTAINS):
        return False
    return True


def archive_stems():
    """角色档案名（含组合档案如「白风与南双」拆出的单名）→ 覆盖集合"""
    if not CHARDIR.exists():
        return set(), []
    stems = set()
    files = []
    for p in CHARDIR.glob("*.md"):
        files.append(p.name)
        stem = p.stem.strip()
        stems.add(stem)
        # 组合档案 / 章节笔记：拆出可用单名
        for part in re.split(r"[与和及、,，\s]+", stem):
            part = part.strip()
            if 2 <= len(part) <= 5 and not re.match(r"^[\d.]+", part):
                stems.add(part)
    return stems, files


def chapter_names_from_terms(ch_dir):
    """章内 术语与人设.md 的 `### 角色名` 标题 + 人名与称谓表首列"""
    hits = set()
    for p in ch_dir.glob("*术语与人设*.md"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        # 只从「## 二、本章角色人设」节内取 ### 标题（术语提取节的 ### 是分类名，不是人名）
        persona = ""
        m = re.search(r"^##\s+二[、.\s]+.*角色人设.*$", text, re.M)
        if m:
            tail = text[m.end():]
            nx = re.search(r"^##\s+", tail, re.M)
            persona = tail[:nx.start()] if nx else tail
        for h in re.finditer(r"^###\s+(.+?)\s*$", persona, re.M):
            raw = h.group(1).split("(")[0].split("（")[0].strip()
            # 人设标题可能是「东方尘泽、曹班」「白风与南双」等合并标题 → 拆成单名
            for name in re.split(r"[、,，与和及/]+", raw):
                name = name.strip()
                if is_probable_name(name):
                    hits.add(name)
        # 「### 人名与称谓」表首列（跳过表头/分隔，过滤分类词）
        in_table = False
        for ln in text.split("\n"):
            s = ln.strip()
            if s.startswith("### 人名与称谓"):
                in_table = True
                continue
            if in_table and s.startswith("### "):
                in_table = False
                continue
            if in_table and s.startswith("|") and not s.startswith("|---"):
                c = [x.strip() for x in s.strip("|").split("|")]
                if c and is_probable_name(c[0]):
                    hits.add(c[0])
    return hits


def scan_chapter(n, d, glossary_names, all_terms, stems):
    """返回 (中文全文, 章内角色名集合, 出现的人名, 档案缺失, 词条缺失)"""
    zh_text = ""
    try:
        bi = chapter_lib.parse_bilingual(d)
        zh_text = "\n".join(p[0] for p in bi.get("pairs", []))
    except Exception:
        zh_text = ""
    if not zh_text.strip():
        # 缺对照版（已知第1/2/70章）→ 回退原文，避免角色被误判「沉睡」
        z = d / f"第{n}章原文.md"
        if z.exists():
            zh_text = z.read_text(encoding="utf-8", errors="replace")
    local_names = chapter_names_from_terms(d)

    # 候选 = glossary 角色名 ∪ 章内人设标题/人名表，先滤掉称谓与事物词
    g_names = [g[0] for g in glossary_names]
    candidates = {x for x in (set(g_names) | local_names) if is_probable_name(x)}
    appeared = sorted(x for x in candidates if x in zh_text)

    miss_archive = [x for x in appeared if x not in stems]
    # 词条缺失：比对 glossary 全节（称谓/官制等已在其它节有定译，不算缺）
    miss_glossary = [x for x in appeared if x not in all_terms]
    return zh_text, local_names, appeared, miss_archive, miss_glossary


def main():
    ap = argparse.ArgumentParser(description="角色与世界观一致性闸门（只读）")
    ap.add_argument("--apply", action="store_true", help="报告落盘（缺省 dry-run）")
    ap.add_argument("--chapter", type=int)
    ap.add_argument("--lo", type=int, default=1)
    ap.add_argument("--hi", type=int, default=90)
    a = ap.parse_args()

    glossary_names = load_glossary_names()
    all_terms = load_all_glossary_terms()
    stems, files = archive_stems()
    lo = hi = a.chapter if a.chapter else None
    if a.chapter is None:
        lo, hi = a.lo, a.hi

    dirs = [(n, d) for n, d in chapter_lib.chapter_dirs(lo, hi)]
    all_zh = []
    rows = []
    for n, d in dirs:
        try:
            zh, local, appeared, ma, mg = scan_chapter(n, d, glossary_names, all_terms, stems)
            all_zh.append(zh)
            rows.append({"n": n, "local": local, "appeared": appeared, "ma": ma, "mg": mg})
        except Exception as e:  # noqa: BLE001
            rows.append({"n": n, "err": str(e)})

    corpus = "\n".join(all_zh)
    # 档案沉睡 / 疑似非角色文件（章节笔记误入 characters/）
    sleeping, non_profile = [], []
    for f in files:
        stem = Path(f).stem.strip()
        if re.match(r"^\d+[.\s]", stem) or any(x in stem for x in ("剧情", "注意事项", "温柔", "本章")):
            non_profile.append(f)
            continue
        parts = [stem] + [x.strip() for x in re.split(r"[与和及、,，\s]+", stem) if x.strip()]
        if not any(p and p in corpus for p in parts):
            sleeping.append(f)

    # 汇总
    ch_miss_a = [(r["n"], r["ma"]) for r in rows if r.get("ma")]
    ch_miss_g = [(r["n"], r["mg"]) for r in rows if r.get("mg")]
    ch_err = [(r["n"], r["err"]) for r in rows if r.get("err")]
    advice_status = [(g[0], g[2]) for g in glossary_names if "[建议]" in g[2]]

    print("=" * 72)
    print("角色与世界观一致性闸门（自动级）")
    print("=" * 72)
    print("扫描章数 %d（%d~%d）· 档案文件 %d · glossary 角色名 %d" % (
        len(dirs), lo, hi, len(files), len(glossary_names)))
    print("档案缺失章节 %d · 词条缺失章节 %d · 沉睡档案 %d · 疑似非角色文件 %d · 解析异常 %d" % (
        len(ch_miss_a), len(ch_miss_g), len(sleeping), len(non_profile), len(ch_err)))
    print("-" * 72)
    for n, names in ch_miss_a[:12]:
        print("  [档案缺失] 第%d章: %s" % (n, "、".join(names[:8])))
    if len(ch_miss_a) > 12:
        print("  ... 另 %d 章" % (len(ch_miss_a) - 12))
    for n, names in ch_miss_g[:12]:
        print("  [词条缺失] 第%d章: %s" % (n, "、".join(names[:8])))
    if len(ch_miss_g) > 12:
        print("  ... 另 %d 章" % (len(ch_miss_g) - 12))
    if sleeping:
        print("  [沉睡档案] %s" % "、".join(sleeping[:10]))
    if non_profile:
        print("  [非角色文件] %s（章节笔记误入 characters/，建议移出，不判角色缺失）" % "、".join(non_profile[:10]))
    if ch_err:
        print("  [解析异常] %s" % ch_err[:5])
    if advice_status:
        print("  [术语状态] glossary 角色名中 %d 条仍为 [建议]（G3 变体判罚以锁定词条为准）" % len(advice_status))

    checklist = [
        "1. 人物关系/称谓是否与既有档案矛盾（辈分、亲称、自称）？",
        "2. 性格/行为动机是否与该角色既有人设冲突？",
        "3. 世界观细节（官制/器物/门派/地理）是否与 glossary 第四节及前文矛盾？",
        "4. 同一角色前后译名/称谓是否漂移？（以 lqa_gates G3 变体结果为准）",
        "5. 跨章时间线 / 事件引用是否自洽？",
    ]
    diff_chapters = sorted({n for n, _ in ch_miss_a} | {n for n, _ in ch_miss_g})

    if a.apply:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = DOCS / ("角色一致性核对_%s.md" % ts)
        b = ["# 角色与世界观设定一致性核对（自动级 + 审校检查单）", "",
             "> 生成：%s（本机系统时间，北京时间 UTC+8）· 工具 `tools/check_characters.py`（只读）" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "> 范围：第%d~%d 章 · 档案 %d 个 · glossary 角色名 %d 条" % (lo, hi, len(files), len(glossary_names)),
             "> **结论均为 `[建议]`**，终裁权在用户；本工具不判罚、不改译文与术语真源。", "",
             "## 一、自动级检出", "",
             "| 类别 | 数量 | 明细 |", "|---|---|---|",
             "| 档案缺失章节 | %d | %s |" % (len(ch_miss_a), "；".join("第%d章(%s)" % (n, "、".join(x[:5])) for n, x in ch_miss_a[:20]) or "无"),
             "| 词条缺失章节 | %d | %s |" % (len(ch_miss_g), "；".join("第%d章(%s)" % (n, "、".join(x[:5])) for n, x in ch_miss_g[:20]) or "无"),
             "| 沉睡档案 | %d | %s |" % (len(sleeping), "、".join(sleeping) or "无"),
             "| 疑似非角色文件 | %d | %s（建议移出 characters/） |" % (len(non_profile), "、".join(non_profile) or "无"),
             "| 解析异常 | %d | %s |" % (len(ch_err), str(ch_err[:5]) or "无"), "",
             "## 二、审校级检查单（对检出差异章节逐章过，不自动判罚）", "",
             "适用章节：**%s**" % ("、".join("第%d章" % n for n in diff_chapters) if diff_chapters else "无"),
             ""]
        b += checklist
        b += ["", "> 世界观术语跨章漂移：另跑 `python tools/check_poem_terms.py --section 4`（世界观与武功）/ `--section 3`（地理与机构）。",
              "> 术语变体正文判罚：另跑 `python tools/lqa_gates.py`（G3）。", ""]
        DOCS.mkdir(exist_ok=True)
        out.write_text("\n".join(b) + "\n", encoding="utf-8")
        print("[OK] 报告 → %s" % out.name)
    else:
        print("\n审校检查单（差异章节 %d 个）：" % len(diff_chapters))
        for c in checklist:
            print("  " + c)
        print("[提示] 加 --apply 才落盘报告。")


if __name__ == "__main__":
    main()
