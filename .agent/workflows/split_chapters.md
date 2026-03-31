---
description: 将合并的源文件拆分为独立章节文件
---

# 章节拆分工作流 (Split Chapters)

## 用途
将 `归档/月上柳梢头，人约黄昏后.md`（合并的完整小说文件）拆分为351个独立章节文件。

## 前置条件
- 源文件存在于 `归档/月上柳梢头，人约黄昏后.md`
- 目标目录 `章节原文/` 已创建（可含空子目录）

## 执行步骤

### 1. 运行拆分脚本
// turbo
```powershell
powershell -ExecutionPolicy Bypass -File split_chapters.ps1
```
工作目录：项目根目录（`第二本小说/`）

### 2. 验证结果
// turbo
```powershell
$dirs = Get-ChildItem "章节原文" -Directory; $filled = 0; foreach ($d in $dirs) { if ((Get-ChildItem $d.FullName -File).Count -gt 0) { $filled++ } }; Write-Host "已填充章节: $filled / $($dirs.Count)"
```

### 3. 抽样检查
- 对比第1章、第100章、第351章的内容是否完整
- 确认章节标题行存在
- 确认无乱码

### 4. 记录拆分日志
// turbo
- `cmd /c "echo %date% %time% - 章节拆分工作流已执行完毕 >> project_log.md"`

## 注意事项
- 脚本会覆盖已有的章节文件
- 输出编码为 UTF-8（无BOM）
- 章节分隔依据正则 `第(\d+)章\s+`
