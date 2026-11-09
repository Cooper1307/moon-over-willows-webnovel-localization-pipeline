---
description: docx 交付与修订模式工作流（3 决策落地）：对照=核验、译文=交付、修订痕迹=审阅版
---

# docx 交付与修订模式工作流 (Docx Delivery & Track-Changes)

> 2026-11-08 用户三条决策落地版。**产物分层 + 复用 MTPE 修订引擎**。
> 决策：①最终只交译文，对照版留给用户核验，后续修订直接体现在 docx；
> ②修订模式模仿 MS Office/WPS，产出带真实 `w:ins`/`w:del` 修订痕迹的审阅版；
> ③全量提交 GitHub，产出交接指令供新对话续干。

## 一、真源与产物分层（红线）
- **md 对照版 `第X章初译_对照.md` 仍是自动化门禁（lqa_gates / project_status）的唯一真源**，中文原文零改动。
- **docx 是人工核验/审阅与交付载体**，分三类，职责单一：

| 产物 | 目录 | 生成器 | 用途 |
|---|---|---|---|
| 对照 docx（中英双语） | `docx交付/第X章_中英对照.docx` | `md_bilingual_to_docx.py` | **留给用户核验**（不交付） |
| 译文 docx（纯英、干净） | `交付版/第X章_译文.docx` | `build_delivery_docx.py` | **最终交付件**（甲方只收这个） |
| 修订痕迹审阅版 | `docx交付/第X章_译文_修订标记版.docx` | `docx_revision.py` | 在 Word/WPS「审阅」显示红字增删，供审阅 |

> 对齐 MTPE 口径：交付版只放甲方要看的干净件；中间件/核验件归 `docx交付/`、`项目文档/`，不进交付版。

## 二、生成命令
- 对照 docx（核验用）：`python tools/md_bilingual_to_docx.py --batch 3-90`（缺对照版自动跳过；已生成 ch3–90 共 87 个）
- 译文 docx（交付用）：`python tools/build_delivery_docx.py --batch 3-90 --apply`（默认 dry-run，缺译文.md 跳过）
- 修订痕迹版：`python tools/docx_revision.py --old 旧.docx --new 新.docx --out 审阅版.docx --author CooperChen`
- 校验修订版：`python tools/verify_revision_docx.py --rev 审阅版.docx --base 旧.docx --expect-ins N`
- 作者字段与时间戳归一：`python tools/scrub_docx_meta.py --dir 交付版 --apply`（唯一笔名 CooperChen + 北京时间戳）

## 三、修订模式（用户决策②）
- **唯一作者笔名 `CooperChen`**（2026-11-09 起生效，不受以往任何其他笔名影响；旧「审校」/「审校CooperChen」等一律作废）。
- 该笔名覆盖**两处**：①docProps 作者字段（`dc:creator`、`cp:lastModifiedBy`）；②修订痕迹作者（`w:ins`/`w:del` 的 `w:author`）。
- 不得写入任何其他作者、协作者、机构或 AI 工具名。
- `docx_revision.py` 对「旧版→新版」两份 docx 做段级 difflib：新增段标 `w:ins`（红色下划线）、删除段用 `w:del`/`w:delText` 保留（红色删除线）。Word/WPS 打开即显修订。
- **修订版是终态审阅产物，不可再作为 docx_diff / 提取 / 门禁输入**（python-docx 读不到 `w:ins` 内 run）。
- 校验只用 `verify_revision_docx.py`，不临时写脚本；校验对象是 md 交付稿与干净 docx，不是修订版内容。
- 后续真实修订：在 Word 里改完 docx（或产出新版译文 md）→ 用本工具生成修订痕迹版供审阅，改定后回填 `第X章初译_对照.md` 真源。

## 四、三阶段推进
- **阶段1（ch32→最新截止章 90）**：已有对照版的章生成译文 docx 交付（本轮批量完成）。
- **阶段2（ch1–31 二次翻译复核）**：生成 docx 后做二次复核与修订（docx 方式），修订处出带痕迹审阅版。
- **阶段3（ch91–351）**：原文库已切分，逐章 翻译→对照→译文 docx，直至全书完成。

## 五、诗词/典籍处理（强制 + skill）
- glossary 第六节真实作品（《诗经》《金刚经》《红楼梦》《水调歌头》《桃夭》《竹里馆》《鹊桥仙·七夕》等），翻译/二创前**必须联网核验现成权威/通行英译样本**。
- 走 skill `poem_web_verify`（主源 `.codebuddy/skills/poem_web_verify/`，按 `MIRRORS.md` 单一主源、不同步五平台）：搜现成译本 → 标注出处与「是否可直接引用」→ 二创仅做最小改动 → 结论登记 `项目文档/诗词核验记录_*.md`。
- 字谜类（如《断肠谜》）按 `translate_chapter.md` 标 `[PUZZLE]` 暂停 AI 翻译，交人工。

## 六、阻塞
- 第1、2、70章缺对照版（真源不存在）→ 无法生成对照/译文 docx，本轮跳过，不擅自补译；列为交接待办，待用户或新对话裁定。

## 七、归档整理（降本增效 / 任务隔离）
> 2026-11-09 用户规则。工具：`tools/scrub_docx_meta.py`。

- **任务隔离**：仅操作 `第二本小说/` 目录内文件；不得读写 `中英剧本MTPE/`、`01_翻译业务/` 其它子项目及其它工作区，避免干扰同环境并发运行的 AI 任务（防双写）。临时脚本一律放系统 `Temp/` 且用完即删。
- **资源节约**：复用既有脚本、不新建运行时、不装依赖；批量任务单进程顺序执行、逐章 try/except 汇总；先 dry-run 列影响清单再 apply；不做大规模 move/delete（避免 IDE 目录句柄占用）。
- **清除项**：系统 Temp 临时脚本与输出、`__pycache__/`、`*.pyc`、`*.bak`、`*.baiduyun.uploading.cfg`、首轮试点残留的旧名 docx。
- **保留项（勿清理）**：`docx交付/` 对照核验 docx（用户核验用）、`归档/` 冷存储、`项目文档/` 报告、`术语表/` 切片、全部 md 真源与既有 `tools/` 脚本。
- **作者信息归一**：交付 docx 的 `dc:creator` 与 `cp:lastModifiedBy` 统一为 `CooperChen`；`Company`/`Manager` 清空；`keywords/category/subject/version/contentStatus/identifier/language` 清空；修订痕迹 `w:author` 统一 `CooperChen`。用脚本批量改，**禁止手工逐个编辑**。
- **最终编辑时间**：以本机系统时钟为基准自动生成为北京时间（UTC+8）。本机已确认时区 `China Standard Time`，本地时间即北京时；写入 `dcterms:modified` 时按 OOXML 规范存 UTC 瞬时值（Word 显示为本地北京时间），并在 `dc:description` 记录可读北京时间串。**禁止硬编码时间、禁止 AI 推断**。
- **验收**：交付 docx 作者字段唯一且为 `CooperChen`、无其它作者/协作者串、时间戳=本机实际北京时；中文原文零改动；门禁 P0/P1 与完成度 24.8% 不劣化；同环境其它任务目录无写入痕迹。
