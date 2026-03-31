[console]::OutputEncoding = [System.Text.Encoding]::UTF8
$knowledgeDir = ".agent\knowledge"
$termDir = "$knowledgeDir\terminology"
$charDir = "$knowledgeDir\characters"

# Clean slate
if (Test-Path $knowledgeDir) { Remove-Item -Path $knowledgeDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $termDir | Out-Null
New-Item -ItemType Directory -Force -Path $charDir | Out-Null

$chapters = Get-ChildItem -Path "章节原文" -Directory | Sort-Object { [int]($_.Name -replace '\D','') }

$termDict = @{}
$charDict = @{}
$challenges = @()

# ========== 角色双名别名映射表 ==========
# 将同一人物的多个称呼统一到一个主档案名下
$charAliasMap = @{
    '朱淑真'     = '千里寻'
    '赵朴'       = '申简辰'
}

function Get-CleanCharName {
    param([string]$rawName)
    # 1. 剥离括号后缀: 千里寻（女主）→ 千里寻
    $name = $rawName -replace '\(.*?\)|（.*?）', ''
    # 2. 剥离破折号后缀: 申简辰— 首次登场 → 申简辰 ; 二杠— 首次正式出场 → 二杠
    $name = $name -replace '[—\-]\s*.*$', ''
    # 3. 清理空白和特殊字符
    $name = $name.Trim() -replace '[\*"<>\\|/:\?]', '_'
    # 4. 处理斜杠/下划线分隔的双名: "千里寻 / 朱淑真" → 取第一个
    if ($name -match '^(.+?)\s*[/_]\s*(.+)$') {
        $firstName = $matches[1].Trim()
        $secondName = $matches[2].Trim()
        # 将第二个名字也加入别名映射
        if (-Not $charAliasMap.ContainsKey($secondName)) {
            $charAliasMap[$secondName] = $firstName
        }
        $name = $firstName
    }
    # 5. 查找别名映射，统一到主名
    if ($charAliasMap.ContainsKey($name)) {
        $name = $charAliasMap[$name]
    }
    return $name
}

function Test-IsTermDataRow {
    param([string]$line)
    # 严格检测：行必须以 | 开头,包含至少4列,且不是表头/分隔符
    if ($line -notmatch '^\s*\|') { return $false }
    # 排除分隔符行 |---|---|
    if ($line -match '^\s*\|[\s\-:]+\|') { return $false }
    # 排除表头行（包含"中文"或"建议英文"或"状态"或"备注"关键字）
    if ($line -match '中文|建议英文|状态|备注') { return $false }
    # 检测至少有4个管道符（4列 = 5个竖线）
    $pipeCount = ($line.ToCharArray() | Where-Object { $_ -eq '|' }).Count
    if ($pipeCount -lt 5) { return $false }
    return $true
}

foreach ($chap in $chapters) {
    if (-Not (Test-Path $chap.FullName)) { continue }
    $files = Get-ChildItem -Path $chap.FullName -Filter "*术语*.md"
    if ($files.Count -eq 0) { continue }
    $filePath = $files[0].FullName
    
    $lines = Get-Content $filePath -Encoding UTF8
    
    $currentSection = ""
    $currentSubCategory = ""
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        
        # 区块识别：宽松匹配，包容 AI 生成过程可能产生的随机空格、不同标点格式
        if ($line -match "^#+\s*.*术语") { $currentSection = "Term"; continue }
        if ($line -match "^#+\s*.*角色") { $currentSection = "Char"; continue }
        if ($line -match "^#+\s*.*挑战") { $currentSection = "Challenge"; continue }
        
        # 处理翻译挑战
        if ($currentSection -eq "Challenge") {
            if (-Not [string]::IsNullOrWhiteSpace($line) -and $line -notmatch "^##") {
                $challenges += "[来自 $($chap.Name)] $line"
            }
            continue
        }
        
        # 处理术语分类标题
        if ($currentSection -eq "Term" -and $line -match "^#+\s*([^#]+)") {
            $currentSubCategory = $matches[1].Trim()
            if (-Not $termDict.ContainsKey($currentSubCategory)) { $termDict[$currentSubCategory] = [ordered]@{} }
            continue
        }
        
        # 处理术语表格数据行（修复版正则：使用函数严格过滤，避免误匹配表头）
        if ($currentSection -eq "Term" -and (Test-IsTermDataRow $line)) {
            # 拆分管道符并提取列
            $cols = $line -split '\|' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
            if ($cols.Count -ge 3) {
                $cn = $cols[0]
                $en = $cols[1]
                $status = if ($cols.Count -ge 3) { $cols[2] } else { '' }
                $note = if ($cols.Count -ge 4) { $cols[3] } else { '' }
                
                if ([string]::IsNullOrWhiteSpace($currentSubCategory)) { $currentSubCategory = "未分类" }
                if (-Not $termDict.ContainsKey($currentSubCategory)) { $termDict[$currentSubCategory] = [ordered]@{} }
                
                if (-Not $termDict[$currentSubCategory].Contains($cn)) {
                    $termDict[$currentSubCategory][$cn] = "| $cn | $en | $status | [首次收录于$($chap.Name)] $note |"
                }
            }
        }
        
        # 处理角色人设
        if ($currentSection -eq "Char" -and $line -match "^#+\s*([^#]+)") {
            $rawName = $matches[1].Trim()
            $currentCharName = Get-CleanCharName $rawName
            
            if ([string]::IsNullOrWhiteSpace($currentCharName) -or $currentCharName -match "^---") { continue }
            if (-Not $charDict.ContainsKey($currentCharName)) { $charDict[$currentCharName] = @() }
            
            $charDesc = @()
            $j = $i + 1
            while ($j -lt $lines.Count -and $lines[$j] -notmatch "^#") {
                $charDesc += $lines[$j]
                $j++
            }
            $i = $j - 1
            $charDict[$currentCharName] += "`n#### 来自 $($chap.Name)`n" + ($charDesc -join "`n")
            continue
        }
    }
}

# === 写入翻译挑战 ===
$challengePath = Join-Path $knowledgeDir "translation_challenges.md"
"# 🎐 全书翻译挑战与诗词定场诗合集 (Translation Challenges)`n`n*(本项目精华翻译底版在此聚顶，请翻译诗词对仗时严厉遵从这里奠定的格式基调)*`n`n" | Out-File -FilePath $challengePath -Encoding UTF8
$challenges -join "`n" | Out-File -FilePath $challengePath -Append -Encoding UTF8

# === 写入术语切片文件 ===
$termFileCount = 0
$termEntryCount = 0
foreach ($category in $termDict.Keys) {
    if ($termDict[$category].Count -eq 0 -or $category -match "^---" -or [string]::IsNullOrWhiteSpace($category)) { continue }
    $catSafe = $category -replace '[\*"<>\\|\\/:\?]', '_'
    $outPath = Join-Path $termDir "$catSafe.md"
    
    "# 术语分类: $category`n`n| 中文 | 建议英文 | 状态 | 备注 |`n|---|---|---|---|`n" | Out-File -FilePath $outPath -Encoding UTF8
    foreach ($cn in $termDict[$category].Keys) {
        $termDict[$category][$cn] | Out-File -FilePath $outPath -Append -Encoding UTF8
        $termEntryCount++
    }
    $termFileCount++
}

# === 写入角色档案卡片 ===
$charFileCount = 0
foreach ($char in $charDict.Keys) {
    if ([string]::IsNullOrWhiteSpace($char) -or $char -match "^---") { continue }
    $outPath = Join-Path $charDir "$char.md"
    "# 角色专属档案: $char`n" | Out-File -FilePath $outPath -Encoding UTF8
    $charDict[$char] | Out-File -FilePath $outPath -Append -Encoding UTF8
    $charFileCount++
}

# === 写入主索引 ===
$indexPath = Join-Path $knowledgeDir "Knowledge_Index.md"
"# 📖 《月上柳梢头，人约黄昏后》全局知识库大纲向导 (Knowledge Index)`n`n" | Out-File -FilePath $indexPath -Encoding UTF8

"## 📚 术语类目切片库 (.agent/knowledge/terminology/)`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8
foreach ($category in $termDict.Keys) {
    if ($termDict[$category].Count -gt 0 -and $category -notmatch "^---" -and -Not [string]::IsNullOrWhiteSpace($category)) {
        "- **$category** (当前含 $($termDict[$category].Count) 个去重词条)`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8
    }
}

"`n## 🎭 已出场角色名册库 (.agent/knowledge/characters/)`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8
foreach ($char in $charDict.Keys) {
   if (-Not [string]::IsNullOrWhiteSpace($char) -and $char -notmatch "^---") {
       "- **$char**`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8
   }
}

"`n## 🎐 诗词与翻译难关库 (.agent/knowledge/translation_challenges.md)`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8
"- **当前已归纳 $( ($challenges | Measure-Object).Count ) 条核心文眼与翻译难点**`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8

"`n> **AI 工作指南**：本文件仅为架构总览。当你需要调用或提取具体人名/术语时，切忌肉眼查找！请调用原生工具 ``grep_search`` 在 ``.agent/knowledge`` 里执行正则检索对应人名/名词块即可！`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8

# === 打印统计摘要 ===
Write-Host ""
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "  知识库重构完毕 — 统计摘要" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "  术语切片文件: $termFileCount 个分类" -ForegroundColor Green
Write-Host "  术语总词条数: $termEntryCount 条 (去重后)" -ForegroundColor Green
Write-Host "  角色档案卡片: $charFileCount 个角色" -ForegroundColor Green
Write-Host "  翻译挑战条目: $( ($challenges | Measure-Object).Count ) 条" -ForegroundColor Green
Write-Host "  索引文件路径: $indexPath" -ForegroundColor Yellow
Write-Host "=============================" -ForegroundColor Cyan
