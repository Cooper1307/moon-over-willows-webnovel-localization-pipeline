# glossary.md — 术语权威主表

> 版本：v0.9（脚本自动生成 + 人工裁定） · 生成时间：2026-09-02 13:46:36
> 生成方式：`python tools/build_glossary_candidates.py --emit-glossary --apply`
> 数据来源：各章 `第X章术语与人设.md`（实测 90 章目录）

## 使用规则（红线）

1. **本表是唯一权威源**；`术语表/术语表_Trados_*.{csv,txt}` 是导出物，由 `tools/export_trados.py` 生成，**不得手工编辑**。
2. **一个词条只允许一个定译**。多译法并列（MTPE 所称 AI 痕迹第 11 类「同义词循环」）是本项目已发生事故的根源。
3. 状态含义：`锁定` = 可直接使用；`[建议]` = 脚本按频次推荐，**需人工确认后改为 `锁定`**；`[!]待裁定` = 存在矛盾，禁止擅改。
4. 术语变更必须**回溯已产出章节**并写入第九节变更记录，禁止只改表不改稿。
5. 术语表仅供参考：若发现更地道译法，以地道表达优先并标注待更新（MTPE 元规则）。

---

## 一 角色人名

| 中文 | 英文 | 状态 | 首现章节 | 备注 |
|---|---|---|---|---|
| 东方尘泽 | Dongfang Chenze | 锁定 | 第18章 |  |
| 乔文仙 | Qiao Wenxian | 锁定 | 第21章 |  |
| 二杠 | Er'gang | 锁定 | 第1章 |  |
| 内侍 | Imperial Attendant | [建议] | 第7章 | 候选：Imperial Attendant / Inner Attendant / Palace Eunuch（按出现频次推荐 `Imperial Attendant`，待确认） |
| 净光法师 | Master Jingguang | 锁定 | 第25章 |  |
| 千里寻 | Qianli Xun | 锁定 | 第1章 |  |
| 向夫人 | Madam Xiang | 锁定 | 第10章 |  |
| 夏果 | Xiaguo | [建议] | 第30章 | 候选：Xiaguo / Xia Guo（按出现频次推荐 `Xiaguo`，待确认） |
| 安明轩 | An Mingxuan | 锁定 | 第18章 |  |
| 慈玄法师 | Master Cixuan | 锁定 | 第26章 |  |
| 春金巧 | Chun Jinqiao | 锁定 | 第3章 |  |
| 曹班 | Cao Ban | 锁定 | 第18章 |  |
| 朱晞颜 | Zhu Xiyan | [建议] | 第5章 | 候选：Zhu Xiyan / Prefect Zhu（按出现频次推荐 `Zhu Xiyan`，待确认） |
| 朱景元 | Zhu Jingyuan | 锁定 | 第12章 |  |
| 李管家 | Butler Li | [建议] | 第41章 | 候选：Butler Li / Steward Li（按出现频次推荐 `Butler Li`，待确认） |
| 林子孝 | Lin Zixiao | 锁定 | 第5章 |  |
| 林家三叔 | Third Uncle Lin | [建议] | 第23章 | 候选：Third Uncle Lin / the Third Uncle（按出现频次推荐 `Third Uncle Lin`，待确认） |
| 林觉 | Lin Jue | 锁定 | 第3章 |  |
| 申简辰 | Shen Jianchen | 锁定 | 第2章 |  |
| 白风 | Bai Feng | 锁定 | 第33章 |  |
| 秀珍嬷嬷 | Matron Xiuzhen | [建议] | 第23章 | 候选：Matron Xiuzhen / Nanny Xiuzhen（按出现频次推荐 `Matron Xiuzhen`，待确认） |
| 老祖宗 | the Old Ancestor | 锁定 | 第23章 |  |
| 苗知瑜 | Miao Zhiyu | 锁定 | 第18章 |  |
| 苦荞 | Kuqiao | 锁定 | 第3章 |  |
| 苦蕨 | Kujue | [建议] | 第29章 | 候选：Kujue / Ku Jue（按出现频次推荐 `Kujue`，待确认） |
| 说话艺人 | storyteller | [建议] | 第37章 | 候选：storyteller / Professional Storyteller / Storyteller / Storytelling Performer / storytellers / storytelling artists（按出现频次推荐 `storyteller`，待确认） |
| 赵佶 | Zhao Ji | 锁定 | 第6章 |  |
| 邹嬷嬷 | Matron Zou | [建议] | 第6章 | ⚠️ 全书惯例 嬷嬷→Matron：由候选提取姓 `Zou`，建议 `Matron Zou`（按频次原选 `Nurse Zou`，已按惯例覆盖） |
| 陆远峰 | Lu Yuanfeng | 锁定 | 第38章 |  |
| 陈文心 | Chen Wenxin | 锁定 | 第12章 |  |
| 陈浩宇 | Chen Haoyu | 锁定 | 第20章 |  |
| 韦嬷嬷 | Matron Wei | [建议] | 第17章 | 候选：Matron Wei / Nanny Wei（按出现频次推荐 `Matron Wei`，待确认） |
| 高俅 | Gao Qiu | 锁定 | 第34章 |  |

## 二 称谓与官制

| 中文 | 英文 | 状态 | 首现章节 | 备注 |
|---|---|---|---|---|
| 东坡居士 | Dongpo Jushi | [建议] | 第79章 | 候选：Dongpo Jushi / Su Shi（按出现频次推荐 `Dongpo Jushi`，待确认） |
| 丫鬟 | maidservant | [建议] | 第53章 | 候选：maidservant / maid（按出现频次推荐 `maidservant`，待确认） |
| 丫鬟房 | Maid's Quarters | 锁定 | 第51章 |  |
| 乔公子 | Young Master Qiao | 锁定 | 第31章 |  |
| 乔夫人 | Madam Qiao | 锁定 | 第55章 |  |
| 乔姑娘 | Young Lady Qiao | 锁定 | 第56章 |  |
| 乔老爷 | Master Qiao | 锁定 | 第55章 |  |
| 二爷 | First Master | [建议] | — | 由复合词条 `大爷 / 二爷` 拆分，需人工定译 |
| 亲家姑娘 | Affinal family's daughter | [建议] | 第20章 | 候选：Affinal family's daughter / Sister-in-law (by marriage)（按出现频次推荐 `Affinal family's daughter`，待确认） |
| 仪王府 | Prince Yi's Manor | 锁定 | 第6章 | 事故项强制锁定（勿改） |
| 六一居士 | Liu Yi Jushi | [建议] | 第80章 | 候选：Liu Yi Jushi / Ouyang Xiu（按出现频次推荐 `Liu Yi Jushi`，待确认） |
| 内侍省 | Palace Eunuch Service | 锁定 | 第7章 |  |
| 千年神柳 | Millennial Divine Willow | 锁定 | 第2章 | 事故项强制锁定（勿改） |
| 大公子 | eldest son | [建议] | 第9章 | 候选：eldest son / the eldest son（按出现频次推荐 `eldest son`，待确认） |
| 大爷 | First Master | [建议] | — | 由复合词条 `大爷 / 二爷` 拆分，需人工定译 |
| 太尉 | Grand Commandant | 锁定 | 第34章 |  |
| 太监 | eunuch | 锁定 | 第7章 |  |
| 夫人 | Madam | [建议] | 第9章 | 候选：Madam / the lady（按出现频次推荐 `Madam`，待确认） |
| 姑娘 | Young Lady | 锁定 | 第54章 |  |
| 姑爷 | Son-in-law | [建议] | 第3章 | 候选：Son-in-law / Young Master (son-in-law) / young master / Master / Master Lin / her husband / the lord（按出现频次推荐 `Son-in-law`，待确认） |
| 官家 | His Majesty | [建议] | 第6章 | 候选：His Majesty / the Emperor / The Emperor / The Sovereign（按出现频次推荐 `His Majesty`，待确认） |
| 官家十三子 | the thirteenth son of the emperor | 锁定 | 第60章 |  |
| 官家赐婚 | Imperial Marriage Decree | [建议] | 第76章 | 候选：Imperial Marriage Decree / Royal（按出现频次推荐 `Imperial Marriage Decree`，待确认） |
| 小厮 | page boy | 锁定 | 第63章 |  |
| 小姐 | Miss | 锁定 | 第3章 |  |
| 少夫人 | Young Madam | [建议] | 第9章 | 候选：Young Madam / the young mistress / young madam（按出现频次推荐 `Young Madam`，待确认） |
| 岳丈大人 | father-in-law | 锁定 | 第53章 |  |
| 岳父大人 | father-in-law | [建议] | 第5章 | 候选：father-in-law / Father-in-law（按出现频次推荐 `father-in-law`，待确认） |
| 师父 | Master | [建议] | 第2章 | 候选：Master / Shifu（按出现频次推荐 `Master`，待确认） |
| 幽栖居士 | Youqi Jushi | [建议] | 第18章 | 候选：Youqi Jushi / Hermit of Youqi / Householder Youqi / Lay Buddhist Youqi / Zhu Shuzhen（按出现频次推荐 `Youqi Jushi`，待确认） |
| 徐公子 | Young Master Xu | 锁定 | 第21章 |  |
| 徐家公子 | Young Master Xu | 锁定 | 第13章 |  |
| 徒弟 | Disciple | 锁定 | 第2章 |  |
| 易安居士 | Yi'an Jushi | [建议] | 第18章 | 候选：Yi'an Jushi / Li Qingzhao（按出现频次推荐 `Yi'an Jushi`，待确认） |
| 曾丞相 | Chancellor Zeng | 锁定 | 第35章 |  |
| 朱府老爷 | Father Zhu | [建议] | 第3章 | 候选：Father Zhu / Lord Zhu（按出现频次推荐 `Father Zhu`，待确认） |
| 林家二爷 | Second Master Lin | 锁定 | 第11章 |  |
| 林家大爷 | Eldest Master Lin | 锁定 | 第11章 |  |
| 殿下 | Your Highness | 锁定 | 第7章 |  |
| 毛爷爷 | Grandpa Mao | [建议] | — | 由复合词条 `毛爷爷 / 伟人` 拆分，需人工定译 |
| 王爷 | His Highness | [建议] | 第6章 | 候选：His Highness / Your Highness / the Prince（按出现频次推荐 `His Highness`，待确认） |
| 申公子 | Young Master Shen | 锁定 | 第55章 |  |
| 知府大人 | Prefect | [建议] | 第55章 | 候选：Prefect / His Excellency the Prefect（按出现频次推荐 `Prefect`，待确认） |
| 秦夫人 | Madam Qin | 锁定 | 第55章 |  |
| 老姑娘 | an old maid | 锁定 | 第4章 |  |
| 老娘 | Yours truly | [建议] | 第1章 | 候选：Yours truly / This queen / "this lady" / I (emphasized) / Old lady（按出现频次推荐 `Yours truly`，待确认） |
| 苗姑娘 | Lady Miao | 锁定 | 第21章 |  |
| 赵佶（官家） | The Sovereign | [建议] | 第7章 | 候选：The Sovereign / Zhao Ji（按出现频次推荐 `The Sovereign`，待确认）；⚠️ 疑似 `赵佶` 的别名/异写，建议合并为同一词条 |
| 闲散王爷 | leisurely prince | 锁定 | 第59章 |  |
| 陈公子 | Young Master Chen | 锁定 | 第21章 |  |
| 魏夫人 | Lady Wei | 锁定 | 第35章 |  |
| 黄花大姑娘 | young virgins | 锁定 | 第85章 |  |

## 三 地理与机构

| 中文 | 英文 | 状态 | 首现章节 | 备注 |
|---|---|---|---|---|
| 七星桥 | Seven Star Bridge (Qixing Bridge) | 锁定 | 第98章 |  |
| 临安府 | Lin'an Prefecture | [建议] | 第37章 | ⚠️ 全书惯例 府→Manor |
| 临安知府 | Prefect of Lin'an | [建议] | 第3章 | ⚠️ 全书惯例 府→Manor |
| 乔府 | The Qiao Manor | 锁定 | 第40章 |  |
| 侧门 | side gate | 锁定 | 第9章 |  |
| 千里拳庄 | Qianli Fist Manor | 锁定 | 第2章 |  |
| 右承天门 | Youchengtian Gate | 锁定 | 第34章 |  |
| 吉祥药房 | Jixiang Pharmacy | 锁定 | 第17章 |  |
| 后门 | back courtyard | [建议] | — | 由复合词条 `后院/后门` 拆分，需人工定译 |
| 后院 | back courtyard | [建议] | — | 由复合词条 `后院/后门` 拆分，需人工定译 |
| 回门 | return visit to maiden home | 锁定 | 第9章 |  |
| 圆房 | Consummate the marriage | [建议] | 第4章 | 候选：Consummate the marriage / consummate the marriage（按出现频次推荐 `Consummate the marriage`，待确认） |
| 垂拱殿 | Chuigong Hall | 锁定 | 第34章 |  |
| 夏日游湖 | "Summer Excursion on the Lake" | 锁定 | 第91章 |  |
| 大观 | Daguan | 锁定 | 第55章 |  |
| 官府 | local yamen | [建议] | — | 由复合词条 `衙门 / 官府` 拆分，需人工定译 |
| 寮房 | Monastic Living Quarters | [建议] | 第26章 | 候选：Monastic Living Quarters / Monks' Quarters（按出现频次推荐 `Monastic Living Quarters`，待确认） |
| 府衙 | prefecture office | [建议] | 第10章 | 候选：prefecture office / Government Office / Prefectural Office（按出现频次推荐 `prefecture office`，待确认） |
| 打道回府 | return home | [建议] | 第81章 | ⚠️ 全书惯例 府→Manor |
| 春香楼 | Chunxiang Brothel | [建议] | 第3章 | 候选：Chunxiang Brothel / Chunxiang Pavilion（按出现频次推荐 `Chunxiang Brothel`，待确认） |
| 望景亭 | Wangjing Pavilion | [建议] | 第67章 | 候选：Wangjing Pavilion / Lake-viewing Pavilion（按出现频次推荐 `Wangjing Pavilion`，待确认） |
| 望月轩 | Wangyue Pavilion | 锁定 | 第85章 |  |
| 木台 | Wooden Stage | 锁定 | 第55章 |  |
| 木质高台 | wooden platform | 锁定 | 第82章 |  |
| 未出阁 | Unmarried (of daughters) | 锁定 | 第8章 |  |
| 朱府 | Zhu Manor | [建议] | 第3章 | 候选：Zhu Manor / Zhu Manor; Zhu residence / Zhu residence / the Zhu residence（按出现频次推荐 `Zhu Manor`，待确认） |
| 朱府花园 | Zhu Family Garden | 锁定 | 第54章 |  |
| 林府 | Lin Manor | [建议] | 第3章 | 候选：Lin Manor / The Lin Manor（按出现频次推荐 `Lin Manor`，待确认） |
| 梁山 | Liangshan | 锁定 | 第34章 |  |
| 正门 | main gate | 锁定 | 第9章 |  |
| 正院 | Main Courtyard | 锁定 | 第13章 |  |
| 水泊梁山 | The Marshes of Mount Liang | [建议] | 第36章 | 候选：The Marshes of Mount Liang / Water Margins of Mount Liang（按出现频次推荐 `The Marshes of Mount Liang`，待确认） |
| 永泰茶楼 | Yongtai Teahouse | 锁定 | 第18章 |  |
| 砚台 | inkstone | 锁定 | 第9章 |  |
| 竹林 | bamboo grove | [建议] | 第28章 | 候选：bamboo grove / Bamboo Forest（按出现频次推荐 `bamboo grove`，待确认） |
| 聚香楼 | Gathering Fragrance Tower | [建议] | 第56章 | 候选：Gathering Fragrance Tower / Juxiang Lou / Juxiang Lou (Pavilion of Gathering Fragrance) / Juxiang Restaurant（按出现频次推荐 `Gathering Fragrance Tower`，待确认） |
| 脚店 | Jiao Dian | [建议] | 第32章 | 候选：Jiao Dian / Rest Tavern（按出现频次推荐 `Jiao Dian`，待确认） |
| 花云楼 | Flower Cloud Pavilion | [建议] | 第71章 | 候选：Flower Cloud Pavilion / Huayun Tower（按出现频次推荐 `Flower Cloud Pavilion`，待确认） |
| 茅房 | latrine | [建议] | 第5章 | 候选：latrine / outhouse / privy（按出现频次推荐 `latrine`，待确认） |
| 衙门 | local yamen | [建议] | — | 由复合词条 `衙门 / 官府` 拆分，需人工定译 |
| 裁缝铺 | Tailor Shop | [建议] | 第69章 | 候选：Tailor Shop / Tailor's Shop（按出现频次推荐 `Tailor Shop`，待确认） |
| 西华门 | Xihua Gate | 锁定 | 第34章 |  |
| 西湖 | West Lake | 锁定 | 第33章 |  |
| 西院 | West Courtyard | [建议] | 第21章 | 候选：West Courtyard / west courtyard（按出现频次推荐 `West Courtyard`，待确认） |
| 观景亭 | Sightseeing Pavilion | 锁定 | 第51章 |  |
| 迷宫 | Labyrinth | [建议] | 第10章 | 候选：Labyrinth / Maze（按出现频次推荐 `Labyrinth`，待确认） |
| 醉云楼 | Drunken Cloud Tower | [建议] | 第64章 | 候选：Drunken Cloud Tower / Zuiyun Tower（按出现频次推荐 `Drunken Cloud Tower`，待确认） |
| 闺阁 | boudoir | [建议] | 第64章 | 候选：boudoir / women's quarters（按出现频次推荐 `boudoir`，待确认） |
| 集英殿 | Jiying Hall | 锁定 | 第35章 |  |
| 青楼 | brothel | 锁定 | 第52章 |  |
| 验兵台 | Drill Ground | [建议] | — | 由复合词条 `校场 / 验兵台` 拆分，需人工定译 |

## 四 世界观与武功

| 中文 | 英文 | 状态 | 首现章节 | 备注 |
|---|---|---|---|---|
| 功名利禄 | Fame and fortune | [建议] | 第49章 | 候选：Fame and fortune / Worldly success（按出现频次推荐 `Fame and fortune`，待确认） |
| 功德箱 | Donation Box | [建议] | 第26章 | 候选：Donation Box / Merit Box（按出现频次推荐 `Donation Box`，待确认） |
| 千里拳 | Qianli Fist | 锁定 | 第2章 |  |
| 快拳 | Quick Fist | [建议] | 第2章 | 候选：Quick Fist / Rapid Strikes（按出现频次推荐 `Quick Fist`，待确认） |
| 拆拳术 | Counter-grapple technique | 锁定 | 第2章 |  |
| 拖延战术 | Delaying Tactics | [建议] | 第78章 | 候选：Delaying Tactics / The Art of Procrastination（按出现频次推荐 `Delaying Tactics`，待确认） |
| 招安 | Amnesty | [建议] | 第37章 | 候选：Amnesty / Pacification（按出现频次推荐 `Amnesty`，待确认） |
| 拳服 | Martial arts uniform | 锁定 | 第2章 |  |
| 法西斯 | Fascist | 锁定 | 第14章 |  |
| 点穴 | Acupoint Pressing | [建议] | 第33章 | 候选：Acupoint Pressing / Dim Mak（按出现频次推荐 `Acupoint Pressing`，待确认） |
| 申拳 | Shen Fist | [建议] | 第2章 | 候选：Shen Fist / Shen Fist (School)（按出现频次推荐 `Shen Fist`，待确认） |
| 约法三章 | Three Rules | 锁定 | 第8章 |  |
| 诗会（正式宴会） | poetry banquet | [建议] | 第18章 | ⚠️ 疑似 `诗会` 的别名/异写，建议合并为同一词条 |
| 软笔书法 | calligraphy with a soft brush | 锁定 | 第9章 |  |
| 轻功 | Light-foot technique | [建议] | 第64章 | 候选：Light-foot technique / Qinggong / qinggong（按出现频次推荐 `Light-foot technique`，待确认） |

## 五 衣食器物与文化项

| 中文 | 英文 | 状态 | 首现章节 | 备注 |
|---|---|---|---|---|
| "打着灯笼都难找" | Hard to find even with a lantern | 锁定 | 第2章 |  |
| 七次注汤 | Seven Water Injections | 锁定 | 第26章 |  |
| 下笔如有神 | the pen moves as if by magic | 锁定 | 第87章 |  |
| 丝帕 | Silk Handkerchief | [建议] | 第6章 | 候选：Silk Handkerchief / silk handkerchief（按出现频次推荐 `Silk Handkerchief`，待确认） |
| 书童 | Attendant | [建议] | 第40章 | 候选：Attendant / Page boy（按出现频次推荐 `Attendant`，待确认） |
| 休书 | Letter of Divorce | [建议] | 第8章 | 候选：Letter of Divorce / letter of repudiation（按出现频次推荐 `Letter of Divorce`，待确认） |
| 台盘司 | Office of Tableware | 锁定 | 第54章 |  |
| 吃着碗里的，还瞧着锅里 | To eat from one’s bowl while eyeing the pot | 锁定 | 第98章 |  |
| 和衣睡倒人怀 | Falling asleep in his arms, fully dressed | [建议] | 第73章 | 候选：Falling asleep in his arms, fully dressed / Falling asleep in someone’s arms while dressed（按出现频次推荐 `Falling asleep in his arms, fully dressed`，待确认） |
| 孟婆汤 | Mengpo's Soup | [建议] | 第6章 | 候选：Mengpo's Soup / the Soup of Oblivion（按出现频次推荐 `Mengpo's Soup`，待确认） |
| 帷帽 | Veiled hat | 锁定 | 第2章 |  |
| 散茶 | Loose-leaf tea | 锁定 | 第37章 |  |
| 斗茶 | Tea Competition | [建议] | 第18章 | 候选：Tea Competition / Tea Whisking Contest / tea competition / whisking contest（按出现频次推荐 `Tea Competition`，待确认） |
| 治淤青的药 | bruise medicine | [建议] | 第21章 | 候选：bruise medicine / bruise-healing ointment（按出现频次推荐 `bruise medicine`，待确认） |
| 灯笼 | lanterns | 锁定 | 第63章 |  |
| 点茶 | Whisked tea | [建议] | 第5章 | 候选：Whisked tea / the art of tea whisking（按出现频次推荐 `Whisked tea`，待确认） |
| 玉盘珍羞直万钱 | Rare delicacies on jade plates, worth a fortune | 锁定 | 第54章 |  |
| 琴瑟和鸣 | conjugal bliss | [建议] | 第53章 | 候选：conjugal bliss / marital harmony（按出现频次推荐 `conjugal bliss`，待确认） |
| 电灯泡 | Light bulb | [建议] | 第66章 | 候选：Light bulb / Lightbulb / Third Wheel / Third wheel（按出现频次推荐 `Light bulb`，待确认） |
| 画像 | portrait | 锁定 | 第56章 |  |
| 知书达礼 | educated and refined | 锁定 | 第54章 |  |
| 竹叶茶 | Bamboo Leaf Tea | 锁定 | 第29章 |  |
| 笔墨纸砚 | Four Treasures of the Study | [建议] | 第9章 | 候选：Four Treasures of the Study / brush, ink, paper, and inkstone（按出现频次推荐 `Four Treasures of the Study`，待确认） |
| 笺纸 | Ornamental paper | [建议] | — | 由复合词条 `花笺 / 笺纸` 拆分，需人工定译 |
| 背灯初解绣裙腰 | as, back to the lamp, I unfasten my silk skirt | 锁定 | 第9章 |  |
| 茶师 | performer | [建议] | 第18章 | 候选：performer / tea artisan / tea master（按出现频次推荐 `performer`，待确认） |
| 茶汤 | tea liquor | 锁定 | 第9章 |  |
| 茶盏 | tea bowl | 锁定 | 第9章 |  |
| 茶碾 | tea roller | 锁定 | 第9章 |  |
| 茶筅 | tea whisk | 锁定 | 第9章 |  |
| 茶筛 | tea sieve | 锁定 | 第9章 |  |
| 茶粉 | tea powder | 锁定 | 第9章 |  |
| 茶艺 | whisked tea | [建议] | — | 由复合词条 `点茶 / 茶艺` 拆分，需人工定译 |
| 茶酒司 | Office of Refreshments | 锁定 | 第54章 |  |
| 药方 | Prescription | 锁定 | 第37章 |  |
| 菜蔬局 | Bureau of Greens | 锁定 | 第54章 |  |
| 落汤鸡 | Drowned rat | [建议] | 第69章 | 候选：Drowned rat / Soaked chicken / drowned rat（按出现频次推荐 `Drowned rat`，待确认） |
| 薰衣草 | lavender | 锁定 | 第60章 |  |
| 藤椅 | rattan chair | 锁定 | 第63章 |  |
| 衾寒枕冷夜香消 | But the quilt and pillow are cold. The night's fragrance is gone | 锁定 | 第9章 |  |
| 襦裙 | Ruqun (Jacket and Skirt) | 锁定 | 第66章 |  |
| 词中有画 | There is painting in the ci | 锁定 | 第81章 |  |
| 诏书 | Imperial Decree | 锁定 | 第7章 |  |
| 说书 | storytelling | 锁定 | 第56章 |  |
| 轿子 | Sedan chair | 锁定 | 第73章 |  |
| 酒壶 | wine pot | 锁定 | 第56章 |  |
| 酒酿 | Fermented rice wine | [建议] | 第71章 | 候选：Fermented rice wine / Sweet rice wine（按出现频次推荐 `Fermented rice wine`，待确认） |
| 醒酒汤 | Hangover Soup | [建议] | 第74章 | 候选：Hangover Soup / Sobriety Soup / hangover soup / sober-up soup（按出现频次推荐 `Hangover Soup`，待确认） |
| 野菜包子 | Wild Vegetable Steamed Buns | 锁定 | 第4章 |  |
| 金樽清酒斗十千 | Clear wine in golden cups, ten thousand coins per vat | 锁定 | 第54章 |  |
| 食盒 | Food Carrier | [建议] | 第51章 | 候选：Food Carrier / Food carrier / Tiered Food Box / Tiered food box（按出现频次推荐 `Food Carrier`，待确认） |
| 食言 | break one's word | 锁定 | 第87章 |  |
| 香火 | ancestral incense | [建议] | 第58章 | 候选：ancestral incense / family line（按出现频次推荐 `ancestral incense`，待确认） |
| 香药局 | Bureau of Incense | 锁定 | 第54章 |  |

## 六 诗词与典故

| 中文 | 英文 | 状态 | 首现章节 | 备注 |
|---|---|---|---|---|
| 《三国志》 | Records of the Three Kingdoms | 锁定 | 第19章 |  |
| 《世说新语》 | A New Account of the Tales of the World | 锁定 | 第19章 |  |
| 《南歌子》 | "Nan Ge Zi" (Southern Song) | 锁定 | 第73章 |  |
| 《太上感应篇》 | "Treatise on Response and Retribution" | 锁定 | 第27章 |  |
| 《子虚赋》 | Rhapsody on Sir Fantasy | 锁定 | 第19章 |  |
| 《对竹一绝》 | "Ode to Bamboo" | 锁定 | 第61章 |  |
| 《少年游》 | "Shaonian You" | [建议] | 第80章 | 候选："Shaonian You" / "Youthful Roaming"（按出现频次推荐 `"Shaonian You"`，待确认） |
| 《断肠谜》 | "The Heartbreak Riddle" | [建议] | 第22章 | 候选："The Heartbreak Riddle" / "Heartbreak Riddle"（按出现频次推荐 `"The Heartbreak Riddle"`，待确认） |
| 《桃夭》 | "Peach Blossoms" | 锁定 | 第55章 |  |
| 《水浒》 | Water Margin | 锁定 | 第34章 |  |
| 《水调歌头》 | "Shuidiao Getou" | [建议] | 第79章 | 候选："Shuidiao Getou" / "Water Melody"（按出现频次推荐 `"Shuidiao Getou"`，待确认） |
| 《汉书》 | Book of Han | 锁定 | 第32章 |  |
| 《江城子·赏春》 | "Jiangchengzi: Admiring the Spring" | 锁定 | 第25章 |  |
| 《浣溪沙·春夜》 | "Huanxisha · Spring Night" | 锁定 | 第9章 |  |
| 《清平乐·夏日游湖》 | "Qing Ping Yue: Summer Day on the Lake" | 锁定 | 第74章 |  |
| 《眼儿媚》 | Yan Er Mei: Fascinating Eyes | 锁定 | 第5章 |  |
| 《竹里馆》 | "The Bamboo Pavilion" | 锁定 | 第26章 |  |
| 《红楼梦》 | Dream of the Red Chamber | 锁定 | 第1章 |  |
| 《红香与玄英》 | "Red Fragrance and Xuan Ying" | 锁定 | 第100章 |  |
| 《腊梅山禽图》 | Winter Plum and Mountain Birds | 锁定 | 第35章 |  |
| 《菊花》 | "Chrysanthemum" (Poem) | 锁定 | 第11章 |  |
| 《菩萨蛮》 | "Pu Sa Man" (Buddhist Coiffure) | 锁定 | 第70章 |  |
| 《诗经》 | Book of Songs | [建议] | 第80章 | 候选：Book of Songs / Classic of Poetry（按出现频次推荐 `Book of Songs`，待确认） |
| 《金刚经》 | The Diamond Sutra | 锁定 | 第19章 |  |
| 《钱神论》 | Discourse on the God of Money | 锁定 | 第19章 |  |
| 《鹊桥仙·七夕》 | "Magpie Bridge Immortal · Qixi" | 锁定 | 第57章 |  |
| 一面之词 | one side of the story | 锁定 | 第87章 |  |
| 以词论词 | Discuss ci based on ci itself | 锁定 | 第81章 |  |
| 山水诗 | landscape poetry | 锁定 | 第81章 |  |
| 谱曲 | Composition | [建议] | 第70章 | 候选：Composition / Setting poems to music（按出现频次推荐 `Composition`，待确认） |
| 鼓子词 | Drum Song | [建议] | — | 由复合词条 `鼓子词 / 鼓词` 拆分，需人工定译 |
| 鼓词 | Drum Song | [建议] | — | 由复合词条 `鼓子词 / 鼓词` 拆分，需人工定译 |

## 七 金句与口头禅锁定表

| 中文 | 英文 | 状态 | 首现章节 | 备注 |
|---|---|---|---|---|
| 家人们 | Chat | [建议] | 第1章 | 候选：Chat / Fam / Guys（按出现频次推荐 `Chat`，待确认） |
| 老娘（千里寻自称） | I (emphasized) | [建议] | 第3章 | 候选：I (emphasized) / This queen / Yours truly（按出现频次推荐 `I (emphasized)`，待确认）；⚠️ 疑似 `老娘` 的别名/异写，建议合并为同一词条 |

## 〇 未分类（待归类）

| 中文 | 英文 | 状态 | 首现章节 | 备注 |
|---|---|---|---|---|
| "如露亦如电，应作如是观" | "Like a dewdrop or a flash of lightning—thus should one view them." | 锁定 | 第19章 |  |
| "月上柳梢头，人约黄昏后" | "The moon above a willow tree | [建议] | 第2章 | 候选："The moon above a willow tree / Shone on my lover close to me."（按出现频次推荐 `"The moon above a willow tree`，待确认） |
| "除非猪能上树" | "When pigs can climb trees" | [建议] | 第2章 | 候选："When pigs can climb trees" / "When pigs fly"（按出现频次推荐 `"When pigs can climb trees"`，待确认） |
| 5A级景区 | 5A-level Scenic Spot | 锁定 | 第67章 |  |
| 一两银子 | One Tael of Silver | 锁定 | 第33章 |  |
| 一家人 | Family members | [建议] | 第70章 | 候选：Family members / One family（按出现频次推荐 `Family members`，待确认） |
| 一溜烟 | in a flash | [建议] | 第53章 | 候选：in a flash / like a streak（按出现频次推荐 `in a flash`，待确认） |
| 一点心意 | a small token of appreciation | 锁定 | 第7章 |  |
| 一诺千金 | a promise worth a thousand gold | 锁定 | 第86章 |  |
| 七出 | Seven Conditions for Repudiating a Wife | [建议] | 第23章 | 候选：Seven Conditions for Repudiating a Wife / Seven Grounds for Divorce（按出现频次推荐 `Seven Conditions for Repudiating a Wife`，待确认） |
| 七夕 | Qixi Festival | 锁定 | 第57章 |  |
| 七夕节 | Qixi Festival | [建议] | 第66章 | 候选：Qixi Festival / Double Seventh Festival / The Double Seventh（按出现频次推荐 `Qixi Festival`，待确认） |
| 七宝素粥 | Seven-treasure Vegetable Porridge | 锁定 | 第76章 |  |
| 万事大吉 | everything is fine | 锁定 | 第86章 |  |
| 上天 | The Heavens | 锁定 | 第6章 |  |
| 上头 | Get tipsy | [建议] | 第69章 | 候选：Get tipsy / Go to one's head（按出现频次推荐 `Get tipsy`，待确认） |
| 上梁不正下梁歪 | Like father, like son (behavior) | [建议] | 第53章 | 候选：Like father, like son (behavior) / The fish stinks from the head down（按出现频次推荐 `Like father, like son (behavior)`，待确认） |
| 下里巴人 | "Lowbrow art" (Popular and unrefined) | [建议] | 第30章 | 候选："Lowbrow art" (Popular and unrefined) / Lower-brow / Vernacular art（按出现频次推荐 `"Lowbrow art" (Popular and unrefined)`，待确认） |
| 不以结婚为目的恋爱是耍流氓 | Dating | [建议] | — | 由复合词条 `谈恋爱 / 不以结婚为目的恋爱是耍流氓` 拆分，需人工定译 |
| 不孝公婆 | Disobedience to parents-in-law | 锁定 | 第23章 |  |
| 不守夫道 | Unfaithful | [建议] | 第3章 | 候选：Unfaithful / Violating the husband's way（按出现频次推荐 `Unfaithful`，待确认） |
| 不知羞耻 | shameless | 锁定 | 第57章 |  |
| 东京汴梁 | Bianliang, the Eastern Capital | [建议] | 第6章 | 候选：Bianliang, the Eastern Capital / Dongjing Bianliang / the Eastern Capital（按出现频次推荐 `Bianliang, the Eastern Capital`，待确认） |
| 东坡肉 | Dongpo Pork | 锁定 | 第78章 |  |
| 东家 | Proprietor | [建议] | — | 由复合词条 `东家 / 老东家` 拆分，需人工定译 |
| 东方兄 | Dongfang Chenze | [建议] | — | 由复合词条 `东方尘泽/东方兄` 拆分，需人工定译 |
| 两刻钟 | 30 minutes | [建议] | 第72章 | 候选：30 minutes / Two quarters of an hour（按出现频次推荐 `30 minutes`，待确认） |
| 两情相悦 | Being of one heart | [建议] | 第59章 | 候选：Being of one heart / Mutual affection / Mutual love / Reciprocal affection / mutually in love（按出现频次推荐 `Being of one heart`，待确认） |
| 中秋节 | Mid-Autumn Festival | 锁定 | 第7章 |  |
| 丰亨豫大 | prosperity and grandeur | 锁定 | 第55章 |  |
| 临安 | Lin'an | 锁定 | 第33章 |  |
| 临安节度使 | Military Commissioner of Lin'an | [建议] | 第36章 | 候选：Military Commissioner of Lin'an / Regional Governor of Lin'an / Jiedushi of Lin'an (Military Governor)（按出现频次推荐 `Military Commissioner of Lin'an`，待确认） |
| 丹青 | Danqing | [建议] | 第36章 | 候选：Danqing / Ink and Color（按出现频次推荐 `Danqing`，待确认） |
| 主君 | Lord | [建议] | 第50章 | 候选：Lord / Master（按出现频次推荐 `Lord`，待确认） |
| 主屋 | Main Hall | [建议] | 第51章 | 候选：Main Hall / Master's Quarters（按出现频次推荐 `Main Hall`，待确认） |
| 举手之劳 | a mere lift of the hand | 锁定 | 第90章 |  |
| 之子于归，宜其室家 | This lady goes to her new home, bringing harmony to her household | 锁定 | 第55章 |  |
| 乌有先生 | Sir No-such | 锁定 | 第19章 |  |
| 乔守仁 | Qiao Shouren | 锁定 | 第40章 |  |
| 乔文渊 | Qiao Wenyuan | 锁定 | 第33章 |  |
| 乔文贤 | Qiao Wenxian | 锁定 | 第18章 |  |
| 乔梦容（佳和郡主） | Princess Jiahe | [建议] | 第6章 | 候选：Princess Jiahe / Qiao Mengrong（按出现频次推荐 `Princess Jiahe`，待确认）；⚠️ 疑似 `佳和郡主` 的别名/异写，建议合并为同一词条 |
| 乔贵妃 | Consort Qiao | [建议] | 第6章 | 候选：Consort Qiao / Noble Consort Qiao（按出现频次推荐 `Consort Qiao`，待确认） |
| 九曲红梅 | Jiuqu Hongmei (Nine-curves Red Plum) | 锁定 | 第76章 |  |
| 乞巧宴 | Qiqiao Banquet (Banquet to Plead for Skill) | 锁定 | 第98章 |  |
| 乞巧果 | Fried Flour and Honey Sweets (Qiqiao-guo) | [建议] | — | 由复合词条 `乞巧果 / 油面蜜糖` 拆分，需人工定译 |
| 乳雾汹涌 | creamy foam rises | 锁定 | 第9章 |  |
| 二叔 | Second Uncle | [建议] | — | 由复合词条 `二叔 / 林子孝` 拆分，需人工定译 |
| 亏大发 | A huge loss | [建议] | 第95章 | 候选：A huge loss / To get the short end of the stick（按出现频次推荐 `A huge loss`，待确认） |
| 五体投地 | prostrate oneself in admiration | 锁定 | 第65章 |  |
| 五戒十善 | The Five Precepts and Ten Virtues | 锁定 | 第27章 |  |
| 五百文铜钱 | Five Hundred Wen (Copper Coins) | 锁定 | 第33章 |  |
| 五花大绑 | truss up | 锁定 | 第85章 |  |
| 五雷轰顶 | as if struck by lightning | 锁定 | 第62章 |  |
| 井水不犯河水 | Each to their own | [建议] | 第8章 | 候选：Each to their own / Mind one's own business（按出现频次推荐 `Each to their own`，待确认） |
| 亭子 | Pavilion | 锁定 | 第55章 |  |
| 亲事 | marriage arrangement | 锁定 | 第62章 |  |
| 亲家 | in-laws | 锁定 | 第84章 |  |
| 人才辈出 | talented people emerge in large numbers | 锁定 | 第55章 |  |
| 人杰地灵 | a place renowned for its talented people | 锁定 | 第55章 |  |
| 以柔克刚 | overcome the hard with the soft | 锁定 | 第87章 |  |
| 以诗会友 | make friends through poetry | 锁定 | 第9章 |  |
| 仪王 | Prince Yi | 锁定 | 第52章 |  |
| 伉俪情深 | deeply devoted couple | 锁定 | 第54章 |  |
| 休了你 | divorce you | 锁定 | 第52章 |  |
| 休了我 | Letter of Divorce | [建议] | — | 由复合词条 `休书 / 休了我` 拆分，需人工定译 |
| 会客厅 | Reception Hall | 锁定 | 第33章 |  |
| 伟人 | Grandpa Mao | [建议] | — | 由复合词条 `毛爷爷 / 伟人` 拆分，需人工定译 |
| 低调 | keep a low profile | 锁定 | 第59章 |  |
| 体察民情 | observe the people's lives | 锁定 | 第57章 |  |
| 佛堂 | Buddhist Shrine | [建议] | 第14章 | 候选：Buddhist Shrine / Buddhist hall / Family Temple / family temple（按出现频次推荐 `Buddhist Shrine`，待确认） |
| 作威作福 | act like a tyrant | [建议] | 第54章 | 候选：act like a tyrant / throw one's weight about（按出现频次推荐 `act like a tyrant`，待确认） |
| 佳和郡主 | Princess Jiahe | 锁定 | 第58章 |  |
| 倒打一耙 | turn around and accuse the victim | 锁定 | 第86章 |  |
| 八字不合 | incompatible horoscopes | 锁定 | 第88章 |  |
| 关雎 | "Guan Ju" | [建议] | 第80章 | 候选："Guan Ju" / "Ospreys"（按出现频次推荐 `"Guan Ju"`，待确认） |
| 冰山美人 | ice beauty | 锁定 | 第88章 |  |
| 决一死战 | Duel | [建议] | — | 由复合词条 `对决/决一死战` 拆分，需人工定译 |
| 决疑 | Doubt Resolution | 锁定 | 第32章 |  |
| 冷暴力 | Cold violence | [建议] | 第8章 | 候选：Cold violence / Silent treatment（按出现频次推荐 `Cold violence`，待确认） |
| 击拂 | Whisking | [建议] | 第9章 | 候选：Whisking / to whisk（按出现频次推荐 `Whisking`，待确认） |
| 切磋 | Spar | 锁定 | 第2章 |  |
| 创作生涯 | creative career | 锁定 | 第1章 |  |
| 初吻 | first kiss | 锁定 | 第90章 |  |
| 判若两人 | like two different people | 锁定 | 第60章 |  |
| 刮骨疗毒 | Scraping the bone to treat poison | 锁定 | 第100章 |  |
| 刺毛肉圆 | Fuzzy Meatball | [建议] | 第68章 | 候选：Fuzzy Meatball / Prickly Meatball（按出现频次推荐 `Fuzzy Meatball`，待确认） |
| 刻骨铭心的恋情 | Unforgettable romance | 锁定 | 第49章 |  |
| 励精图治 | devote oneself to governance | 锁定 | 第55章 |  |
| 势均力敌 | Evenly matched | [建议] | 第8章 | 候选：Evenly matched / On equal footing（按出现频次推荐 `Evenly matched`，待确认） |
| 勾栏 | Goulan (Theater | [建议] | 第100章 | 候选：Goulan (Theater / Performance Hall)（按出现频次推荐 `Goulan (Theater`，待确认） |
| 勾栏瓦肆 | Goulan Wasi | [建议] | 第20章 | 候选：Goulan Wasi / Entertainment quarters / Entertainment Precincts / entertainment district / entertainment quarters / pleasure quarters（按出现频次推荐 `Goulan Wasi`，待确认） |
| 包袱 | bundle | 锁定 | 第63章 |  |
| 包间 | booth | [建议] | 第18章 | 候选：booth / private room（按出现频次推荐 `booth`，待确认） |
| 化雨 | Huayu | 锁定 | 第18章 |  |
| 匾额 | Inscribed Board | [建议] | 第39章 | 候选：Inscribed Board / Wooden Plaque（按出现频次推荐 `Inscribed Board`，待确认） |
| 千夫所指 | pointed at by a thousand fingers | 锁定 | 第84章 |  |
| 半个时辰 | half a shichen (one hour) | 锁定 | 第60章 |  |
| 卖艺不卖身 | Performing arts only, not body | 锁定 | 第71章 |  |
| 卖身契 | deed of sale | 锁定 | 第86章 |  |
| 南双 | Nan Shuang | [建议] | 第25章 | 候选：Nan Shuang / Nanshuang（按出现频次推荐 `Nan Shuang`，待确认） |
| 占卜 | Divination | [建议] | — | 由复合词条 `占卜 / 算卦` 拆分，需人工定译 |
| 印朱 | ink paste | 锁定 | 第61章 |  |
| 厅堂 | Main Hall | [建议] | 第7章 | 候选：Main Hall / Reception Hall / main hall（按出现频次推荐 `Main Hall`，待确认） |
| 压手印 | affixing our thumbprints | 锁定 | 第5章 |  |
| 厨司 | Office of Cuisine | 锁定 | 第54章 |  |
| 及时雨 | Timely Rain | 锁定 | 第34章 |  |
| 双头莲 | Double-headed Lotus | [建议] | — | 由复合词条 `双头莲 / 并蒂莲` 拆分，需人工定译 |
| 受教 | I've learned something | 锁定 | 第59章 |  |
| 口多言 | Gossip | [建议] | 第23章 | 候选：Gossip / Talkativeness（按出现频次推荐 `Gossip`，待确认） |
| 口水文 | Drivel | [建议] | 第1章 | 候选：Drivel / Vapid writing（按出现频次推荐 `Drivel`，待确认） |
| 合拍 | in sync | [建议] | 第82章 | 候选：in sync / on the same wavelength（按出现频次推荐 `in sync`，待确认） |
| 名声 | family honor | [建议] | 第58章 | 候选：family honor / reputation（按出现频次推荐 `family honor`，待确认） |
| 呲溜 | whoosh | [建议] | 第53章 | 候选：whoosh / zip（按出现频次推荐 `whoosh`，待确认） |
| 和离 | mutual divorce | [建议] | 第5章 | 候选：mutual divorce / Amicable Divorce / An amicable divorce / Divorce by mutual agreement / Mutual Divorce / a mutual divorce / amicable divorce / amicable parting / consensual divorce / the separation / the split（按出现频次推荐 `mutual divorce`，待确认） |
| 品行不端 | Misconduct | [建议] | 第8章 | 候选：Misconduct / Moral depravity（按出现频次推荐 `Misconduct`，待确认） |
| 唇脂 | Lip Rouge | [建议] | 第66章 | 候选：Lip Rouge / Lipstick（按出现频次推荐 `Lip Rouge`，待确认） |
| 唠唠嗑 | catch up | [建议] | 第54章 | 候选：catch up / have a chat（按出现频次推荐 `catch up`，待确认） |
| 唱曲的 | singing girls | [建议] | 第79章 | 候选：singing girls / songstresses（按出现频次推荐 `singing girls`，待确认） |
| 商妓 | commercial courtesan | [建议] | 第3章 | 候选：commercial courtesan / Commercial prostitute / Merchant Courtesan（按出现频次推荐 `commercial courtesan`，待确认） |
| 善妒 | Jealousy | 锁定 | 第23章 |  |
| 喜兰 | Xilan | 锁定 | 第31章 |  |
| 喜蛛应巧 | Spider's web prophecy | 锁定 | 第66章 |  |
| 四司六局 | Four Departments and Six Bureaus | 锁定 | 第54章 |  |
| 四大名著 | the Four Great Classical Novels | 锁定 | 第1章 |  |
| 四目相对 | eyes meet | 锁定 | 第55章 |  |
| 国泰民安 | the country is prosperous and the people are at peace | 锁定 | 第55章 |  |
| 地桃花 | Caesarweed | [建议] | 第28章 | 候选：Caesarweed / Urena lobata（按出现频次推荐 `Caesarweed`，待确认） |
| 地痞流氓 | local thugs | 锁定 | 第63章 |  |
| 境界参差不齐 | Mixed aesthetic standards | [建议] | 第91章 | 候选：Mixed aesthetic standards / Varied levels of enlightenment（按出现频次推荐 `Mixed aesthetic standards`，待确认） |
| 大卸八块 | chop into pieces | 锁定 | 第56章 |  |
| 大权旁落 | lose power to others | 锁定 | 第59章 |  |
| 天下大事 | Affairs of the realm | [建议] | 第71章 | 候选：Affairs of the realm / National affairs（按出现频次推荐 `Affairs of the realm`，待确认） |
| 天之美禄 | Heaven's Beautiful Boon | [建议] | 第32章 | 候选：Heaven's Beautiful Boon / Heaven's Fine Gift（按出现频次推荐 `Heaven's Beautiful Boon`，待确认） |
| 天助我也 | Heaven is helping me | 锁定 | 第53章 |  |
| 天机不可露 | Heaven's secrets must not be revealed | 锁定 | 第55章 |  |
| 天然景色 | natural scenery | [建议] | 第7章 | 候选：natural scenery / wilderness（按出现频次推荐 `natural scenery`，待确认） |
| 太子 | Crown Prince | 锁定 | 第34章 |  |
| 夫云妇德，不必才明绝异也 | A woman's virtue need not be exceptional in talent | 锁定 | 第81章 |  |
| 夫君 | Husband | [建议] | 第70章 | 候选：Husband / My Lord（按出现频次推荐 `Husband`，待确认） |
| 失忆 | amnesia | [建议] | 第52章 | 候选：amnesia / memory loss（按出现频次推荐 `amnesia`，待确认） |
| 头疼脑热 | a slight illness | 锁定 | 第87章 |  |
| 女为悦己者容 | A woman adorns herself for the one who delights in her | 锁定 | 第68章 |  |
| 女子无才便是德 | "A woman's virtue is having no talent" | [建议] | 第14章 | 候选："A woman's virtue is having no talent" / "Ignorance is a woman's virtue"（按出现频次推荐 `"A woman's virtue is having no talent"`，待确认） |
| 女德 | Code of Conduct | [建议] | 第74章 | 候选：Code of Conduct / Feminine Virtue（按出现频次推荐 `Code of Conduct`，待确认） |
| 女才郎貌 | A talented woman and a handsome man | 锁定 | 第69章 |  |
| 女词人 | female ci poet | [建议] | 第5章 | 候选：female ci poet / woman ci poet（按出现频次推荐 `female ci poet`，待确认） |
| 女诫 | Admonitions for Women | 锁定 | 第81章 |  |
| 奸臣 | Treacherous Official | 锁定 | 第34章 |  |
| 妾室 | Concubine | [建议] | 第40章 | 候选：Concubine / concubine（按出现频次推荐 `Concubine`，待确认） |
| 娘家蒙羞 | Shaming the paternal family | 锁定 | 第8章 |  |
| 媒人 | a matchmaker | [建议] | — | 由复合词条 `媒婆 / 媒人` 拆分，需人工定译 |
| 媒婆 | matchmaker | 锁定 | 第56章 |  |
| 嫁出去的女儿泼出去的水 | "A married daughter is like water poured out." | 锁定 | 第3章 |  |
| 嫁妆 | Dowry | [建议] | 第14章 | 候选：Dowry / dowry（按出现频次推荐 `Dowry`，待确认） |
| 嬉皮笑脸 | grinning from ear to ear | 锁定 | 第55章 |  |
| 子虚子 | Sir Fantasy | [建议] | 第19章 | 候选：Sir Fantasy / Sir Vacuity（按出现频次推荐 `Sir Fantasy`，待确认） |
| 孔方兄 | Brother Kong Fang | [建议] | 第19章 | 候选：Brother Kong Fang / Lord Square Hole（按出现频次推荐 `Brother Kong Fang`，待确认） |
| 字谜 | Glyph-puzzle | [建议] | 第76章 | 候选：Glyph-puzzle / Word Riddle（按出现频次推荐 `Glyph-puzzle`，待确认） |
| 宁为穷人妻，不为富人妾 | Rather be a poor man's wife than a rich man's concubine | 锁定 | 第51章 |  |
| 宅子 | courtyard house | [建议] | 第58章 | 候选：courtyard house / residence（按出现频次推荐 `courtyard house`，待确认） |
| 守一辈子 | remain loyal for life | 锁定 | 第7章 |  |
| 安提举 | Intendant An | 锁定 | 第55章 |  |
| 宋江 | Song Jiang | 锁定 | 第34章 |  |
| 宣和 | Xuanhe | 锁定 | 第55章 |  |
| 宣和四年 | The 4th Year of Xuanhe | [建议] | 第3章 | 候选：The 4th Year of Xuanhe / The fourth year of Xuanhe / the fourth year of the Xuanhe era（按出现频次推荐 `The 4th Year of Xuanhe`，待确认） |
| 对决 | Duel | [建议] | — | 由复合词条 `对决/决一死战` 拆分，需人工定译 |
| 小吏 | minor clerk | [建议] | 第3章 | 候选：minor clerk / petty official（按出现频次推荐 `minor clerk`，待确认） |
| 小瓷坛 | small porcelain jar | 锁定 | 第9章 |  |
| 小白文 | Brainless read | [建议] | 第1章 | 候选：Brainless read / Fast-food fiction / Shallow fiction（按出现频次推荐 `Brainless read`，待确认） |
| 小鸡双色莲子羹 | Two-Color Lotus Seed Chicken Soup | 锁定 | 第4章 |  |
| 尼姑庵 | nunnery | [建议] | 第41章 | 候选：nunnery / Convent / Nunnery（按出现频次推荐 `nunnery`，待确认） |
| 山泉 | Mountain stream | [建议] | — | 由复合词条 `溪水 / 山泉` 拆分，需人工定译 |
| 山禽矜逸态，梅粉弄轻柔。已有丹青约，千秋指白头。 | The mountain bird boasts a leisurely grace,<br>The plum blossoms display their gentle softness.<br>An eternal pact in ink and color we embrace,<br>For a thousand autumns, till our heads turn white. | 锁定 | 第35章 |  |
| 岳飞 | Yue Fei | 锁定 | 第71章 |  |
| 崇宁 | Chongning | 锁定 | 第55章 |  |
| 巳时 | Si Hour (9:00 AM - 11:00 AM) | 锁定 | 第8章 |  |
| 布袋 | cloth bag | 锁定 | 第89章 |  |
| 帐设司 | Office of Setup | 锁定 | 第54章 |  |
| 平原督邮 | Pingyuan Postmaster | 锁定 | 第19章 |  |
| 平步青云 | rapid promotion | [建议] | 第54章 | 候选：rapid promotion / rise to power（按出现频次推荐 `rapid promotion`，待确认） |
| 并蒂莲 | Double-headed Lotus | [建议] | — | 由复合词条 `双头莲 / 并蒂莲` 拆分，需人工定译 |
| 幺蛾子 | Dirty tricks | [建议] | 第8章 | 候选：Dirty tricks / Mischief / Trickery（按出现频次推荐 `Dirty tricks`，待确认） |
| 幽林别居 | Secluded Forest Villa | [建议] | 第41章 | 候选：Secluded Forest Villa / Youlin Villa / Youlin Biejü（按出现频次推荐 `Secluded Forest Villa`，待确认） |
| 废水盂 | Waste Water Bowl | 锁定 | 第26章 |  |
| 康王 | Prince of Kang | 锁定 | 第34章 |  |
| 建中靖国 | Jianzhong Jingguo | 锁定 | 第55章 |  |
| 开荤 | break one's vow of abstinence | [建议] | 第79章 | 候选：break one's vow of abstinence / eat meat again（按出现频次推荐 `break one's vow of abstinence`，待确认） |
| 张叔夜 | Zhang Shuye | 锁定 | 第34章 |  |
| 强人所难 | force someone against their will | 锁定 | 第62章 |  |
| 当头一棒 | A crushing blow | [建议] | 第51章 | 候选：A crushing blow / Like a bolt from the blue（按出现频次推荐 `A crushing blow`，待确认） |
| 当家主母 | Head Matriarch | [建议] | 第51章 | 候选：Head Matriarch / Head wife / Mistress of the household / Ruling Mistress（按出现频次推荐 `Head Matriarch`，待确认） |
| 待字闺中 | Awaiting marriage | [建议] | 第40章 | 候选：Awaiting marriage / Unmarried（按出现频次推荐 `Awaiting marriage`，待确认） |
| 心怀鬼胎 | Harboring sinister designs | [建议] | 第96章 | 候选：Harboring sinister designs / Treacherous intent（按出现频次推荐 `Harboring sinister designs`，待确认） |
| 心有灵犀一点通 | telepathic connection | [建议] | 第58章 | 候选：telepathic connection / two hearts beating as one（按出现频次推荐 `telepathic connection`，待确认） |
| 心知肚明 | know in one's heart | 锁定 | 第55章 |  |
| 性情中人 | A person of true feeling | [建议] | 第91章 | 候选：A person of true feeling / A real, unfiltered person（按出现频次推荐 `A person of true feeling`，待确认） |
| 恕罪 | forgive | 锁定 | 第60章 |  |
| 恨情和梦更无聊 | Regret comes to me in dream. There is no escape | 锁定 | 第9章 |  |
| 悍妇 | Tigress | [建议] | — | 由复合词条 `母老虎 / 悍妇` 拆分，需人工定译 |
| 悠悠编辑 | Editor Youyou | 锁定 | 第1章 |  |
| 情何以堪 | How can one bear it? | [建议] | 第51章 | 候选：How can one bear it? / How can one face it?（按出现频次推荐 `How can one bear it?`，待确认） |
| 慈空 | Master Cikong | 锁定 | 第27章 |  |
| 我见犹怜 | so pitiful that even I feel sorry | 锁定 | 第82章 |  |
| 戒色 | abstain from sex | 锁定 | 第85章 |  |
| 手稿 | manuscript | 锁定 | 第56章 |  |
| 打保票 | guarantee | 锁定 | 第85章 |  |
| 打倒 | Down with | 锁定 | 第81章 |  |
| 执手 | holding hands | 锁定 | 第83章 |  |
| 扶危济困 | Aiding the imperiled and assisting the destitute | 锁定 | 第39章 |  |
| 扶正 | Promote to primary wife | 锁定 | 第51章 |  |
| 承佛慈力 | "By the Compassionate Power of the Buddha" | 锁定 | 第25章 |  |
| 折可存 | Zhe Kecun | 锁定 | 第37章 |  |
| 披帛 | Drape | [建议] | 第66章 | 候选：Drape / Pibo / Silk Scarf（按出现频次推荐 `Drape`，待确认） |
| 披风 | Cape | [建议] | 第70章 | 候选：Cape / Cloak（按出现频次推荐 `Cape`，待确认） |
| 拆字谜 | Chinese character puzzle | 锁定 | 第23章 |  |
| 拨浪鼓 | pellet drum | 锁定 | 第88章 |  |
| 拱手致谢 | cup one's hands in salute to express thanks | 锁定 | 第53章 |  |
| 指印 | fingerprint | 锁定 | 第61章 |  |
| 按指印 | Red ink paste | [建议] | — | 由复合词条 `印朱 / 按指印` 拆分，需人工定译 |
| 排办局 | Bureau of Logistics | 锁定 | 第54章 |  |
| 接风洗尘 | welcome banquet | 锁定 | 第59章 |  |
| 提举 | Intendant | 锁定 | 第18章 |  |
| 提亲 | Formal proposal | [建议] | 第75章 | 候选：Formal proposal / To propose marriage（按出现频次推荐 `Formal proposal`，待确认） |
| 搭茬 | interrupt butting in | 锁定 | 第86章 |  |
| 摩睺罗 | Mo Hou Luo (Miniature Clay Dolls) | 锁定 | 第98章 |  |
| 政和 | Zhenghe | 锁定 | 第55章 |  |
| 教诲 | guidance | [建议] | 第59章 | 候选：guidance / instructions（按出现频次推荐 `guidance`，待确认） |
| 散官 | Sinecure | [建议] | 第34章 | 候选：Sinecure / Unofficial（按出现频次推荐 `Sinecure`，待确认） |
| 文以载道 | convey the Way | 锁定 | 第1章 |  |
| 文心 | Wenxin | 锁定 | 第54章 |  |
| 文慧 | Wenhui | 锁定 | 第40章 |  |
| 文秀 | Wenxiu | 锁定 | 第40章 |  |
| 断片 | Blackout | [建议] | 第74章 | 候选：Blackout / Memory loss（按出现频次推荐 `Blackout`，待确认） |
| 新宅 | new residence | 锁定 | 第63章 |  |
| 方腊 | Fang La | 锁定 | 第37章 |  |
| 方腊起义 | Fang La Rebellion | 锁定 | 第71章 |  |
| 族中长辈 | clan elders | 锁定 | 第60章 |  |
| 无子 | Failure to bear a son | 锁定 | 第23章 |  |
| 无风不起浪 | There is no smoke without fire | 锁定 | 第99章 |  |
| 时辰 | hour | [建议] | 第8章 | 候选：hour / time（按出现频次推荐 `hour`，待确认） |
| 明媒正娶 | Legally wed | [建议] | 第51章 | 候选：Legally wed / Marry through proper matchmaking（按出现频次推荐 `Legally wed`，待确认） |
| 昏君 | Incompetent Emperor | [建议] | 第34章 | 候选：Incompetent Emperor / Tyrant（按出现频次推荐 `Incompetent Emperor`，待确认） |
| 暗送秋波 | exchange secret glances | 锁定 | 第84章 |  |
| 曲径通幽 | Winding paths to secluded spots | 锁定 | 第10章 |  |
| 曹经略使 | Military Commissioner Cao | 锁定 | 第55章 |  |
| 曹雪芹 | Cao Xueqin | 锁定 | 第1章 |  |
| 月桂 | Yuegui | 锁定 | 第12章 |  |
| 月老 | The Old Man Under the Moon | [建议] | 第41章 | 候选：The Old Man Under the Moon / Yue Lao / the Matchmaker God（按出现频次推荐 `The Old Man Under the Moon`，待确认） |
| 月钱 | monthly allowance | 锁定 | 第57章 |  |
| 有失妇德 | Lose one's wifely virtue | 锁定 | 第51章 |  |
| 有头有脸 | influential | [建议] | 第53章 | 候选：influential / prominent（按出现频次推荐 `influential`，待确认） |
| 有女怀春，吉士诱之 | A maiden in spring, a gentleman courts her | 锁定 | 第80章 |  |
| 有情人终成眷属 | lovers finally unite | 锁定 | 第57章 |  |
| 望月穿针 | Threading a needle under the moon | 锁定 | 第66章 |  |
| 木梦容 | Mu Mengrong | 锁定 | 第31章 |  |
| 未时 | the hour of wei (1-3 pm) | 锁定 | 第63章 |  |
| 朱勔 | Zhu Mian | 锁定 | 第34章 |  |
| 朱淑真 | Zhu Shuzhen | 锁定 | 第3章 |  |
| 杀杀威风 | take someone down a peg | 锁定 | 第54章 |  |
| 果子局 | Bureau of Fruit | 锁定 | 第54章 |  |
| 枷锁 | Chains | [建议] | 第78章 | 候选：Chains / Fetters / Shackles（按出现频次推荐 `Chains`，待确认） |
| 校场 | Drill Ground | [建议] | — | 由复合词条 `校场 / 验兵台` 拆分，需人工定译 |
| 桂花糯米藕 | Osmanthus Glutinous Rice Lotus Root | 锁定 | 第68章 |  |
| 桂花酿 | Osmanthus Wine | [建议] | 第68章 | 候选：Osmanthus Wine / osmanthus wine（按出现频次推荐 `Osmanthus Wine`，待确认） |
| 桃之夭夭，灼灼其华 | Peach blossoms so fair, glowing bright and clear | 锁定 | 第55章 |  |
| 桃花饭 | Peach Blossom Rice | 锁定 | 第28章 |  |
| 桥头瓦 | Qiaotou Wa | 锁定 | 第99章 |  |
| 梁师成 | Liang Shicheng | 锁定 | 第34章 |  |
| 检校太傅 | Honorary Grand Tutor | 锁定 | 第34章 |  |
| 楚楚可怜 | pitiful and delicate | 锁定 | 第82章 |  |
| 榻 | couch | [建议] | 第53章 | 候选：couch / daybed / kang bed-sitting platform / low platform bed（按出现频次推荐 `couch`，待确认） |
| 欺君之罪 | Crime of Deceiving the Sovereign | 锁定 | 第6章 |  |
| 歌伎 | Singing girls | [建议] | 第10章 | 候选：Singing girls / Songstresses / female performers / singing girl / singing girls（按出现频次推荐 `Singing girls`，待确认） |
| 正室 | Primary wife | [建议] | 第3章 | 候选：Primary wife / Legal wife / Main wife / the first wife / the legitimate wife（按出现频次推荐 `Primary wife`，待确认） |
| 正思正念 | Right Thought and Right Mindfulness | 锁定 | 第51章 |  |
| 死对头 | Nemesis | [建议] | 第69章 | 候选：Nemesis / Sworn enemy（按出现频次推荐 `Nemesis`，待确认） |
| 段晖 | Duan Hui | 锁定 | 第32章 |  |
| 母夜叉 | Female Yaksha | [建议] | 第5章 | 候选：Female Yaksha / She-devil / a vicious shrew（按出现频次推荐 `Female Yaksha`，待确认） |
| 母老虎 | Shrew | [建议] | 第52章 | 候选：Shrew / Tigress / shrew / tigress（按出现频次推荐 `Shrew`，待确认） |
| 毒害 | corrupt | [建议] | 第81章 | 候选：corrupt / poison（按出现频次推荐 `corrupt`，待确认） |
| 毒打 | brutal beating | 锁定 | 第58章 |  |
| 比试 | Match | 锁定 | 第2章 |  |
| 民脂民膏 | The People's Blood and Sweat | 锁定 | 第34章 |  |
| 水文字 | Fluff | [建议] | 第1章 | 候选：Fluff / Padding the word count（按出现频次推荐 `Fluff`，待确认） |
| 水灵 | fresh and lively | 锁定 | 第85章 |  |
| 永宁居 | Yongning Residence | 锁定 | 第85章 |  |
| 江南女词人 | The Poetess of Jiangnan | 锁定 | 第10章 |  |
| 汴梁 | Bianliang | 锁定 | 第32章 |  |
| 油烛局 | Bureau of Lighting | 锁定 | 第54章 |  |
| 油面蜜糖 | Fried Flour and Honey Sweets (Qiqiao-guo) | [建议] | — | 由复合词条 `乞巧果 / 油面蜜糖` 拆分，需人工定译 |
| 泥人 | clay figurine | 锁定 | 第83章 |  |
| 泼妇 | shrew | 锁定 | 第62章 |  |
| 洗耳恭听 | I'm all ears | 锁定 | 第8章 |  |
| 活卖契约 | Conditional Sale Contract | 锁定 | 第38章 |  |
| 流星赶月 | Meteor Chasing the Moon | 锁定 | 第36章 |  |
| 流氓 | hooligan | 锁定 | 第89章 |  |
| 流芳百世 | be remembered for generations | 锁定 | 第65章 |  |
| 海涵 | to show forbearance | 锁定 | 第7章 |  |
| 淫 | Adultery | [建议] | 第23章 | 候选：Adultery / Unchastity (首选)（按出现频次推荐 `Adultery`，待确认） |
| 深院重关春寂寂 | Spring is a deep courtyard of many locked doors | 锁定 | 第9章 |  |
| 清平乐 | Pure Peace and Joy | [建议] | 第80章 | 候选：Pure Peace and Joy / Qingpingle（按出现频次推荐 `Pure Peace and Joy`，待确认） |
| 清誉 | Honor | [建议] | 第8章 | 候选：Honor / Reputation / honor / reputation（按出现频次推荐 `Honor`，待确认） |
| 渣男 | Playboy | [建议] | — | 由复合词条 `花心大萝卜 / 渣男` 拆分，需人工定译 |
| 温盏 | Warming the Tea Bowl | 锁定 | 第26章 |  |
| 湖水 | Lake | [建议] | — | 由复合词条 `湖水 / 荷叶 / 花骨朵` 拆分，需人工定译 |
| 溪水 | Mountain stream | [建议] | — | 由复合词条 `溪水 / 山泉` 拆分，需人工定译 |
| 满地找牙 | pick teeth from the ground | 锁定 | 第88章 |  |
| 火炕 | Fire Pit | [建议] | 第33章 | 候选：Fire Pit / Hot Bed（按出现频次推荐 `Fire Pit`，待确认） |
| 灵魂 | soul | 锁定 | 第83章 |  |
| 照壁 | Screen wall | [建议] | 第41章 | 候选：Screen wall / Spirit screen（按出现频次推荐 `Screen wall`，待确认） |
| 燕云十六州 | Sixteen Prefectures of Yanyun | [建议] | 第71章 | 候选：Sixteen Prefectures of Yanyun / The Sixteen Prefectures of Yanyun（按出现频次推荐 `Sixteen Prefectures of Yanyun`，待确认） |
| 父母之命媒妁之言 | parents' orders and matchmakers' words | 锁定 | 第58章 |  |
| 父母之命，媒妁之言 | Parents' orders and matchmaker's words | 锁定 | 第67章 |  |
| 爽文 | Power fantasy | [建议] | 第1章 | 候选：Power fantasy / Wish-fulfillment fiction（按出现频次推荐 `Power fantasy`，待确认） |
| 狭路相逢 | meet on a narrow path | 锁定 | 第56章 |  |
| 猪能上树 | unless pigs can climb trees | 锁定 | 第55章 |  |
| 玉体金钗一样娇 | Spring night, my jade body is soft as a gold hairpin | 锁定 | 第9章 |  |
| 玉兰树 | Magnolia Trees | 锁定 | 第13章 |  |
| 王右丞 | Wang Youcheng | [建议] | 第21章 | 候选：Wang Youcheng / Wang Wei / Wang Youcheng (Wang Wei)（按出现频次推荐 `Wang Youcheng`，待确认） |
| 王右丞诗集 | Collected Poems of Wang Youcheng | 锁定 | 第21章 |  |
| 王黼 | Wang Fu | 锁定 | 第34章 |  |
| 球头 | Lead Striker | [建议] | 第36章 | 候选：Lead Striker / Team Captain（按出现频次推荐 `Lead Striker`，待确认） |
| 琵琶 | Chinese lute | [建议] | 第55章 | 候选：Chinese lute / Pipa（按出现频次推荐 `Chinese lute`，待确认） |
| 用典 | Historical allusions | 锁定 | 第19章 |  |
| 用膳厅 | Dining Hall | 锁定 | 第7章 |  |
| 田根 | Land Root | [建议] | 第38章 | 候选：Land Root / Original Title Deed（按出现频次推荐 `Land Root`，待确认） |
| 男儿膝下有黄金 | A man's knees are made of gold | 锁定 | 第62章 |  |
| 病秧子 | sickly prince | 锁定 | 第57章 |  |
| 登徒子 | lecher | 锁定 | 第88章 |  |
| 白堤 | Bai Causeway | 锁定 | 第67章 |  |
| 白头偕老 | Till death do us part | [建议] | 第73章 | 候选：Till death do us part / To grow old together（按出现频次推荐 `Till death do us part`，待确认） |
| 皇亲国戚 | imperial relatives | [建议] | 第52章 | 候选：imperial relatives / Imperial Relatives / Relatives of the Crown（按出现频次推荐 `imperial relatives`，待确认） |
| 皇都春 | "Capital Spring" (Huangdou Chun) | 锁定 | 第78章 |  |
| 盗窃 | Theft | 锁定 | 第23章 |  |
| 相州 | Xiangzhou | 锁定 | 第71章 |  |
| 眉来眼去 | exchange flirtatious glances | [建议] | 第56章 | 候选：exchange flirtatious glances / exchange glances（按出现频次推荐 `exchange flirtatious glances`，待确认） |
| 看命 | Destiny Reading | 锁定 | 第32章 |  |
| 眼屎 | Eye boogers | [建议] | 第68章 | 候选：Eye boogers / Sleep in one's eyes（按出现频次推荐 `Eye boogers`，待确认） |
| 眼色 | awareness | [建议] | 第83章 | 候选：awareness / tact（按出现频次推荐 `awareness`，待确认） |
| 知州 | Prefect | 锁定 | 第34章 |  |
| 知己 | confidant | [建议] | 第52章 | 候选：confidant / close friend / soulmate（按出现频次推荐 `confidant`，待确认） |
| 石杵 | stone pestle | 锁定 | 第9章 |  |
| 石臼 | stone mortar | 锁定 | 第9章 |  |
| 研磨 | to grind ink | 锁定 | 第9章 |  |
| 碎银 | Loose silver | [建议] | 第49章 | 候选：Loose silver / Silver scraps（按出现频次推荐 `Loose silver`，待确认） |
| 磕三个响头 | kowtow three times with a loud sound | 锁定 | 第90章 |  |
| 礼数 | etiquette | [建议] | 第60章 | 候选：etiquette / propriety（按出现频次推荐 `etiquette`，待确认） |
| 祖母（已故） | Late Grandmother | 锁定 | 第40章 |  |
| 神柳 | Divine Willow | [建议] | 第53章 | 候选：Divine Willow / Sacred Willow（按出现频次推荐 `Divine Willow`，待确认） |
| 神课 | Divine Divination | 锁定 | 第32章 |  |
| 禀报 | to report (to a superior) | 锁定 | 第7章 |  |
| 福气 | blessing | [建议] | 第62章 | 候选：blessing / good fortune（按出现频次推荐 `blessing`，待确认） |
| 离家出走 | Running away from home | 锁定 | 第78章 |  |
| 租子 | Rent | [建议] | 第14章 | 候选：Rent / Tenancy tax / Tenant rent（按出现频次推荐 `Rent`，待确认） |
| 秦晋之好 | Marital alliance | [建议] | 第14章 | 候选：Marital alliance / Tie the knot（按出现频次推荐 `Marital alliance`，待确认） |
| 穴位 | Acupoints | 锁定 | 第33章 |  |
| 窈窕淑女，君子好逑 | A modest maiden is a fit wife for a gentleman | 锁定 | 第80章 |  |
| 立秋 | Beginning of Autumn | 锁定 | 第89章 |  |
| 竖大拇指 | give a thumbs-up | 锁定 | 第53章 |  |
| 章献明肃皇后 | Empress Zhangxian Mingsu (Liu E) | 锁定 | 第95章 |  |
| 童贯 | Tong Guan | 锁定 | 第34章 |  |
| 竹兰居 | Zhulan Residence | [建议] | 第4章 | 候选：Zhulan Residence / Zhulan Pavilion / Bamboo and Orchid Court / Bamboo and Orchid Pavilion（按出现频次推荐 `Zhulan Residence`，待确认） |
| 竹屋 | Bamboo House | [建议] | 第29章 | 候选：Bamboo House / Bamboo Hut（按出现频次推荐 `Bamboo House`，待确认） |
| 竹筒饭 | Bamboo Tube Rice | 锁定 | 第29章 |  |
| 竹篮打水一场空 | Fetching water with a wicker basket | [建议] | 第75章 | 候选：Fetching water with a wicker basket / To end in vain（按出现频次推荐 `Fetching water with a wicker basket`，待确认） |
| 笑容可掬 | beaming with smiles | 锁定 | 第55章 |  |
| 算卦 | Divination | [建议] | — | 由复合词条 `占卜 / 算卦` 拆分，需人工定译 |
| 米氏 | Concubine Mi | [建议] | 第40章 | 候选：Concubine Mi / Madam Mi（按出现频次推荐 `Concubine Mi`，待确认） |
| 粉丝群 | Fan group (chat) | 锁定 | 第1章 |  |
| 糯米藕 | Glutinous Rice Lotus Root | 锁定 | 第68章 |  |
| 紫砂壶 | purple clay teapot | 锁定 | 第9章 |  |
| 紫薇花树 | crepe myrtle tree | 锁定 | 第57章 |  |
| 红口白牙 | red mouth and white teeth | 锁定 | 第86章 |  |
| 红杏出墙 | have affairs | [建议] | 第84章 | 候选：have affairs / red apricot over the wall（按出现频次推荐 `have affairs`，待确认） |
| 红绸 | Red Silk Ribbon | [建议] | 第27章 | 候选：Red Silk Ribbon / red silk / red silk ribbon / Prayer Ribbon / Red Ribbons / Red Silk / Red silk ribbon（按出现频次推荐 `Red Silk Ribbon`，待确认） |
| 红颜薄命 | A beautiful woman's fate is hard | [建议] | 第54章 | 候选：A beautiful woman's fate is hard / Beauty is ill-fated（按出现频次推荐 `A beautiful woman's fate is hard`，待确认） |
| 纨绔子弟 | Dandy | [建议] | 第20章 | 候选：Dandy / Dandyish youths / Fops / Playboy / Playboys / dandy / playboy / 纨绔 son（按出现频次推荐 `Dandy`，待确认） |
| 纳妾 | take a concubine | 锁定 | 第58章 |  |
| 练兵官 | Military Training Officer | [建议] | 第3章 | 候选：Military Training Officer / Military Training Official / training officer（按出现频次推荐 `Military Training Officer`，待确认） |
| 练兵署 | Military Training Office | [建议] | 第50章 | 候选：Military Training Office / The Drill Command / Military Training Office (Lianbing Shu) / Training Office（按出现频次推荐 `Military Training Office`，待确认） |
| 练家子 | Martial artist | [建议] | 第3章 | 候选：Martial artist / Trained fighter（按出现频次推荐 `Martial artist`，待确认） |
| 统领 | Commandant | [建议] | 第96章 | 候选：Commandant / Commander / Commander) / Tongling (Commandant（按出现频次推荐 `Commandant`，待确认） |
| 绿桃 | Lutao | [建议] | 第11章 | 候选：Lutao / Lvtao（按出现频次推荐 `Lutao`，待确认） |
| 绿色的通话键 | green call button | 锁定 | 第1章 |  |
| 编派 | badmouth | [建议] | 第58章 | 候选：badmouth / speak ill of（按出现频次推荐 `badmouth`，待确认） |
| 网文 | Web fiction | [建议] | 第1章 | 候选：Web fiction / Web novel（按出现频次推荐 `Web fiction`，待确认） |
| 网文界 | Web novel community | [建议] | 第1章 | 候选：Web novel community / Web novel scene（按出现频次推荐 `Web novel community`，待确认） |
| 网暴 | Cancel culture | [建议] | 第1章 | 候选：Cancel culture / Cyberbullying / Online hate mob（按出现频次推荐 `Cancel culture`，待确认） |
| 美言几句 | put in a good word | 锁定 | 第7章 |  |
| 老东家 | Proprietor | [建议] | — | 由复合词条 `东家 / 老东家` 拆分，需人工定译 |
| 老相好 | old flame | 锁定 | 第84章 |  |
| 老苦 | Old Ku | 锁定 | 第29章 |  |
| 耳目一新 | refreshing and new | 锁定 | 第65章 |  |
| 肠粉 | Steamed rice roll | 锁定 | 第2章 |  |
| 腐肌膏 | Corrosive Paste | [建议] | 第17章 | 候选：Corrosive Paste / Flesh-corroding Ointment（按出现频次推荐 `Corrosive Paste`，待确认） |
| 自作孽 | bring disaster upon oneself | 锁定 | 第58章 |  |
| 自作孽不可活 | One reaps what one sows | [建议] | 第99章 | 候选：One reaps what one sows / Self-inflicted ruin（按出现频次推荐 `One reaps what one sows`，待确认） |
| 舞伎 | dancing girl | [建议] | 第10章 | 候选：dancing girl / Dancers / Dancing girls / courtesan / dancing girls / female dancer / female dancers（按出现频次推荐 `dancing girl`，待确认） |
| 艮岳 | Genyue | 锁定 | 第34章 |  |
| 良田铺子 | Estates and storefronts | [建议] | 第31章 | 候选：Estates and storefronts / Fertile fields and shops（按出现频次推荐 `Estates and storefronts`，待确认） |
| 节度使 | Jiedushi | [建议] | 第72章 | 候选：Jiedushi / Jiedushi (Military Governor) / Military Commissioner / Military Governor（按出现频次推荐 `Jiedushi`，待确认） |
| 花心大萝卜 | A total playboy | [建议] | 第91章 | 候选：A total playboy / Two-timing carrot（按出现频次推荐 `A total playboy`，待确认） |
| 花甲之年 | Past sixty years of age | 锁定 | 第40章 |  |
| 花痴 | love-struck | 锁定 | 第52章 |  |
| 花笺 | Ornamental paper | [建议] | — | 由复合词条 `花笺 / 笺纸` 拆分，需人工定译 |
| 花骨朵 | Lake | [建议] | — | 由复合词条 `湖水 / 荷叶 / 花骨朵` 拆分，需人工定译 |
| 苍蝇屎 | fly speck | 锁定 | 第88章 |  |
| 苏堤 | Su Causeway | 锁定 | 第67章 |  |
| 苟且之事 | illicit affair | 锁定 | 第85章 |  |
| 苦修 | Ascetic practice | [建议] | 第27章 | 候选：Ascetic practice / Asceticism（按出现频次推荐 `Ascetic practice`，待确认） |
| 草民 | commoner | 锁定 | 第53章 |  |
| 荡然无存 | completely gone | [建议] | 第53章 | 候选：completely gone / vanished without a trace（按出现频次推荐 `completely gone`，待确认） |
| 荷叶 | Lake | [建议] | — | 由复合词条 `湖水 / 荷叶 / 花骨朵` 拆分，需人工定译 |
| 莱宝 | Laibao | 锁定 | 第12章 |  |
| 莱州 | Laizhou | 锁定 | 第31章 |  |
| 菊花 | Chrysanthemum | 锁定 | 第11章 |  |
| 落花和雨夜迢迢 | Petals falling in falling rain make the night seem forever | 锁定 | 第9章 |  |
| 落花流水 | Fallen Flowers and Flowing Water | 锁定 | 第36章 |  |
| 葱花肉 | Minced Pork with Scallions | [建议] | 第68章 | 候选：Minced Pork with Scallions / Scallion Pork（按出现频次推荐 `Minced Pork with Scallions`，待确认） |
| 蓬头垢面 | Unkempt and disheveled | 锁定 | 第68章 |  |
| 蔡京 | Cai Jing | 锁定 | 第34章 |  |
| 蔡邕 (蔡伯喈) | Cai Yong (Cai Bojie) | 锁定 | 第30章 |  |
| 藕花 | lotus flowers | 锁定 | 第80章 |  |
| 虚写 | imaginary description | [建议] | 第80章 | 候选：imaginary description / poetic license（按出现频次推荐 `imaginary description`，待确认） |
| 蜜煎局 | Bureau of Confections | 锁定 | 第54章 |  |
| 蜜饯 | Candied Preserves | [建议] | 第58章 | 候选：Candied Preserves / Honeyed Fruits / candied fruit / preserved fruit（按出现频次推荐 `Candied Preserves`，待确认） |
| 被休 | To be cast out | [建议] | 第8章 | 候选：To be cast out / to be cast out / to be repudiated（按出现频次推荐 `To be cast out`，待确认） |
| 装模作样 | put on an act | 锁定 | 第55章 |  |
| 西三胡同 | West Third Alley | [建议] | 第53章 | 候选：West Third Alley / West Three Alley / Xisan Hutong（按出现频次推荐 `West Third Alley`，待确认） |
| 覆水难收 | what's done cannot be undone | 锁定 | 第83章 |  |
| 觥筹交错 | cups and wine tokens crisscrossing | 锁定 | 第55章 |  |
| 诊金 | Consultation fee | 锁定 | 第37章 |  |
| 词坛前辈 | senior in the ci poetry world | 锁定 | 第79章 |  |
| 词坛双璧 | Twin Jewels of Ci Poetry | 锁定 | 第3章 |  |
| 词女之夫 | Husband of the Poetess | 锁定 | 第76章 |  |
| 诗会 | Poetry Banquet | [建议] | 第10章 | 候选：Poetry Banquet / Poetry Gathering / Poetry Salon / poetry gathering（按出现频次推荐 `Poetry Banquet`，待确认） |
| 诗会（文人雅集） | poetry salon | [建议] | 第18章 | ⚠️ 疑似 `诗会` 的别名/异写，建议合并为同一词条 |
| 诗眼 | Poetic core | 锁定 | 第19章 |  |
| 话本 | Huaben | [建议] | 第30章 | 候选：Huaben / Prompt-book / Storybook / Storytelling Manuscript / Storytelling Script / Vernacular short stories / story scripts / storytelling script / storytelling scripts（按出现频次推荐 `Huaben`，待确认） |
| 说话 | Storytelling | 锁定 | 第30章 |  |
| 请帖 | Invitation Card | 锁定 | 第51章 |  |
| 谈恋爱 | Dating | [建议] | — | 由复合词条 `谈恋爱 / 不以结婚为目的恋爱是耍流氓` 拆分，需人工定译 |
| 豆浆 | Soy milk | 锁定 | 第2章 |  |
| 豆腐脑 | Tofu pudding | 锁定 | 第2章 |  |
| 貌若潘安 | Handsome as Pan An | 锁定 | 第33章 |  |
| 负鼓盲翁 | The Blind Drummer | 锁定 | 第30章 |  |
| 财产分割 | execute the division of property | 锁定 | 第5章 |  |
| 费心 | take the trouble | 锁定 | 第59章 |  |
| 赏花钓鱼宴 | Flower-Viewing and Fishing Banquet | 锁定 | 第5章 |  |
| 赐婚 | Imperial Betrothal | 锁定 | 第6章 |  |
| 走一步看一步 | take it one step at a time | 锁定 | 第53章 |  |
| 赵太丞 | Grand Physician Zhao | 锁定 | 第33章 |  |
| 赵太丞家 | Grand Physician Zhao's Residence | 锁定 | 第33章 |  |
| 赵朴 | Zhao Pu | 锁定 | 第32章 |  |
| 赵朴（仪王） | Prince Yi | [建议] | 第6章 | 候选：Prince Yi / Zhao Pu（按出现频次推荐 `Prince Yi`，待确认）；⚠️ 疑似 `赵朴` 的别名/异写，建议合并为同一词条 |
| 起死回生 | brought back to life | [建议] | 第54章 | 候选：brought back to life / resurrection（按出现频次推荐 `brought back to life`，待确认） |
| 跳舞的 | dancers | [建议] | 第79章 | 候选：dancers / dancing girls（按出现频次推荐 `dancers`，待确认） |
| 蹴鞠 | Cuju | [建议] | 第36章 | 候选：Cuju / Ancient Chinese Football / ancient Chinese football（按出现频次推荐 `Cuju`，待确认） |
| 身孕 | pregnancy | 锁定 | 第9章 |  |
| 身有恶疾 | Afflicted with a severe illness | 锁定 | 第23章 |  |
| 轮回崖 | Reincarnation Cliff | 锁定 | 第100章 |  |
| 轻描淡写 | downplay | [建议] | 第58章 | 候选：downplay / make light of（按出现频次推荐 `downplay`，待确认） |
| 辱没门楣 | Tarnishing the family reputation | 锁定 | 第8章 |  |
| 辽国 | Liao Dynasty | [建议] | 第71章 | 候选：Liao Dynasty / Liao State（按出现频次推荐 `Liao Dynasty`，待确认） |
| 过嘴瘾 | have a verbal spat | 锁定 | 第56章 |  |
| 迎宾处 | Reception Area | 锁定 | 第55章 |  |
| 远迎 | welcome from afar | 锁定 | 第59章 |  |
| 送外卖 | Food Delivery | [建议] | 第67章 | 候选：Food Delivery / Takeout Service（按出现频次推荐 `Food Delivery`，待确认） |
| 选亲 | bride selection | 锁定 | 第56章 |  |
| 透心凉 | Chilled to the bone | 锁定 | 第51章 |  |
| 通判 | Vice-Prefect | 锁定 | 第18章 |  |
| 造化弄人 | Irony of destiny | [建议] | 第74章 | 候选：Irony of destiny / Trick of fate（按出现频次推荐 `Irony of destiny`，待确认） |
| 道貌岸然 | hypocritical | [建议] | 第52章 | 候选：hypocritical / sanctimonious（按出现频次推荐 `hypocritical`，待确认） |
| 郎才女貌 | A talented man and a beautiful woman | 锁定 | 第69章 |  |
| 郡主 | Commandery Princess | [建议] | 第32章 | 候选：Commandery Princess / County Princess（按出现频次推荐 `Commandery Princess`，待确认） |
| 酉时 | Hour of the Rooster (5 PM to 7 PM) | 锁定 | 第100章 |  |
| 酩酊大醉 | dead drunk | [建议] | 第82章 | 候选：dead drunk / thoroughly drunk（按出现频次推荐 `dead drunk`，待确认） |
| 释然 | feel relieved | 锁定 | 第59章 |  |
| 重和 | Chonghe | 锁定 | 第55章 |  |
| 重生 | Rebirth | [建议] | 第4章 | 候选：Rebirth / Resurgence（按出现频次推荐 `Rebirth`，待确认） |
| 野有死麕 | "A Dead Deer in the Wild" | 锁定 | 第80章 |  |
| 金口玉言 | The Sovereign's word is law | [建议] | 第7章 | 候选：The Sovereign's word is law / imperial words / the Sovereign's word is law / words from the emperor's mouth（按出现频次推荐 `The Sovereign's word is law`，待确认） |
| 金国 | Jin Dynasty | [建议] | 第71章 | 候选：Jin Dynasty / Jin State（按出现频次推荐 `Jin Dynasty`，待确认） |
| 钱氏 | Madam Qian | 锁定 | 第40章 |  |
| 钱袋 | Money Pouch | 锁定 | 第33章 |  |
| 铁杆粉丝 | die-hard fan | 锁定 | 第65章 |  |
| 银子 | Silver | 锁定 | 第8章 |  |
| 银杏 | Yinxing | [建议] | 第10章 | 候选：Yinxing / Ginkgo（按出现频次推荐 `Yinxing`，待确认） |
| 银枪蜡头 | all flash and no steel—pretty to look at, useless in a fight | 锁定 | 第23章 |  |
| 银镯子 | silver bracelet | 锁定 | 第88章 |  |
| 锁和钥匙 | lock and key | 锁定 | 第59章 |  |
| 锦盒 | brocade box | 锁定 | 第6章 |  |
| 长命百岁金锁 | Longevity Gold Lock | 锁定 | 第11章 |  |
| 长廊 | Long Corridor | 锁定 | 第55章 |  |
| 长辈 | elders | 锁定 | 第62章 |  |
| 门楣 | Family Honor | [建议] | 第77章 | 候选：Family Honor / Family Reputation（按出现频次推荐 `Family Honor`，待确认） |
| 闪避 | Dodge | [建议] | 第2章 | 候选：Dodge / Evasion（按出现频次推荐 `Dodge`，待确认） |
| 闫媒婆 | Matchmaker Yan | 锁定 | 第22章 |  |
| 阳春白雪 | "Spring Snow" (Highbrow art) | 锁定 | 第30章 |  |
| 阿弥陀佛 | Amitabha | 锁定 | 第97章 |  |
| 附庸风雅 | affecting literary airs | 锁定 | 第5章 |  |
| 附庸风雅的玩意儿 | fancy word games | [建议] | 第23章 | 候选：fancy word games / flowery pretentious garbage / pretentious poetry nonsense（按出现频次推荐 `fancy word games`，待确认） |
| 陆放翁 | Lu You | [建议] | — | 由复合词条 `陆游 / 陆放翁` 拆分，需人工定译 |
| 陆游 | Lu You | [建议] | — | 由复合词条 `陆游 / 陆放翁` 拆分，需人工定译 |
| 陈世美 | Chen Shimei | 锁定 | 第30章 |  |
| 陈家 | The Chen Family | 锁定 | 第38章 |  |
| 陈词滥调 | clichés | 锁定 | 第65章 |  |
| 随大流 | follow the crowd | 锁定 | 第55章 |  |
| 隐疾 | Hidden illness | [建议] | 第51章 | 候选：Hidden illness / Private ailment（按出现频次推荐 `Hidden illness`，待确认） |
| 青州从事 | Qingzhou Inspector | [建议] | 第19章 | 候选：Qingzhou Inspector / Qingzhou wine attendants（按出现频次推荐 `Qingzhou Inspector`，待确认） |
| 青梅竹马，两小无猜 | innocently devoted childhood sweethearts | 锁定 | 第4章 |  |
| 青楼（泛指） | Qinglou | [建议] | 第3章 | ⚠️ 疑似 `青楼` 的别名/异写，建议合并为同一词条 |
| 青清 | Qingqing | 锁定 | 第81章 |  |
| 非分之想 | improper thoughts | 锁定 | 第52章 |  |
| 非礼 | Assault | [建议] | 第51章 | 候选：Assault / Molest（按出现频次推荐 `Assault`，待确认） |
| 顽石 | Boulders | [建议] | 第49章 | 候选：Boulders / Stubborn rocks（按出现频次推荐 `Boulders`，待确认） |
| 风度翩翩 | Elegant and Refined | 锁定 | 第33章 |  |
| 风流眼 | Goal Ring | [建议] | 第36章 | 候选：Goal Ring / The Flowing Wind Eye（按出现频次推荐 `Goal Ring`，待确认） |
| 饮料 | Beverage | [建议] | 第69章 | 候选：Beverage / Soft Drink（按出现频次推荐 `Beverage`，待确认） |
| 马步 | Horse Stance | 锁定 | 第33章 |  |
| 鬼主意 | tricky ideas | 锁定 | 第87章 |  |
| 鬼门关 | Gates of Hell | 锁定 | 第6章 |  |
| 魏玩 | Lady Wei | [建议] | — | 由复合词条 `魏夫人/魏玩` 拆分，需人工定译 |
| 黄梅细雨 | plum rain drizzle | 锁定 | 第80章 |  |
| 黄粱一梦 | A fleeting dream | [建议] | 第69章 | 候选：A fleeting dream / A golden millet dream（按出现频次推荐 `A fleeting dream`，待确认） |
| 黎民百姓 | the common people | 锁定 | 第53章 |  |
| 鼓凳 | drum stools | 锁定 | 第54章 |  |

---

## 八 待裁定清单（[!]）

> 共 309 条，列出前 120 条。**逐条确认后改状态为 `锁定`，并回溯已产出章节。**

| # | 中文 | 推荐定译 | 现有候选/问题 |
|---|---|---|---|
| 1 | 勾栏 | Goulan (Theater | Goulan (Theater / Performance Hall) |
| 2 | 蜜饯 | Candied Preserves | Candied Preserves / Honeyed Fruits / candied fruit / preserved fruit |
| 3 | 和衣睡倒人怀 | Falling asleep in his arms, fully dressed | Falling asleep in his arms, fully dressed / Falling asleep in someone’s arms while dressed |
| 4 | 性情中人 | A person of true feeling | A person of true feeling / A real, unfiltered person |
| 5 | 花心大萝卜 | A total playboy | A total playboy / Two-timing carrot |
| 6 | 境界参差不齐 | Mixed aesthetic standards | Mixed aesthetic standards / Varied levels of enlightenment |
| 7 | 官家赐婚 | Imperial Marriage Decree | Imperial Marriage Decree / Royal |
| 8 | 电灯泡 | Light bulb | Light bulb / Lightbulb / Third Wheel / Third wheel |
| 9 | 当家主母 | Head Matriarch | Head Matriarch / Head wife / Mistress of the household / Ruling Mistress |
| 10 | 七夕节 | Qixi Festival | Qixi Festival / Double Seventh Festival / The Double Seventh |
| 11 | 下里巴人 | "Lowbrow art" (Popular and unrefined) | "Lowbrow art" (Popular and unrefined) / Lower-brow / Vernacular art |
| 12 | 亏大发 | A huge loss | A huge loss / To get the short end of the stick |
| 13 | 临安节度使 | Military Commissioner of Lin'an | Military Commissioner of Lin'an / Regional Governor of Lin'an / Jiedushi of Lin'an (Military Governor) |
| 14 | 练兵署 | Military Training Office | Military Training Office / The Drill Command / Military Training Office (Lianbing Shu) / Training Office |
| 15 | 节度使 | Jiedushi | Jiedushi / Jiedushi (Military Governor) / Military Commissioner / Military Governor |
| 16 | 统领 | Commandant | Commandant / Commander / Commander) / Tongling (Commandant |
| 17 | 燕云十六州 | Sixteen Prefectures of Yanyun | Sixteen Prefectures of Yanyun / The Sixteen Prefectures of Yanyun |
| 18 | 心怀鬼胎 | Harboring sinister designs | Harboring sinister designs / Treacherous intent |
| 19 | 聚香楼 | Gathering Fragrance Tower | Gathering Fragrance Tower / Juxiang Lou / Juxiang Lou (Pavilion of Gathering Fragrance) / Juxiang Restaurant |
| 20 | 红绸 | Red Silk Ribbon | Red Silk Ribbon / red silk / red silk ribbon / Prayer Ribbon / Red Ribbons / Red Silk / Red silk ribbon |
| 21 | 母夜叉 | Female Yaksha | Female Yaksha / She-devil / a vicious shrew |
| 22 | 自作孽不可活 | One reaps what one sows | One reaps what one sows / Self-inflicted ruin |
| 23 | 银杏 | Yinxing | Yinxing / Ginkgo |
| 24 | 府衙 | prefecture office | prefecture office / Government Office / Prefectural Office |
| 25 | 歌伎 | Singing girls | Singing girls / Songstresses / female performers / singing girl / singing girls |
| 26 | 舞伎 | dancing girl | dancing girl / Dancers / Dancing girls / courtesan / dancing girls / female dancer / female dancers |
| 27 | 诗会 | Poetry Banquet | Poetry Banquet / Poetry Gathering / Poetry Salon / poetry gathering |
| 28 | 迷宫 | Labyrinth | Labyrinth / Maze |
| 29 | 竹兰居 | Zhulan Residence | Zhulan Residence / Zhulan Pavilion / Bamboo and Orchid Court / Bamboo and Orchid Pavilion |
| 30 | 绿桃 | Lutao | Lutao / Lvtao |
| 31 | 佛堂 | Buddhist Shrine | Buddhist Shrine / Buddhist hall / Family Temple / family temple |
| 32 | 嫁妆 | Dowry | Dowry / dowry |
| 33 | 租子 | Rent | Rent / Tenancy tax / Tenant rent |
| 34 | 女子无才便是德 | "A woman's virtue is having no talent" | "A woman's virtue is having no talent" / "Ignorance is a woman's virtue" |
| 35 | 秦晋之好 | Marital alliance | Marital alliance / Tie the knot |
| 36 | 腐肌膏 | Corrosive Paste | Corrosive Paste / Flesh-corroding Ointment |
| 37 | 韦嬷嬷 | Matron Wei | Matron Wei / Nanny Wei |
| 38 | 幽栖居士 | Youqi Jushi | Youqi Jushi / Hermit of Youqi / Householder Youqi / Lay Buddhist Youqi / Zhu Shuzhen |
| 39 | 易安居士 | Yi'an Jushi | Yi'an Jushi / Li Qingzhao |
| 40 | 诗会（文人雅集） | poetry salon | 疑似别名，与主词条 `诗会` 重复 |
| 41 | 诗会（正式宴会） | poetry banquet | 疑似别名，与主词条 `诗会` 重复 |
| 42 | 茶师 | performer | performer / tea artisan / tea master |
| 43 | 斗茶 | Tea Competition | Tea Competition / Tea Whisking Contest / tea competition / whisking contest |
| 44 | 包间 | booth | booth / private room |
| 45 | 青州从事 | Qingzhou Inspector | Qingzhou Inspector / Qingzhou wine attendants |
| 46 | 孔方兄 | Brother Kong Fang | Brother Kong Fang / Lord Square Hole |
| 47 | 子虚子 | Sir Fantasy | Sir Fantasy / Sir Vacuity |
| 48 | 老娘 | Yours truly | Yours truly / This queen / "this lady" / I (emphasized) / Old lady |
| 49 | 家人们 | Chat | Chat / Fam / Guys |
| 50 | 网暴 | Cancel culture | Cancel culture / Cyberbullying / Online hate mob |
| 51 | 网文 | Web fiction | Web fiction / Web novel |
| 52 | 网文界 | Web novel community | Web novel community / Web novel scene |
| 53 | 水文字 | Fluff | Fluff / Padding the word count |
| 54 | 口水文 | Drivel | Drivel / Vapid writing |
| 55 | 爽文 | Power fantasy | Power fantasy / Wish-fulfillment fiction |
| 56 | 小白文 | Brainless read | Brainless read / Fast-food fiction / Shallow fiction |
| 57 | 亲家姑娘 | Affinal family's daughter | Affinal family's daughter / Sister-in-law (by marriage) |
| 58 | 勾栏瓦肆 | Goulan Wasi | Goulan Wasi / Entertainment quarters / Entertainment Precincts / entertainment district / entertainment quarters / pleasure quarters |
| 59 | 纨绔子弟 | Dandy | Dandy / Dandyish youths / Fops / Playboy / Playboys / dandy / playboy / 纨绔 son |
| 60 | 乔贵妃 | Consort Qiao | Consort Qiao / Noble Consort Qiao |
| 61 | 王右丞 | Wang Youcheng | Wang Youcheng / Wang Wei / Wang Youcheng (Wang Wei) |
| 62 | 西院 | West Courtyard | West Courtyard / west courtyard |
| 63 | 治淤青的药 | bruise medicine | bruise medicine / bruise-healing ointment |
| 64 | 《断肠谜》 | "The Heartbreak Riddle" | "The Heartbreak Riddle" / "Heartbreak Riddle" |
| 65 | 七出 | Seven Conditions for Repudiating a Wife | Seven Conditions for Repudiating a Wife / Seven Grounds for Divorce |
| 66 | 淫 | Adultery | Adultery / Unchastity (首选) |
| 67 | 口多言 | Gossip | Gossip / Talkativeness |
| 68 | 和离 | mutual divorce | mutual divorce / Amicable Divorce / An amicable divorce / Divorce by mutual agreement / Mutual Divorce / a mutual divorce / amicable divorce / amicable parting / consensual divorce / the separation / the split |
| 69 | 休书 | Letter of Divorce | Letter of Divorce / letter of repudiation |
| 70 | 被休 | To be cast out | To be cast out / to be cast out / to be repudiated |
| 71 | 附庸风雅的玩意儿 | fancy word games | fancy word games / flowery pretentious garbage / pretentious poetry nonsense |
| 72 | 林家三叔 | Third Uncle Lin | Third Uncle Lin / the Third Uncle |
| 73 | 秀珍嬷嬷 | Matron Xiuzhen | Matron Xiuzhen / Nanny Xiuzhen |
| 74 | 南双 | Nan Shuang | Nan Shuang / Nanshuang |
| 75 | 寮房 | Monastic Living Quarters | Monastic Living Quarters / Monks' Quarters |
| 76 | 功德箱 | Donation Box | Donation Box / Merit Box |
| 77 | 击拂 | Whisking | Whisking / to whisk |
| 78 | 苦修 | Ascetic practice | Ascetic practice / Asceticism |
| 79 | 地桃花 | Caesarweed | Caesarweed / Urena lobata |
| 80 | 竹林 | bamboo grove | bamboo grove / Bamboo Forest |
| 81 | 苦蕨 | Kujue | Kujue / Ku Jue |
| 82 | 竹屋 | Bamboo House | Bamboo House / Bamboo Hut |
| 83 | 师父 | Master | Master / Shifu |
| 84 | 申拳 | Shen Fist | Shen Fist / Shen Fist (School) |
| 85 | 快拳 | Quick Fist | Quick Fist / Rapid Strikes |
| 86 | 闪避 | Dodge | Dodge / Evasion |
| 87 | "月上柳梢头，人约黄昏后" | "The moon above a willow tree | "The moon above a willow tree / Shone on my lover close to me." |
| 88 | "除非猪能上树" | "When pigs can climb trees" | "When pigs can climb trees" / "When pigs fly" |
| 89 | 话本 | Huaben | Huaben / Prompt-book / Storybook / Storytelling Manuscript / Storytelling Script / Vernacular short stories / story scripts / storytelling script / storytelling scripts |
| 90 | 夏果 | Xiaguo | Xiaguo / Xia Guo |
| 91 | 良田铺子 | Estates and storefronts | Estates and storefronts / Fertile fields and shops |
| 92 | 邹嬷嬷 | Nurse Zou | Nurse Zou / Nanny Zou |
| 93 | 邹嬷嬷 | Matron Zou | Nanny Zou / Nurse Zou → Matron Zou |
| 94 | 官家 | His Majesty | His Majesty / the Emperor / The Emperor / The Sovereign |
| 95 | 郡主 | Commandery Princess | Commandery Princess / County Princess |
| 96 | 脚店 | Jiao Dian | Jiao Dian / Rest Tavern |
| 97 | 天之美禄 | Heaven's Beautiful Boon | Heaven's Beautiful Boon / Heaven's Fine Gift |
| 98 | 内侍 | Imperial Attendant | Imperial Attendant / Inner Attendant / Palace Eunuch |
| 99 | 点穴 | Acupoint Pressing | Acupoint Pressing / Dim Mak |
| 100 | 火炕 | Fire Pit | Fire Pit / Hot Bed |
| 101 | 散官 | Sinecure | Sinecure / Unofficial |
| 102 | 昏君 | Incompetent Emperor | Incompetent Emperor / Tyrant |
| 103 | 水泊梁山 | The Marshes of Mount Liang | The Marshes of Mount Liang / Water Margins of Mount Liang |
| 104 | 蹴鞠 | Cuju | Cuju / Ancient Chinese Football / ancient Chinese football |
| 105 | 风流眼 | Goal Ring | Goal Ring / The Flowing Wind Eye |
| 106 | 球头 | Lead Striker | Lead Striker / Team Captain |
| 107 | 丹青 | Danqing | Danqing / Ink and Color |
| 108 | 朱晞颜 | Zhu Xiyan | Zhu Xiyan / Prefect Zhu |
| 109 | 临安府 | Lin'an Prefecture | Lin'an Prefecture → X Manor |
| 110 | 说话艺人 | storyteller | storyteller / Professional Storyteller / Storyteller / Storytelling Performer / storytellers / storytelling artists |
| 111 | 招安 | Amnesty | Amnesty / Pacification |
| 112 | 林府 | Lin Manor | Lin Manor / The Lin Manor |
| 113 | 田根 | Land Root | Land Root / Original Title Deed |
| 114 | 匾额 | Inscribed Board | Inscribed Board / Wooden Plaque |
| 115 | 朱府老爷 | Father Zhu | Father Zhu / Lord Zhu |
| 116 | 姑爷 | Son-in-law | Son-in-law / Young Master (son-in-law) / young master / Master / Master Lin / her husband / the lord |
| 117 | 练兵官 | Military Training Officer | Military Training Officer / Military Training Official / training officer |
| 118 | 临安知府 | Prefect of Lin'an | Prefect of Lin'an → X Manor |
| 119 | 春香楼 | Chunxiang Brothel | Chunxiang Brothel / Chunxiang Pavilion |
| 120 | 青楼（泛指） | Qinglou | 疑似别名，与主词条 `青楼` 重复 |

---

## 九 变更记录

| 日期 | 变更 | 理由 | 影响范围 |
|---|---|---|---|
| 2026-09-02 | 建表 v0.9：463 条锁定 / 304 条建议 / 复合词条拆分 42 条 | 由 90 章术语文件回溯抽取 | 全书（后续由 export_trados.py 导出 CAT 格式） |

> ⚠️ 待人工裁定完成前，`[建议]` 条目不得直接用于新章初译；初译时如遇 `[建议]` 词条，按「忠实原文 > 术语锁 > 表达自然」处理并上报。
