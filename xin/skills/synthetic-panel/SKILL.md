---
name: synthetic-panel
description: "SSR 合成消费者调研面板：基于 PyMC Labs×高露洁 SSR 方法（arXiv 2510.08338），用 LLM persona 写质性感想 + 嵌入语义映射 Likert 购买意向，一夜模拟 1000 场客户访谈，输出分群购买意向分布、定价需求曲线、痛点投放文案。"
when_to_use: when user says /synthetic-panel, 合成消费者, 模拟用户调研, 合成访谈, 购买意向模拟, SSR 调研, 定价测试, 价格敏感度, PMF 快速验证, synthetic consumers, purchase intent simulation, or wants to simulate N customer interviews for a product/pricing decision; ALSO auto-propose (ux-feedback mini mode) whenever user asks 心 to 模拟产品经理/模拟用户视角 evaluating UIUX, 功能优先级, 文案 A/B, or design direction — bounded panel replaces open-ended PM roleplay
version: 1.0.0
languages: all
model: opus
effort: xhigh
user-invocable: false
---

# /synthetic-panel — SSR 合成消费者调研面板

> 方法来源：**LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings**（PyMC Labs × Colgate-Palmolive，[arXiv 2510.08338](https://arxiv.org/abs/2510.08338)，官方实现 [pymc-labs/semantic-similarity-rating](https://github.com/pymc-labs/semantic-similarity-rating)）。
> 核心思想：**不问数字，问故事** —— 直接让 LLM 打分会产生失真分布；让合成 persona 写自由文本感想，再用嵌入相似度映射到 5 级 Likert 分布，对 57 份真实问卷 / 9,300 人回应达到人类 test-retest 信度的 90%（KS 相似度 >0.85）。
> 算法细节与本实现偏差见 [reference/method.md](reference/method.md)。**禁止改公式**（来源级别①公认标准——已发表论文+官方实现）。

## 适用判断（先想清再跑）

| 适用 ✅ | 不适用 ❌ |
|---------|----------|
| 产品概念排序 / 分群意向对比（论文验证域，最可信输出） | 替代真实用户验收（合成≠真人，重大决策仍需真人数据） |
| 分群痛点挖掘 + 投放文案语料 | 法律/医疗/金融等高风险合规判断 |
| 多价格点 A/B（⚠️ 2026-06-13 实测：朴素价格注入灵敏度不足，LLM 为任何价格自圆其说——结果只当方向参考，详见 reference/method.md Dogfood 发现①） | 样本 <100 的小跑（统计噪音大，直接访谈更快） |

## 两种模式（先选模式再进管线）

| | market 模式（默认） | **ux-feedback 模式（mini 面板）** |
|---|---|---|
| 用途 | 产品概念/客群/定价调研 | **替代开放式 PM 扮演**：UIUX 方向、功能优先级、文案 A/B、空态/onboarding 等设计决策 |
| n | 500-1000 | 80-120（8 群 × 10-15，估算 ~400-600K tokens / 3-5 min） |
| 锚点 | `anchors-zh.json`（购买意向） | `anchors-ux-zh.json`（使用意愿，⚠️ 未经真人校准的构念扩展） |
| brief | 产品概念 | **界面截图（agent 可 Read 图）/ 交互流程描述 / 两版方案对比** |
| 问题 | 「你有多大可能购买？」 | 「你会用它吗？哪里让你犹豫/困惑？」（Step 3 prompt 对应替换） |
| 迭代 A/B | — | **同 seed 同 persona 面板跑改版前后**，分差+语料 diff 即证据 |


## 执行管线（7 步，全自动，主对话编排）

**SKILL_DIR** = ；**RUN_DIR** = `<项目>/research/synthetic-panel/<YYYY-MM-DD-slug>/`（非项目场景用 `~/Desktop/synthetic-panel-runs/`）。

### Step 1 — 产品概念 + 面板配置（心起草，唯一判断步）
- 写 `RUN_DIR/product-brief.md`：产品名/形态/核心功能 5-8 条/价值主张/交付方式。**价格不写在 brief 里**（由 persona 卡片注入，实现价格 A/B）。
- 写 `RUN_DIR/panel-config.json`（schema 见 [templates/panel-config.example.json](templates/panel-config.example.json)）：
  - **archetypes 5-8 个**：有会员/用户数据 → 从数据归纳；无 → 从目标市场推导。每个含 age_range/genders/regions/income_bands/pains(≥4 条)/context + 任意 numeric_attrs/categorical_attrs。
  - **price_variants**：2-5 个价格点（均匀分配到每个 archetype 内部，保证分群×价格正交）。
  - n_personas 默认 1000，batch_size 默认 20，seed 固定（可复现）。

### Step 2 — 生成 persona 实例（确定性脚本）
```bash
uv run "$SKILL_DIR/scripts/generate_personas.py" --config "$RUN_DIR/panel-config.json" --out-dir "$RUN_DIR"
```
产出 `personas.jsonl` + `batches/batch-NNN.json`。stdout 给出 batch 清单。

### Step 3 — Workflow fan-out 访谈（50 agents × 20 persona）
用 Workflow 工具，`scriptPath` = `$SKILL_DIR/templates/workflow-interviews.js`，args：
```json
{ "brief": "<RUN_DIR>/product-brief.md", "outDir": "<RUN_DIR>/out",
  "batches": [{"id":"batch-001","file":"<RUN_DIR>/batches/batch-001.json"}, ...],
  "model": "sonnet" }
```
访谈 agent = 机械生成类 → sonnet（路由表合规）。agent 只回一行计数（输出背压合规），正文写文件。

### Step 4 — 覆盖校验 + 缺失重跑（零侥幸门控）
```bash
uv run "$SKILL_DIR/scripts/validate_batches.py" --personas "$RUN_DIR/personas.jsonl" --out-dir "$RUN_DIR/out"
```
exit 0 = 100% 覆盖；exit 2 = stdout 列缺失 batch → 仅把缺失项重新跑 Step 3（同 workflow、args 只含缺失 batches）。**覆盖 <100% 禁止进 Step 5。**

### Step 5 — SSR 语义评分（官方公式，本地嵌入，免 API key）
```bash
uv run --with sentence-transformers --with numpy "$SKILL_DIR/scripts/score_ssr.py" \
  --personas "$RUN_DIR/personas.jsonl" --reviews-dir "$RUN_DIR/out" \
  --anchors "$SKILL_DIR/templates/anchors-zh.json" --run-dir "$RUN_DIR" \
  --extra-segments "地区,收入档"
```
产出 `aggregates.json`（总分布/分群/价格需求曲线/弹性）+ `quotes.json`（每群 top/bottom 引文）+ `themes-input/<archetype>.jsonl`。
**分布健全红旗**：单一 Likert 档占比 >80% → 检查锚点语言与感想语言是否一致、温度参数，修后重跑评分（不重跑访谈）。
**双模型稳健性门控（2026-06-13 dogfood 立，强制）**：再用 `--model BAAI/bge-small-zh-v1.5` 重跑一次（先 `cp aggregates.json aggregates-<model>.json` 备份），对比分群排序——**报告只交付两版一致的结论**，位次翻转的群标注「模型敏感」。两版评分都只读 `out/`，互不干扰、不重跑访谈。

### Step 6 — Workflow 主题提取（每 archetype 1 个 opus agent）
`scriptPath` = `$SKILL_DIR/templates/workflow-themes.js`，args：
```json
{ "inputs": [{"id":"<aid>","file":"<RUN_DIR>/themes-input/<aid>.jsonl"}, ...],
  "outDir": "<RUN_DIR>/themes", "brief": "<RUN_DIR>/product-brief.md" }
```
每群产出：购买驱动 top3 / 拒绝理由 top3 / 价格敏感观察 / 3 条取自 persona 原话的投放文案。

### Step 7 — 报告（心写，判断归心）
按 [templates/report-template.md](templates/report-template.md) 写 `RUN_DIR/report.md`：
- **所有数字必须引自 `aggregates.json` 真实输出**（fabrication guard——禁凭记忆填数）。
- 必含「方法与局限」段（见模板，不可删）：合成≠真人、论文验证域是 CPG 快消品、本实现偏差清单。
- 在项目内运行时：报告落 `docs/` 须同步 `docs/INDEX.md`；按项目交付铁律 commit+push。

## 质量门控（汇总）

| 门控 | 标准 | 失败动作 |
|------|------|---------|
| 覆盖率 | reviews == n_personas（100%，含已知损坏自愈修复） | 仅重跑缺失 batch |
| 分布健全 | 无单档 >80% | 查锚点/温度，重评分 |
| 双模型稳健 | large+small 两版排序对比，只交付一致结论 | 不一致项标「模型敏感」 |
| 价格正交 | 每 archetype 内各价格 n 差 ≤1（generate 脚本保证） | 重新生成 |
| 数字溯源 | 报告每个数字可在 aggregates.json 找到 | 重写报告 |
| 诚实披露 | 报告含「方法与局限」段 | 补段后才交付 |

## 成本/耗时参考（n=1000 实测口径见 method.md）
访谈 50× sonnet agent ≈ 5-10 min 墙钟；嵌入本地 bge-small-zh（首跑下载 ~50MB 模型）≈ 1-2 min；主题 8× opus ≈ 3-5 min。
