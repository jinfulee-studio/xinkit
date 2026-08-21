# <产品名> 合成消费者调研报告（SSR，n=<N>）

> 方法：Semantic Similarity Rating（arXiv 2510.08338，PyMC Labs × Colgate-Palmolive）
> 运行：<日期> · <RUN_DIR 相对路径> · 嵌入模型 <model> · 锚点集 <k> 个 · T=<temperature>
> ⚠️ 本报告全部数字来自 `aggregates.json` 脚本输出，引文逐字来自 `scores.jsonl`。

## TL;DR（≤5 行）
<总体购买意向均值与 top-2-box、最优价格点、最强人群、最大拒绝理由、一句话行动建议>

## 1. 总体购买意向分布
| 指标 | 值 |
|------|-----|
| 期望分均值（1-5） | <overall.mean_expected> ± <std> |
| Top-2-Box（很可能买+肯定买） | <overall.top2box_pct>% |
| PMF（1→5） | <overall.pmf> |

## 2. 定价需求曲线
| 价格 | n | Top-2-Box % | 期望分 |
|------|---|------------|--------|
<demand_curve 每行>

价格拟合：<price_fit.model>，b=<b_per_ln_price>（每 ln(价格) 单位的 top2box 变化），R²=<r2>。
<解读：弹性大小、最优价格区间、是否存在分群差异化定价机会>

## 3. 分群洞察（按购买意向排序）
| 人群 | n | 期望分 | Top-2-Box % | 一句话判词 |
|------|---|--------|------------|-----------|
<by_archetype 每行 + themes/<id>.md 判词>

<每群 2-4 句：谁买、为什么买、为什么不买、价格反应 —— 引 themes/ 与 quotes.json>

## 4. 痛点投放文案精选
<从 themes/*.md 挑 5-8 条最锋利的，注明人群与来源 persona_id>

## 5. 方法与局限（不可删）
- **合成 ≠ 真人**：本结果是 LLM persona 模拟，论文在快消品（CPG）域验证达人类 test-retest 信度的 90%；**本产品所在域未经真人问卷校准**，结论用于排序与方向判断，绝对值（如 top2box）不可直接当真实转化率。
- 本实现与论文的偏差清单见 skill 的 `reference/method.md`（嵌入模型 / 锚点语言 / LLM / 采样数）。
- 建议用法：用本报告筛选 2-3 个最优概念/价格点，再投真人小样本验证。

## 复现
```bash
# 见 RUN_DIR/panel-config.json（seed 固定，全管线确定性可复现）
```
