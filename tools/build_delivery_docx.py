# -*- coding: utf-8 -*-
"""
build_delivery_docx.py — 译文 md -> 干净译文 docx（最终交付件）

按用户决策①：最终交付只交译文（不交对照）。本工具产出 `交付版/第X章_译文.docx`：
纯英、无中文、无修订标记，即甲方要看的干净交付件。对照 docx 由 md_bilingual_to_docx.py
生成、归 docx交付/ 供核验；修订痕迹版由 docx_revision.py 生成、归 docx交付/ 供审阅。

输入：`章节原文/第X章/第X章译文.md`（`# Chapter N: ...` 标题 + 空行分段，纯英）
输出：`交付版/第X章_译文.docx`

用法：
  python tools/build_delivery_docx.py --chapter 32            # dry-run，仅报告
  python tools/build_delivery_docx.py --chapter 32 --apply     # 写 docx
  python tools/build_delivery_docx.py --batch 3-90 --apply     # 批量（缺译文.md 的章跳过）

工程规范：仅标准库 + python-docx；默认 dry-run，`--apply` 才写；CLI 仅 ASCII 参数；
stdout 重配 UTF-8；中文路径由 __file__ 推导；逐章 try/except 汇总成败。
红线：不改动译文 md 真源；发现中文字符仅告警（不擅自改，忠实原文）。
"""
import os, re, argparse, sys
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CJK = re.compile(r'[\u3400-\u9fff\uf900-\ufaff]')
BJ = timezone(timedelta(hours=8))  # 北京时间 UTC+8
AUTHOR = 'CooperChen'  # 唯一作者笔名（2026-11-09 起生效，不受以往任何其他笔名影响）


def parse_en_md(text):
    """返回 (标题, [段落...])；第一行为 # 标题，其余按空行分段。"""
    lines = text.split('\n')
    title = ''
    body_start = 0
    for i, ln in enumerate(lines):
        if ln.strip().startswith('# '):
            title = ln.strip()[2:].strip()
            body_start = i + 1
            break
    body = '\n'.join(lines[body_start:])
    paras = [b.strip().replace('\n', ' ') for b in re.split(r'\n\s*\n', body) if b.strip()]
    return title, paras


def build_one(ch, out_dir, apply):
    md = os.path.join(REPO, '章节原文', f'第{ch}章', f'第{ch}章译文.md')
    if not os.path.exists(md):
        return False, f'缺译文.md（跳过）', 0
    text = open(md, encoding='utf-8').read()
    title, paras = parse_en_md(text)
    cn_hits = len(CJK.findall(text))
    if not apply:
        return True, f'[dry-run] 标题={title[:30]!r} 段={len(paras)} 中文字符告警={cn_hits}', cn_hits
    try:
        from docx import Document
        doc = Document()
        if title:
            doc.add_heading(title, level=1)
        for p in paras:
            doc.add_paragraph(p)
        # 作者字段归一：唯一笔名 CooperChen（2026-11-09 起生效）；不写入任何协作者/AI 名
        cp = doc.core_properties
        cp.author = AUTHOR
        cp.last_modified_by = AUTHOR
        cp.revision = 1
        for attr in ('category', 'comments', 'keywords', 'subject', 'content_status',
                     'identifier', 'language', 'version'):
            try:
                setattr(cp, attr, '')
            except Exception:
                pass
        # 最终编辑时间：本机系统时钟 -> 北京时间(UTC+8)；OOXML 要求存 UTC 瞬时值
        bj = datetime.now(timezone.utc).astimezone(BJ)
        utc_naive = bj.astimezone(timezone.utc).replace(tzinfo=None)
        cp.created = utc_naive
        cp.modified = utc_naive
        cp.comments = f"最后编辑时间：{bj.strftime('%Y-%m-%d %H:%M:%S')}（北京时间 UTC+8）"
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, f'第{ch}章_译文.docx')
        doc.save(out)
        # 文件系统 mtime = 本机系统时间
        os.utime(out, (bj.timestamp(), bj.timestamp()))
        return True, f'{out}（{len(paras)} 段, 中文字符告警={cn_hits}）', cn_hits
    except Exception as e:  # noqa: BLE001
        return False, f'ERR {e}', cn_hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chapter', type=int)
    ap.add_argument('--batch')
    ap.add_argument('--apply', action='store_true', help='真正写 docx（缺省 dry-run）')
    args = ap.parse_args()

    out_dir = os.path.join(REPO, '交付版')
    chapters = []
    if args.chapter:
        chapters = [args.chapter]
    elif args.batch:
        m = re.match(r'(\d+)-(\d+)', args.batch)
        if not m:
            raise SystemExit('batch 格式: 3-90')
        chapters = list(range(int(m.group(1)), int(m.group(2)) + 1))
    else:
        raise SystemExit('use --chapter N or --batch A-B [--apply]')

    mode = 'APPLY' if args.apply else 'DRY-RUN'
    ok_n = skip_n = 0
    cn_total = 0
    problems = []
    for ch in chapters:
        ok, msg, cn = build_one(ch, out_dir, args.apply)
        cn_total += cn
        if ok:
            ok_n += 1
            if cn:
                problems.append(f'  第{ch}章 含 {cn} 个中文字符（源文数据质量项，未擅改，建议人工核）')
        else:
            skip_n += 1
            problems.append(f'  第{ch}章 {msg}')
        if not args.batch:
            print(f'{"OK" if ok else "SKIP"} 第{ch}章: {msg}')

    print(f'=== {mode}: OK {ok_n} · SKIP/FAIL {skip_n} · 中文字符告警合计 {cn_total} ===')
    if problems:
        print('注意项：')
        for p in problems:
            print(p)


if __name__ == '__main__':
    main()
