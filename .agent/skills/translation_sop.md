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

本项目使用 **RAG（检索增强生成）** 架构。翻译前，AI 必须主动检索 `.agent/knowledge/` 目录以获取最新的术语和人设。

### 1.1 检索指令 (Search Directive)

> [!IMPORTANT]
> **翻译前必做**：调用 `grep_search` 在 `.agent/knowledge/` 中检索本章涉及的关键人名、官职或文化词汇。禁止在未检索的情况下自行发挥。

### 1.2 核心常驻角色 (Tier 1 Characters)

*以下为必须常驻上下文的核心人设，其余角色请通过检索获取。*

| 中文 | 英文 | 语调备注 |
|------|------|----------|
| 千里寻/朱淑真（女主） | Zhu Shuzhen / Qianli Xun | Sassy, modern, sarcastic |
| 申简辰/赵朴（男主） | Shen Jianchen / Prince Yi | Composed, authoritative, slightly possessive |
| 乔梦容（女配） | Qiao Mengrong | Meek, dramatic, overly formal |
| 苦荞（丫鬟） | Kuqiao | Loyal, simple, earnest |
| 林觉 | Lin Jue | Rough, blunt |
| 老娘 | Yours truly / This queen | 女主专属自称 |

### 1.2 官职与机构

| 中文 | 英文 |
|------|------|
| 司理院 | Judicial Department |
| 知府 | Prefect |
| 内侍 | Eunuch Attendant |
| 练兵官 | Drill Commander |

### 1.3 武学与动作

| 中文 | 英文 |
|------|------|
| 千里拳 | Qianli Fist |
| 千里拳庄 | Qianli Fist Manor |
| 幻影闪移 | Phantom Shift |

### 1.4 文化特色

| 中文 | 英文 | 备注 |
|------|------|------|
| 点茶 | Tea Whisking | 宋代特色 |
| 双头莲 | Twin-lotus | Symbol of eternal love |
| 元宵节 | Lantern Festival | |
| 千年神柳 | Millennial Divine Willow | 关键道具 |

---

## 二、角色语调档案 (Character Voice Profiles)

### 朱淑真/千里寻（女主）

* **人设**：现代网络作家穿越到宋代。性格火爆、直率、爱吐槽。

* **英文语调**：Sassy, modern, sarcastic
* **内心独白**：用 *斜体* 表示，语言更现代化
* **示例**：
  * ❌ "Dog official! I am not afraid of him!"
  * ✅ *"Corrupt bastard," she scoffed inwardly. "As if yours truly would ever be scared of the likes of him!"*

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
7. Preserve the "face-slapping" tension and pacing of web novel style.
8. Use dynamic action verbs for fight scenes (smash, evade, strike, pummel) instead of generic ones.
9. Add a [TN: ...] note for culturally specific references that Western readers may not understand.

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
* [ ] **动作连贯性**：打戏动词是否有打击感（非通用动词）
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
