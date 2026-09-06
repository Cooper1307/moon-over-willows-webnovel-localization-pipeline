# AGENTS.md — 项目引导（Antigravity 自动加载；其它平台兼容）

《月上柳梢头，人约黄昏后》中译英本地化（古装穿越 · 全书 351 章）。

## 开工顺序（新会话必读）
1. `_记忆索引.md` — 入口与文件指针
2. `.codebuddy/rules/project_rules.md` — 主源规则（通用 LAYER + 本地工程 LAYER）
3. `.codebuddy/rules/novel_rules.md` — 古装题材专项（异域保留分级）

> 以上 rules 已同步镜像至 `.trae/.qoder/.antigravity/.workbuddy/rules`（同内容，勿手改单份）；改主源后跑
> `python tools/sync_rules.py --root . --master cb --apply`。

## 红线速览（详见 rules）
- 中文原文零改动（有 MD5 基线可查证）；对照版中文与原文逐字一致（全角标点）。
- 对照版是唯一真源；`第X章译文.md` 是脚本派生物（`tools/sync_bilingual.py` 生成），禁手工编辑。
- 术语一个词条一个定译，终裁权在用户；禁止凭记忆断言一致性。
- 去 AI 痕迹、反 -ly 副词修饰动词；忠实原文 > 术语锁 > 跨章一致 > 表达自然。

## 工具
`tools/`：project_status（进度基线）· sync_bilingual（译文生成/校验）· normalize_cn_punct（中文标点归一）· scan_halfwidth_zh（标点扫描）· sync_rules（平台规则同步）。
