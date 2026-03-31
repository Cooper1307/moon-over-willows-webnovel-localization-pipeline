---
description: 提取术语及人设表格片段生成轻量级去重结构化知识库大纲
---

# 构建切片知识库工作流 (Build Knowledge Base)

## 用法
这是整个工程极为重要的架构升级环。每推进完若干新章节后，务必运行：`/build_knowledge`

## 执行步骤

### 1. 运行重构脚本
此操作利用 PowerShell 去重合并过去提取的所有 `.md` 表单，并将结果撕裂、分发到 `.agent/knowledge/` 系统的对应档案里。
// turbo
```powershell
powershell -ExecutionPolicy Bypass -File build_knowledge.ps1
```

### 2. 检查输出地图
确认全新的 Knowledge 层级索引正常更新：
// turbo
```powershell
Get-ChildItem -Path .agent\knowledge -File | Format-List Name,Length
```

### 3. 写日志
同步更新到总项目记事本：
// turbo
```powershell
cmd /c "echo %date% %time:~0,8% - 成功执行 [知识库切片解构与重组] 工作流，词条和人设已被智能去重和分流更新。 >> project_log.md"
```
