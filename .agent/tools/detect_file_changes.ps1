#Requires -Version 5.1
<#
.SYNOPSIS
    文件变更检测工具
.DESCRIPTION
    自动检测指定目录中的文件名变更，并与历史快照对比
.PARAMETER Action
    操作类型：snapshot（生成快照）、sync（检测变更并同步引用）、compare（仅对比不执行）
.PARAMETER Verbose
    显示详细检测过程
.EXAMPLE
    .\detect_file_changes.ps1 -Action snapshot
.EXAMPLE
    .\detect_file_changes.ps1 -Action sync
.EXAMPLE
    .\detect_file_changes.ps1 -Action compare
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("snapshot", "sync", "compare")]
    [string]$Action,
    
    [switch]$Verbose
)

# 设置项目根目录
$ProjectRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent | Split-Path -Parent
$ConfigFile = Join-Path $ProjectRoot ".agent\config\file_reference_config.json"
$SnapshotFile = Join-Path $ProjectRoot ".agent\cache\file_snapshot.json"
$SyncScript = Join-Path $PSScriptRoot "sync_file_references.ps1"

# 加载配置
function Load-Config {
    if (Test-Path $ConfigFile) {
        return Get-Content $ConfigFile -Encoding UTF8 | ConvertFrom-Json
    } else {
        Write-Host "错误: 配置文件不存在 $ConfigFile" -ForegroundColor Red
        exit 1
    }
}

# 生成文件快照
function New-Snapshot {
    param($Config)
    
    $snapshot = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        files = @()
    }
    
    foreach ($dir in $Config.watchDirectories) {
        $dirPath = Join-Path $ProjectRoot $dir
        if (Test-Path $dirPath) {
            foreach ($pattern in $Config.watchFileTypes) {
                $files = Get-ChildItem -Path $dirPath -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue
                
                foreach ($file in $files) {
                    # 检查是否被排除
                    $exclude = $false
                    foreach ($excludePattern in $Config.excludePatterns) {
                        if ($file.FullName -like "*$excludePattern*") {
                            $exclude = $true
                            break
                        }
                    }
                    
                    if (-not $exclude) {
                        $snapshot.files += @{
                            path = $file.FullName
                            name = $file.Name
                            nameNoExt = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                            lastWriteTime = $file.LastWriteTime.ToString("yyyy-MM-ddTHH:mm:ss")
                            size = $file.Length
                        }
                    }
                }
            }
        }
    }
    
    return $snapshot
}

# 对比快照
function Compare-Snapshots {
    param(
        $OldSnapshot,
        $NewSnapshot
    )
    
    $changes = @{
        added = @()
        removed = @()
        renamed = @()
        modified = @()
    }
    
    # 创建旧文件索引（按名称）
    $oldFilesByName = @{}
    foreach ($file in $OldSnapshot.files) {
        if (-not $oldFilesByName.ContainsKey($file.name)) {
            $oldFilesByName[$file.name] = @()
        }
        $oldFilesByName[$file.name] += $file
    }
    
    # 创建新文件索引（按名称）
    $newFilesByName = @{}
    foreach ($file in $NewSnapshot.files) {
        if (-not $newFilesByName.ContainsKey($file.name)) {
            $newFilesByName[$file.name] = @()
        }
        $newFilesByName[$file.name] += $file
    }
    
    # 查找新增和修改的文件
    foreach ($newFile in $NewSnapshot.files) {
        if (-not $oldFilesByName.ContainsKey($newFile.name)) {
            # 检查是否是重命名（通过文件大小和修改时间相似度判断）
            $potentialRename = $OldSnapshot.files | Where-Object {
                $_.size -eq $newFile.size -and 
                $_.name -ne $newFile.name -and
                -not ($newFilesByName.ContainsKey($_.name))
            }
            
            if ($potentialRename) {
                $changes.renamed += @{
                    oldName = $potentialRename[0].name
                    oldPath = $potentialRename[0].path
                    newName = $newFile.name
                    newPath = $newFile.path
                }
            } else {
                $changes.added += $newFile
            }
        } else {
            # 检查是否修改
            $oldFile = $oldFilesByName[$newFile.name] | Select-Object -First 1
            if ($oldFile.lastWriteTime -ne $newFile.lastWriteTime) {
                $changes.modified += $newFile
            }
        }
    }
    
    # 查找删除的文件
    foreach ($oldFile in $OldSnapshot.files) {
        if (-not $newFilesByName.ContainsKey($oldFile.name)) {
            # 检查是否已被标记为重命名
            $isRenamed = $changes.renamed | Where-Object { $_.oldName -eq $oldFile.name }
            if (-not $isRenamed) {
                $changes.removed += $oldFile
            }
        }
    }
    
    return $changes
}

# 显示变更信息
function Show-Changes {
    param($Changes)
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "文件变更检测结果" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    if ($Changes.added.Count -gt 0) {
        Write-Host "新增文件 ($($Changes.added.Count)):" -ForegroundColor Green
        foreach ($file in $Changes.added) {
            Write-Host "  + $($file.name)" -ForegroundColor Green
        }
        Write-Host ""
    }
    
    if ($Changes.removed.Count -gt 0) {
        Write-Host "删除文件 ($($Changes.removed.Count)):" -ForegroundColor Red
        foreach ($file in $Changes.removed) {
            Write-Host "  - $($file.name)" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    if ($Changes.renamed.Count -gt 0) {
        Write-Host "重命名文件 ($($Changes.renamed.Count)):" -ForegroundColor Yellow
        foreach ($rename in $Changes.renamed) {
            Write-Host "  ~ $($rename.oldName) → $($rename.newName)" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    
    if ($Changes.modified.Count -gt 0) {
        Write-Host "修改文件 ($($Changes.modified.Count)):" -ForegroundColor Blue
        foreach ($file in $Changes.modified) {
            Write-Host "  * $($file.name)" -ForegroundColor Blue
        }
        Write-Host ""
    }
    
    if ($Changes.added.Count -eq 0 -and $Changes.removed.Count -eq 0 -and 
        $Changes.renamed.Count -eq 0 -and $Changes.modified.Count -eq 0) {
        Write-Host "未检测到文件变更" -ForegroundColor Gray
    }
}

# 主程序
$config = Load-Config

switch ($Action) {
    "snapshot" {
        Write-Host "正在生成文件快照..." -ForegroundColor Cyan
        $snapshot = New-Snapshot -Config $config
        
        # 保存快照
        $snapshotDir = Split-Path $SnapshotFile -Parent
        if (-not (Test-Path $snapshotDir)) {
            New-Item -ItemType Directory -Path $snapshotDir -Force | Out-Null
        }
        
        $snapshot | ConvertTo-Json -Depth 10 | Set-Content $SnapshotFile -Encoding UTF8
        Write-Host "✅ 快照已保存到: $SnapshotFile" -ForegroundColor Green
        Write-Host "   文件总数: $($snapshot.files.Count)" -ForegroundColor Gray
    }
    
    "compare" {
        if (-not (Test-Path $SnapshotFile)) {
            Write-Host "错误: 快照文件不存在，请先运行 -Action snapshot" -ForegroundColor Red
            exit 1
        }
        
        $oldSnapshot = Get-Content $SnapshotFile -Encoding UTF8 | ConvertFrom-Json
        $newSnapshot = New-Snapshot -Config $config
        
        $changes = Compare-Snapshots -OldSnapshot $oldSnapshot -NewSnapshot $newSnapshot
        Show-Changes -Changes $changes
    }
    
    "sync" {
        if (-not (Test-Path $SnapshotFile)) {
            Write-Host "错误: 快照文件不存在，请先运行 -Action snapshot" -ForegroundColor Red
            exit 1
        }
        
        $oldSnapshot = Get-Content $SnapshotFile -Encoding UTF8 | ConvertFrom-Json
        $newSnapshot = New-Snapshot -Config $config
        
        $changes = Compare-Snapshots -OldSnapshot $oldSnapshot -NewSnapshot $newSnapshot
        Show-Changes -Changes $changes
        
        # 如果有重命名文件，调用同步脚本
        if ($changes.renamed.Count -gt 0) {
            Write-Host "`n检测到 $($changes.renamed.Count) 个文件重命名，开始同步引用..." -ForegroundColor Yellow
            
            foreach ($rename in $changes.renamed) {
                Write-Host "`n处理: $($rename.oldName) → $($rename.newName)" -ForegroundColor Cyan
                
                & $SyncScript -OldName $rename.oldName -NewName $rename.newName
            }
            
            # 更新快照
            $newSnapshot | ConvertTo-Json -Depth 10 | Set-Content $SnapshotFile -Encoding UTF8
            Write-Host "`n✅ 快照已更新" -ForegroundColor Green
        } else {
            Write-Host "`n无需同步引用" -ForegroundColor Gray
        }
    }
}
