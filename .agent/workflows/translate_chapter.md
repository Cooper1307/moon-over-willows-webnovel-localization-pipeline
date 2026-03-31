---
description: 单章翻译全流程，从原文到终稿的完整工作流
---

# 单章翻译工作流 (Translate Single Chapter)

## 前置条件
- 章节原文文件已存在于 `章节原文/第X章/第X章原文.md`
- 已阅读 `.agent/skills/translation_sop.md` 中的术语库和规范

## 工作流步骤

### 1. 读取原文
// turbo
- 读取 `章节原文/第X章/第X章原文.md`
- 确认章节编号和标题

### 2. 文本预分析
- 识别本章是否包含：
  - 古诗词 → 标记为 `[POEM]` 待人工重构
  - 打戏/动作戏 → 标记需要强化动词
  - 文化梗/字谜 → 标记需要 TN 注释
  - 角色首次登场 → 确认术语库中有对应翻译

### 3. AI 初译 (Draft Translation)
- 按照 `translation_sop.md` 中的 Prompt 模板翻译
- 每次输入不超过 1000 中文字
- 保持段落结构一致
- 输出到 `章节原文/第X章/第X章初译.md`

### 4. L1 双语精校 (Bilingual Post-Editing)
- 按照 L1 检查清单逐项审核
- 重点修复：代词错误、主语补全、动作描写、诗词重构
- 输出到 `章节原文/第X章/第X章L1校审.md`

### 5. L2 母语润色 (Native Polishing)
- 语调校准：强化女主的"爽感"与反差萌
- 句式重构：切短过长句子，加快阅读节奏
- 添加副词强化对话张力（sneered, murmured, retorted coldly）
- 输出到 `章节原文/第X章/第X章L2润色.md`

### 6. QA 质检
- 格式标准化检查（斜体、诗词排版、拟声词）
- 术语一致性扫描
- TN 注释完整性检查
- 输出终稿到 `章节原文/第X章/第X章终稿.md`

### 7. 更新项目日志
// turbo
- `"$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - 成功完成单章翻译：第X章" | Out-File -FilePath project_log.md -Append -Encoding UTF8`

## 输出文件命名规范

每章目录下最终包含：
```
第X章/
├── 第X章原文.md      # 中文原文
├── 第X章初译.md      # AI初译稿
├── 第X章L1校审.md    # L1双语精校稿
├── 第X章L2润色.md    # L2母语润色稿
└── 第X章终稿.md      # QA后终稿
```
