# 项目变更与操作日志

**项目远程仓库 (GitHub):**  
[https://github.com/Cooper1307/moon-over-willows-webnovel-localization-pipeline](https://github.com/Cooper1307/moon-over-willows-webnovel-localization-pipeline)

## 2026-03-31 12:31:09 初始构建与术语库预研阶段

- 初始化本地化翻译SOP和AI翻译策略。
- 创建单章翻译、批量翻译、拆分源文件的自动化Agent工作流（Workflow）。
- 结合AI处理《月上柳梢头，人约黄昏后》第1章至第10章原文，完成核心"术语库"（翻译字典）及"角色人设档案"提取。
- 确定项目远程仓库名为 `moon-over-willows-webnovel-localization-pipeline`，并确立仓库URL链接。
- 生成 `迁移prompt_术语提取任务.md` 以平滑过渡至 Trae IDE （由于工具切换）。
- 升级 Workflow 文件流程（导入 `cmd` 自动化日志模块），使得以后每次跑完工作流，都能自动追加带时间戳的记录到本日志文件。

---
## 2026-03-31 13:46:00 知识库 RAG 切片体系重构与全栈代码登云同步

- 废除单表纵向拼接逻辑，在根目录搭建 `.agent/knowledge` RAG 切片体系。
- 建立并执行第一代 `build_knowledge.ps1` 数据抽取清洗脚卷。
- 提取全书隐藏文眼，并将翻译挑战与原著古诗词汇编至 `translation_challenges.md`。
- 全面调整优化 `迁移prompt`，赋予 Agent 更宽容的查询能力与硬核严格的角色录入“思考链 (CoT)”锁定，消亡“同义双名”。
- 修复因 Cmd 双向命令行推送导致该本地 `project_log` 出现字节崩环（乱码并不可读）的严重错误。
- 本地所有修改（含本日志文件）已通过 `git_sync` 同步推送到远端 `master` 分支，目前系统已经准备完全并对后续提取流程高度可用。
