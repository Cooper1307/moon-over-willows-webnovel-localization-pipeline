# -*- coding: utf-8 -*-
"""校验「带修订痕迹」docx 的结构与安全性（V1–V7）。

移植自 中英剧本MTPE/tools/verify_revision_docx.py，并按本项目「译文 docx 改写」模型增强：
  - MTPE 模型 = 中文底稿 + 纯新增英文行（w:ins only）
  - 本项目模型 = 译文 docx 逐段改写（w:del 删除旧句 + w:ins 插入新句）

断言清单：
  V1 `w:ins` 段落级标记数 = --expect-ins（给定时校验）
  V2 `w:del` 元素数 = --expect-del（给定时校验）；始终打印实际值
  V3 `w:delText` 内不含中文（删的是英文译文；若删中文字符说明误删中文原文）
  V4 **接受全部修订**后的正文 == 新版 docx 正文（抓丢行/串行/错位）
  V5 **拒绝全部修订**后的正文 == 基线 docx 正文（抓原内容被破坏）
  V6 `w:ins` 内不含中文
  V7 docx 可被 python-docx 正常打开
  V8（可选）`w:ins` 内文本序列与参考 docx 英文段序列逐条一致

用法：
    python tools/verify_revision_docx.py --rev 修订版.docx --base 基线.docx --new 新版.docx \
        [--expect-ins 1] [--expect-del 1]

退出码：0 全通过；1 有断言失败。
"""
import argparse
import io
import os
import re
import sys
import zipfile
from xml.sax.saxutils import unescape

from docx import Document

sys.stdout.reconfigure(encoding='utf-8')

CJK = re.compile(r'[\u4e00-\u9fff]')
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def read_document_xml(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if 'word/document.xml' not in names:
            raise SystemExit('[ERR] 不是有效 docx：缺 word/document.xml')
        if '[Content_Types].xml' not in names:
            raise SystemExit('[ERR] zip 结构损坏：缺 [Content_Types].xml')
        return z.read('word/document.xml').decode('utf-8')


def simulate_revisions(path, mode):
    """模拟接受/拒绝全部修订，返回按段落切分的正文序列。

    mode='accept' → 采用插入、丢弃删除（= 终稿应呈现的样子）
    mode='reject' → 丢弃插入、采用删除（= 改动前的样子）
    """
    from lxml import etree
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml')
    root = etree.fromstring(xml)
    out = []
    for p in root.iter(W + 'p'):
        buf = []
        for node in p.iter():
            tag = node.tag
            if tag == W + 't':
                # 判断是否位于 w:del 内
                anc = [a.tag for a in node.iterancestors()]
                in_del = W + 'del' in anc
                in_ins = W + 'ins' in anc
                if mode == 'accept':
                    if not in_del:
                        buf.append(node.text or '')
                else:
                    if not in_ins:
                        buf.append(node.text or '')
            elif tag == W + 'delText':
                if mode == 'reject':
                    buf.append(node.text or '')
        txt = ''.join(buf).strip()
        if txt:
            out.append(txt)
    return out


def docx_paras(path):
    d = Document(path)
    return [p.text.strip() for p in d.paragraphs if p.text.strip()]


def main():
    ap = argparse.ArgumentParser(description='校验带修订痕迹的 docx')
    ap.add_argument('--rev', required=True, help='修订标记版 docx')
    ap.add_argument('--base', default=None, help='基线 docx（改动前）')
    ap.add_argument('--new', default=None, help='新版 docx（改动后）')
    ap.add_argument('--expect-ins', type=int, default=None, help='预期插入段落数')
    ap.add_argument('--expect-del', type=int, default=None, help='预期删除段落数')
    ap.add_argument('--same-en-docx', default=None,
                    help='可选：拿另一份 docx 的英文段序列，与 w:ins 内文本逐条比对')
    ap.add_argument('--cn-extra', default=None,
                    help='项目级「纯拉丁中文台词行」清单：命中的段按中文段处理（缺省不启用）')
    args = ap.parse_args()

    cn_extra = set()
    if args.cn_extra:
        if not os.path.exists(args.cn_extra):
            raise SystemExit('[FATAL] --cn-extra 文件不存在：%s' % args.cn_extra)
        for _ln in io.open(args.cn_extra, encoding='utf-8'):
            _ln = _ln.strip()
            if _ln and not _ln.startswith('#'):
                cn_extra.add(_ln)

    xml = read_document_xml(args.rev)
    ins_els = re.findall(r'<w:ins\b[^>]*>', xml)
    del_els = re.findall(r'<w:del\b[^>]*>', xml)
    del_text = re.findall(r'<w:delText[^>]*>(.*?)</w:delText>', xml, re.S)
    ins_para = len(re.findall(r'<w:rPr>(?:(?!</w:rPr>).)*?<w:ins\b', xml, re.S))
    authors = sorted(set(re.findall(r'<w:ins\b[^>]*w:author="([^"]*)"', xml)))
    ins_blocks = re.findall(r'<w:ins\b[^>]*>(.*?)</w:ins>', xml, re.S)
    ins_text = ' '.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', ' '.join(ins_blocks), re.S))
    ins_cjk = CJK.findall(ins_text)

    fails = []
    print('=' * 62)
    print('修订 docx 校验')
    print('=' * 62)
    print(f'  w:ins 元素总数      : {len(ins_els)}（段落标记 + run 各一条）')
    print(f'  w:ins 段落级标记    : {ins_para}')
    print(f'  w:ins 去重作者      : {authors}')
    print(f'  w:del 元素          : {len(del_els)}')
    print(f'  w:delText 段        : {len(del_text)}')

    if args.expect_ins is not None and ins_para != args.expect_ins:
        fails.append(f'V1 插入段数 {ins_para} ≠ 预期 {args.expect_ins}')
    if args.expect_del is not None and len(del_text) != args.expect_del:
        fails.append(f'V2 删除段数 {len(del_text)} ≠ 预期 {args.expect_del}')
    del_cjk = CJK.findall(' '.join(del_text))
    if del_cjk:
        fails.append(f'V3 w:delText 内含 {len(del_cjk)} 个中文字符（疑似误删中文原文）')
    if ins_cjk:
        fails.append(f'V6 w:ins 内含 {len(ins_cjk)} 个中文字符')

    # V4 接受全部修订 == 新版正文
    if args.new:
        acc = simulate_revisions(args.rev, 'accept')
        newp = docx_paras(args.new)
        print(f'  接受全部修订 / 新版段数 : {len(acc)} / {len(newp)}')
        if acc != newp:
            n = min(len(acc), len(newp))
            first = next((i for i in range(n) if acc[i] != newp[i]), n)
            fails.append(f'V4 接受全部修订后与新版不一致：首个差异段 #{first}（长度 {len(acc)} vs {len(newp)}）')
        else:
            print('  ✓ V4 接受全部修订 == 新版正文')

    # V5 拒绝全部修订 == 基线正文
    if args.base:
        rej = simulate_revisions(args.rev, 'reject')
        basep = docx_paras(args.base)
        print(f'  拒绝全部修订 / 基线段数 : {len(rej)} / {len(basep)}')
        if rej != basep:
            n = min(len(rej), len(basep))
            first = next((i for i in range(n) if rej[i] != basep[i]), n)
            fails.append(f'V5 拒绝全部修订后与基线不一致：首个差异段 #{first}（长度 {len(rej)} vs {len(basep)}）')
        else:
            print('  ✓ V5 拒绝全部修订 == 基线正文')

    # V7 docx 可打开
    try:
        Document(args.rev)
        print('  ✓ V7 docx 可正常打开')
    except Exception as e:  # noqa: BLE001
        fails.append(f'V7 docx 无法打开：{e}')

    # V8（可选）w:ins 英文序列 vs 参考稿
    if args.same_en_docx:
        ref = Document(args.same_en_docx)
        ref_en = [p.text.strip() for p in ref.paragraphs
                  if p.text.strip() and not CJK.search(p.text) and p.text.strip() not in cn_extra]
        ins_seq = [unescape(t).strip() for t in re.findall(r'<w:ins\b[^>]*>(.*?)</w:ins>', xml, re.S)
                   for t in re.findall(r'<w:t[^>]*>(.*?)</w:t>', t, re.S)
                   if unescape(t).strip() and not CJK.search(unescape(t)) and unescape(t).strip() not in cn_extra]
        print(f'  参考英文段 / 修订内英文段 : {len(ref_en)} / {len(ins_seq)}')
        if ref_en != ins_seq:
            fails.append('V8 插入英文序列与参考稿不一致')
        else:
            print('  ✓ V8 插入英文序列与参考稿逐条一致')

    print('-' * 62)
    if fails:
        print('  ✗ 未通过：')
        for f in fails:
            print('    - ' + f)
        sys.exit(1)
    print('  ✓ 全部断言通过')
    sys.exit(0)


if __name__ == '__main__':
    main()
