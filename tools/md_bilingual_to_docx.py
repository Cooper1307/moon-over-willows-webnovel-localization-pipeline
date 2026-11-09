# -*- coding: utf-8 -*-
"""
md_bilingual_to_docx.py — 中英对照 md -> docx 生成（降本增效 · docx 交付流水线）

背景：本小说工作区原为主源 markdown（第X章初译_对照.md）。现按交付要求改为 docx 形态：
  md 对照版（唯一真源/自动化门禁口径不变） -> 本工具 -> docx（人工在 Word 修订模式下审校/二创）。

用法：
  python tools/md_bilingual_to_docx.py --md 章节原文/第32章/第32章初译_对照.md
  python tools/md_bilingual_to_docx.py --md <对照.md> --out docx交付/第32章_中英对照.docx
  python tools/md_bilingual_to_docx.py --batch 32-90        # 批量生成（跳过缺对照版的章）

解析约定（与 第X章初译_对照.md 格式一致）：
  - 前两行 `# 章标题`(中) / `# Chapter N: ...`(英) 为标题；
  - 之后以单独一行 `---` 分隔，正文按「中文段 / 英文段」成对出现。

红线：本工具只读 md、只写 docx，不改动词条与译文真源；docx 为交付/审校载体，非自动化门禁输入。
"""
import os, re, argparse, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_blocks(text):
    blocks, cur = [], []
    for ln in text.split('\n'):
        if ln.strip() == '---':
            blocks.append('\n'.join(cur).strip())
            cur = []
        else:
            cur.append(ln)
    blocks.append('\n'.join(cur).strip())
    return blocks


def extract_titles(block0):
    cn = en = ''
    for ln in block0.split('\n'):
        ln = ln.strip()
        if ln.startswith('# '):
            if not cn:
                cn = ln[2:].strip()
            elif not en:
                en = ln[2:].strip()
    return cn, en


def split_cn_en(block):
    """每个 `---` 块内 = 中文段(+空行)+英文段。按首个空行切分中/英。"""
    lines = block.split('\n')
    for i, ln in enumerate(lines):
        if ln.strip() == '':
            return '\n'.join(lines[:i]).strip(), '\n'.join(lines[i + 1:]).strip()
    return block.strip(), ''


def md_to_docx(md_path, out_path):
    from docx import Document
    from docx.shared import RGBColor, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    text = open(md_path, encoding='utf-8').read()
    blocks = parse_blocks(text)
    cn_title, en_title = extract_titles(blocks[0])

    doc = Document()
    if cn_title:
        doc.add_heading(cn_title, level=1)
    if en_title:
        h = doc.add_heading(en_title, level=2)

    pairs = 0
    for block in blocks[1:]:
        if not block.strip():
            continue
        cn, en = split_cn_en(block)
        if cn:
            doc.add_paragraph(cn)
        if en:
            p = doc.add_paragraph()
            r = p.add_run(en)
            r.italic = True
            r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            r.font.size = Pt(11)
        if cn or en:
            pairs += 1

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # 作者字段归一：唯一笔名 CooperChen（2026-11-09 起生效）；核验件同样不得含其它作者/AI 名
    from datetime import datetime, timezone, timedelta
    BJ = timezone(timedelta(hours=8))
    cp = doc.core_properties
    cp.author = 'CooperChen'
    cp.last_modified_by = 'CooperChen'
    cp.revision = 1
    for attr in ('category', 'comments', 'keywords', 'subject', 'content_status',
                 'identifier', 'language', 'version'):
        try:
            setattr(cp, attr, '')
        except Exception:
            pass
    bj = datetime.now(timezone.utc).astimezone(BJ)
    utc_naive = bj.astimezone(timezone.utc).replace(tzinfo=None)
    cp.created = utc_naive
    cp.modified = utc_naive
    cp.comments = f"最后编辑时间：{bj.strftime('%Y-%m-%d %H:%M:%S')}（北京时间 UTC+8）"
    doc.save(out_path)
    os.utime(out_path, (bj.timestamp(), bj.timestamp()))
    return pairs


def one_chapter(ch, out_dir):
    md = os.path.join(REPO, '章节原文', f'第{ch}章', f'第{ch}章初译_对照.md')
    if not os.path.exists(md):
        return False, f'缺对照版: {md}'
    out = os.path.join(out_dir, f'第{ch}章_中英对照.docx')
    try:
        pairs = md_to_docx(md, out)
        return True, f'{out} ({pairs} 段对)'
    except Exception as e:
        return False, f'ERR {e}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md')
    ap.add_argument('--out')
    ap.add_argument('--batch', help='章号区间，如 32-90 或 3-31')
    args = ap.parse_args()

    out_dir = os.path.join(REPO, 'docx交付')
    if args.md:
        m = re.search(r'第(\d+)章', args.md)
        name = f'第{m.group(1)}章_中英对照.docx' if m else (os.path.splitext(os.path.basename(args.md))[0] + '.docx')
        out = args.out or os.path.join(out_dir, name)
        ok, msg = True, ''
        try:
            pairs = md_to_docx(args.md, out)
            msg = f'{out} ({pairs} 段对)'
        except Exception as e:
            ok, msg = False, f'ERR {e}'
        print(f'{"OK " if ok else "FAIL"} {msg}')
        return
    if args.batch:
        m = re.match(r'(\d+)-(\d+)', args.batch)
        if not m:
            raise SystemExit('batch 格式: 32-90')
        a, b = int(m.group(1)), int(m.group(2))
        ok_n = fail_n = 0
        fails = []
        for ch in range(a, b + 1):
            ok, msg = one_chapter(ch, out_dir)
            if ok:
                ok_n += 1
            else:
                fail_n += 1
                fails.append(f'  第{ch}章: {msg}')
        print(f'BATCH {args.batch}: OK {ok_n}, SKIP/FAIL {fail_n}')
        for f in fails:
            print(f)
        return
    raise SystemExit('use --md <path> or --batch A-B')


if __name__ == '__main__':
    main()
