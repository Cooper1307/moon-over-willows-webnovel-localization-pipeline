---
name: translation_sop
description: 网文小说《月上柳梢头，人约黄昏后》中译英本地化翻译SOP技能
---

# 翻译SOP技能 (Translation Standard Operating Procedure)

本技能定义了网文小说中译英本地化翻译的完整标准操作规范，基于 AI-PE（AI辅助翻译+人工审校）模式。

---

## 环境声明 (Work Environment)

**本项目的本地化翻译工作流运行在 AI IDE 环境下（如 Antigravity / Trae ），请后续接手的 AI 智能体悉知：**

* **工具调用能力**：您具备直接读写项目文件、全局搜索、调用命令行的权限，应当主动管理 `.agent/knowledge` 下的术语库和角色库文件。
* **多轮次协作**：我们倡导**一个章节或一组特定任务开启一个新的对话 (New Chat/Session)**，以确保您的上下文窗口 (Context Window) 不被冗长的历史记录填满，保持最高水平的逻辑推理与记忆精度。

---

## 一、术语库规范 (Glossary & Knowledge Retrieval)

本项目使用 **RAG（检索增强生成）** 架构。翻译前，AI 必须主动按照**优先级**进行检索：优先检索当前章节文件夹下的术语和人设（如 `第X章术语与人设.md`），若无相关词条则退而检索全局的 `.agent/knowledge/` 目录。

### 1.1 检索指令 (Search Directive)

> [!IMPORTANT]
> **翻译前必做**：
>
> 1. **第一层级（本地优先）**：首先读取当前章节目录下的专属术语表（如 `章节原文/第X章/第X章术语与人设.md`）。
> 2. **第二层级（全局兜底）**：若某些关键人名、官职或文化词汇在本地未能完全覆盖，再调用 `grep_search` 在 `.agent/knowledge/` 中检索补充。禁止在未检索的情况下自行发挥。


## 二、角色语调档案 (Character Voice Profiles)

### 朱淑真/千里寻（女主）

* **人设**：现代网络作家穿越到宋代。性格火爆、直率、爱吐槽。

* **英文语调**：Sassy, modern, sarcastic
* **内心独白**：用 *斜体* 表示，语言更现代化
* **示例**（仅适用于女主情感高爆点时刻）：
  * ❌ "Dog official! I am not afraid of him!"
  * ✅ *"Corrupt bastard," she scoffed inwardly. "As if yours truly would ever be scared of the likes of him!"*

> ⚠️ **适用范围警告**：上述示例中的扩写风格**仅限**于原文情绪明确爆发的高光时刻。日常对话、动作描写及叙述句，必须保持与原文相同的粒度，严禁套用此种创意扩写模式。

### 申简辰（男主）

* **人设**：霸道总裁穿越成不受宠的皇子。隐忍、腹黑、深情。

* **英文语调**：Composed, authoritative, slightly possessive
* **示例**：语句简练有力，偶尔流露深情

### 乔梦容（女配）

* **人设**：古代传统白莲花/绿茶。

* **英文语调**：Meek, dramatic, overly formal
* **示例**：用词过于正式和戏剧化

---

## 三、AI Prompt 模板 (System Prompt Template)

翻译每个章节时，使用以下系统提示词：

```text
Act as an expert English translator specializing in Chinese web novels (Historical Romance / Transmigration genre).
Translate the following text into fluent, engaging English for a Western audience.

Rules:
1. Keep the female protagonist's (朱淑真/千里寻) inner thoughts and modern slang slightly modern, sassy, and sarcastic. Use *italics* for inner thoughts.
2. Keep the dialogue of ancient characters formal and elegant.
3. Strictly adhere to the provided Glossary. Do not create alternative translations for established terms.
4. Do not summarize. Translate line by line, preserving paragraph structure.
5. If you encounter a classical Chinese poem, FIRST search online for existing authoritative translations (e.g. by Xu Yuanchong, Burton Watson). If found, use it directly and credit via [TN: Translated by ...]. Only if no authoritative version exists, translate it poetically yourself and mark [TN: Translator's rendering]. Wrap all poems in blockquote (> ) format.
6. Pay attention to pronouns (he/she), ensuring they match the character's gender contextually.
7. Preserve pacing by faithfully translating the source text's inherent rhythm and tone. Do NOT add dramatic flair, emotional amplifiers (e.g. sharply, furiously, dismissively), or actions not present in the original Chinese. The "face-slapping" effect must emerge from the source material itself, never from translation embellishment.
8. Contextual Integration: Prioritize integrating cultural explanations naturally into the text. Only use [TN: ...] for highly specific concepts where contextual integration disrupts the flow.
9. Refactoring over Transliteration: Restructure sentences for natural English flow instead of mirroring literal Chinese clause structures (e.g. fix comma splices, insert subjects, employ active voice).
10. Dynamic Synonym Replacement: Vary vocabulary. Do not reuse the same translated verbs or adverbs for common repeated Chinese descriptors within a 100-line span.

[GLOSSARY]
{插入术语库}
```

---

## 四、分块策略 (Chunking Strategy)

* 每次喂给AI约 **1000中文字**（约一个场景）
* 按场景自然分段，不要在对话中间切断
* 切块时保留上一段的最后2-3句作为上下文

---

## 五、纯英译稿提取规程 (Pure English Extraction)

完成双语对照稿的 L1/L2 审校、QA 质检后，应提取纯英译稿作为最终交付文件。

* 从 `第X章终稿_对照.md`（或最新对照稿）中，**逐段剔除所有中文行**，仅保留英文翻译。
* 保留 Markdown 格式：斜体 `*...*`、诗词引用块 `>`、`[TN: ...]` 注释和段落分隔空行。
* **操作约束**：严禁将全章英文直接作为回复内容打印在对话框中。必须使用文件写入工具将结果直接写入文件 `第X章纯英译稿.md`。
* 写入完成后，仅输出一条简短的成功确认报告。

---

## 六、L1精校检查清单 (Bilingual Post-Editing Checklist)

* [ ] **代词纠错**：逐句核对 he/she/they 是否匹配正确角色
* [ ] **防重复机制 (Synonym Replacement)**：检测临近段落是否高频重复使用单一副助词或动词，确保词汇多样性。
* [ ] **句法重构 (Refactoring Syntax)**：检查长难句是否生硬直译，打破中式因果/状语结构，采用从句和自然英语语序重构。
* [ ] **内嵌式注释 (Contextual Integration)**：文化词汇优先采用内嵌自然语境的解说，减少冗余突兀的 `[TN:]`。
* [ ] **隐藏主语补全**：中文省略的主语在英文中必须补全
* [ ] **诗词重构**：AI翻译的诗词必须优先检索名家译本（许渊冲等），确认无名家版时方可手动重写，并附加 TN
* [ ] **术语一致性**：所有专有名词是否与术语库匹配
* [ ] **语调分层**：女主现代感 vs 古人典雅感是否分明

---

## 七、格式标准 (Formatting Standards)

* **心理描写**：统一用 *斜体*
* **诗词**：使用 `>` 块引用，居中排列
* **拟声词**：本地化为英语拟声词，斜体标识（*Bang! Thud!*）
* **译者注**：格式为 `[TN: 解释内容]`，放在相关段落后
* **章节标题**：保留中文章节号，附英文标题。格式：`## Chapter X: English Title`
