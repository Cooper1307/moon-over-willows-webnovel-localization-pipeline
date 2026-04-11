---
name: GitHub 远程代码与资产同步规范
description: 指导并规范如何与 GitHub 远程仓库保持一致，并提供出现冲突时的应对策略。
---

# GitHub 同步关联规范

## 1. 仓库基础数据
- **项目名称**: moon-over-willows-webnovel-localization-pipeline
- **远程 URL**: `https://github.com/Cooper1307/moon-over-willows-webnovel-localization-pipeline`
- **主要分支**: `master`

## 2. 提交与同步时机 (Sync Timing)
作为一套涉及长篇连载体量的辅助翻译工程，推荐按以下频率进行同步：
- 每次**批量章节处理完毕**时（例如每完成 10 章的提取或 10 章初译）。
- 每次**新增重要 Workflow** 或**重大规则 SOP 改动**时。
- 每次打算在多台设备（或向其他开发者/IDE）**迁移开发状态**前。

## 3. 标准化操作指引
1. 要执行一键式上传及同步，请直接调用现成的工作流：**`/git_sync "你要说的提交信息"`**。
2. 该工作流会自动走完 `add -> commit -> pull --rebase -> push` 链条，并写一条打点记录到 `project_log_3_new.md` 之中。

## 4. 异常处理：Git 冲突 (Merge Conflicts)
若是执行了 Workflow 但在 `pull --rebase` 环节抛出错导致拉取失败：
1. 立刻中止或避免后续强行 `git push` 的动作。
2. 运行 `git status` 查询出带有冲突标记 (both modified) 的清单。
3. 如果是在纯文本中存在冲突，打开对应的文件，搜寻 `<<<<<<<` 及 `======`、`>>>>>>>` 进行人工调和，并完成 `git rebase --continue`。
4. 在没搞清楚状态之前，**严禁**使用 `git push -f` 强推，以防冲毁他人的本地化翻译进度成果。
