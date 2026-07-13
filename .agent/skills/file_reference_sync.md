---
name: 文件引用同步更新技能
description: 自动检测文件名变更并更新其他文件中的引用，支持批量处理和变更历史追溯
version: 1.0.0
---

# 文件引用同步更新技能 (File Reference Sync)

## 功能概述

本技能用于解决项目中文件名变更后，其他文件中引用未同步更新的问题。主要功能包括：

1. **自动检测文件名变更**：监控指定目录中的文件重命名操作
2. **智能引用识别**：在项目中搜索旧文件名的引用
3. **批量替换更新**：一次性更新所有文件中的引用
4. **变更预览确认**：在执行替换前展示变更清单
5. **历史记录追溯**：记录所有变更操作，支持回滚

## 使用场景

- 重命名日志文件后，更新 workflow 和 skill 中的引用
- 调整目录结构后，更新配置文件中的路径引用
- 批量重构文件名时，保持引用一致性

## 使用方法

### 方法 1：手动指定变更

当你知道旧文件名和新文件名时：

```powershell
# 同步单个文件引用
powershell -ExecutionPolicy Bypass -File .agent\tools\sync_file_references.ps1 -OldName "project_log_3_new.md" -NewName "项目日志_04_20260411-至今_翻译与工具整理.md"

# 批量同步多个文件
powershell -ExecutionPolicy Bypass -File .agent\tools\sync_file_references.ps1 -BatchFile "file_changes.json"
```

### 方法 2：自动检测变更

自动对比上次快照，检测文件名变更：

```powershell
# 生成当前快照（首次运行）
powershell -ExecutionPolicy Bypass -File .agent\tools\detect_file_changes.ps1 -Action snapshot

# 检测变更并同步引用
powershell -ExecutionPolicy Bypass -File .agent\tools\detect_file_changes.ps1 -Action sync
```

### 方法 3：交互式模式

```powershell
# 交互式选择要同步的变更
powershell -ExecutionPolicy Bypass -File .agent\tools\sync_file_references.ps1 -Interactive
```

## 配置文件

配置文件位于 `.agent\config\file_reference_config.json`：

```json
{
  "watchDirectories": [
    "章节原文",
    ".agent",
    "术语表",
    "归档"
  ],
  "watchFileTypes": [
    "*.md",
    "*.ps1",
    "*.py",
    "*.json"
  ],
  "excludePatterns": [
    "*.log",
    "node_modules",
    ".git",
    ".obsidian"
  ],
  "referencePatterns": [
    "{filename}",
    "{filename_noext}",
    "{filepath}"
  ],
  "historyFile": ".agent\\logs\\file_reference_history.json",
  "snapshotFile": ".agent\\cache\\file_snapshot.json",
  "backupEnabled": true,
  "backupDir": ".agent\\backups"
}
```

## 输出示例

### 变更预览

```
========================================
文件引用同步预览
========================================

检测到以下文件名变更：

1. project_log_3_new.md → 项目日志_04_20260411-至今_翻译与工具整理.md

将在以下文件中更新引用：

[1] .agent\skills\git_management.md
    行 21: ...记录到 `project_log_3_new.md` 之中。
    → ...记录到 `项目日志_04_20260411-至今_翻译与工具整理.md` 之中。

[2] .agent\workflows\git_sync.md
    行 51: ... -FilePath project_log_3_new.md -Append ...
    → ... -FilePath 项目日志_04_20260411-至今_翻译与工具整理.md -Append ...

[3] .agent\workflows\batch_translate.md
    行 48: ... -FilePath project_log_3_new.md -Append ...
    → ... -FilePath 项目日志_04_20260411-至今_翻译与工具整理.md -Append ...

[4] .agent\workflows\build_knowledge.md
    行 30: ... -FilePath project_log_3_new.md -Append ...
    → ... -FilePath 项目日志_04_20260411-至今_翻译与工具整理.md -Append ...

[5] .agent\workflows\split_chapters.md
    行 36: ... -FilePath project_log_3_new.md -Append ...
    → ... -FilePath 项目日志_04_20260411-至今_翻译与工具整理.md -Append ...

========================================
总计：5 个文件将被更新
========================================

是否执行更新？(Y/N):
```

### 执行结果

```
✅ 已更新: .agent\skills\git_management.md
✅ 已更新: .agent\workflows\git_sync.md
✅ 已更新: .agent\workflows\batch_translate.md
✅ 已更新: .agent\workflows\build_knowledge.md
✅ 已更新: .agent\workflows\split_chapters.md

变更历史已记录到: .agent\logs\file_reference_history.json
备份文件位于: .agent\backups\20260713_191500\
```

## 变更历史记录

历史记录格式（`.agent\logs\file_reference_history.json`）：

```json
{
  "changes": [
    {
      "timestamp": "2026-07-13T19:15:00",
      "oldName": "project_log_3_new.md",
      "newName": "项目日志_04_20260411-至今_翻译与工具整理.md",
      "affectedFiles": [
        {
          "path": ".agent\\skills\\git_management.md",
          "line": 21,
          "oldContent": "...project_log_3_new.md...",
          "newContent": "...项目日志_04_20260411-至今_翻译与工具整理.md..."
        }
      ],
      "backupPath": ".agent\\backups\\20260713_191500\\"
    }
  ]
}
```

## 回滚操作

如果需要撤销某次变更：

```powershell
# 查看历史记录
powershell -ExecutionPolicy Bypass -File .agent\tools\sync_file_references.ps1 -ShowHistory

# 回滚到指定时间点
powershell -ExecutionPolicy Bypass -File .agent\tools\sync_file_references.ps1 -Rollback "20260713_191500"
```

## 注意事项

1. **备份机制**：默认启用备份，所有修改前的文件都会保存到 `.agent\backups\` 目录
2. **编码保持**：替换时保持原文件编码（UTF-8/UTF-8 BOM/GBK）
3. **路径分隔符**：自动处理 Windows (`\`) 和 Unix (`/`) 路径分隔符
4. **特殊字符**：正确处理文件名中的中文、空格等特殊字符
5. **排除规则**：通过 `excludePatterns` 排除不需要扫描的目录和文件

## 集成到工作流

可以在其他工作流中调用此技能：

```powershell
# 在重命名工作流中调用
if ($fileRenamed) {
    & .agent\tools\sync_file_references.ps1 -OldName $oldName -NewName $newName -AutoConfirm
}
```

## 故障排查

### 问题：某些引用未被识别

**解决方案**：
- 检查 `referencePatterns` 配置是否包含你的引用格式
- 确认文件类型在 `watchFileTypes` 列表中
- 检查文件是否被 `excludePatterns` 排除

### 问题：替换后文件编码异常

**解决方案**：
- 检查原文件编码，确保系统支持该编码
- 在配置文件中指定 `encoding: "UTF-8"` 或 `encoding: "GBK"`

### 问题：路径引用未更新

**解决方案**：
- 在 `referencePatterns` 中添加 `{filepath}` 模式
- 使用 `-Verbose` 参数查看详细扫描过程
