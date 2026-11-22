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
   段落按英文小说习惯划分即可；中文分段只是内容参考，不要求一一对应。硬要求是内容不漏、不加、顺序不乱。
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
- **按英文小说的习惯分段**：中文原文的分段只是内容参考，不是段落模具。一段中文可以拆成两段英文（如对话从叙述里独立出来），几段中文也可以合成一段英文（如连续短对白）。以英语读者读起来顺为准。
- 但内容不能漏、不能加、顺序不能乱：每段英文都必须对应原文语义，所有中文内容都要出现在译文里。
- 章题只写在 `#TITLE:` 行，正文从第一段开始。
"""

OUTPUT_TEMPLATE_REVIEW = """#CH <章号>
锚点（该 [EN] 段前40字逐字复制） | P0/P1/P2 | 现状片段 | 建议改为 | 理由
锚点 | P1 | Qianlixun everywhere | Qianli Xun | 拼写漂移，与既定事实表冲突
（该章无问题则不写这个 #CH 块）
#CH <下一章号>
...

## 审校意见
一句话总评（这批整体质量如何）
中文原词 | 建议译法 | 理由
（没有术语建议就写"无"）

【格式铁律】
- 只出意见行，**绝不重写整章译文**。
- 锚点必须从 03_SOURCE/ALL_SOURCE.md 的 [EN] 段逐字复制前 40 字（手打会导致本地匹配失败）。
- 不要用代码围栏；不要输出两遍；每章的 #CH 只出现一次。
"""

SYSTEM_TXT = """你是宋代古装穿越小说《月上柳梢头，人约黄昏后》的中译英初译师。
输入是按 `#CH N` 分章的中文原文（每行一段）。逐章输出英文，**每行一段**，章间用 `#CH N` 分隔，每章首行 `#TITLE: <英文题名>`。
不要用代码围栏，不要给段落编号。**分段按英文小说习惯**：中文分段只是内容参考不是模具，可拆可合，以英语读者读起来顺为准；内容不漏不加、顺序不乱。末尾写「## 译法建议」（没有就写"无"）。
只输出一遍终稿：内部先初译再自审，把修正直接并入译文后一次性输出。不要先贴初译再贴修订稿，不要重发任何段落。

优先级：忠实原文 > 术语锁 > 跨章一致 > 表达自然。
风格：地道英文、手机阅读节奏、短句有画面感；角色音色分层（女主 modern/sassy、男主 composed/protective）。
异域保留：宋代朝代、都城、真实人名（Zhu Shuzhen 等）、词牌、官制、和离、银两全部保留；句法节奏彻底英语化，不做完全西化置换。
禁：把官家写成 King、嬷嬷写成 Nanny、银两写成 pounds、词牌写成 sonnet/ode；编造原文没有的史实（如"父母焚稿"）；给前 3 章额外加宋代背景或注释。
允许 -ly 词：really/perfectly/truly/entirely/miraculously；只禁"副词修饰动作动词"的弱填充。
"""

REVIEW_SYSTEM_TXT = """你是宋代古装穿越小说《月上柳梢头，人约黄昏后》中译英的资深审校。
输入是按 `#CH N` 分章的中英对照（`[ZH]` 中文段 / `[EN]` 英文段交替）。逐章审校，末尾输出「## 审校意见」汇总（没有问题就写"通过，无修改建议"）。
不重写整章译文，只输出需要修改的条目；没有实质问题就不提。
"""

REVIEW_PROMPT_TEMPLATE = """# 任务：审校 {count} 章中译英译文

你收到 {count} 章的**中英对照**（`03_SOURCE/ALL_SOURCE.md`，按 `#CH N` 分章；每段带 `[ZH] ` 或 `[EN] ` 前缀，交替排列；章号见 MANIFEST.json）。
逐章对照中文审校英文，输出**可落地的修改意见**。

## 一、审什么（按优先级）
1. **漏译/误译**：中文内容在英文里缺失、或意思翻反/翻错（逐组对照扫）。
2. **指代与施受**：代词指代是否对得上现场人物；施动者/受动者是否与中文一致。
3. **专名与术语**：人名拼写漂移（如 Qianlixun ≠ Qianli Xun）、称谓/官制/度量是否与 `02_CONTEXT.md` 一致。
4. **AI 痕迹**：delve/leverage/pivotal/myriad/tapestry/testament 等词；动词+-ly 弱填充副词（really/perfectly/truly/entirely/miraculously 允许）；em dash 过量。
5. **自然度**：读起来是否像英语母语小说；不顺的句子给改法。

## 二、反向护栏（不许犯）
- **不为改而改**：正确的表达哪怕朴素也是对的；只有真问题才提。
- **不判错正确的陌生表达**：拿不准的写"存疑"，别下结论。
- **不破坏锁定译名**：人名/称谓/官制/词牌按 `02_CONTEXT.md`；有异议只能以"译法建议"提出。
- **不以中文段落结构苛求英文**：英文分段按英文习惯，中英段数不等是正常现象，不算问题。
- 诗词的 `[TN: ...]` 译者注和字形解释（如 `(寻)`）是合法内容，不是污染。

## 三、输出格式（严格，机器回收）
每章以 `#CH <章号>` 单独一行开始。发现的问题逐条列出，每条一行：
`锚点 | 严重度 | 现状片段 | 建议改为 | 理由`
- 锚点 = 该 `[EN]` 段**前 40 字符逐字复制**（如 `The Dongfang family's dancers soon entered`），本地靠子串匹配定位。
- 严重度：P0 漏译误译 / P1 术语与拼写 / P2 表达优化。
- 「建议改为」只在确有改法时填；漏译类可填 `（补译：…要点…）`。
- 章内无问题就不写该章的 `#CH`。所有章审完写 `## 审校意见`：一句话总评 + 术语建议行 `中文 | 建议 | 理由`（没有写"无"）。
- 禁止重写整章译文；禁止输出两遍；禁止代码围栏；锚点必须逐字复制，手打会匹配失败。

## 四、自检
- [ ] 每条意见的锚点都是从 03_SOURCE 逐字复制的 `[EN]` 段前 40 字
- [ ] 严重度只用 P0/P1/P2
- [ ] 末尾有「## 审校意见」
- [ ] 全文只有一遍，无重复 `#CH`

附录：`00_RULES.md` · `01_GLOSSARY.md` · `02_CONTEXT.md` · `03_SOURCE/ALL_SOURCE.md`（中英对照）· `MANIFEST.json`。
AI Studio 用法：SYSTEM.txt 贴指令栏，PROMPT.md 贴对话框，上传 03_SOURCE/ALL_SOURCE.md。选 Gemini 4 Neon。
"""

PROMPT_TEMPLATE = """# 任务：把 {count} 章中文原文译成英文

你收到 {count} 章中文原文（`03_SOURCE/ALL_SOURCE.md`，按 `#CH N` 分章，每行一段；章号见 MANIFEST.json）。
为每一章输出英文译文：**每行一段**，段落按英文小说习惯划分。

## 一、输出格式（机器要自动切分，必须严格）
1. 每章以 `#CH <章号>` 单独一行开始，紧跟 `#TITLE: <英文题名>` 一行，之后每行一段英文。
2. 章与章之间只靠 `#CH` 分隔。**禁止**代码围栏（```）、`<PARA ...>` 锚点、`**Paragraph 3:**`/`P3.`/`3)` 之类编号标签、markdown 列表符号。
3. **分段规则（重要）**：不要照搬中文的段落切分。中文原文里一句话自成一段、或几段连续短对白，在英文里通常该合并成一段；反过来，中文的长段里如果换了说话人或场景，英文里该拆成两段。**按英语小说读者的阅读习惯分段**。唯一硬要求：内容不漏、不加、顺序不乱。
   ⚠ **本地校验器会逐章计算「英文段数 ÷ 中文段数」**：正常翻译在 0.5–1.0 之间（合并短对白会略小于 1）；**低于 0.35 的章会被判为摘要、整章退回重做**。长对话、长打斗、连续对白场景也必须逐场景译出，不许用一句话带过整页内容。
4. 每段英文里不要嵌入中文译文；但原文字形解释（如 `the character "Xun" (寻， meaning "to seek")`）和成对弯引号 `“ ”` 是合法内容，**禁止清除**。
5. 所有章输出完后写 `## 译法建议`，格式 `中文原词 | 你采用的英文 | 理由（一句话）`；没有就写"无"。
6. **只输出一遍终稿**：先在内部完成初译+自审，把修正直接并入上面的译文。
   **禁止**先贴一遍初译、再贴一遍修订稿——回收器会拒绝这种重复输出，必须只交终稿。
   若有审校说明，只在「## 译法建议」里用一行写结论，不要重发任何译文段落。

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
- 不要为了本地扫描脚本的历史句长/段长阈值改写——英文自然优先，但别为了凑阈值硬改内容。
- 角色音色靠语气区分：女主 sassy/modern、男主 composed/protective、女配 meek/dramatic。

## 五、输出前自检（逐条过一遍）
- [ ] 章数 = {count}，章号见 MANIFEST.json（每章的 `#CH N` 都要有）
- [ ] 每章英文段数合理（不要求等于中文段数；按英文习惯可拆可合）
- [ ] 无代码围栏、无段落编号、无 `#CH` 残留在正文
- [ ] 每章都有 `#TITLE:`
- [ ] 末尾有「## 译法建议」（哪怕写"无"）
- [ ] **全文只有一遍译文**（没有"初译/修订稿"两份，没有重复的 `#CH` 章头）
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
    ap.add_argument("--start", type=int, help="起始章号（与 --end 配合）")
    ap.add_argument("--end", type=int, help="结束章号（与 --start 配合）")
    ap.add_argument("--chapters", help="离散章号，如 110,124,132（与 --start/--end 二选一）")
    ap.add_argument("--context", help="已生成的上下文 md 路径（默认自动 build_context）")
    ap.add_argument("--tag", help="自定义批次标签（离散章时建议给，如 retry_101_150）")
    ap.add_argument("--mode", choices=["translate", "review"], default="translate",
                    help="translate=初译（默认，喂中文原文）；review=审校（喂中英对照，只出修改意见）")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if args.chapters:
        try:
            chapters = sorted({int(x.strip()) for x in args.chapters.split(",") if x.strip()})
        except ValueError:
            print("[ERROR] --chapters 只能是逗号分隔的数字")
            return 2
        if not chapters or any(n < 1 for n in chapters):
            print("[ERROR] --chapters 章号无效")
            return 2
        lo, hi = chapters[0], chapters[-1]
    else:
        if args.start is None or args.end is None:
            print("[ERROR] 请给 --start/--end 或 --chapters")
            return 2
        if args.start > args.end or args.start < 1:
            print("[ERROR] 章号区间无效")
            return 2
        chapters = list(range(args.start, args.end + 1))
        lo, hi = args.start, args.end
    tag = args.tag or f"batch_{lo:03d}_{hi:03d}"
    out_dir = PACKS / tag
    zip_path = PACKS / f"{tag}.zip"
    review_mode = args.mode == "review"

    # 原文/对照（逐字取自磁盘，零改动）
    sources = {}
    manifest_ch = []
    all_src = io.StringIO()
    if review_mode:
        # 审校模式：源 = 中英对照（[ZH]/[EN] 前缀逐段），来自对照版唯一真源
        import chapter_lib as _CL
        for n in chapters:
            ch_dir = BASE / "章节原文" / f"第{n}章"
            bi = _CL.parse_bilingual(ch_dir)
            if not bi["pairs"]:
                print(f"[ERROR] 第{n}章无对照版，审校模式要求译文已落地")
                return 2
            title_zh = nonempty_lines(ch_dir / f"第{n}章原文.md")[0]
            manifest_ch.append({"n": n, "expected_paras": len(bi["pairs"]),
                                "title_zh": title_zh, "mode": "review"})
            all_src.write(f"#CH {n}\n")
            for zh, en, _ln in bi["pairs"]:
                if zh:
                    for zl in zh.split("\n"):
                        if zl.strip():
                            all_src.write("[ZH] " + zl + "\n")
                if en:
                    for el in en.split("\n"):
                        if el.strip():
                            all_src.write("[EN] " + el + "\n")
            all_src.write("\n")
    else:
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
            context = build_context(hi)["text"]
    else:
        context = build_context(hi)["text"]

    chapter_desc = (f"{lo}–{hi} 章" if args.chapters is None
                    else f"以下 {len(chapters)} 章（章号见 MANIFEST.json）")
    if review_mode:
        prompt = REVIEW_PROMPT_TEMPLATE.format(count=len(chapters))
        system = REVIEW_SYSTEM_TXT
        out_template = OUTPUT_TEMPLATE_REVIEW
        out_per_para = 18  # 审校只出意见行，远小于全文翻译
    else:
        prompt = PROMPT_TEMPLATE.format(count=len(chapters), start=lo, end=hi,
                                        chapter_desc=chapter_desc)
        system = SYSTEM_TXT
        out_template = OUTPUT_TEMPLATE
        out_per_para = 34
    manifest = {
        "batch": tag,
        "mode": args.mode,
        "generated": datetime.now().isoformat(timespec="seconds") if hasattr(datetime, "isoformat") else datetime.now().isoformat,
        "chapters": manifest_ch,
        "counts": {"chapters": len(chapters), "paragraphs": sum(c["expected_paras"] for c in manifest_ch),
                   "glossary_total": gtotal, "glossary_locked": glocked, "glossary_suggest": gsuggest},
        "est_tok": {"input_rules": est_tok(rules), "input_glossary": est_tok(glossary),
                    "input_context": est_tok(context), "input_source": est_tok(all_src.getvalue()),
                    "output_estimate": sum(c["expected_paras"] * out_per_para for c in manifest_ch)},
        "note": "Gemini 4 Neon 网页端共用 1048576 tok 窗口（输入+思考+输出），用户已调大输出上限；"
                "总用量远低于上限，但单批超过 50 章时中间遗忘/段数错位风险上升，建议 40-50 章/批。",
    }
    manifest["generated"] = datetime.now().isoformat(timespec="seconds")

    files = {
        "PROMPT.md": prompt,
        "SYSTEM.txt": system,
        "00_RULES.md": rules,
        "01_GLOSSARY.md": glossary,
        "02_CONTEXT.md": context,
        "03_SOURCE/ALL_SOURCE.md": all_src.getvalue(),
        "04_OUTPUT_TEMPLATE.txt": out_template,
        "MANIFEST.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    }
    for n, lines in sources.items():
        files[f"03_SOURCE/ch{n}.txt"] = "\n".join(lines) + "\n"

    est = manifest["est_tok"]
    print(f"[PACK] {tag} · {len(chapters)} 章 · {manifest['counts']['paragraphs']} 段")
    print(f"  est_tok: 规则 {est['input_rules']} · 术语 {est['input_glossary']} · 上下文 {est['input_context']} "
          f"· 原文 {est['input_source']} · 输出约 {est['output_estimate']}")
    total_est = (est["input_rules"] + est["input_glossary"] + est["input_context"]
                 + est["input_source"] + est["output_estimate"])
    if total_est > 900000:
        print(f"  [WARN] 输入+输出估算 {total_est} tok，接近 1M 共用窗口 → 请缩小批次")
    if len(chapters) > 50:
        print(f"  [WARN] {len(chapters)} 章超过建议上限 50 → 中间遗忘/段数错位风险上升")
    print(f"  窗口用量估算 {total_est} / 1048576 tok（含思考余量）")
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
