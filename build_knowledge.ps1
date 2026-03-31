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
        
        # 补丁一：极其宽松的模糊匹配，包容 AI 生成过程可能产生的随机空格、不同标点格式
        if ($line -match "^#+\s*.*术语") { $currentSection = "Term"; continue }
        if ($line -match "^#+\s*.*角色") { $currentSection = "Char"; continue }
        if ($line -match "^#+\s*.*挑战") { $currentSection = "Challenge"; continue }
        
        # 处理翻译挑战
        if ($currentSection -eq "Challenge") {
            # 跳过仅含标题的内容或空行
            if (-Not [string]::IsNullOrWhiteSpace($line) -and $line -notmatch "^##") {
                $challenges += "[来自 $($chap.Name)] $line"
            }
            continue
        }
        
        # 处理术语分类
        if ($currentSection -eq "Term" -and $line -match "^#+\s*([^#]+)") {
            $currentSubCategory = $matches[1].Trim()
            if (-Not $termDict.ContainsKey($currentSubCategory)) { $termDict[$currentSubCategory] = [ordered]@{} }
            continue
        }
        
        # 处理角色人设
        if ($currentSection -eq "Char" -and $line -match "^#+\s*([^#]+)") {
            $rawName = $matches[1].Trim()
            # 补丁二：强行清洗角色异名。剔除角色名后面的 (仪王)、（备注） 等副标题以确保单一卡片绑定
            $cleanName = $rawName -replace '\(.*\)|（.*）', ''
            $currentCharName = $cleanName.Trim() -replace '[\*"<>\|\\/:\?]', '_' # Sanitize filename
            
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
        
        # 处理 Markdown Term 表格（带容错抓取，不强制开头紧贴管道符）
        if ($currentSection -eq "Term" -and $line -match "\|\s*(?!中文|---|状态)([^\|]+)\s*\|\s*([^\|]+)\s*\|\s*([^\|]+)\s*\|\s*([^\|]*)\s*\|") {
            $cn = $matches[1].Trim()
            $en = $matches[2].Trim()
            $status = $matches[3].Trim()
            $note = $matches[4].Trim()
            
            if (-Not $termDict[$currentSubCategory].ContainsKey($cn)) {
                $termDict[$currentSubCategory][$cn] = "| $cn | $en | $status | [首次收录于$($chap.Name)] $note |"
            }
        }
    }
}

# 写入翻译挑战 (全书最核心文化底子)
$challengePath = Join-Path $knowledgeDir "translation_challenges.md"
"# 🎐 全书翻译挑战与诗词定场诗合集 (Translation Challenges)`n`n*(本项目精华翻译底版在此聚顶，请翻译诗词对仗时严厉遵从这里奠定的格式基调)*`n`n" | Out-File -FilePath $challengePath -Encoding UTF8
$challenges -join "`n" | Out-File -FilePath $challengePath -Append -Encoding UTF8

# Write terminology files
foreach ($category in $termDict.Keys) {
    if ($termDict[$category].Count -eq 0 -or $category -match "---") { continue }
    $catSafe = $category -replace '[\*"<>\|\\/:\?]', '_'
    $outPath = Join-Path $termDir "$catSafe.md"
    
    "# 术语分类: $category`n`n| 中文 | 建议英文 | 状态 | 备注 |`n|---|---|---|---|`n" | Out-File -FilePath $outPath -Encoding UTF8
    foreach ($cn in $termDict[$category].Keys) {
        $termDict[$category][$cn] | Out-File -FilePath $outPath -Append -Encoding UTF8
    }
}

# Write character files
foreach ($char in $charDict.Keys) {
    if ([string]::IsNullOrWhiteSpace($char) -or $char -match "---") { continue }
    $outPath = Join-Path $charDir "$char.md"
    "# 角色专属档案: $char`n" | Out-File -FilePath $outPath -Encoding UTF8
    $charDict[$char] | Out-File -FilePath $outPath -Append -Encoding UTF8
}

# Write Master Index
$indexPath = Join-Path $knowledgeDir "Knowledge_Index.md"
"# 📖 《月上柳梢头，人约黄昏后》全局知识库大纲向导 (Knowledge Index)`n`n" | Out-File -FilePath $indexPath -Encoding UTF8

"## 📚 术语类目切片库 (.agent/knowledge/terminology/)`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8
foreach ($category in $termDict.Keys) {
    if ($termDict[$category].Count -gt 0 -and $category -notmatch "---") {
        "- **$category** (当前含 $($termDict[$category].Count) 个去重词条)`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8
    }
}

"`n## 🎭 已出场角色名册库 (.agent/knowledge/characters/)`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8
foreach ($char in $charDict.Keys) {
   if (-Not [string]::IsNullOrWhiteSpace($char) -and $char -notmatch "---") {
       "- **$char**`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8
   }
}

"`n## 🎐 诗词与翻译难关库 (.agent/knowledge/translation_challenges.md)`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8
"- **当前已归纳 $( ($challenges | Measure-Object).Count ) 条核心文眼与翻译难点**`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8

"`n> **AI 工作指南**：本文件仅为架构总览。当你需要调用或提取具体人名/术语时，切忌肉眼查找！请调用原生工具 `grep_search` 在 `.agent/knowledge` 里执行正则检索对应人名/名词块即可！`n" | Out-File -FilePath $indexPath -Append -Encoding UTF8

Write-Host "防弹级：结构化知识库提取与重切片完毕！地图索引路径: $indexPath"
