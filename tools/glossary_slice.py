# -*- coding: utf-8 -*-
"""
glossary_slice.py — 术语库切片工具（降本增效：替代单章任务全量读取 glossary.md）

用法：
  python tools/glossary_slice.py --index
      生成 术语表/glossary_index.md（精简索引：中文|英文|状态|首现章节，无备注）
  python tools/glossary_slice.py --chapter 31
      生成 术语表/glossary_slice_第31章.md（累积词表：首现章节 ≤ 31，替代全量加载）
  python tools/glossary_slice.py --chapter 31 --strict
      仅保留本章正文（对照/原文）实际命中的词条（最小加载集）
  python tools/glossary_slice.py --chapter 31 --with-notes
      切片附带备注列（含候选/裁定痕迹），体积较大

设计要点：
  - 用整行正则提取「第N章」判定首现章节，规避个别单元格内多余 | 造成的列错位。
  - 第八节（待裁定）无首现章节，不进入按章切片；索引单独列出，翻译任务按需查阅。
  - 默认 dry-run 友好：所有生成均落盘到 术语表/（导出物，不进真源）。
  - token 估算口径：CJK 字符 ÷1.6 + 非 CJK ÷4（与 token_budget.py 一致）。

红线：本工具只读 glossary.md、只写 术语表/ 派生文件，不改动词条内容与译文真源。
"""
import os, re, argparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY = os.path.join(REPO, "glossary.md")
TERM_DIR = os.path.join(REPO, "术语表")

SECTION_RE = re.compile(r'^##\s+(.*)$')
ROW_RE = re.compile(r'^\s*\|')
SEP_RE = re.compile(r'^\s*\|[\s:\-|]+\|\s*$')
CHAP_RE = re.compile(r'第(\d+)章')


def est_tok(text):
    cjk = len(re.findall(r'[\u3400-\u9fff\uf900-\ufaff]', text))
    return int(cjk / 1.6 + (len(text) - cjk) / 4)


def status_of(cells):
    for x in cells:
        if '锁定' in x or '[建议]' in x or '[!]' in x:
            return x
    return ''


def parse(path):
    sections, cur = [], None
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            m = SECTION_RE.match(line)
            if m:
                cur = {'title': m.group(1).strip(), 'rows': []}
                sections.append(cur)
                continue
            if cur is None:
                continue
            if ROW_RE.match(line) and not SEP_RE.match(line):
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                if len(cells) < 2:
                    continue
                chap = None
                for c in cells:
                    mm = CHAP_RE.search(c)
                    if mm:
                        chap = int(mm.group(1))
                        break
                cur['rows'].append({'cells': cells, 'chap': chap})
    return sections


def is_term_section(title):
    return title and not title.startswith('使用规则') and not title.startswith('九')


def is_pending(title):
    return title.startswith('八')


def emit_index(sections):
    out = ['# glossary_index — 精简索引（词条|英文|状态|首现章节，无备注）',
           '> 由 `tools/glossary_slice.py --index` 从 `glossary.md` 生成。完整候选/裁定痕迹见 `glossary.md`。',
           '']
    for s in sections:
        if not is_term_section(s['title']):
            continue
        out.append(f'## {s["title"]}')
        if is_pending(s['title']):
            out += ['| # | 中文 | 推荐定译 | 现有候选/问题 |', '|---|---|---|---|']
            for r in s['rows']:
                c = r['cells']
                out.append(f'| {c[0] if len(c) > 0 else ""} | {c[1] if len(c) > 1 else ""} | {c[2] if len(c) > 2 else ""} | {c[3] if len(c) > 3 else ""} |')
        else:
            out += ['| 中文 | 英文 | 状态 | 首现章节 |', '|---|---|---|---|']
            for r in s['rows']:
                c = r['cells']
                zh = c[0] if len(c) > 0 else ''
                en = c[1] if len(c) > 1 else ''
                out.append(f'| {zh} | {en} | {status_of(c)} | {("第%d章" % r["chap"]) if r["chap"] else "—"} |')
        out.append('')
    return '\n'.join(out) + '\n'


def emit_slice(sections, N, strict, with_notes):
    out = [f'# glossary_slice — 第{N}章 术语切片（累积词表：首现章节 ≤ {N}）',
           f'> 由 `tools/glossary_slice.py --chapter {N}` 生成，替代全量 `glossary.md` 加载。',
           '> 待裁定词条（第八节，无首现章节）请按需查阅 `glossary.md` 第八节或 `glossary_index.md`。',
           '']
    chap_text = ''
    if strict:
        for suf in ['初译_对照.md', '原文.md']:
            p = os.path.join(REPO, '章节原文', f'第{N}章', f'第{N}章{suf}')
            if os.path.exists(p):
                chap_text += open(p, encoding='utf-8').read()
    matched = 0
    for s in sections:
        if not is_term_section(s['title']) or is_pending(s['title']):
            continue
        rows_out = []
        for r in s['rows']:
            if r['chap'] is None or r['chap'] > N:
                continue
            if strict:
                zh = r['cells'][0] if r['cells'] else ''
                if zh and zh not in chap_text:
                    continue
            rows_out.append(r)
            matched += 1
        if not rows_out:
            continue
        out.append(f'## {s["title"]}')
        if with_notes:
            out += ['| 中文 | 英文 | 状态 | 首现章节 | 备注 |', '|---|---|---|---|---|']
            for r in rows_out:
                c = r['cells']
                note = c[4] if len(c) > 4 else (c[3] if len(c) > 3 else '')
                out.append(f'| {c[0] if len(c) > 0 else ""} | {c[1] if len(c) > 1 else ""} | {status_of(c)} | {("第%d章" % r["chap"]) if r["chap"] else "—"} | {note} |')
        else:
            out += ['| 中文 | 英文 | 状态 | 首现章节 |', '|---|---|---|---|']
            for r in rows_out:
                c = r['cells']
                out.append(f'| {c[0] if len(c) > 0 else ""} | {c[1] if len(c) > 1 else ""} | {status_of(c)} | {("第%d章" % r["chap"]) if r["chap"] else "—"} |')
        out.append('')
    return '\n'.join(out) + '\n', matched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glossary', default=GLOSSARY)
    ap.add_argument('--index', action='store_true')
    ap.add_argument('--chapter', type=int)
    ap.add_argument('--strict', action='store_true')
    ap.add_argument('--with-notes', action='store_true')
    args = ap.parse_args()

    sections = parse(args.glossary)

    if args.index:
        text = emit_index(sections)
        p = os.path.join(TERM_DIR, 'glossary_index.md')
        open(p, 'w', encoding='utf-8').write(text)
        print(f'INDEX -> {p}  ({len(text)/1024:.2f} KB, ~{est_tok(text)} tok)')
        return

    if args.chapter:
        N = args.chapter
        text, matched = emit_slice(sections, N, args.strict, args.with_notes)
        p = os.path.join(TERM_DIR, f'glossary_slice_第{N}章.md')
        open(p, 'w', encoding='utf-8').write(text)
        full = open(args.glossary, encoding='utf-8').read()
        ft, st = est_tok(full), est_tok(text)
        print(f'SLICE ch{N} -> {p}')
        print(f'  slice : {len(text)/1024:.2f} KB, ~{st} tok, {matched} terms'
              + ('  [strict]' if args.strict else ''))
        print(f'  full  : {len(full)/1024:.2f} KB, ~{ft} tok')
        print(f'  saving: ~{ft - st} tok ({(1 - st/ft)*100:.0f}% off full)')
        return

    total = sum(len(s['rows']) for s in sections if is_term_section(s['title']) and not is_pending(s['title']))
    pend = sum(len(s['rows']) for s in sections if is_pending(s['title']))
    print(f'parsed glossary: term rows (一~七,〇) = {total}, 待裁定(八) = {pend}')
    print('use --index  or  --chapter N [--strict] [--with-notes]')


if __name__ == '__main__':
    main()
