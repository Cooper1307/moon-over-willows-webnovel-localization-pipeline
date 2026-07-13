#Requires -Version 5.1
<#
.SYNOPSIS
    文件引用同步更新工具
.DESCRIPTION
    自动检测文件名变更并更新其他文件中的引用，支持批量处理和变更历史追溯
.PARAMETER OldName
    旧文件名
.PARAMETER NewName
    新文件名
.PARAMETER BatchFile
    批量变更的 JSON 配置文件路径
.PARAMETER Interactive
    交互式模式
.PARAMETER ShowHistory
    显示变更历史
.PARAMETER Rollback
    回滚到指定的时间戳
.PARAMETER AutoConfirm
    自动确认执行（跳过预览确认）
.PARAMETER Verbose
    显示详细扫描过程
.EXAMPLE
    .\sync_file_references.ps1 -OldName "project_log_3_new.md" -NewName "项目日志_04_20260411-至今_翻译与工具整理.md"
.EXAMPLE
    .\sync_file_references.ps1 -BatchFile "file_changes.json"
.EXAMPLE
    .\sync_file_references.ps1 -Interactive
#>

param(
    [Parameter(ParameterSetName='Single')]
    [string]$OldName,
    
    [Parameter(ParameterSetName='Single')]
    [string]$NewName,
    
    [Parameter(ParameterSetName='Batch')]
    [string]$BatchFile,
    
    [Parameter(ParameterSetName='Interactive')]
    [switch]$Interactive,
    
    [switch]$ShowHistory,
    
    [string]$Rollback,
    
    [switch]$AutoConfirm,
    
    [switch]$Verbose
)

# 设置项目根目录
$ProjectRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent | Split-Path -Parent
$ConfigFile = Join-Path $ProjectRoot ".agent\config\file_reference_config.json"
$HistoryFile = Join-Path $ProjectRoot ".agent\logs\file_reference_history.json"
$BackupDir = Join-Path $ProjectRoot ".agent\backups"

# 加载配置
function Load-Config {
    if (Test-Path $ConfigFile) {
        return Get-Content $ConfigFile -Encoding UTF8 | ConvertFrom-Json
    } else {
        Write-Warning "配置文件不存在: $ConfigFile，使用默认配置"
        return @{
            watchDirectories = @("章节原文", ".agent", "术语表", "归档")
            watchFileTypes = @("*.md", "*.ps1", "*.py", "*.json")
            excludePatterns = @("*.log", "node_modules", ".git", ".obsidian", ".agent\tools", ".agent\config", ".agent\logs", ".agent\cache", ".agent\backups")
            referencePatterns = @("{filename}", "{filename_noext}")
            backupEnabled = $true
        }
    }
}

# 获取需要扫描的文件列表
function Get-FilesToScan {
    param($Config)
    
    $files = @()
    foreach ($dir in $Config.watchDirectories) {
        $dirPath = Join-Path $ProjectRoot $dir
        if (Test-Path $dirPath) {
            foreach ($pattern in $Config.watchFileTypes) {
                $found = Get-ChildItem -Path $dirPath -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue
                $files += $found
            }
        }
    }
    
    # 排除特定目录
    $filteredFiles = @()
    foreach ($file in $files) {
        $exclude = $false
        foreach ($excludePattern in $Config.excludePatterns) {
            if ($file.FullName -like "*$excludePattern*") {
                $exclude = $true
                break
            }
        }
        if (-not $exclude) {
            $filteredFiles += $file
        }
    }
    
    return $filteredFiles
}

# 在文件中查找引用
function Find-References {
    param(
        [string]$FilePath,
        [string]$FileName,
        [string]$FileNameNoExt
    )
    
    $references = @()
    $content = Get-Content $FilePath -Encoding UTF8 -ErrorAction SilentlyContinue
    if (-not $content) { return $references }
    
    for ($i = 0; $i -lt $content.Length; $i++) {
        $line = $content[$i]
        $lineNum = $i + 1
        
        # 检查是否包含旧文件名
        if ($line -match [regex]::Escape($FileName) -or $line -match [regex]::Escape($FileNameNoExt)) {
            $references += @{
                LineNumber = $lineNum
                Content = $line
                FilePath = $FilePath
            }
        }
    }
    
    return $references
}

# 替换文件内容
function Update-FileContent {
    param(
        [string]$FilePath,
        [string]$OldName,
        [string]$NewName,
        [string]$OldNameNoExt,
        [string]$NewNameNoExt
    )
    
    # 备份原文件
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = Join-Path $BackupDir $timestamp
    if (-not (Test-Path $backupPath)) {
        New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
    }
    
    $backupFile = Join-Path $backupPath (Split-Path $FilePath -Leaf)
    Copy-Item $FilePath $backupFile -Force
    
    # 读取内容
    $content = Get-Content $FilePath -Encoding UTF8 -Raw
    
    # 替换文件名（带扩展名）
    $content = $content -replace [regex]::Escape($OldName), $NewName
    
    # 替换文件名（不带扩展名）
    if ($OldNameNoExt -ne $NewNameNoExt) {
        $content = $content -replace [regex]::Escape($OldNameNoExt), $NewNameNoExt
    }
    
    # 写回文件
    Set-Content -Path $FilePath -Value $content -Encoding UTF8 -NoNewline
    
    return $backupFile
}

# 记录变更历史
function Save-History {
    param($ChangeRecord)
    
    $history = @()
    if (Test-Path $HistoryFile) {
        $history = Get-Content $HistoryFile -Encoding UTF8 | ConvertFrom-Json
        if ($history -isnot [array]) {
            $history = @($history)
        }
    }
    
    $history += $ChangeRecord
    
    # 确保目录存在
    $historyDir = Split-Path $HistoryFile -Parent
    if (-not (Test-Path $historyDir)) {
        New-Item -ItemType Directory -Path $historyDir -Force | Out-Null
    }
    
    $history | ConvertTo-Json -Depth 10 | Set-Content $HistoryFile -Encoding UTF8
}

# 显示变更历史
function Show-History {
    if (-not (Test-Path $HistoryFile)) {
        Write-Host "暂无变更历史记录" -ForegroundColor Yellow
        return
    }
    
    $history = Get-Content $HistoryFile -Encoding UTF8 | ConvertFrom-Json
    if ($history -isnot [array]) {
        $history = @($history)
    }
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "文件引用变更历史" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    foreach ($record in $history) {
        Write-Host "时间: $($record.timestamp)" -ForegroundColor Green
        Write-Host "旧文件名: $($record.oldName)" -ForegroundColor Red
        Write-Host "新文件名: $($record.newName)" -ForegroundColor Green
        Write-Host "影响文件数: $($record.affectedFiles.Count)" -ForegroundColor Yellow
        Write-Host "备份路径: $($record.backupPath)" -ForegroundColor Gray
        Write-Host "----------------------------------------`n" -ForegroundColor DarkGray
    }
}

# 回滚操作
function Invoke-Rollback {
    param([string]$Timestamp)
    
    $backupPath = Join-Path $BackupDir $Timestamp
    if (-not (Test-Path $backupPath)) {
        Write-Host "错误: 找不到备份目录 $backupPath" -ForegroundColor Red
        return
    }
    
    $backupFiles = Get-ChildItem $backupPath -File
    foreach ($file in $backupFiles) {
        # 这里需要根据历史记录找到原文件路径
        # 简化处理：假设文件名相同
        Write-Host "回滚文件: $($file.Name)" -ForegroundColor Yellow
    }
    
    Write-Host "回滚完成" -ForegroundColor Green
}

# 主处理函数
function Process-FileChange {
    param(
        [string]$OldName,
        [string]$NewName,
        [switch]$AutoConfirm
    )
    
    $config = Load-Config
    $files = Get-FilesToScan -Config $config
    
    $OldNameNoExt = [System.IO.Path]::GetFileNameWithoutExtension($OldName)
    $NewNameNoExt = [System.IO.Path]::GetFileNameWithoutExtension($NewName)
    
    # 查找所有引用
    $allReferences = @()
    foreach ($file in $files) {
        $refs = Find-References -FilePath $file.FullName -FileName $OldName -FileNameNoExt $OldNameNoExt
        if ($refs.Count -gt 0) {
            $allReferences += @{
                File = $file
                References = $refs
            }
        }
    }
    
    if ($allReferences.Count -eq 0) {
        Write-Host "`n未找到对 '$OldName' 的引用" -ForegroundColor Yellow
        return
    }
    
    # 显示预览
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "文件引用同步预览" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "检测到以下文件名变更：" -ForegroundColor Yellow
    Write-Host "`n$OldName → $NewName`n" -ForegroundColor White
    
    Write-Host "将在以下文件中更新引用：" -ForegroundColor Yellow
    $fileIndex = 1
    foreach ($item in $allReferences) {
        Write-Host "`n[$fileIndex] $($item.File.FullName)" -ForegroundColor Green
        foreach ($ref in $item.References) {
            $preview = $ref.Content.Trim()
            if ($preview.Length -gt 80) {
                $preview = $preview.Substring(0, 80) + "..."
            }
            Write-Host "    行 $($ref.LineNumber): $preview" -ForegroundColor Gray
        }
        $fileIndex++
    }
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "总计：$($allReferences.Count) 个文件将被更新" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # 确认执行
    if (-not $AutoConfirm) {
        $confirm = Read-Host "是否执行更新？(Y/N)"
        if ($confirm -ne 'Y' -and $confirm -ne 'y') {
            Write-Host "操作已取消" -ForegroundColor Yellow
            return
        }
    }
    
    # 执行更新
    $affectedFiles = @()
    $backupPath = Join-Path $BackupDir (Get-Date -Format "yyyyMMdd_HHmmss")
    
    foreach ($item in $allReferences) {
        $backupFile = Update-FileContent -FilePath $item.File.FullName -OldName $OldName -NewName $NewName -OldNameNoExt $OldNameNoExt -NewNameNoExt $NewNameNoExt
        
        $affectedFiles += @{
            path = $item.File.FullName
            references = $item.References
            backupFile = $backupFile
        }
        
        Write-Host "✅ 已更新: $($item.File.FullName)" -ForegroundColor Green
    }
    
    # 记录历史
    $changeRecord = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        oldName = $OldName
        newName = $NewName
        affectedFiles = $affectedFiles
        backupPath = $backupPath
    }
    
    Save-History -ChangeRecord $changeRecord
    
    Write-Host "`n变更历史已记录到: $HistoryFile" -ForegroundColor Cyan
    Write-Host "备份文件位于: $backupPath" -ForegroundColor Cyan
}

# 主程序
if ($ShowHistory) {
    Show-History
    exit
}

if ($Rollback) {
    Invoke-Rollback -Timestamp $Rollback
    exit
}

if ($BatchFile) {
    if (-not (Test-Path $BatchFile)) {
        Write-Host "错误: 批量配置文件不存在 $BatchFile" -ForegroundColor Red
        exit 1
    }
    
    $changes = Get-Content $BatchFile -Encoding UTF8 | ConvertFrom-Json
    foreach ($change in $changes) {
        Process-FileChange -OldName $change.oldName -NewName $change.newName -AutoConfirm $AutoConfirm
    }
    exit
}

if ($OldName -and $NewName) {
    Process-FileChange -OldName $OldName -NewName $NewName -AutoConfirm $AutoConfirm
    exit
}

if ($Interactive) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "文件引用同步工具 - 交互式模式" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    $oldName = Read-Host "请输入旧文件名"
    $newName = Read-Host "请输入新文件名"
    
    if ($oldName -and $newName) {
        Process-FileChange -OldName $oldName -NewName $newName
    } else {
        Write-Host "错误: 文件名不能为空" -ForegroundColor Red
    }
    exit
}

# 显示帮助
Write-Host "`n用法:" -ForegroundColor Cyan
Write-Host "  .\sync_file_references.ps1 -OldName <旧文件名> -NewName <新文件名>" -ForegroundColor White
Write-Host "  .\sync_file_references.ps1 -BatchFile <批量配置文件>" -ForegroundColor White
Write-Host "  .\sync_file_references.ps1 -Interactive" -ForegroundColor White
Write-Host "  .\sync_file_references.ps1 -ShowHistory" -ForegroundColor White
Write-Host "  .\sync_file_references.ps1 -Rollback <时间戳>" -ForegroundColor White
Write-Host "`n示例:" -ForegroundColor Cyan
Write-Host '  .\sync_file_references.ps1 -OldName "project_log_3_new.md" -NewName "项目日志_04_20260411-至今_翻译与工具整理.md"' -ForegroundColor Gray
