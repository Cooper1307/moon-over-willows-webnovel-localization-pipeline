# split_chapters.ps1
# 将合并的源文件拆分为351个独立章节文件
# 用法: powershell -ExecutionPolicy Bypass -File split_chapters.ps1

$ErrorActionPreference = "Stop"
$sourceFile = "$PSScriptRoot\归档\月上柳梢头，人约黄昏后.md"
$outputBase = "$PSScriptRoot\章节原文"

Write-Host "=== 章节拆分脚本 ===" -ForegroundColor Cyan
Write-Host "源文件: $sourceFile"
Write-Host "输出目录: $outputBase"
Write-Host ""

# 读取完整文件内容
Write-Host "正在读取源文件..." -ForegroundColor Yellow
$content = [System.IO.File]::ReadAllText($sourceFile, [System.Text.Encoding]::UTF8)
Write-Host "文件大小: $($content.Length) 字符"

# 使用正则匹配所有章节标记位置
$pattern = '第(\d+)章'
$matches = [regex]::Matches($content, $pattern)
Write-Host "找到章节标记: $($matches.Count) 个" -ForegroundColor Green

if ($matches.Count -eq 0) {
    Write-Host "错误: 未找到任何章节标记！" -ForegroundColor Red
    exit 1
}

$successCount = 0
$errorCount = 0

for ($i = 0; $i -lt $matches.Count; $i++) {
    $match = $matches[$i]
    $chapterNum = $match.Groups[1].Value
    $startIndex = $match.Index

    # 确定章节结束位置（下一章开始处或文件末尾）
    if ($i -lt $matches.Count - 1) {
        $endIndex = $matches[$i + 1].Index
    } else {
        $endIndex = $content.Length
    }

    # 提取章节内容
    $chapterContent = $content.Substring($startIndex, $endIndex - $startIndex).Trim()

    # 在章节标题前加一个空行（与已有格式一致）
    $chapterContent = "`r`n" + $chapterContent + "`r`n"

    # 构建输出路径
    $chapterDir = Join-Path $outputBase "第${chapterNum}章"
    $chapterFile = Join-Path $chapterDir "第${chapterNum}章原文.md"

    # 确保目录存在
    if (-not (Test-Path $chapterDir)) {
        New-Item -ItemType Directory -Path $chapterDir -Force | Out-Null
    }

    # 写入文件
    try {
        [System.IO.File]::WriteAllText($chapterFile, $chapterContent, [System.Text.Encoding]::UTF8)
        $successCount++
        if ($successCount % 50 -eq 0 -or $i -eq $matches.Count - 1) {
            Write-Host "  已完成: $successCount / $($matches.Count)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  错误: 第${chapterNum}章写入失败 - $_" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Host "=== 拆分完成 ===" -ForegroundColor Cyan
Write-Host "成功: $successCount 章" -ForegroundColor Green
if ($errorCount -gt 0) {
    Write-Host "失败: $errorCount 章" -ForegroundColor Red
}
