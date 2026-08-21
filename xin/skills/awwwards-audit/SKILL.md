---
user-invocable: false
name: awwwards-audit
description: 以 Awwwards 官方 Design 40% / Usability 30% / Creativity 20% / Content 10% 模型和独立发布门禁审核网站、Figma、截图、原型或前端实现，输出证据化量化报告、置信度、GO/HOLD/NO-GO 审批、根因分析、Awwwards 级优化方案和复测闭环。用于 UI/UX review、设计评审、上线审核、Awwwards 风格差距分析、可访问性/性能/动效/响应式审计、评分争议或利益相关者要求抬高分数时。
---

# 评审 Awwwards 级 UI/UX

## 审计原则

担任独立评审者，不担任分数辩护人。

1. Awwwards 是奖项和策展平台，不是单一设计公司；审核“作品竞争力”，不审核是否套中某个皮肤。
2. 作品分与发布决定完全分离。高 Design/Creativity 分不能抵消核心任务、无障碍、内容真实性或性能阻断。
3. 不按利益相关者期望倒推分数。分数必须由证据、锚点和公式产生。
4. 未测不等于失败，也不等于通过；标 `UNKNOWN`，降低置信度，并在发布关键项未知时给 `HOLD`。
5. 截图不能证明交互、语义、性能或辅助技术兼容；单次 Lighthouse 不能证明真实用户 Core Web Vitals。
6. 内部预测不得描述为 Awwwards 官方评分、SOTD 阈值或获奖保证。

## 开始前读取

- 评分、锚点、聚合与优先级：读取 [references/scoring-rubric.md](references/scoring-rubric.md)。
- 发布门禁、P0/P1 和审批逻辑：读取 [references/quality-gates.md](references/quality-gates.md)。
- 完整报告与整改任务格式：读取 [references/report-template.md](references/report-template.md)。
- 官方事实、冲突和外部标准：读取 [references/source-policy.md](references/source-policy.md)。
- 需要多人聚合或正式审批时，使用 `scripts/score_audit.py`；输入结构见 [references/sample-audit.json](references/sample-audit.json)。

若用户要求最新政策、最新获奖作品或指定 Awwwards 页面，重新访问官方来源，记录访问日期。不得仅依赖本地快照。

## 工作流

### 1. 冻结审计对象

记录：

- 项目、URL/文件、版本/commit、日期；
- 目标产物类型：`production` / `staging` / `prototype` / `figma` / `screenshots`；
- 实际访问方式：`runtime` / `interactive_prototype` / `design_file` / `screenshots`；不得因目标是 staging 而把 staging 截图写成 runtime；
- 页面、流程和排除范围；
- 关键受众、任务与业务结果；
- 视口、设备、浏览器、输入方式、语言与网络；
- 测试环境、工具、现场数据窗口；
- 提供者、审计者和潜在利益冲突。

版本不明时报告为 `PARTIAL`。审计中产物改变时创建新版本，不把新旧证据混在同一分数。

### 2. 建立证据账本

每条证据只用以下标签：

| 标签 | 含义 |
|---|---|
| `MEASURED` | 在已记录环境中测得，可复现 |
| `OBSERVED` | 评审者直接检查到 |
| `PROVIDED` | 用户或团队提供，尚未独立复核 |
| `INFERRED` | 从有限产物推断 |
| `UNKNOWN` | 没有足够证据 |
| `CONFLICT` | 可靠来源互相冲突 |

记录证据 ID、标签、证据类型、来源、环境、含时区时间、适用范围与限制。证据类型使用 `screenshot`、`design_inspection`、`prototype_walkthrough`、`runtime_walkthrough`、`code_inspection`、`lab_measurement`、`field_data`、`user_test`、`automated_scan`、`content_record`、`asset_license`、`release_plan`、`approval_record` 或 `other`。类型必须与实际访问方式相容。

所有分数、问题和门禁都引用证据 ID。`MEASURED`、`OBSERVED`、`PROVIDED`、`INFERRED` 的单项置信度上限依次为 1.0、0.8、0.6、0.4；`UNKNOWN/CONFLICT` 不能单独支撑数值分。无法访问目标时说明阻塞，并输出可完成的部分；不得模拟浏览、测试或用户反馈。

### 3. 独立评审

多 Agent 可用时，至少安排三个独立视角：

- Creative：Design + Creativity；
- UX/Content：Usability + Content；
- Engineering/A11y：响应式、语义、WPO、Accessibility 与发布门禁。

给每个评审者相同原始产物和范围，不先透露目标分数、其他评审结果或预期缺陷。记录真实评审身份与角色；只改 ID 的克隆分卡不算独立评审。让各评审者仍对四个主维度给分，以发现视角差异。Awwwards 官方使用更大评审团；内部三人模型只是质量控制，不得冒充官方流程。

只有单一评审者时，分三个隔离 pass 执行，最后再汇总；将整体置信度上限设为 0.8。

### 4. 计算作品竞争力分

按 `scoring-rubric.md` 的子项和锚点评 0–10：

`Overall = 0.40 × Design + 0.30 × Usability + 0.20 × Creativity + 0.10 × Content`

要求：

- 每个子项至少一个证据 ID 和一个反证/限制；
- 只对有证据的项评分，未知项不默认为 0；
- 评分器输入中，每个子项都写 `value`、`confidence`、`evidence_ids` 与 `limitation`；未知项使用 `value: null`、`confidence: 0`，由脚本输出 `INCOMPLETE` 与区间而不是伪精确总分；
- 同时报告分数与 0–1 置信度；
- 多评审者按维度取中位数；
- 同一维度最高与最低相差 >1.5 时标 `RECONCILE`，展示分歧，不静默平均；
- 只有满足锚点的罕见证据才给 9–10，禁止“视觉不错所以 9 分”。

脚本对 9–10 额外要求至少两个不同来源与不同证据类型，同时含 `MEASURED` 和 `OBSERVED`，置信度 ≥0.8；单张截图、单一团队提供材料或纯推断不能得到 9–10。

6.5 只能作为保守的内部 HM 比较线；官方页面对 HM 条件存在冲突。SOTD 没有公开固定分数线。

### 5. 独立执行发布门禁

逐项检查 `quality-gates.md` 的 `Q-G01`–`Q-G12`，状态只允许 `PASS`、`FAIL`、`UNKNOWN`、`N/A`。`Q-` 命名空间用于区别设计流程的 `D-Gx`。`N/A` 必须写理由。

文档给出的严重度是最低级别，可以向 P0 升级，不能向 P2/P3 降级。Q-G03 的确认欺骗/侵权/高影响误导、Q-G04 的危险闪烁或动效造成核心任务阻断、以及关键无障碍/付款/数据损失问题都升级为 P0。

决策优先级：

1. 任一 P0 `FAIL` → `NO-GO`；
2. 任一 P0 `UNKNOWN` → `HOLD`；
3. 任一 P1 `FAIL` 且无完整风险接受记录 → `HOLD`；
4. 任一 P1 `UNKNOWN` → `HOLD`；
5. P1 `FAIL` 全部有真实批准人、原文、时间、版本、范围、Owner 与期限 → `CONDITIONAL-GO`；
6. 其余 → `GO`。

P0 不可风险接受。没有门禁数据时必须 `HOLD`。门禁 `PASS/FAIL` 至少引用一条 `MEASURED` 或 `OBSERVED` 证据，否则脚本降级为 `UNKNOWN`。用脚本复算，报告中的数字和决定必须与脚本一致。

评分器会把缺失的 Q-G01–Q-G12 自动补成 `UNKNOWN`，防止通过删字段绕过门禁；Q-G12 是最终发布所需的 P1 监测/回滚门禁，必须 PASS，不允许风险接受。能力矩阵同时检查实际 `access_mode` 与各 Gate 引用的证据类型；截图、设计文件或原型不能证明的确定性 `PASS/FAIL` 结论会降级为 `UNKNOWN`。没有测到不等于失败。

可接受的 P1 风险记录必须含 `decision: ACCEPT_RISK`、精确版本/范围、未来到期时间、独立核验人、`DECISION_AND_QUOTE_CONSISTENT` 核验声明，以及专用 `approval_record` 证据。该证据的结构化 gate/decision/version/scope/approver/role/quote hash 必须匹配，记录时间位于批准与核验之间。明显包含拒绝语义的原文直接 HOLD；其他语言与上下文仍由核验人负责。脚本不能替代人类对身份、权限和签名真实性的控制。

### 6. 写问题，不写审美意见

每条 finding 包含：

`ID → 严重度 → 证据 → 受影响用户/任务 → 根因 → 对四维/门禁的影响 → 具体修复 → 验收方法 → Owner/依赖`

严重度：

- P0：安全、法律、真实性、危险动效或关键任务阻断；不可发布；
- P1：显著影响主要用户/任务或质量目标；发布前解决或正式风险接受；
- P2：明显质量差距；进入近期迭代；
- P3：精修与机会项。

不要把所有建议写成 P0/P1。把多个症状合并到共同根因，防止“修 20 个像素问题却不修信息架构”。

### 7. 生成可执行优化方案

先给两条并行轨：

- **Stabilize**：修 P0/P1、证据缺口、关键路径、内容真实性、无障碍、响应式和性能；
- **Elevate**：从品牌真相与内容资产建立原创概念、排版/网格/媒体/动效系统和一个签名机制。

每项整改写清：

- 当前问题与证据；
- 目标状态及受影响组件/页面/状态；
- 内容、设计 token、交互、响应式与技术变更；
- 移动、键盘、减少动效和失败回退；
- 可复制的验收步骤与数值门槛；
- Owner、依赖、工作量级、风险和先后关系；
- 预计改善的评分子项与门禁，但不承诺具体分数增量。

不要把“加入 3D/WebGL/视差/磁吸”当作 Awwwards 优化。先修概念、内容、任务和系统，再决定表达技术。

### 8. 自我迭代与复审

每轮：

1. 冻结 baseline 版本、分数、门禁和证据；
2. 选择一个共同根因的最小变更批次；
3. 在同环境复测；
4. 对关键任务做回归；
5. 用脚本重算；
6. 报告绝对值、差值、置信度和副作用；
7. 由独立评审决定保留、回退或继续。

不得只重测修复项。若改版尚未实施，输出 `REVIEW REQUIRED` 而不是伪造“优化后分数”。批准记录必须包含真实批准主体、原文、时间、产物版本和适用范围；作者不能批准自己的最终发布。

## 输出顺序

1. 一句话结论、版本、覆盖范围和 `GO/HOLD/NO-GO`；
2. 作品竞争力总分、四维分、置信度、评审分歧；
3. 发布门禁表；
4. 证据完整性与限制；
5. P0–P3 findings；
6. 根因图与高杠杆整改；
7. 分阶段执行计划；
8. 验收、复测与回归方案；
9. 审批记录、残余风险和下一门禁；
10. 官方事实、外部标准与项目启发式的来源分层；
11. 评分器版本、rubric 版本与输入 SHA-256，确保可复算的是同一产物。

若用户只给截图，仍按该结构输出，但交互、性能、语义、键盘与辅助技术相关项必须为 `UNKNOWN`，发布决定不得为 GO。

## 红线

- 为满足“至少 90 分”而改公式、权重、锚点或证据；
- 把未知记为通过、零分或主观猜测；
- 用平均分掩盖 P0；
- 把 Lighthouse、截图或设计稿当作生产体验全证据；
- 把旧 Developer Guideline 的技术检查项当作当前标准；
- 声称 SOTD 有固定门槛或承诺获奖；
- 给没有 Owner、验收方法和复测证据的泛泛建议；
- 在没有真实审批记录时写 `APPROVED`。
