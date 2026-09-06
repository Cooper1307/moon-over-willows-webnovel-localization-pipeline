#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
术语候选与冲突扫描器（Glossary Candidate & Conflict Scanner）

从各章 `第X章术语与人设.md` 回溯抽取术语，识别三类问题，为重建 glossary.md 权威主表提供输入：
  1. 章内译法冲突：同一中文词条在同一章内用 `A / B` 并列多个译法
  2. 跨章译法冲突：同一中文词条在不同章采用不同译法
  3. 复合词条：中文侧本身含 `/`（如 `湖水 / 荷叶 / 花骨朵`），需拆分为独立词条

用法：
  python tools/build_glossary_candidates.py                 # dry-run，只打印统计
  python tools/build_glossary_candidates.py --apply          # 写报告到 项目文档/术语候选与冲突清单.md
  python tools/build_glossary_candidates.py --limit 150      # 调整清单条数上限（默认 80）

规范（照搬 MTPE tools/）：仅标准库；默认 dry-run；只读源文件，不修改任何章节文件；
路径由 __file__ 推导，避免 Windows 中文路径经命令行传参导致 GBK 乱码。
"""
import argparse
import re
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
CHAPTERS = BASE / "章节原文"
DOCS = BASE / "项目文档"
DEFAULT_REPORT = DOCS / "术语候选与冲突清单.md"

GLOSSARY_FILE_RE = re.compile(r"术语与人设\.md$")


def clean_text(text: str) -> str:
    """清理 Markdown 标记（保留 [TN:] 之类语义内容）"""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = " ".join(text.split())
    return text.strip()


def clean_state(text: str) -> str:
    """状态列去掉方括号标记，只留文字"""
    return re.sub(r"[\[\]]", "", clean_text(text)).strip()


def parse_glossary_file(path: Path):
    """解析单个术语与人设文件，返回 [(中文, 英文, 状态)]"""
    rows = []
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return rows

    cn_idx = en_idx = st_idx = None
    in_table = False

    for raw in content.split("\n"):
        line = raw.strip()
        if not line.startswith("|"):
            in_table = False
            cn_idx = en_idx = st_idx = None
            continue

        cells = [c.strip() for c in line.strip("|").split("|")]

        if not in_table:
            # 表头行：定位「中文」「建议英文」「状态」列
            joined = "".join(cells)
            if ("中文" in joined) and ("建议英文" in joined or "英文" in joined):
                for i, c in enumerate(cells):
                    c_clean = re.sub(r"[*`\s]", "", c)
                    if cn_idx is None and c_clean == "中文":
                        cn_idx = i
                    elif en_idx is None and ("建议英文" in c_clean or c_clean == "英文"):
                        en_idx = i
                    elif st_idx is None and c_clean in ("状态", "生命周期"):
                        st_idx = i
                if cn_idx is not None and en_idx is not None:
                    in_table = True
            continue

        # 分隔行
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue

        if len(cells) <= max(cn_idx, en_idx):
            continue

        cn = clean_text(cells[cn_idx])
        en = clean_text(cells[en_idx])
        st = clean_state(cells[st_idx]) if (st_idx is not None and st_idx < len(cells)) else ""

        if not cn or not en or cn in ("中文", "---"):
            continue
        rows.append((cn, en, st))

    return rows


def split_variants(text: str):
    """按 ' / ' 与 '／' 拆分并列写法"""
    parts = [p.strip() for p in re.split(r"\s*[/／]\s*", text) if p.strip()]
    return parts


GLOSSARY_FILE = BASE / "glossary.md"
CHARACTER_DIR = BASE / ".agent" / "knowledge" / "characters"

# 事故项强制锁定（曾发生跨文件回改事故，见方案 3.4.2）
KNOWN_LOCKS = {
    "仪王府": "Prince Yi's Manor",
    "小爷": "Young Master",
    "千年神柳": "Millennial Divine Willow",
    "嬷嬷": "Matron",
}

SECTION_NAMES = [
    "一 角色人名", "二 称谓与官制", "三 地理与机构", "四 世界观与武功",
    "五 衣食器物与文化项", "六 诗词与典故", "七 金句与口头禅锁定表",
    "〇 未分类（待归类）",
]

PLACE_SUFFIX = ("府", "院", "殿", "阁", "楼", "园", "寺", "观", "庄", "衙", "铺", "店",
                "桥", "亭", "台", "轩", "斋", "宫", "城", "街", "巷", "村", "镇", "县",
                "山", "河", "湖", "林", "门", "房")
TITLE_HINT = ("夫人", "小姐", "公子", "娘子", "相公", "嬷嬷", "丫鬟", "官家", "陛下",
              "娘娘", "太尉", "丞相", "大人", "师父", "徒弟", "殿下", "老祖宗", "管家",
              "内侍", "居士", "少爷", "姑娘", "婆子", "小厮", "太监", "将军")
MARTIAL_HINT = ("拳", "功", "法", "术", "招", "式", "剑", "刀", "掌", "内力", "轻功", "点穴")
CULTURE_HINT = ("衣", "帽", "簪", "裙", "袍", "衫", "鞋", "茶", "酒", "食", "菜", "汤",
                "糕", "饼", "碗", "筷", "椅", "墩", "灯", "香", "药", "扇", "伞", "琴",
                "棋", "书", "画", "笔", "墨", "纸", "砚", "轿", "车", "船", "镜", "梳",
                "帕", "巾", "炉", "瓶", "盘", "盆")
POEM_HINT = ("《", "》", "典故")
MOTTO_HINT = ("老娘", "家人们", "口头禅", "咱", "俺")


def load_character_names():
    """从 RAG 角色知识库切片文件名读取角色名词表"""
    if not CHARACTER_DIR.exists():
        return set()
    names = set()
    for p in CHARACTER_DIR.glob("*.md"):
        n = p.stem.strip()
        if not n or re.match(r"^[\d.]", n) or "本章" in n or "注意事项" in n:
            continue  # 过滤混入的非角色切片
        names.add(n)
    return names


def classify(cn: str, char_names: set) -> str:
    if cn in char_names:
        return "一 角色人名"
    if cn in KNOWN_LOCKS or any(cn.endswith(h) for h in ("爷", "娘", "夫人", "大人")) or any(h in cn for h in TITLE_HINT):
        return "二 称谓与官制"
    if cn.endswith(PLACE_SUFFIX):
        return "三 地理与机构"
    if any(h in cn for h in MARTIAL_HINT):
        return "四 世界观与武功"
    if any(h in cn for h in POEM_HINT) or cn.endswith(("诗", "词", "曲", "赋")):
        return "六 诗词与典故"
    if any(h in cn for h in MOTTO_HINT):
        return "七 金句与口头禅锁定表"
    if any(h in cn for h in CULTURE_HINT):
        return "五 衣食器物与文化项"
    return "〇 未分类（待归类）"


def _chapters_of(variants):
    return sorted({c for v in variants.values() for c in v})


def _chapter_num(chapters):
    nums = [int(m.group(1)) for c in chapters if (m := re.search(r"第(\d+)章", c))]
    return f"第{min(nums)}章" if nums else "—"


def build_glossary(term_map, compound, limit_pending=120):
    """由扫描结果生成 glossary.md v0.9 内容（复用同一解析结果，不重复解析文件）"""
    char_names = load_character_names()
    sections = OrderedDict((name, []) for name in SECTION_NAMES)
    pending = []

    for cn, variants in term_map.items():
        if "/" in cn or "／" in cn:
            continue  # 复合词条统一在下方拆分处理
        ranked = sorted(variants.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        chapters = _chapters_of(variants)
        first_ch = _chapter_num(chapters)

        if cn in KNOWN_LOCKS:
            en, status, note = KNOWN_LOCKS[cn], "锁定", "事故项强制锁定（勿改）"
        elif len(ranked) > 1:
            en = ranked[0][0]
            alts = " / ".join(k for k, _ in ranked)
            status, note = "[建议]", f"候选：{alts}（按出现频次推荐 `{en}`，待确认）"
            pending.append((cn, en, alts))
        else:
            en, status, note = ranked[0][0], "锁定", ""

        # 全书惯例校验：府→Manor、嬷嬷→Matron
        if cn not in KNOWN_LOCKS:
            if cn.endswith("府") and not en.endswith("Manor"):
                status, note = "[建议]", (note + "；" if note else "") + "⚠️ 全书惯例 府→Manor"
                pending.append((cn, en, en + " → X Manor"))
            elif cn.endswith("嬷嬷") and not en.startswith("Matron"):
                # 从各候选译法的尾词提取姓的罗马字（Nurse Zou / Nanny Zou -> Zou）
                tails = [v.split()[-1] for v in variants.keys() if v.split()]
                if tails:
                    surname = max(set(tails), key=tails.count)
                    old_en = en
                    en = f"Matron {surname}"
                    status = "[建议]"
                    note = (f"⚠️ 全书惯例 嬷嬷→Matron：由候选提取姓 `{surname}`，"
                            f"建议 `{en}`（按频次原选 `{old_en}`，已按惯例覆盖）")
                    pending.append((cn, en, " / ".join(variants.keys()) + f" → {en}"))
                else:
                    status, note = "[建议]", (note + "；" if note else "") + "⚠️ 全书惯例 嬷嬷→Matron（Matron + 姓）"

        # 括号别名检测：`赵朴（仪王）` 这类写法应与主名合并，避免同一人物重复收录
        alias_of = ""
        m_alias = re.search(r"(.+?)（(.+?)）", cn)
        if m_alias:
            base, inner = m_alias.group(1).strip(), m_alias.group(2).strip()
            for cand in (base, inner):
                if cand in term_map and cand != cn:
                    alias_of = cand
                    break
        if alias_of:
            status = "[建议]"
            note = (note + "；" if note else "") + f"⚠️ 疑似 `{alias_of}` 的别名/异写，建议合并为同一词条"
            pending.append((cn, en, f"疑似别名，与主词条 `{alias_of}` 重复"))

        sections[classify(cn, char_names)].append((cn, en, status, first_ch, note))

    # 复合词条拆分并入
    split_count = 0
    for cn, variants in compound:
        base_en = variants[0] if variants else ""
        for part in split_variants(cn):
            if part and part not in term_map:
                sections[classify(part, char_names)].append(
                    (part, base_en, "[建议]", "—", f"由复合词条 `{cn}` 拆分，需人工定译"))
                pending.append((part, "", "复合拆分，待定译"))
                split_count += 1

    for name in sections:
        sections[name].sort(key=lambda r: r[0])

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    locked = sum(1 for rows in sections.values() for r in rows if r[2] == "锁定")
    suggested = sum(1 for rows in sections.values() for r in rows if r[2] == "[建议]")

    lines = [
        "# glossary.md — 术语权威主表",
        "",
        f"> 版本：v0.9（脚本自动生成 + 人工裁定） · 生成时间：{now}",
        "> 生成方式：`python tools/build_glossary_candidates.py --emit-glossary --apply`",
        "> 数据来源：各章 `第X章术语与人设.md`（实测 90 章目录）",
        "",
        "## 使用规则（红线）",
        "",
        "1. **本表是唯一权威源**；`术语表/术语表_Trados_*.{csv,txt}` 是导出物，由 `tools/export_trados.py` 生成，**不得手工编辑**。",
        "2. **一个词条只允许一个定译**。多译法并列（MTPE 所称 AI 痕迹第 11 类「同义词循环」）是本项目已发生事故的根源。",
        "3. 状态含义：`锁定` = 可直接使用；`[建议]` = 脚本按频次推荐，**需人工确认后改为 `锁定`**；`[!]待裁定` = 存在矛盾，禁止擅改。",
        "4. 术语变更必须**回溯已产出章节**并写入第九节变更记录，禁止只改表不改稿。",
        "5. 术语表仅供参考：若发现更地道译法，以地道表达优先并标注待更新（MTPE 元规则）。",
        "",
        "---",
        "",
    ]

    for name in SECTION_NAMES:
        rows = sections[name]
        lines += [f"## {name}", "", f"| 中文 | 英文 | 状态 | 首现章节 | 备注 |", "|---|---|---|---|---|"]
        if rows:
            for cn, en, status, first_ch, note in rows:
                lines.append(f"| {cn} | {en} | {status} | {first_ch} | {note} |")
        else:
            lines.append("| — | | | | |")
        lines.append("")

    lines += [
        "---",
        "",
        "## 八 待裁定清单（[!]）",
        "",
        f"> 共 {len(pending)} 条，列出前 {limit_pending} 条。**逐条确认后改状态为 `锁定`，并回溯已产出章节。**",
        "",
        "| # | 中文 | 推荐定译 | 现有候选/问题 |",
        "|---|---|---|---|",
    ]
    for i, (cn, en, alts) in enumerate(pending[:limit_pending], 1):
        lines.append(f"| {i} | {cn} | {en or '（空）'} | {alts} |")
    if not pending:
        lines.append("| — | | | |")
    lines += [
        "",
        "---",
        "",
        "## 九 变更记录",
        "",
        "| 日期 | 变更 | 理由 | 影响范围 |",
        "|---|---|---|---|",
        f"| {now[:10]} | 建表 v0.9：{locked} 条锁定 / {suggested} 条建议 / 复合词条拆分 {split_count} 条 | 由 90 章术语文件回溯抽取 | 全书（后续由 export_trados.py 导出 CAT 格式） |",
        "",
        "> ⚠️ 待人工裁定完成前，`[建议]` 条目不得直接用于新章初译；初译时如遇 `[建议]` 词条，按「忠实原文 > 术语锁 > 表达自然」处理并上报。",
        "",
    ]

    stat = OrderedDict([
        ("词条总数", sum(len(v) for v in sections.values())),
        ("锁定（可直接使用）", locked),
        ("建议（待人工确认）", suggested),
        ("待裁定清单条目", len(pending)),
        ("复合词条拆分并入", split_count),
        ("角色名词表（来自 RAG 库）", len(char_names)),
    ])
    return "\n".join(lines), stat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="写入报告文件（默认 dry-run）")
    ap.add_argument("--limit", type=int, default=80, help="每类清单输出条数上限")
    ap.add_argument("--emit-glossary", action="store_true",
                    help="改为生成/更新 glossary.md 权威主表 v0.9（默认 dry-run，需配合 --apply 写文件）")
    args = ap.parse_args()

    if not CHAPTERS.exists():
        print(f"[ERROR] 未找到章节目录：{CHAPTERS}")
        return 1

    files = sorted(p for p in CHAPTERS.rglob("*") if p.is_file() and GLOSSARY_FILE_RE.search(p.name))
    if not files:
        print(f"[ERROR] 未匹配到任何 术语与人设.md（搜索根：{CHAPTERS}）")
        return 1

    # cn -> {en_variant: [章节...]}
    term_map = OrderedDict()
    per_file_count = []
    total_rows = 0

    for f in files:
        rows = parse_glossary_file(f)
        if rows:
            per_file_count.append((f.parent.name, len(rows)))
        total_rows += len(rows)
        chapter = f.parent.name
        for cn, en, st in rows:
            for variant in split_variants(en):
                term_map.setdefault(cn, OrderedDict()).setdefault(variant, []).append(chapter)

    # 分类
    inner_conflict = []   # 章内 A / B 并列（英文侧多写法）
    cross_conflict = []   # 跨章不同译法
    compound = []         # 中文侧含 /
    consistent = []       # 全书一致

    for cn, variants in term_map.items():
        if "/" in cn or "／" in cn:
            compound.append((cn, list(variants.keys())))
            continue
        if len(variants) > 1:
            chapters = sorted({c for v in variants.values() for c in v})
            # 同一章内出现多种写法 = 章内并列（源表写了 A / B）
            if len(chapters) == 1:
                inner_conflict.append((cn, list(variants.keys()), chapters[0]))
            else:
                cross_conflict.append((cn, variants, chapters))
        else:
            en = list(variants.keys())[0]
            chapters = sorted(set(variants[en]))
            consistent.append((cn, en, chapters))

    # 统计
    stats = OrderedDict([
        ("扫描文件数", len(files)),
        ("术语条目总数（行）", total_rows),
        ("唯一中文词条数", len(term_map)),
        ("章内译法冲突（A / B 并列）", len(inner_conflict)),
        ("跨章译法冲突", len(cross_conflict)),
        ("复合词条（中文含 /，需拆分）", len(compound)),
        ("全书一致项（可直接锁定）", len(consistent)),
    ])

    print("=" * 60)
    print("术语候选与冲突扫描（dry-run）" if not args.apply else "术语候选与冲突扫描（--apply）")
    print("=" * 60)
    for k, v in stats.items():
        print(f"  {k:<28} {v}")
    print("-" * 60)
    print(f"  词条数 Top5 章节：{sorted(per_file_count, key=lambda x: -x[1])[:5]}")
    print(f"  报告输出：{DEFAULT_REPORT}")

    if args.emit_glossary:
        content, gstat = build_glossary(term_map, compound)
        print("-" * 60)
        for k, v in gstat.items():
            print(f"  {k:<26} {v}")
        print(f"  主表输出：{GLOSSARY_FILE}")
        if not args.apply:
            print("\n[DRY-RUN] 加 --apply 才写 glossary.md。")
            return 0
        GLOSSARY_FILE.write_text(content, encoding="utf-8")
        print(f"\n[OK] 主表已写入：{GLOSSARY_FILE}")
        return 0

    if not args.apply:
        print("\n[DRY-RUN] 加 --apply 才写报告文件。")
        return 0

    # ---- 生成报告 ----
    DOCS.mkdir(parents=True, exist_ok=True)
    limit = args.limit
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# 术语候选与冲突清单（自动扫描）",
        "",
        f"> 生成时间：{now}",
        f"> 扫描范围：`{CHAPTERS.relative_to(BASE)}/**/*术语与人设.md`（{len(files)} 个文件）",
        "> 用途：重建 `glossary.md` 权威主表的输入；**本报告为内部文件，不交付**。",
        "",
        "## 一、统计",
        "",
        "| 指标 | 数值 |",
        "|---|---|",
    ]
    lines += [f"| {k} | {v} |" for k, v in stats.items()]
    lines += ["", "---", ""]

    # 二、章内并列冲突
    lines += [
        "## 二、章内译法冲突（源表写了 `A / B` 并列，需裁定一个定译）",
        "",
        f"> 共 {len(inner_conflict)} 条，列出前 {limit} 条。",
        "",
        "| # | 中文 | 并列译法 | 出现章节 |",
        "|---|---|---|---|",
    ]
    for i, (cn, variants, ch) in enumerate(inner_conflict[:limit], 1):
        lines.append(f"| {i} | {cn} | {' / '.join(variants)} | {ch} |")
    if not inner_conflict:
        lines.append("| — | （无） | | |")
    lines += ["", "---", ""]

    # 三、跨章冲突
    lines += [
        "## 三、跨章译法冲突（同一中文在不同章译法不同，优先级最高）",
        "",
        f"> 共 {len(cross_conflict)} 条，列出前 {limit} 条。",
        "",
        "| # | 中文 | 译法 → 出现章节 |",
        "|---|---|---|",
    ]
    for i, (cn, variants, chapters) in enumerate(cross_conflict[:limit], 1):
        detail = "；".join(f"`{en}`（{', '.join(sorted(set(cs)))}）" for en, cs in variants.items())
        lines.append(f"| {i} | {cn} | {detail} |")
    if not cross_conflict:
        lines.append("| — | （无） | |")
    lines += ["", "---", ""]

    # 四、复合词条
    lines += [
        "## 四、复合词条（中文侧含 `/`，建议拆分为独立词条）",
        "",
        f"> 共 {len(compound)} 条，列出前 {limit} 条。",
        "",
        "| # | 中文（复合） | 现有英文 |",
        "|---|---|---|",
    ]
    for i, (cn, variants) in enumerate(compound[:limit], 1):
        lines.append(f"| {i} | {cn} | {' / '.join(variants)} |")
    if not compound:
        lines.append("| — | （无） | |")
    lines += ["", "---", ""]

    # 五、一致项清单（供直接锁定）
    lines += [
        "## 五、全书一致项（可直接标 `锁定`）",
        "",
        f"> 共 {len(consistent)} 条，列出前 {limit} 条（完整清单由 `glossary.md` 承载）。",
        "",
        "| # | 中文 | 英文 | 出现章节 |",
        "|---|---|---|---|",
    ]
    for i, (cn, en, chapters) in enumerate(consistent[:limit], 1):
        ch_txt = ", ".join(chapters[:6]) + ("…" if len(chapters) > 6 else "")
        lines.append(f"| {i} | {cn} | {en} | {ch_txt} |")
    if not consistent:
        lines.append("| — | （无） | | |")
    lines += [
        "",
        "---",
        "",
        "## 使用说明",
        "",
        "1. 先裁第二节（章内并列）与第三节（跨章冲突）——**每个中文只留一个定译**，其余写入备注或弃用。",
        "2. 第四节复合词条拆分为独立词条后并入主表。",
        "3. 第五节一致项直接标 `锁定`，冲突项标 `[!]待裁定`。",
        "4. 定译确认后由 `tools/export_trados.py`（待建）导出 CSV/Tab。",
        "",
        "> ⚠️ 术语表仅供参考：若发现更地道译法，以地道表达优先并标注术语表待更新（MTPE 元规则）。",
        "",
    ]

    DEFAULT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[OK] 报告已写入：{DEFAULT_REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
