#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_external.py — 外部 AI 输出 → run_batch 收件目录（chN_en.txt）

把外部模型吐回的一大段文本切章、清洗、按段对齐，只有段数完全匹配才写
`项目文档/待译英文行/chN_en.txt`。任何错位都出可操作诊断，不静默写盘。

用法（参数全 ASCII）：
  python tools/harvest_external.py --start 91 --end 95 --input 项目文档/回收/raw.txt
  python tools/harvest_external.py --start 91 --end 95 --input 项目文档/回收/raw.txt --apply
  python tools/harvest_external.py --start 91 --end 95 --clipboard

红线：只读回收文本与原文，只写 待译英文行/ 与回收诊断；不改真源、不跑门禁。
"""
import argparse
import difflib
import io
import re
import sys
from datetime import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
DOCS = BASE / "项目文档"
INBOX = DOCS / "待译英文行"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose_bilingual import nonempty_lines  # noqa: E402

# 章题行识别（CH 头 + 英文章题行均视为元信息）
CH_RE = re.compile(r"^\s*#CH\s+(\d+)\s*$", re.I)
CHAPTER_ALT_RE = re.compile(r"^\s*(?:#{1,4}\s*)?(?:Chapter|第)\s*(\d+)\s*(?:章)?\s*[:：.#\-—]?\s*(.*)$", re.I)
TITLE_RE = re.compile(r"^\s*#TITLE\s*[:：]\s*(.*)$", re.I)
SUGGEST_HEAD = re.compile(r"^\s*##\s*译法建议\s*$")
SUGGEST_LINE = re.compile(r"^\s*[^|]+\|[^|]+\|")

# 自造标签/编号（归一化时剥；但要保护英文段内嵌的合法括号中文）
FAKE_LABEL_RE = re.compile(
    r"^\s*(?:>\s*)?(?:\*\*)?(?:Paragraph|Para\.?|P|段|段落)?\s*(\d+)\s*(?:\*\*)?\s*[:：.)\]\-—]\s*", re.I)
LIST_PREFIX_RE = re.compile(r"^\s*(?:[-*•]\s+|>\s*)")

# 中文段里用于打分对齐的锚点：数字、全角引号内短语、glossary 首选词由调用方补
ANCHOR_NUM_RE = re.compile(r"\d+")


def expected_paras(n):
    p = BASE / "章节原文" / f"第{n}章" / f"第{n}章原文.md"
    if not p.is_file():
        return None, []
    lines = nonempty_lines(p)
    return (lines[0] if lines else ""), (lines[1:] if lines else [])


def strip_fences(lines):
    """去掉整块代码围栏行（``` / ~~~）。"""
    return [ln for ln in lines if not re.match(r"^\s*(```|~~~)", ln)]


def normalize_model_output(raw):
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = strip_fences(text.split("\n"))
    out = []
    for ln in lines:
        s = ln.rstrip()
        if not s.strip():
            continue
        if SUGGEST_HEAD.match(s):
            break  # 译法建议之后不是正文
        if CH_RE.match(s):
            m = CH_RE.match(s)
            out.append(f"#CH {int(m.group(1))}")
            continue
        if TITLE_RE.match(s):
            out.append(f"#TITLE: {TITLE_RE.match(s).group(1).strip()}")
            continue
        if SUGGEST_LINE.match(s):
            break
        if not out:
            continue  # 正文前的说明文字
        # 自造标签先剥编号，再剥列表符号
        s = FAKE_LABEL_RE.sub("", s)
        s = re.sub(r"^\*\*\s*", "", s)  # 剥标签后残留的开头 **
        s = LIST_PREFIX_RE.sub("", s)
        if s.strip():
            out.append(s.strip())
    return out


def split_chapters(lines, start, end):
    """把归一化行切成 {n: {'title':..., 'lines':[...]}}。"""
    result = {}
    cur = None
    for ln in lines:
        if ln.startswith("#CH "):
            n = int(ln[4:].strip())
            if start <= n <= end:
                cur = n
                result.setdefault(n, {"title": "", "lines": []})
            else:
                cur = None
            continue
        if cur is None:
            # 兼容无 #CH 的输出：用 ## Chapter N 识别
            m = CHAPTER_ALT_RE.match(ln)
            if m and start <= int(m.group(1)) <= end:
                cur = int(m.group(1))
                result.setdefault(cur, {"title": "", "lines": []})
            continue
        if ln.startswith("#TITLE:"):
            result[cur]["title"] = ln[len("#TITLE:"):].strip()
        else:
            result[cur]["lines"].append(ln)
    return result


def anchor_score(zh, en):
    """中文段 vs 英文行的粗略匹配分（共有数字 + ASCII 词重合的近似）。"""
    nums = set(ANCHOR_NUM_RE.findall(zh))
    en_nums = set(ANCHOR_NUM_RE.findall(en))
    score = len(nums & en_nums) * 3
    # 专有名词/括号中文：直接看中文里的 ASCII 串是否出现在英文行
    for token in re.findall(r"[A-Za-z][A-Za-z'\-]{2,}", zh):
        if token.lower() in en.lower():
            score += 1
    return score


def align(zh_paras, got_lines):
    """
    单调 DP 对齐：返回 (pairs, diagnostics)。
    pairs = [(zh_idx, en_idx)]，索引 0-based；诊断列出缺失/多余/疑似折行。
    """
    n, m = len(zh_paras), len(got_lines)
    if n == m:
        return [(i, i) for i in range(n)], []
    # LCS 风格 DP，带 anchor_score
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = anchor_score(zh_paras[i - 1], got_lines[j - 1])
            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1] + s + 1)
    pairs = []
    i, j = n, m
    while i > 0 and j > 0:
        s = anchor_score(zh_paras[i - 1], got_lines[j - 1])
        if dp[i][j] == dp[i - 1][j - 1] + s + 1:
            pairs.append((i - 1, j - 1)); i -= 1; j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    pairs.reverse()
    matched_zh = {p[0] for p in pairs}
    matched_en = {p[1] for p in pairs}
    diags = []
    missing = [i + 1 for i in range(n) if i not in matched_zh]
    extra = [j + 1 for j in range(m) if j not in matched_en]
    if missing:
        diags.append(f"缺译中文段号：{missing[:20]}" + ("…" if len(missing) > 20 else ""))
    if extra:
        diags.append(f"多余英文行号：{extra[:20]}" + ("…" if len(extra) > 20 else ""))
    # 疑似折行：相邻两行前者不以句末标点结尾、后者以小写开头
    merged = []
    for j in range(m - 1):
        if not re.search(r"[.!?。！？\"”']\s*$", got_lines[j]) and re.match(r"^[a-z]", got_lines[j + 1]):
            merged.append(j + 1)
    if merged:
        diags.append(f"疑似行内折行（英文行号）：{merged[:20]}")
    return pairs, diags


def write_inbox(n, title, lines, apply, force=False):
    target = INBOX / f"ch{n}_en.txt"
    if target.exists() and not force:
        return False, "已存在（--force 未给）"
    if not apply:
        return True, f"[DRY-RUN] 将写 {target.name}"
    INBOX.mkdir(parents=True, exist_ok=True)
    text = (f"#TITLE: {title or f'Chapter {n}'}\n" + "\n".join(lines) + "\n")
    target.write_text(text, encoding="utf-8", newline="\n")
    return True, f"[OK] 已写 {target.name}"


def read_clipboard():
    import subprocess
    r = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
                       capture_output=True, encoding="utf-8", errors="replace", timeout=30)
    if r.returncode != 0 or not r.stdout:
        raise SystemExit("[ERROR] 剪贴板读取失败；请先把输出保存为 UTF-8 文件再用 --input")
    return r.stdout


def main():
    ap = argparse.ArgumentParser(description="外部输出回收 → 待译英文行")
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="外部输出原始文本文件路径")
    src.add_argument("--clipboard", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true", help="允许覆盖已有 chN_en.txt")
    args = ap.parse_args()

    raw = read_clipboard() if args.clipboard else Path(args.input).read_text(encoding="utf-8-sig")
    lines = normalize_model_output(raw)
    got = split_chapters(lines, args.start, args.end)
    report = io.StringIO()
    report.write(f"# 外部输出回收诊断（{args.start}–{args.end} · {datetime.now():%Y-%m-%d %H:%M:%S}）\n\n")
    report.write("> 只有段数完全匹配的章会写入收件目录；其余需人工补行或重出。\n\n")
    report.write("| 章 | 原文段 | 收到段 | 结果 | 诊断 |\n|---|---|---|---|---|\n")

    ok_all = True
    for n in range(args.start, args.end + 1):
        title_zh, zh = expected_paras(n)
        if zh is None:
            report.write(f"| {n} | - | - | ERROR | 原文不存在 |\n")
            ok_all = False
            continue
        block = got.get(n)
        if not block:
            report.write(f"| {n} | {len(zh)} | 0 | ERROR | 输出里找不到该章 `#CH {n}` |\n")
            ok_all = False
            continue
        got_lines = block["lines"]
        pairs, diags = align(zh, got_lines)
        if len(got_lines) != len(zh):
            ok_all = False
            diag = "；".join(diags[:3]) if diags else "段数不等"
            report.write(f"| {n} | {len(zh)} | {len(got_lines)} | ERROR | {diag} |\n")
            # 前 3 段对照，方便人工定位
            for k in range(min(3, len(zh))):
                en = got_lines[k] if k < len(got_lines) else "（缺）"
                report.write(f"   - 段{k+1} 中：{zh[k][:70]}\n")
                report.write(f"     段{k+1} 英：{en[:70]}\n")
            continue
        written, msg = write_inbox(n, block["title"], got_lines, args.apply, args.force)
        if not written:
            ok_all = False
        report.write(f"| {n} | {len(zh)} | {len(got_lines)} | {'OK' if written else 'SKIP'} | {msg} |\n")

    name = f"回收诊断_{datetime.now():%Y%m%d_%H%M%S}.md"
    report.write(f"\n总结：{'全部章节可落地' if ok_all else '存在待处理章，见上表 ERROR 行'}。\n")
    print(f"[HARVEST] {args.start}–{args.end} · {'全部匹配' if ok_all else '有错位'}")
    print(report.getvalue()[:3000])
    if args.apply:
        (DOCS / name).write_text(report.getvalue(), encoding="utf-8", newline="\n")
        print(f"[OK] 诊断已写 {name}")
    else:
        print("[DRY-RUN] 加 --apply 落盘 chN_en.txt 与诊断")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
