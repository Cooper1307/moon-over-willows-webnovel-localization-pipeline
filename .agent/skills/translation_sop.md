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

### 1.2 核心常驻角色 (Tier 1 Characters)

*以下为必须常驻上下文的核心人设，其余角色请通过检索获取。*

| 中文 | 英文 | 语调备注 |
|------|------|----------|
| 千里寻/朱淑真（女主） | Qianli Xun / Zhu Shuzhen | Sassy, modern, sarcastic, confrontational |
| 申简辰（男主） | Shen Jianchen | Composed, authoritative, slightly possessive |
| 二杠（徒弟） | Er'gang | Casual, blunt, secretly caring |
| 苦荞（丫鬟） | Kuqiao | Loyal, simple, earnest |
| 林觉（丈夫/反派） | Lin Jue | Rough, blunt, arrogant |
| 春金巧（青楼女配） | Chun Jinqiao | Dramatic, honeyed and affected voice |

### 1.3 核心称谓与自称

| 中文 | 英文 | 备注 |
|------|------|----------|
| 老娘 | Yours truly / This queen / *I* (emphasized) | 千里寻专属自称。愤怒回怼时用强调的*I*，自恋/戏谑时用This queen。 |
| 小姐 | Miss | 苦荞及下仆对未出阁或仍保留原生家庭尊称的女主的称呼，避免使用 My Lady。 |
| 姑爷 | Master Lin / the lord / Son-in-law | 苦荞对话直呼：Master Lin；内心独白：the lord。 |
| 师父 | Master / Shifu | 二杠对千里寻的称呼。 |

### 1.4 官职、机构与场所

| 中文 | 英文 | 备注 |
|------|------|------|
| 临安知府 | Prefect of Lin'an | 朱淑真父亲的官职 |
| 练兵官 | Military Training Officer | 林觉的军职 |
| 千里拳庄 | Qianli Fist Manor | 千里寻的武地 |
| 申拳流派 | Shen Fist (School) | 申简辰的门派 |
| 青楼 / 春香楼 | Qinglou / Chunxiang Pavilion | [TN: Qinglou, or pleasure quarters...] |

### 1.5 武学特色与核心道具

| 中文 | 英文 | 备注 |
|------|------|------|
| 千里拳 / 快拳 | Qianli Fist / Quick Fist / Rapid Strikes | 女主的武术与招数 |
| 拆拳术 | Counter-grapple technique | 男主的招数 |
| 千年神柳 | Millennial Divine Willow | 关键穿越道具 |

### 1.6 文化引语与金句

| 中文 | 英文 | 备注 |
|------|------|------|
| 词坛双璧 | Twin Jewels of Ci Poetry | 专指李清照与朱淑真，全局概念 |
| "月上柳梢头，人约黄昏后" | "The moon above a willow tree / Shone on my lover close to me." | 许渊冲译本，本书标题灵感 |

---

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
5. If you encounter a classical Chinese poem, translate it literally but poetically, and wrap it in a blockquote (> ) format.
6. Pay attention to pronouns (he/she), ensuring they match the character's gender contextually.
7. Preserve pacing by faithfully translating the source text's inherent rhythm and tone. Do NOT add dramatic flair, emotional amplifiers (e.g. sharply, furiously, dismissively), or actions not present in the original Chinese. The "face-slapping" effect must emerge from the source material itself, never from translation embellishment.
8. Add a [TN: ...] note for culturally specific references that Western readers may not understand.

[GLOSSARY]
{插入术语库}
```

---

## 四、分块策略 (Chunking Strategy)

* 每次喂给AI约 **1000中文字**（约一个场景）
* 按场景自然分段，不要在对话中间切断
* 切块时保留上一段的最后2-3句作为上下文

---

## 五、L1精校检查清单 (Bilingual Post-Editing Checklist)

* [ ] **代词纠错**：逐句核对 he/she/they 是否匹配正确角色
* [ ] **隐藏主语补全**：中文省略的主语在英文中必须补全
* [ ] **诗词重构**：AI翻译的诗词必须手动重写，附加 TN
* [ ] **术语一致性**：所有专有名词是否与术语库匹配
* [ ] **语调分层**：女主现代感 vs 古人典雅感是否分明

---

## 六、格式标准 (Formatting Standards)

* **心理描写**：统一用 *斜体*
* **诗词**：使用 `>` 块引用，居中排列
* **拟声词**：本地化为英语拟声词，斜体标识（*Bang! Thud!*）
* **译者注**：格式为 `[TN: 解释内容]`，放在相关段落后
* **章节标题**：保留中文章节号，附英文标题。格式：`## Chapter X: English Title`
