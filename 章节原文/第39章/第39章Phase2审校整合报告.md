# 第39章 Phase 2 再次MTPE · 审校意见整合报告

**处理文件**：`第39章初译_对照.md`（主改）、`第39章译文.md`（同步）
**依据**：`translation_optimization_workflow.md` Phase 2 + 术语表 + 第38章跨章一致性
**段落校验**：对照版中文段与原文结构一致（未增删段）；译文版同步，英文逐句一致。
**裁决原则**：忠实原文 > 术语一致 > 跨章一致 > 表达自然；外部意见仅为参考，不添加原文没有的细节（红线）。

---

## 一、已采纳（Adopted）

| # | 来源 | 问题描述 | 修改前 | 修改后 |
|---|------|----------|--------|--------|
| 1 | Qwen | 英文栏误混入中文（格式事故） | `…each punch and kick containing destructive power. 千里寻灵活地躲避着，运用精湛的拳法技巧，以柔克刚，努力化解对方的攻势。` | 删除混入中文，保留纯英文 |
| 2 | Qwen | 夏果 拼写与术语表/Ch38 不一致 | `Xiaguo`（合写） | `Xia Guo`（分写，11处全章统一） |
| 3 | Qwen | 苦荞 拼写与术语表/Ch38 不一致 | `Ku Qiao`（分写） | `Kuqiao`（合写） |
| 4 | Qwen | expert 重复约12次（审美疲劳） | 打斗段连续 `the expert` | 首提保留 `the martial arts expert`，其余轮换为 `the fighter` / `the man` / `he` / `Lu Yuanfeng` |
| 5 | Qwen | obsequious 书面化且重复2次 | `with an obsequious smile` / `his face full of obsequious smiles` | `with a smile` / `all smiles` |
| 6 | Qwen | "Are the people behind me not human?" 直译生硬 | `Are the people behind me not human?` | `What, these men don't count?` |
| 7 | Qwen | "a face full of fierce flesh" 中式英语 | `with a face full of fierce flesh` | `his face all hard, brutal flesh` |
| 8 | Qwen | "overcome hardness with softness" 逐字直译 | `using her exquisite martial arts skills to overcome hardness with softness` | `using yielding technique to turn his force aside and deflect his attacks` |
| 9 | 自主 | "The more peaceful…stimulated her literary thoughts" 抽象直译 | `The more peaceful she was, the more it stimulated her literary thoughts` | `The quieter she grew, the more her imagination stirred` |
| 10 | 自主 | "greet me politely" 偏弱（原文"问好行礼"） | `greet me politely` | `greet me with a bow` |

---

## 二、部分采纳（Partially Adopted）

| # | 来源 | 意见内容 | 采纳部分 | 未采纳部分 | 理由 |
|---|------|----------|----------|------------|------|
| 1 | Gemini | 夏果被打断用 em-dash | 用 `—` 替代 `!...` 表打断 | 加 `to some awful place`（原文仅"被卖的份儿"） | 忠实原文，不加戏 |
| 2 | Gemini | 高手爆衣/以柔克刚描写强化 | 轻微润色"震碎→tear…to shreds" | 注入 `Qianli Fist`、加围观者反应 | 本句原文只写"拳法技巧、以柔克刚"，未点名拳法；"千里拳"虽在术语表但此处未出现 |
| 3 | Gemini | 三条件台词更硬性 | "greet me politely"→"greet me with a bow" | "waive all rent permanently / never harass / scram" 等重写 | 原译已忠实，重写属加戏 |
| 4 | Qwen | said 重复（>3/章） | 降频：`stared at Xia Guo and said`→断句；`couldn't help but say`→`spoke up` | 逐条替换为带动作标签（lips curling / waved a hand 等） | 工作流2.3：对话标签仅在有明确情绪信号时补，严禁臆测情绪/加戏 |
| 5 | Qwen | "She believed accepting…most correct choice" 学术腔 | 改 `Accepting the challenge was, she knew, the only right move` | 改为内心独白+碎片句加戏 | 去学术腔即可，不加戏 |
| 6 | Qwen | "The more peaceful…literary thoughts" | 见上"已采纳#9" | `two lifetimes` / `She picked up her brush` 等 | 转世/拾笔均非原文 |
| 7 | Qwen | 高手震碎上衣缺乏冲击 | 微润 `Channeling his inner qi, he tore his upper garment to shreds` | `Xia Guo flinched / village head stepped back` 等超出"让人看了都害怕"的扩写 | 原文"让人看了都害怕"已由 `intimidating everyone who saw them` 承载 |
| 8 | Qwen | 韦嬷嬷柔中带刚劝说段（信息量大） | 保留原文单段忠实独白 | 拆分为"韦嬷嬷说→千里寻反应→韦嬷嬷继续"并加 `bleed for a maid` 等 | 原文韦嬷嬷为连续发言，无千里寻插话；拆分=加戏 |

---

## 三、未采纳（Rejected）

| # | 来源 | 意见内容 | 不采纳理由 |
|---|------|----------|------------|
| 1 | Gemini | 拜师处 "in her past life" 替 "another era" | 千里寻为**时间穿越者**，"另一个时代"指其现代过往；"past life"暗示转世，语义失真。保留 `another era`。 |
| 2 | Gemini | 少管闲事→"stop sticking your neck out" + 称 "My Lady" + 加 "gently patting her hand" | 原译 "stay out of other people's business" 已忠实；"My Lady" 破坏与 Ch38 一致的 `Young Miss` 称谓锁；拍手为加戏。 |
| 3 | Qwen | 修改点7–10 内心独白扩写（加 "The children eating properly" / "hands twisted in her apron" 等） | 现有对照版 4 处内心独白**已正确使用斜体**，仅保留未重写；Qwen 扩写含加戏细节，违反红线。 |
| 4 | Qwen | "looked at…with great displeasure" 改加 "jaw tightened" + "*Disgusting.*" | 现有直译可接受；补写下颌/内心吐槽属加戏。 |
| 5 | Qwen | 陈浩宇田根权属长句拆分，加 "Everyone else is decoration" | 原文为单段独白，忠实保留；添加句为加戏。 |
| 6 | Qwen | 千里寻回应韦嬷嬷改写（regurgitate / why leave money on the table） | 保留忠实译法；俚语改写超出原文。 |
| 7 | Qwen | 开篇重写加 "arena" / "refilling a cup that didn't need refilling" | 大改添加环境隐喻与动作=加戏；保留忠实开篇。 |
| 8 | Qwen | 拜师反转加 "tea cup slipped / mouth fell open" | 原文无此细节，属加戏。 |
| 9 | Qwen | 陈浩宇"傻眼"改写加 "wanted the ground to open and swallow him" | 保留 `completely dumbfounded`；扩写为加戏。 |
| 10 | Qwen | 结尾加 "bamboo creaked…Like applause" | 原文无竹响描写，属加戏。 |
| 11 | Qwen | hooligans→lackeys（修改点24） | **跨章一致性裁决**：本章"地痞流氓"对应 `hooligans`，而 Ch38 已用 `hooligans` 译"地痞流氓"；`lackeys/henchmen` 是"小弟(陈浩宇的)"译法。改之会破坏跨章一致。→ 保留 `hooligans`。 |
| 12 | Qwen | "suppressed her anger" 改加 "fists curling/uncurling" | 原译忠实"忍住怒火"；补写攥拳为加戏。 |

---

## 四、自主审校补充（Phase 2.1–2.5）

- **中式英语**：已修 以柔克刚、一脸横肉、文学思想 三处 Chinglish（见已采纳#8/7/9）。
- **重复用词**：expert 12→2（首提+1处非重复）；said 适度降频；obsequious 全清。
- **标点/格式**：夏果被打断由 `!...` 改为 em-dash `—`；4 处内心独白斜体已合规。
- **-ly 副词修饰动词**：扫描全章 0 处（respectfully/panting heavily/naturally 均忠实源于原文"恭敬地/粗气/当然"，保留；未新增弱填充副词）。
- **跨章节**：Xia Guo / Kuqiao / hooligans / Proprietor / Young Miss 与 Ch38 一致。

---

## 五、关键判断说明

1. **术语与跨章一致性优先于外部润色建议**：Qwen 的 lackeys 建议虽在其章内合理，但与 Ch38 已定稿的 `hooligans`（地痞流氓）冲突，故拒。
2. **"加戏"是首要否决线**：Gemini、Qwen 多数大幅改写都补写了原文没有的微表情、围观反应、环境隐喻、内心吐槽。凡此类一律拒，只吸收"去 Chinglish / 去重复 / 更自然"的纯语言层优化。
3. **角色设定约束**：千里寻是穿越者（another era），非转世（past life）；称谓锁 Young Miss 不可因"更地道"而改 My Lady。
