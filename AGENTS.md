# AGENTS.md — 项目引导（Antigravity 自动加载；其它平台兼容）

《月上柳梢头，人约黄昏后》中译英本地化（古装穿越 · 全书 351 章）。

## 开工顺序（新会话必读）
1. `_记忆索引.md` — 入口与文件指针
2. `.codebuddy/rules/project_rules.md` — 主源规则（通用 LAYER + 本地工程 LAYER）
3. `.codebuddy/rules/novel_rules.md` — 古装题材专项（异域保留分级）

> 以上 rules 已同步镜像至 `.trae/.qoder/.workbuddy/rules` 与 `.agent/rules`（同内容，勿手改单份）；改主源后跑
> `python tools/sync_rules.py --root . --master cb --targets .trae,.qoder,.workbuddy,.agent --apply`。
> （`.antigravity/` 已于 2026-09-07 清空移出：Antigravity 不自动读取该目录；本项目 Antigravity 入口 = 本文件 + `.agent/rules/`。）

## 红线速览（详见 rules）
- 中文原文零改动（有 MD5 基线可查证）；对照版中文与原文逐字一致（全角标点）。
- 对照版是唯一真源；`第X章译文.md` 是脚本派生物（`tools/sync_bilingual.py` 生成），禁手工编辑。
- 术语一个词条一个定译，终裁权在用户；禁止凭记忆断言一致性。
- 去 AI 痕迹、反 -ly 副词修饰动词；忠实原文 > 术语锁 > 跨章一致 > 表达自然。

## 记忆使用约定（降本 · 防噪声）
- 本工作区记忆系统按整个 `01_翻译业务` 注入，其中 **D&S 贸易单据 / 4PX 发货 / 三菱 CAD / 狼王·大叔剧本** 等条目与网文任务无关。
- 网文会话：**仅按需引用 novel 相关记忆**（中文零改动、反向护栏、门禁、术语终裁、交付形态等）；不要主动复述或加载无关子项目的记忆内容，避免凭空注入数千 token 噪声。
- 跨项目记忆属其他子项目，**不删不改**；仅当任务明确涉及对应子项目时才加载。

## 消息与回复
- 日常对话一律说人话（口语、直给要点、去报告腔）；请求含糊/多任务未编号/缺交付物 → 先回读成"任务卡片"或 ≤3 个澄清问题再执行（skill `prompt-sharpener`）；产出文件用结构化格式但文字直白、禁模板腔。

## 需要联网核查时
敏感内容 / 真实性 / 时效性 / 平台规范 / 查论文资料 → 用 skill **`web-verify`**（主源 `.codebuddy/skills/web-verify/`，五方+`.agent` 镜像）：内知先提假设 → 强制联网取 ≥2 独立来源 → 冲突标 `[待人工裁定]` → 记录落盘。**结论只作建议，不擅自改译文/术语。**

## 工具
`tools/`：project_status（进度基线）· sync_bilingual（译文生成/校验）· normalize_cn_punct（中文标点归一）· scan_halfwidth_zh（标点扫描）· sync_rules（平台规则同步）。
