# 多平台镜像策略（降本增效 · 镜像收敛）

> 生成：2026-11-08　依据：`tools/token_budget.py --mirrors` 实测

## 决策
- **唯一主源（source of truth）= `.codebuddy/`**（CodeBuddy 会话加载此份）。
- `.trae/` `.qoder/` `.workbuddy/` `.agent/` 为**冻结只读镜像**，本工作区不再主动 `sync_rules` 同步到这四份。
- **不删除**冻结镜像：保留跨平台能力与本地回滚。

## 实测体量（2026-11-08）
| 平台 | KB |
|---|---|
| .codebuddy | 92.9 |
| .trae | 92.9 |
| .qoder | 92.9 |
| .workbuddy | 136.6 |
| .agent | 613.5 |
| **合计** | **1028.9** |

收敛为单一主源后，可减去其余 4 份 ≈ **823 KB** 的存储与同步漂移面。

## 重要澄清（防误解）
- 多平台镜像**不计入每会话 token**：CodeBuddy 会话只加载 `.codebuddy/` 一份规则/技能/Agent；`.agent/` 的 `knowledge/translation_challenges.md`（99.45KB）等仅在 Antigravity 会话或显式调用技能时加载。
- 镜像收敛的真实收益是**存储下降 + 消除同步漂移 + 降低维护成本**，而非直接降每回合 token。直接降每会话 token 的杠杆是 glossary 切片（见 `顶层设计方案_降本增效与工程架构.md` 7.4）与 memory 按需标注。

## 何时重新同步
仅当用户明确在某一冻结平台（如 Trae / Qoder / WorkBuddy / Antigravity）上工作、且 `.codebuddy/` 已有规则/技能变更时，才运行：
```
python tools/sync_rules.py --root . --master cb --targets .trae,.qoder,.workbuddy,.agent --apply
```
日常网文任务一律只改 `.codebuddy/`。
