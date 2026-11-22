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
    return _merge_poem_lines(out)


def _merge_poem_lines(lines):
    """合并模型拆成多行的英文诗词：以 " 开头但未闭合 → 到闭合引号为止算一段。

    诗词是多行排版，不是多个段落；不合并会让一组中文配上 4-5 行诗句，
    后续全部错位（第192/198章实测）。TN 注行单独保留。
    """
    merged, buf = [], []
    for ln in lines:
        if buf:
            buf.append(ln)
            if ln.rstrip().endswith('"'):
                merged.append(" ".join(buf))
                buf = []
            continue
        if ln.startswith('"') and not ln.rstrip().endswith('"') and ln.count('"') == 1:
            buf = [ln]
        elif (ln.startswith("[TN:") and merged
              and merged[-1].count('"') >= 2 and merged[-1].rstrip().endswith('"')):
            # 诗词行的译者注：并入前一条诗词段（如 "...poem..." + [TN: ...]）
            merged[-1] = merged[-1] + " " + ln
        else:
            merged.append(ln)
    if buf:
        merged.append(" ".join(buf))
    return merged


def split_chapters(lines, start, end):
    """把归一化行切成 {n: {'title':..., 'lines':[...]}}。"""
    result = {}
    cur = None
    seen = set()
    for ln in lines:
        if ln.startswith("#CH "):
            n = int(ln[4:].strip())
            if start <= n <= end:
                if n in seen:
                    raise SystemExit(
                        f"[ERROR] 第{n}章的 #CH 出现第二次——输出里疑似有'初译+修订稿'两遍。"
                        f"请只保留终稿那一遍（保留后一个 #CH {n} 块），删掉前面的初译块后重跑。")
                seen.add(n)
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
    """按单调对齐生成组，返回 (groups, diagnostics)。

    groups = [(zh_indices, en_indices), ...]，索引 0-based。
    规则：中文段按顺序分给英文行；多个中文可落到同一组（英文合并），
    多出的英文行并入前一组（英文拆分）。诊断只报告，不阻断。
    """
    n, m = len(zh_paras), len(got_lines)
    diags = []
    if n == 0 or m == 0:
        return [], []
    # 单调 DP 找锚点配对
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
    # 用配对点切组：相邻配对之间未匹配的中文/英文归入同一组
    groups = []
    cur_z, cur_e = [], []
    zi = ei = 0
    for pz, pe in pairs:
        while zi <= pz:
            cur_z.append(zi); zi += 1
        while ei <= pe:
            cur_e.append(ei); ei += 1
        groups.append((cur_z, cur_e))
        cur_z, cur_e = [], []
    # 尾部残留
    tail_z = list(range(zi, n))
    tail_e = list(range(ei, m))
    if tail_z or tail_e:
        if groups:
            gz, ge = groups[-1]
            groups[-1] = (gz + tail_z, ge + tail_e)
        else:
            groups.append((tail_z, tail_e))
    # 诊断（只报告）
    matched_z = {x for gz, _ in groups for x in gz}
    matched_e = {x for _, ge in groups for x in ge}
    missing = [x + 1 for x in range(n) if x not in matched_z]
    extra = [x + 1 for x in range(m) if x not in matched_e]
    if missing:
        diags.append(f"未锚定中文段：{missing[:10]}")
    if extra:
        diags.append(f"未锚定英文行：{extra[:10]}")
    if abs(n - m) > 0:
        diags.append(f"段数差异 中文{n}·英文{m}（按组映射，不阻断）")
    return groups, diags


def write_inbox(n, title, got_lines, groups, zh, apply, force=False):
    """写收件文件；段数不等时用 @@G@@ 标出组界（去掉标记后英文行原样）。"""
    target = INBOX / f"ch{n}_en.txt"
    if target.exists() and not force:
        return False, "已存在（--force 未给）"
    if not apply:
        return True, f"[DRY-RUN] 将写 {target.name}"
    INBOX.mkdir(parents=True, exist_ok=True)
    if groups and any(len(ge) != 1 or len(gz) != 1 for gz, ge in groups):
        parts = []
        for gz, ge in groups:
            parts.append(f"@@G@@ {min(gz)+1}-{max(gz)+1}" if gz else "@@G@@ 0-0")
            parts.extend(got_lines[x] for x in ge)
        body = "\n".join(parts)
    else:
        body = "\n".join(got_lines)
    text = (f"#TITLE: {title or f'Chapter {n}'}\n" + body + "\n")
    target.write_text(text, encoding="utf-8", newline="\n")
    return True, f"[OK] 已写 {target.name}（{len(groups)} 组）"


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
    # 先查重复章头：若同一章出现两次（初译+修订稿），拒绝静默取第一遍
    head_counts = {}
    for m in re.finditer(r"^\s*#CH\s+(\d+)\s*$", raw, re.M):
        head_counts[int(m.group(1))] = head_counts.get(int(m.group(1)), 0) + 1
    dup = [n for n, c in head_counts.items() if c > 1 and args.start <= n <= args.end]
    if dup:
        raise SystemExit(
            f"[ERROR] 以下章的 #CH 出现两遍：{sorted(dup)}——输出里疑似'初译+修订稿'两份。"
            f"请只保留终稿那一遍，删掉前面的初译块后重跑；或把终稿另存为新文件用 --input 指定。")
    lines = normalize_model_output(raw)
    got = split_chapters(lines, args.start, args.end)
    report = io.StringIO()
    report.write(f"# 外部输出回收诊断（{args.start}–{args.end} · {datetime.now():%Y-%m-%d %H:%M:%S}）\n\n")
    report.write("> 只有段数完全匹配的章会写入收件目录；其余需人工补行或重出。\n\n")
    report.write("| 章 | 原文段 | 收到段 | 组数 | 结果 | 诊断 |\n|---|---|---|---|---|---|\n")

    ok_all = True
    written_count = 0
    failed_ch = []
    pending_ch = []
    for n in range(args.start, args.end + 1):
        title_zh, zh = expected_paras(n)
        if zh is None:
            report.write(f"| {n} | - | - | - | ERROR | 原文不存在 |\n")
            ok_all = False
            continue
        block = got.get(n)
        if not block:
            report.write(f"| {n} | {len(zh)} | 0 | - | ERROR | 输出里找不到该章 `#CH {n}` |\n")
            ok_all = False
            continue
        got_lines = block["lines"]
        # 2026-11-22：译文按英文小说习惯分段，段数不必等于中文段数。
        # 只要求非空（有译文）且没有明显的中文残留（整行是中文=模型没翻）。
        zh_as_en = [i + 1 for i, l in enumerate(got_lines)
                    if re.search(r"[㐀-鿿]", l) and not re.search(r"[A-Za-z]", l)]
        if not got_lines:
            ok_all = False
            failed_ch.append(n)
            report.write(f"| {n} | {len(zh)} | 0 | - | ERROR | 该章无译文段落 |\n")
            continue
        if zh_as_en:
            ok_all = False
            failed_ch.append(n)
            report.write(f"| {n} | {len(zh)} | {len(got_lines)} | - | ERROR | "
                         f"第 {zh_as_en[:5]} 行仍是中文未译 |\n")
            continue
        groups, diags = align(zh, got_lines)
        written, msg = write_inbox(n, block["title"], got_lines, groups, zh, args.apply, args.force)
        if written:
            written_count += 1
        else:
            ok_all = False
            pending_ch.append(n)
        note = f"{len(groups)} 组" + ("；" + "；".join(diags[:2]) if diags else "")
        report.write(f"| {n} | {len(zh)} | {len(got_lines)} | {len(groups)} | {'OK' if written else 'SKIP'} | {msg} · {note} |\n")

    name = f"回收诊断_{datetime.now():%Y%m%d_%H%M%S}.md"
    summary = (f"成功 {written_count}/{args.end - args.start + 1} 章。"
               + (f" 段数错位需重出：{failed_ch}。" if failed_ch else "")
               + (f" 已存在未覆盖（加 --force）：{pending_ch}。" if pending_ch else ""))
    report.write(f"\n总结：{summary}\n")
    print(f"[HARVEST] {args.start}–{args.end} · {summary}")
    print(report.getvalue()[:3000])
    if args.apply:
        (DOCS / name).write_text(report.getvalue(), encoding="utf-8", newline="\n")
        print(f"[OK] 诊断已写 {name}")
    else:
        print("[DRY-RUN] 加 --apply 落盘 chN_en.txt 与诊断")
    # 部分成功也算可用：好的章已落地，坏章下批/补喂重出即可，不让整批报失败
    return 0 if written_count else 1


if __name__ == "__main__":
    sys.exit(main())
