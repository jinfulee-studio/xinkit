# SSR 方法保真档案

## 来源（来源级别①：已发表论文 + 官方开源实现）

- 论文：Maier et al., *LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings*, [arXiv 2510.08338](https://arxiv.org/abs/2510.08338)（PyMC Labs × Colgate-Palmolive, 2025-10）
- 官方实现：[pymc-labs/semantic-similarity-rating](https://github.com/pymc-labs/semantic-similarity-rating)（`compute.py::similarities_to_pmf` 已逐行对齐到本 skill 的 `scripts/score_ssr.py`）
- 验证规模：57 份真实问卷 / 9,300 真人回应；达人类 test-retest 信度 90%（ρ 相关性获得率），分布 KS 相似度 >0.85

## 核心公式（禁改）

```
sim        = (1 + cosine(response, anchor)) / 2          # 缩放至 [0,1]
numerator  = sim - min_row(sim)；ε 加在最小位（ε 默认 0）
denominator= sum_row(sim) - K·min_row(sim) + ε
pmf_set    = numerator / denominator                      # 每锚点集
pmf        = mean(pmf_set over sets)                      # 多集平均（论文 6 集）
pmf(T)     ∝ pmf^(1/T)                                    # 温度，论文 T=1
expected   = Σ pmf_r · r,  r ∈ 1..5
```

## 论文设置 vs 本实现偏差清单（诚实披露，报告必引）

| 维度 | 论文 | 本实现 | 影响评估 |
|------|------|--------|---------|
| 嵌入模型 | OpenAI text-embedding-3-small | BAAI/bge-small-zh-v1.5（本地，免 key） | 论文实测 small↔large 差异可忽略，嵌入模型选择不敏感；中文语料用中文优化模型更合理。[未经配对验证] |
| 锚点集 | 6 集英文 | 3 集中文（anchors-zh.json） | 集数减半轻微降稳健；锚点语言与感想语言一致是必要条件 |
| 受访 LLM | GPT-4o / Gemini-2.0-flash，T_LLM=0.5，n=2/prompt | Claude（sonnet 默认），n=1/persona | 论文显示方法对 LLM 选择稳健；n=1 用 persona 多样性补采样多样性 |
| persona 条件 | 年龄/性别/收入/地区/族裔 | 同 + 痛点/使用场景/预算等扩展字段 | 更丰富的条件 → 更分散的文本 → SSR 区分度更好 |
| 验证域 | 个护快消品（CPG） | 任意产品（**未经真人校准**） | 跨域外推风险：绝对值不可当转化率，用于排序/方向判断 |
| 价格处理 | 概念图含价格 | 价格变体注入 persona 卡片（群内 round-robin 正交） | 支持需求曲线/弹性估计（论文未做价格 A/B） |

## Dogfood 实测发现（2026-06-13，SEE Dashboard n=1000）

1. **价格 A/B 维度灵敏度不足（红旗）**：4 价格点（$9/$19/$49/$99）top-2-box 全局 37.7%→38.5% 几乎平坦，连预算最敏感的学生群也无下行反应（37.2%@$19 → 39.6%@$99）。根因 [分析性结论]：LLM 角色扮演会为看到的任何价格自圆其说（叙事顺应），且 14 天免费试用话术软化价格异议；SSR 把「贵但心动」与「便宜且心动」的文本映射到相近意向。**论文本身只验证了概念排序，未验证价格弹性——价格 A/B 是本 skill 的扩展，当前设计下其输出只能当方向参考，禁止当结论交付。** 改进方向：价格显著性强化（强制 persona 给出「愿意/不愿意按此价付费」的明确表态句）或改用 Van Westendorp 四问式。
2. **分群排序对嵌入模型敏感（初版「排序扎实」断言已被自家对照实验推翻）**：bge-small-zh vs bge-large-zh 两版 8 群排序 Spearman ρ=0.524（中度）——组内统计 SE 小 ≠ 跨模型稳健。**强制纪律：正式报告必须双模型重评分，只交付两版一致的结论**（上/下半区归属、方向性差异），位次翻转的群标注「模型敏感」。large 版还修复了 small 的口语意向误判（「先上再说/不试白不试」类无"买"字表态，案例 P0085 2.20→3.10），默认模型已切 bge-large-zh-v1.5。
5. **最可信产出排序**：① 质性痛点语料 + 主题提取（opus 在 125 条/群语料里能读出数值层丢失的价格语言梯度）② 跨模型一致的群间方向差异 ③ 总体意向水位（两模型 3.0-3.3 / 38-40%）。数值绝对值与精细位次最弱。
3. **JSON 转义损坏率 12/50 批**：sonnet 在中文感想里写英文双引号致 JSON 失效。已双层根治：validate_batches.py 自愈修复（内容零损伤，239/240 自动恢复）+ 访谈 prompt 禁英文双引号改中文引号「」。
4. **漏写率 1/1000**：单 agent 漏 1 个 persona，由覆盖门控捕获 + 单人补批闭环。验证了「agent 报成功 ≠ 产物完整，必须脚本终审」。

## 设计决策记录

1. **不直接依赖官方 pip 包**：包的 ResponseRater 绑定 OpenAI 嵌入工作流；本地 bge 嵌入 + 自实现 30 行公式（逐行对齐官方源码）换来零 API key 依赖 + 全离线可复现。
2. **判断归心搜集归脚本**：persona 卡起草、报告解读 = 心/agent 判断；展开、评分、聚合 = 确定性脚本（seed 固定）。
3. **访谈 agent 用 sonnet**：机械生成类（路由表合规）；主题提取用 opus（评审类）。
4. **agent 输出背压**：感想正文一律写文件，agent 最终回复仅一行计数（subagent fan-out 预算铁律）。
