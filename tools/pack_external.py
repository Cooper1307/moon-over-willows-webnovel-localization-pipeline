#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pack_external.py — 生成给外部 AI Studio 的投喂包（目录 + zip）

一条命令产出一个批次的完整上下文：规则（只取 .codebuddy 的 UNIVERSAL 段）、
全量术语表（标"可推翻"）、滚动既定事实、中文原文（原文零改动）、
输出模板与 PROMPT/SYSTEM。默认 dry-run，--apply 落盘。

用法（参数全 ASCII；中文路径全由 __file__ 推导）：
  python tools/pack_external.py --start 91 --end 95
  python tools/pack_external.py --start 91 --end 95 --apply
  python tools/pack_external.py --start 91 --end 95 --context 项目文档/投喂上下文_第90章.md --apply

红线：只读原文/规则/术语/上下文，只写 项目文档/投喂包/；不改任何真源。
"""
import argparse
import io
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[1]
DOCS = BASE / "项目文档"
PACKS = DOCS / "投喂包"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import chapter_lib as L  # noqa: E402
from compose_bilingual import nonempty_lines  # noqa: E402
from glossary_slice import est_tok  # noqa: E402
from build_context import build_context  # noqa: E402


# ---------------------------------------------------------------- 文本块

RULES_PRELUDE = """【打包器消歧说明 · 必读】
1. 主规则"终裁权在用户"与"术语表仅供参考"两条**同时生效**：初译遇到术语表与更地道译法冲突，
   按"地道优先"处理并把候选回传，不得自行宣布术语表已修改，也不得机械替换。
2. 主规则里"≥40 词必拆 / 段长 ≤150"是本地扫描脚本的历史阈值，**本次初译不要求为凑阈值改写或拆段**。
   段落与原文严格 1:1 是更高优先级的要求。
3. 对外只暴露通用翻译规则；本地工程约定（路径、笔名、git、脚本）与本任务无关，已剥离。
"""

GLOSSARY_PRELUDE = """# 全量术语表（历史产物，可推翻）

本表收录 {n} 条历史词条，其中 {locked} 条标"锁定"、{suggest} 条标"[建议]"。
状态列反映的是脚本按出现频次自动升级的结果，**不是人工逐条裁定，也不是命令**。

使用方式：
1. 把本表当作"前人用过的说法参考"，不是必须执行的替换清单。
2. 若你判断另一个译法更贴合原文语境、更地道，**直接用你的译法**，不要为了对齐本表牺牲译文。
3. 用其它译法时，在本章输出末尾的「## 译法建议」里写一行：
   `中文原词 | 你采用的英文 | 理由（一句话）`
4. 优先级始终是：忠实原文 > 术语锁 > 跨章一致 > 表达自然。
   "可推翻"不等于"可以不顾原文"；专名/官制的既定写法见 02_CONTEXT.md。
5. 表内 `[建议]` 条目是未定候选，**不要自行选一个然后全书照抄**。

"""

OUTPUT_TEMPLATE = """#CH <章号>
#TITLE: <英文题名>
<第1段英文>
<第2段英文>
...
<最后一段英文>
#CH <下一章号>
#TITLE: <英文题名>
...

## 译法建议
中文原词 | 你采用的英文 | 理由（一句话）
（没有就写"无"）

【格式铁律】
- 每行一段，段与段之间不空行；不要给段落编号、不要加 **Paragraph N:** 之类标签。
- 不要用代码围栏（```）包住输出。
- 每段必须与 `03_SOURCE/ALL_SOURCE.md` 对应章的同序号中文段对齐，不合并、不拆分、不补写。
- 章题只写在 `#TITLE:` 行，正文从第一段开始。
"""

SYSTEM_TXT = """你是宋代古装穿越小说《月上柳梢头，人约黄昏后》的中译英初译师。
输入是按 `#CH N` 分章的中文原文（每行一段）。逐章输出英文，**每行一段**，章间用 `#CH N` 分隔，每章首行 `#TITLE: <英文题名>`。
不要用代码围栏，不要给段落编号，不要合并或拆分段落。末尾写「## 译法建议」（没有就写"无"）。

优先级：忠实原文 > 术语锁 > 跨章一致 > 表达自然。
风格：地道英文、手机阅读节奏、短句有画面感；角色音色分层（女主 modern/sassy、男主 composed/protective）。
异域保留：宋代朝代、都城、真实人名（Zhu Shuzhen 等）、词牌、官制、和离、银两全部保留；句法节奏彻底英语化，不做完全西化置换。
禁：把官家写成 King、嬷嬷写成 Nanny、银两写成 pounds、词牌写成 sonnet/ode；编造原文没有的史实（如"父母焚稿"）；给前 3 章额外加宋代背景或注释。
允许 -ly 词：really/perfectly/truly/entirely/miraculously；只禁"副词修饰动作动词"的弱填充。
"""

PROMPT_TEMPLATE = """# 任务：把 {count} 章中文原文逐段译成英文

你收到 {start}–{end} 章的中文原文（`03_SOURCE/ALL_SOURCE.md`，按 `#CH N` 分章，每行一段）。
为每一章输出一份**逐段英文**：每段一行，行数与中文段数严格相等。

## 一、输出格式（机器要自动切分，必须严格）
1. 每章以 `#CH <章号>` 单独一行开始，紧跟 `#TITLE: <英文题名>` 一行，之后每行一段英文。
2. 章与章之间只靠 `#CH` 分隔。**禁止**代码围栏（```）、`<PARA ...>` 锚点、`**Paragraph 3:**`/`P3.`/`3)` 之类编号标签、markdown 列表符号。
3. 段落与中文原文**严格 1:1**：不合并、不拆分、不补写、不漏译。中文段数见 `MANIFEST.json`。
4. 每段英文里不要嵌入中文译文；但原文字形解释（如 `the character "Xun" (寻， meaning "to seek")`）和成对弯引号 `“ ”` 是合法内容，**禁止清除**。
5. 所有章输出完后写 `## 译法建议`，格式 `中文原词 | 你采用的英文 | 理由（一句话）`；没有就写"无"。

## 二、翻译红线
- 优先级：**忠实原文 > 术语锁 > 跨章一致 > 表达自然**。
- 题材：宋代古装穿越，保留中国文化身份；句法节奏彻底英语化（这是网文，短句、口语、有画面感）。
- **不可西化**：朝代 the Song、都城 Lin'an、真实人名 Zhu Shuzhen/Qianli Xun/Qiao Wenxian/Kuqiao、词牌拼音、官制（官家=His Majesty、嬷嬷=Matron、郡主=Princess Jiahe）、和离（独立制度词，首现给 ≤12 词内嵌解释）、度量（taels of silver）全部保留。禁 King/Queen/Duke/Marquis 换官制，禁 pounds/dollars 换算，禁 sonnet/ode 换词牌。
- 剧情承重位：第73章艳词是角色当场现作、没写完、旁人后加标题；首现按原文场景译（醉酒后主动坐怀），转述允许自然变体。不许写成完整传世名词。
- **不许补史实**：全书原文没有"父母焚稿/焚毁/断肠集"，不得写进译文正文；翻译只翻原文已有的东西。
- 前 3 章不加宋代背景介绍或 TN 注（原文前 2 章本身就是现代网暴/都市）。
- 诗词遇 `[POEM]/[PUZZLE]` 标记 → 停机回报，不硬翻；其余诗词用权威译本并标 `[TN: Translated by …]`，自译标 `[TN: Translator's rendering]`。

## 三、术语表怎么用
`01_GLOSSARY.md` 是**全量历史术语表，整份可推翻**。状态列是脚本按频次自动升级的，不是命令。
更地道的译法直接用，并在「译法建议」回传。不要机械替换牺牲译文。
`02_CONTEXT.md` 是人工确认过的既定事实，**优先级高于术语表的 `[建议]` 状态，但低于忠实原文**。

## 四、写作标准
- 去 AI 痕迹：禁 delve/leverage/pivotal/myriad/tapestry/testament 等；em dash 不过量；三段式排比仅限原文刻意设计。
- `-ly` 只禁"副词修饰动作动词"的弱填充；`really/perfectly/truly/entirely/miraculously` 允许。
- 不要为了本地扫描脚本的历史句长/段长阈值改写或拆段——段落 1:1 更高优先。
- 角色音色靠语气区分：女主 sassy/modern、男主 composed/protective、女配 meek/dramatic。

## 五、输出前自检（逐条过一遍）
- [ ] 章数 = {count}，章号 {start}–{end} 全齐
- [ ] 每章英文段数 = MANIFEST 里该章 expected_paras
- [ ] 无代码围栏、无段落编号、无 `#CH` 残留在正文
- [ ] 每章都有 `#TITLE:`
- [ ] 末尾有「## 译法建议」（哪怕写"无"）
- [ ] 角色名拼写与 02_CONTEXT.md 完全一致，无变体

附录文件：`00_RULES.md`（规则）· `01_GLOSSARY.md`（术语）· `02_CONTEXT.md`（既定事实）· `03_SOURCE/ALL_SOURCE.md`（原文）· `04_OUTPUT_TEMPLATE.txt`（格式样例）· `MANIFEST.json`（段数）。
AI Studio 用法：把 `SYSTEM.txt` 全文贴进"指令/系统提示"栏，把 `PROMPT.md` 全文贴进对话框，上传/粘贴 `03_SOURCE/ALL_SOURCE.md` 与其余 md（或把几个文件依次贴进同一条消息）。选 Gemini 4 Neon，思考档位调中低、输出额度留足。
"""


def read_universal_rules():
    p = BASE / ".codebuddy" / "rules" / "project_rules.md"
    t = p.read_text(encoding="utf-8-sig")
    m = re.search(r"<!--\s*LAYER:UNIVERSAL_START\s*-->(.*?)<!--\s*LAYER:UNIVERSAL_END\s*-->", t, re.S)
    if not m:
        raise SystemExit("[ERROR] project_rules.md 找不到 UNIVERSAL 层标记")
    universal = m.group(1).strip()
    novel = (BASE / ".codebuddy" / "rules" / "novel_rules.md").read_text(encoding="utf-8-sig").strip()
    # -ly 正反例：唯一完整清单在 .workbuddy/memory/MEMORY.md，只提取那几行
    mem = BASE / ".workbuddy" / "memory" / "MEMORY.md"
    ly_lines = []
    if mem.is_file():
        for ln in mem.read_text(encoding="utf-8-sig").splitlines():
            if re.search(r"-ly|finally came|blooming defiantly|rarely saw|immediately bowed|bitterly cold|barely containing|允许", ln):
                ly_lines.append(ln.strip())
    out = ["# 通用规则（可投喂外部）", "", RULES_PRELUDE, universal, "", "---", "", novel]
    if ly_lines:
        out += ["", "## 附：-ly 副词正反例（用户规则，与本地旧扫描器实现不一致，以本节为准）", ""]
        out += ly_lines
    return "\n".join(out) + "\n"


def build_glossary():
    entries = L.load_glossary()
    locked = sum(1 for e in entries if e.get("status") == L.STATUS_LOCKED)
    suggest = sum(1 for e in entries if e.get("status") == L.STATUS_SUGGEST)
    out = io.StringIO()
    out.write(GLOSSARY_PRELUDE.format(n=len(entries), locked=locked, suggest=suggest))
    out.write("| 中文 | 英文 | 状态 | 首现章 |\n|---|---|---|---|\n")
    for e in entries:
        cn = str(e.get("cn", "")).replace("|", "\\|")
        en = str(e.get("en", "")).replace("|", "\\|")
        out.write(f"| {cn} | {en} | {e.get('status','')} | {e.get('first','')} |\n")
    return out.getvalue(), len(entries), locked, suggest


def main():
    ap = argparse.ArgumentParser(description="打包外部 AI Studio 投喂包")
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True)
    ap.add_argument("--context", help="已生成的上下文 md 路径（默认自动 build_context）")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if args.start > args.end or args.start < 1:
        print("[ERROR] 章号区间无效")
        return 2
    chapters = list(range(args.start, args.end + 1))
    tag = f"batch_{args.start:03d}_{args.end:03d}"
    out_dir = PACKS / tag
    zip_path = PACKS / f"{tag}.zip"

    # 原文（逐字取自磁盘，零改动）
    sources = {}
    manifest_ch = []
    all_src = io.StringIO()
    for n in chapters:
        p = BASE / "章节原文" / f"第{n}章" / f"第{n}章原文.md"
        if not p.is_file():
            print(f"[ERROR] 第{n}章原文不存在")
            return 2
        lines = nonempty_lines(p)
        if not lines:
            print(f"[ERROR] 第{n}章原文为空")
            return 2
        title_zh, paras = lines[0], lines[1:]
        sources[n] = lines
        manifest_ch.append({"n": n, "expected_paras": len(paras), "title_zh": title_zh})
        all_src.write(f"#CH {n}\n")
        for para in paras:
            all_src.write(para + "\n")
        all_src.write("\n")

    rules = read_universal_rules()
    glossary, gtotal, glocked, gsuggest = build_glossary()
    if args.context:
        ctx = Path(args.context)
        context = ctx.read_text(encoding="utf-8-sig") if ctx.is_file() else ""
        if not context:
            print(f"[WARN] 指定上下文 {args.context} 不存在，自动生成")
            context = build_context(args.end)["text"]
    else:
        context = build_context(args.end)["text"]

    prompt = PROMPT_TEMPLATE.format(count=len(chapters), start=args.start, end=args.end)
    manifest = {
        "batch": tag,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "chapters": manifest_ch,
        "counts": {"chapters": len(chapters), "paragraphs": sum(c["expected_paras"] for c in manifest_ch),
                   "glossary_total": gtotal, "glossary_locked": glocked, "glossary_suggest": gsuggest},
        "est_tok": {"input_rules": est_tok(rules), "input_glossary": est_tok(glossary),
                    "input_context": est_tok(context), "input_source": est_tok(all_src.getvalue()),
                    "output_estimate": sum(c["expected_paras"] * 34 for c in manifest_ch)},
        "note": "Gemini 4 Neon 单次输出硬顶 65536 tok（思考+输出共用）；如 output_estimate 超过 60000 请缩小批次。",
    }

    files = {
        "PROMPT.md": prompt,
        "SYSTEM.txt": SYSTEM_TXT,
        "00_RULES.md": rules,
        "01_GLOSSARY.md": glossary,
        "02_CONTEXT.md": context,
        "03_SOURCE/ALL_SOURCE.md": all_src.getvalue(),
        "04_OUTPUT_TEMPLATE.txt": OUTPUT_TEMPLATE,
        "MANIFEST.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    }
    for n, lines in sources.items():
        files[f"03_SOURCE/ch{n}.txt"] = "\n".join(lines) + "\n"

    est = manifest["est_tok"]
    print(f"[PACK] {tag} · {len(chapters)} 章 · {manifest['counts']['paragraphs']} 段")
    print(f"  est_tok: 规则 {est['input_rules']} · 术语 {est['input_glossary']} · 上下文 {est['input_context']} "
          f"· 原文 {est['input_source']} · 输出约 {est['output_estimate']}")
    if est["output_estimate"] > 60000:
        print("  [WARN] 输出估算超过 60000 tok，网页端可能被截断 → 建议缩小批次")
    print(f"  将生成 {len(files)} 个文件于 {out_dir.relative_to(BASE)} 与 {zip_path.relative_to(BASE)}")

    if not args.apply:
        print("[DRY-RUN] 加 --apply 落盘")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    PACKS.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        fp = out_dir / rel
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(text, encoding="utf-8", newline="\n")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in files:
            zf.write(out_dir / rel, rel)
    print(f"[OK] 已写投喂包目录与 zip：{zip_path.relative_to(BASE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
