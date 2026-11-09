# -*- coding: utf-8 -*-
"""
scrub_docx_meta.py — docx 作者信息归一 + 最终编辑时间戳（按本机系统时间生成北京时间）

用户 2026-11-09 决策：
  - 最终交付文件的作者信息字段仅保留唯一笔名 CooperChen，自即日起生效，不受以往任何其他笔名影响；
  - 不得写入其他作者或协作者信息；
  - 文档最终编辑时间须以本机系统时间为基准自动生成为北京时间。

处理项：
  docProps/core.xml    dc:creator              -> CooperChen
                        cp:lastModifiedBy       -> CooperChen
                        dc:description          -> 「最后编辑时间：YYYY-MM-DD HH:MM:SS（北京时间 UTC+8）」
                        dcterms:created/modified-> 本机系统时间对应的 UTC 时刻（OOXML 规定存 UTC）
                        keywords/category/subject/version/contentStatus/identifier/language -> 清空
                        cp:revision             -> 1
  docProps/app.xml     Company/Manager         -> 清空
  word/document.xml    w:ins / w:del 的 w:author -> CooperChen（修订痕迹作者一并归一）
  文件系统 mtime                             -> 本机系统时间（Windows 默认即本地时区）

用法：
  python tools/scrub_docx_meta.py --dir 交付版 --apply
  python tools/scrub_docx_meta.py --file 交付版/第32章_译文.docx --apply
  python tools/scrub_docx_meta.py --dir docx交付 --author CooperChen --apply

默认 dry-run（只报告将改什么）；--apply 才落盘。
工程规范：仅标准库 + python-docx；CLI 只收 ASCII 参数；中文路径由 __file__ 推导。
"""
import os
import re
import sys
import glob
import shutil
import zipfile
import argparse
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding="utf-8")

try:
    from docx import Document
except ImportError:
    print("[ERR] 需要 python-docx：python -m pip install python-docx", file=sys.stderr)
    sys.exit(2)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BJ = timezone(timedelta(hours=8))  # 北京时间 UTC+8


def now_beijing():
    """本机系统时钟 → 北京时间。本机时区已确认为 China Standard Time(UTC+8)；
    这里显式按 UTC+8 换算，保证任何机器上都稳定产出北京时间。"""
    return datetime.now(timezone.utc).astimezone(BJ)


def _core_patch(core_xml, author, bj_dt):
    """在 docProps/core.xml 上做定向替换（不依赖 python-docx 的排序逻辑，最稳）。"""
    utc_str = bj_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    bj_str = bj_dt.strftime("%Y-%m-%d %H:%M:%S")
    desc = "最后编辑时间：%s（北京时间 UTC+8）" % bj_str

    def set_tag(xml, tag, value, attrs=None):
        """把 <tag .../> 替换为带指定属性的同标签（value 为 None 时删除该标签）。"""
        pat = re.compile(r"<%s\b[^>]*/>|<%s\b[^>]*>.*?</%s>" % (tag, tag, tag), re.S)

        def repl(m):
            if value is None:
                return ""
            extra = "".join(' %s="%s"' % (k, v) for k, v in (attrs or {}).items())
            return "<%s%s>%s</%s>" % (tag, extra, value, tag)

        if pat.search(xml):
            return pat.sub(repl, xml, count=1)
        if value is None:
            return xml
        inject = "<%s%s>%s</%s>" % (tag, "".join(' %s="%s"' % (k, v) for k, v in (attrs or {}).items()), value, tag)
        # 插到 </cp:coreProperties> 前
        return xml.replace("</cp:coreProperties>", inject + "</cp:coreProperties>")

    xml = core_xml
    xml = set_tag(xml, "dc:creator", author)
    xml = set_tag(xml, "cp:lastModifiedBy", author)
    xml = set_tag(xml, "dc:description", desc)
    xml = set_tag(xml, "dcterms:created", utc_str)
    xml = set_tag(xml, "dcterms:modified", utc_str)
    xml = set_tag(xml, "cp:revision", "1")
    for tag in ("cp:keywords", "cp:category", "dc:subject", "cp:version",
                "cp:contentStatus", "dc:identifier", "dc:language", "cp:lastPrinted"):
        xml = set_tag(xml, tag, None)
    return xml


def _app_patch(app_xml):
    """清空 Company / Manager 等机构性作者字段。"""
    xml = app_xml
    for tag in ("Company", "Manager"):
        xml = re.sub(r"<%s>.*?</%s>" % (tag, tag), "<%s></%s>" % (tag, tag), xml, flags=re.S)
        xml = re.sub(r"<%s/>" % tag, "<%s></%s>" % (tag, tag), xml)
    return xml


def _doc_patch(doc_xml, author):
    """把修订痕迹里的作者名统一为 author（只改 w:ins / w:del 的 w:author 属性）。"""
    def repl(m):
        # 分组：1=标签前缀，2=标签后缀（w:author 属性夹在两者之间）
        return m.group(1) + 'w:author="%s"' % author + m.group(2)

    return re.sub(r'(<w:(?:ins|del)\b[^>]*?)w:author="[^"]*"(.*?>)', repl, doc_xml)


def scrub_file(path, author="CooperChen", apply=False):
    """归一单个 docx 的作者信息与时间戳。返回 (ok, 摘要)。"""
    if not os.path.exists(path):
        return False, "文件不存在"
    bj_dt = now_beijing()
    utc_str = bj_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    bj_str = bj_dt.strftime("%Y-%m-%d %H:%M:%S")

    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if "word/document.xml" not in names or "docProps/core.xml" not in names:
                return False, "非有效 docx（缺 document.xml / core.xml）"
            data = {n: z.read(n) for n in names}
    except Exception as e:  # noqa: BLE001
        return False, "读取失败：%s" % e

    changed = []
    if "docProps/core.xml" in data:
        old = data["docProps/core.xml"].decode("utf-8")
        new = _core_patch(old, author, bj_dt)
        if new != old:
            changed.append("core.xml")
        data["docProps/core.xml"] = new.encode("utf-8")
    if "docProps/app.xml" in data:
        old = data["docProps/app.xml"].decode("utf-8")
        new = _app_patch(old)
        if new != old:
            changed.append("app.xml")
        data["docProps/app.xml"] = new.encode("utf-8")
    old_doc = data["word/document.xml"].decode("utf-8")
    new_doc = _doc_patch(old_doc, author)
    if new_doc != old_doc:
        changed.append("document.xml(修订作者)")
    data["word/document.xml"] = new_doc.encode("utf-8")

    summary = "作者=%s · 最后编辑=%s(UTC+8) · 修改[%s]" % (author, bj_str, ",".join(changed) or "无")
    if not apply:
        return True, "[dry-run] " + summary

    tmp = path + ".tmp_scrub"
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
            for n in data:  # 保持原有条目顺序
                zo.writestr(n, data[n])
        shutil.move(tmp, path)
    except Exception as e:  # noqa: BLE001
        if os.path.exists(tmp):
            os.remove(tmp)
        return False, "写回失败：%s" % e

    # 文件系统 mtime = 本机系统时间
    ts = bj_dt.timestamp()
    os.utime(path, (ts, ts))
    return True, summary


def main():
    ap = argparse.ArgumentParser(description="docx 作者信息归一 + 北京时间时间戳")
    ap.add_argument("--dir", help="目录（递归处理其中 .docx）")
    ap.add_argument("--file", help="单个 docx")
    ap.add_argument("--author", default="CooperChen", help="唯一作者笔名")
    ap.add_argument("--apply", action="store_true", help="真正写入（缺省 dry-run）")
    args = ap.parse_args()

    targets = []
    if args.file:
        targets = [args.file]
    elif args.dir:
        d = args.dir if os.path.isabs(args.dir) else os.path.join(REPO, args.dir)
        targets = sorted(glob.glob(os.path.join(d, "**", "*.docx"), recursive=True))
    else:
        raise SystemExit("use --dir <path> or --file <path> [--apply]")

    mode = "APPLY" if args.apply else "DRY-RUN"
    ok_n = fail_n = 0
    fails = []
    for t in targets:
        ok, msg = scrub_file(t, args.author, args.apply)
        if ok:
            ok_n += 1
        else:
            fail_n += 1
            fails.append("  %s : %s" % (os.path.basename(t), msg))
        if not args.dir:
            print(("OK " if ok else "ERR") + " " + msg)

    print("=== %s: OK %d · FAIL %d（共 %d 个）===" % (mode, ok_n, fail_n, len(targets)))
    for f in fails:
        print(f)
    if not args.apply:
        print("[提示] 加 --apply 才真正写入。")


if __name__ == "__main__":
    main()
