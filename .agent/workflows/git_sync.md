---
description: 同步本地修改到 GitHub 远程仓库的脚本流
---

# Git 同步对齐工作流 (Git Sync)

## 用法
您可以通过工作流命令执行代码同步，例如：`/git_sync "完善1-10章术语库与自动日志配置"`
如果不指定提交信息，系统会自动生成带有当前时间戳的提交信息。

## 前置条件
- Git 环境已经安装，且已经在本地执行过 `git init`。
- 已关联远程 GitHub 仓库：
  `git remote add origin https://github.com/Cooper1307/moon-over-willows-webnovel-localization-pipeline`。
- 具有对应的 Push 权限。

## 执行步骤

### 1. 暂存所有变更
将本地新文件及所有修改添加到暂存区。
// turbo
```powershell
git add .
```

### 2. 提交变更并自动处理提交信息
如果未提供提交说明（即执行了不带参数的命令），则默认使用时间戳记录。
// turbo
```powershell
$commitMsg = $args[0]
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Auto commit: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
}
git commit -m "$commitMsg"
```

### 3. 拉取远端更新
使用 rebase 模式拉取远端修改，避免无用的 merge 节点，保持提交历史干净。
// turbo
```powershell
git pull origin main --rebase
```
*(注：如果默认主分支为 master，命令将拉取失败，提示用户确认分支名。)*

### 4. 推送到远程
将本地合并完毕的版本推送到远程 GitHub 仓库。
// turbo
```powershell
git push origin main
```

### 5. 记录日志打点
利用 cmd 命令向统一的项目日志文件里添加同步追溯记录。
// turbo
```powershell
"$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - 本地文件已同步推送到远程 GitHub 仓库" | Out-File -FilePath project_log.md -Append -Encoding UTF8
```
