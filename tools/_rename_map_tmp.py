# -*- coding: utf-8 -*-
"""临时：生成「命名归一映射建议」报告（dry，不改盘）。用完即删。
目标规范（与 sync_bilingual / project_status 槽位匹配一致）：
  第N章原文.md / 第N章术语与人设.md / 第N章初译_对照.md / 第N章译文.md /
  第N章翻译质量评估报告.md / 第N章商业审校报告.md /
  第N章审校意见YYYYMMDDHHMM-来源.md / 第N章审校意见整合报告.md
其余（润色报告/审校日志/审计报告等）标 [合并到整合报告?] 供人工定夺。
"""
import io
import os
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS = os.path.join(BASE, "章节原文")
DOCS = os.path.join(BASE, "项目文档")

CH_RE = re.compile(r"^第(\d+)章$")
TS_RE = re.compile(r"(\d{8,14})")
# 每个章节内属于该章的文件均以 第N章 开头


def plan(chapter_name, num, fname):
    """返回 (动作, 新名或None, 说明)"""
    if fname.startswith("."):
        return ("keep", None, "dotfile")
    m = re.match(r"^第%s章(.*?)(\.md)$" % num, fname)
    if not m:
        return ("keep", None, "非本章命名")
    stem = m.group(1)  # 不含 第N章 与 .md 的剩余
    # 已合规
    if stem in ("原文", "术语与人设", "初译_对照", "译文", "翻译质量评估报告",
                "商业审校报告", "审校意见整合报告", "术语表"):
        return ("keep", None, "合规")
    if "copy" in stem.lower():
        return ("ask", None, "copy 残留副本 → 建议核对内容后删除/归档")
    if stem.startswith("审校意见") and TS_RE.search(stem):
        # 去掉命名中的杂散下划线/空格（但保留合法来源字母与时间）
        new_stem = re.sub(r"[_\s]+", "", stem)
        if new_stem != stem:
            return ("rename", "第%s章%s.md" % (num, new_stem), "审校意见：去下划线/空格")
        return ("keep", None, "审校意见合规")
    # 质量评估（缺报告二字）
    if stem == "翻译质量评估":
        return ("rename", "第%s章翻译质量评估报告.md" % num, "补『报告』")
    if stem == "纯译文":
        return ("conflict", "第%s章译文.md" % num, "并入译文.md（防撞名需人工）")
    if stem in ("润色报告", "润色提升报告", "审校日志", "审校意见整合报告",
                "重复性与吸引力审计报告", "Phase2审校整合报告", "Phase3审校整合报告",
                "Phase4审校整合报告", "Phase审校整合报告"):
        return ("merge?", "第%s章审校意见整合报告.md" % num, "同类异名→整合报告？需人工定夺")
    if stem.startswith("初译_纯英文"):
        return ("merge?", "第%s章译文.md" % num, "旧纯英命名→译文.md？需人工定夺")
    return ("keep", None, "其它：" + stem[:24])


def main():
    lines = []
    auto, ask, keep = 0, 0, 0
    for d in sorted(os.listdir(CHAPTERS)):
        if not CH_RE.match(d):
            continue
        num = CH_RE.match(d).group(1)
        p = os.path.join(CHAPTERS, d)
        for f in sorted(os.listdir(p)):
            fp = os.path.join(p, f)
            if not os.path.isfile(fp) or not f.endswith(".md"):
                continue
            act, new, why = plan(d, num, f)
            if act == "keep":
                keep += 1
            elif act == "rename":
                auto += 1
                lines.append((d, f, "AUTO", new, why))
            else:
                ask += 1
                lines.append((d, f, act, new, why))
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(DOCS, "命名归一建议_%s.md" % now)
    os.makedirs(DOCS, exist_ok=True)
    w = ["# 命名归一映射建议（dry 报告）", "",
         f"> 生成：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · 统计：可自动改名 {auto} · 需人工定夺 {ask} · 合规/保持 {keep}",
         "", "| 章节 | 现文件名 | 动作 | 建议新名 | 说明 |", "|---|---|---|---|---|"]
    for d, f, act, new, why in lines:
        esc = f.replace("|", "\\|")
        w.append(f"| {d} | {esc} | {act} | {new or '-'} | {why} |")
    w.append("")
    io.open(out, "w", encoding="utf-8").write("\n".join(w))
    print(f"[OK] 报告：{out}")
    print(f"auto {auto} · ask {ask} · keep {keep}")
    print("待人工定夺样例：")
    for d, f, act, new, why in lines[:12]:
        print(f"  {d} | {f} | {act} | {new} | {why}")


if __name__ == "__main__":
    main()
