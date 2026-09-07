# `.antigravity/` — 不再使用（空壳说明）

**2026-09-07**：联网查证确认 Antigravity **不自动读取本目录**。官方规则入口是：
- 根 `AGENTS.md` / `GEMINI.md`（自动）
- 工作区补充规则目录 `.agent/rules/`（旧路径兼容）或 `.agents/rules/`（2.0 默认）

此前经 `sync_rules.py` 复制到此的 `rules/skills/memory/agents` 镜像**已清空**，且已从同步平台列表移除，不再写入。

**本项目 Antigravity 实际生效路径**：根 `AGENTS.md`（指针式）→ `.agent/rules/`（rules 镜像）。
**恢复方法**：旧内容仍在 git 历史（本目录曾被跟踪）；如需重建，运行
`python tools/sync_rules.py --root . --master cb --targets .antigravity --apply`（脚本已支持自定义目录名）。
