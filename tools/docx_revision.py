# -*- coding: utf-8 -*-
"""生成「带修订痕迹（track changes）」的 docx：WPS / Word 打开即显示红字修订。

移植自 中英剧本MTPE/tools/docx_revision.py（OOXML 修订标记，已验证）。
不依赖第三方库，直接写 OOXML 修订标记（w:ins / w:del）：
- 新增段落 → 段落标记 + 内容均标为插入（WPS 显示红色下划线）
- 删除段落 → 以 w:del + w:delText 的「删除段」形式保留在原位置（红色删除线）
- 修改段落 → 删旧 + 插新（段级，逐段对照）

⚠ 修订版仅供人工审阅：python-docx 读不到 w:ins 内的 run，
  故「修订标记版」不要作为其他工具（docx_diff / extract / 门禁）的输入。

用法：
    python tools/docx_revision.py --old 基线.docx --new 终稿.docx
    python tools/docx_revision.py --old a.docx --new b.docx --out 修订版.docx --author CooperChen
    python tools/docx_revision.py --old a.docx --new b.docx --ignore-case

默认输出：`<new 同目录>/<new 主名>_修订标记版.docx`

作者笔名：唯一笔名 CooperChen（2026-11-09 起生效，不受以往任何其他笔名影响）。
生成后用 `tools/scrub_docx_meta.py --apply` 归一 docProps 作者字段与北京时间戳。
"""
import argparse
import difflib
import os
import re
import sys
from copy import deepcopy
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

try:
    from docx import Document
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.text.paragraph import Paragraph
except ImportError:
    print("[ERR] 需要 python-docx：python -m pip install python-docx", file=sys.stderr)
    sys.exit(2)


def load_texts(path):
    doc = Document(path)
    return doc, [p for p in doc.paragraphs if p.text.strip()]


def norm(s, ignore_case=False):
    s = re.sub(r"[ \t\u3000]+", " ", s).strip()
    return s.lower() if ignore_case else s


class RevIds:
    def __init__(self, start=1000):
        self.n = start

    def next(self):
        self.n += 1
        return str(self.n)


def _ins_el(ids, author, date):
    el = OxmlElement("w:ins")
    el.set(qn("w:id"), ids.next())
    el.set(qn("w:author"), author)
    el.set(qn("w:date"), date)
    return el


def _del_el(ids, author, date):
    el = OxmlElement("w:del")
    el.set(qn("w:id"), ids.next())
    el.set(qn("w:author"), author)
    el.set(qn("w:date"), date)
    return el


def mark_paragraph_inserted(paragraph, ids, author, date):
    """整段标记为插入：段落标记 + 内容 run 全部包进 w:ins。"""
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    rPr = pPr.find(qn("w:rPr"))
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        pPr.append(rPr)
    rPr.append(_ins_el(ids, author, date))

    runs = p.findall(qn("w:r"))
    if not runs:
        return
    ins = _ins_el(ids, author, date)
    first_idx = list(p).index(runs[0])
    p.insert(first_idx, ins)
    for r in runs:
        p.remove(r)
        ins.append(r)


def make_deleted_paragraph(anchor_paragraph, text, ids, author, date):
    """在 anchor 之前插入一个「已删除」段（内容为旧文本，红色删除线）。"""
    src = anchor_paragraph._p
    new_p = deepcopy(src)
    for tag in ("w:r", "w:ins", "w:del", "w:hyperlink"):
        for el in new_p.findall(qn(tag)):
            new_p.remove(el)
    pPr = new_p.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        new_p.insert(0, pPr)
    for old_rpr_ins in pPr.findall(qn("w:rPr")):
        pPr.remove(old_rpr_ins)
    rPr = OxmlElement("w:rPr")
    rPr.append(_del_el(ids, author, date))
    pPr.append(rPr)

    dele = _del_el(ids, author, date)
    run = OxmlElement("w:r")
    dt = OxmlElement("w:delText")
    dt.set(qn("xml:space"), "preserve")
    dt.text = text
    run.append(dt)
    dele.append(run)
    new_p.append(dele)

    src.addprevious(new_p)
    return Paragraph(new_p, anchor_paragraph._parent)


def main():
    ap = argparse.ArgumentParser(description="生成带修订痕迹（track changes）的 docx")
    ap.add_argument("--old", required=True, help="基线文档（改动前）")
    ap.add_argument("--new", required=True, help="终稿文档（改动后）")
    ap.add_argument("--out", help="输出路径（默认 <new>_修订标记版.docx）")
    ap.add_argument("--author", default="CooperChen", help="修订作者名（默认 CooperChen，唯一笔名）")
    ap.add_argument("--date", help="修订时间 ISO8601（默认当前 UTC）")
    ap.add_argument("--ignore-case", action="store_true")
    args = ap.parse_args()

    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not args.out:
        base, _ = os.path.splitext(args.new)
        args.out = base + "_修订标记版.docx"

    try:
        _, old_paras = load_texts(args.old)
        doc, new_paras = load_texts(args.new)
    except Exception as e:  # noqa: BLE001
        print(f"[ERR] 读取失败：{e}", file=sys.stderr)
        sys.exit(2)

    old_n = [norm(p.text, args.ignore_case) for p in old_paras]
    new_n = [norm(p.text, args.ignore_case) for p in new_paras]
    sm = difflib.SequenceMatcher(None, old_n, new_n, autojunk=False)

    ids = RevIds()
    ins_count = del_count = 0

    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    for tag, i1, i2, j1, j2 in reversed(ops):
        if tag == "insert":
            for j in range(j2 - 1, j1 - 1, -1):
                mark_paragraph_inserted(new_paras[j], ids, args.author, date)
                ins_count += 1
        elif tag == "delete":
            anchor = new_paras[j1] if j1 < len(new_paras) else (new_paras[-1] if new_paras else None)
            if anchor is None:
                continue
            for i in range(i2 - 1, i1 - 1, -1):
                make_deleted_paragraph(anchor, old_paras[i].text.strip(), ids, args.author, date)
                del_count += 1
        else:  # replace：旧段以删除线保留 + 新段标插入
            anchor = new_paras[j1] if j1 < len(new_paras) else (new_paras[-1] if new_paras else None)
            if anchor is not None:
                for i in range(i1, i2):
                    make_deleted_paragraph(anchor, old_paras[i].text.strip(), ids, args.author, date)
                    del_count += 1
            for j in range(j1, j2):
                mark_paragraph_inserted(new_paras[j], ids, args.author, date)
                ins_count += 1

    doc.save(args.out)
    total = sum(1 for op in ops)
    print(f"基线段数 {len(old_paras)} → 终稿段数 {len(new_paras)}")
    print(f"差异块 {total} 个 · 标记插入 {ins_count} 段 · 标记删除 {del_count} 段")
    print(f"[OK] 修订标记版 → {args.out}")
    print("（WPS/Word 打开后在「审阅」中查看修订；修订版仅供审阅，勿再作为工具输入）")


if __name__ == "__main__":
    main()
