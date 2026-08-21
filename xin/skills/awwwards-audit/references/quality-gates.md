# 发布质量门禁

## 状态与严重度

- 状态：`PASS` / `FAIL` / `UNKNOWN` / `N/A`
- 严重度：P0 / P1 / P2 / P3
- `N/A` 必须说明为什么不适用。
- 没测过的发布关键项标 `UNKNOWN`，不按 0 分，也不默认通过。

P0 是确认的不可降级阻断，任何 P0 FAIL 都是 NO-GO。P1 是发布前必须解决或由真实发布权责人完整接受的高风险。P0/P1 UNKNOWN 都是 HOLD。表中级别是最低严重度：可向 P0 升级，不可降级。

## 门禁目录

| ID | 默认级别 | 门禁 | 最低证据 |
|---|---|---|---|
| Q-G01 | P0 | 核心任务完整 | 主要用户能在目标环境完成主任务；无死路、数据丢失或不可恢复失败 |
| Q-G02 | P0 | 输入方式可操作 | 键盘、触摸和主要输入方式可完成关键导航/表单/购买/联系；无键盘陷阱 |
| Q-G03 | P1→P0 | 内容真实性与资产权利 | 客户、指标、奖项、声明与授权可追溯；确认欺骗/侵权/高影响误导时升 P0 |
| Q-G04 | P1→P0 | 动效安全与控制 | 自动运动可停止、用户可控制；危险闪烁、核心任务阻断或关键内容无替代时升 P0 |
| Q-G05 | P1→P0 | WCAG 2.2 A/AA | 语义、名称/角色/值、焦点、对比、替代内容、字幕、错误与缩放有自动+人工证据；关键路径完全无替代时升 P0 |
| Q-G06 | P1 | 响应式与内容完整 | 320 CSS px、200% 文本、横竖屏和主要断点无关键内容/功能丢失 |
| Q-G07 | P1 | 性能与稳定 | 当前字段数据或可复现预发布实验室证据；无持续阻塞主线程、严重布局跳动或首屏资源失控 |
| Q-G08 | P1 | 回退与渐进增强 | JavaScript、视频、WebGL、字体或第三方失败时核心内容与任务可用 |
| Q-G09 | P1→P0 | 错误、表单与交易 | 标签、验证、错误恢复、确认、重复提交、付款/数据风险按业务场景通过；高影响付款/隐私/数据损失升 P0 |
| Q-G10 | P1 | 浏览器/设备/辅助技术范围 | 已批准的矩阵有实测证据；未覆盖范围清楚 |
| Q-G11 | P2 | SEO/语义/元数据 | 标题、描述、结构化内容、分享元数据、索引策略与语义正确 |
| Q-G12 | P1 | 分析、监测与回滚 | 关键事件、错误、CWV、回滚触发与责任人明确；最终发布不得未知 |

门禁级别可因业务提高，不能为了上线降低；评分器拒绝低于表中最低级别的输入。每个 `PASS/FAIL` 至少引用一条 `MEASURED` 或 `OBSERVED` 证据，否则降为 `UNKNOWN`。

`PASS` 还必须引用与 Gate 能力相符的证据类型：

| Gate | PASS 所需证据类型 |
|---|---|
| Q-G01 / Q-G02 / Q-G06 / Q-G09 / Q-G10 | `runtime_walkthrough` 或 `user_test` |
| Q-G03 | `content_record` 或 `asset_license` |
| Q-G04 | `runtime_walkthrough` |
| Q-G05 | `runtime_walkthrough/user_test`，并加 `code_inspection/automated_scan/lab_measurement` |
| Q-G07 | production 必须 `field_data`；staging 可用合格 `lab_measurement` 暂行证明 |
| Q-G08 | `runtime_walkthrough` |
| Q-G11 | `code_inspection` 或 `automated_scan` |
| Q-G12 | `release_plan` |

`FAIL` 同样必须有足以直接观察对应失败的证据类型：

| Gate | FAIL 可接受的直接证据类型 |
|---|---|
| Q-G01 / Q-G02 | `runtime_walkthrough`、`user_test` 或 `code_inspection` |
| Q-G03 | `content_record` 或 `asset_license` |
| Q-G04 | `runtime_walkthrough` 或 `lab_measurement` |
| Q-G05 | `runtime_walkthrough`、`user_test`、`code_inspection`、`automated_scan` 或 `lab_measurement` |
| Q-G06 / Q-G10 | `runtime_walkthrough` 或 `user_test` |
| Q-G07 | `lab_measurement` 或 `field_data` |
| Q-G08 | `runtime_walkthrough` 或 `code_inspection` |
| Q-G09 | `runtime_walkthrough`、`user_test` 或 `code_inspection` |
| Q-G11 | `code_inspection` 或 `automated_scan` |
| Q-G12 | `release_plan` |

目标环境与访问方式分开记录。目标是 staging、但实际只拿到截图时，`access_mode` 仍是 `screenshots`。证据类型与访问方式不兼容时输入无效；只靠截图不能把键盘、语义、性能或回退标为确定性 `PASS/FAIL`。没有测到不等于失败，应标 `UNKNOWN`。

## 不可风险接受的 P0

以下确认问题始终 P0：

- 主要用户在主要环境无法完成核心任务；
- 键盘陷阱或核心路径只支持 hover/拖动且无等价替代；
- 会造成癫痫风险的闪烁；
- 关键内容或操作完全没有可访问替代；
- 虚构客户、指标、奖项或关键产品能力；
- 未经授权使用会造成明确法律风险的资产；
- 已确认的高影响安全、付款、隐私或数据损失问题。

P0 不能通过总分、期限、Owner 或风险接受变成 GO。

## WCAG 2.2 A/AA 检查

至少人工检查：

- 页面语言、标题、landmarks、标题层级和阅读顺序；
- 所有功能键盘可操作，焦点可见、不被遮挡并按逻辑移动；
- 普通文字对比度 ≥4.5:1，大文字 ≥3:1；非文本控件/状态按适用条款检查；
- 320 CSS px 重排；文本放大 200% 不丢内容和功能；
- AA 目标尺寸至少 24×24 CSS px 或满足标准例外；关键操作可设项目目标 44×44；
- 图片替代、视频字幕/文字替代、音频控制；
- 自动开始且超过 5 秒的并行运动可暂停、停止或隐藏；
- 项目严格目标：交互动效可关闭或响应 `prefers-reduced-motion`。WCAG 2.2 的 Animation from Interactions 是 AAA，不冒充 AA 最低要求；
- 表单标签、错误识别、建议、状态消息和身份验证；
- 自定义组件的 name/role/value 与状态。

自动扫描只能补充，不能替代键盘、焦点、缩放、运动、语义和屏幕阅读器抽检。

## 性能门禁

### 已上线且有字段数据

移动端与桌面端分别看真实用户第 75 百分位：

- LCP ≤2.5s；
- INP ≤200ms；
- CLS ≤0.1。

任一指标不达标时为 FAIL；覆盖不足或窗口/样本不可靠时为 UNKNOWN，并说明数据量与时间窗。

### 预发布且无字段数据

不能声称“Core Web Vitals 已通过”。可以把 Q-G07 标为 PASS（prelaunch provisional），但必须同时满足：

- 在已批准的代表性设备、网络和页面上多次实验室测量；
- 记录中位数、波动、工具版本和节流条件；
- 检查实际 LCP 元素、长任务、布局偏移来源和第三方脚本；
- 有上线后字段监测、责任人、阈值和回滚/降级方案。

缺任一项为 UNKNOWN/HOLD。Lighthouse 总分不能替代上述证据。

## 动效与沉浸技术

对 video、Canvas、WebGL、3D、页面转场、视差、横滚、磁吸光标逐项检查：

- 目的：Orientation / Causality / Hierarchy / Narrative / Delight；
- 用户触发与取消；
- 键盘/触摸等价；
- reduced-motion 与低性能回退；
- 内容/任务是否仍可达；
- GPU/CPU、内存、主线程和网络影响；
- 页面隐藏、离屏、失焦时是否停止不必要工作。

“Awwwards 常见”不是采用理由，也不是通过证据。

## 审批记录

完整 P1 风险接受必须同时包含：

```text
approver: 真实姓名或可验证身份
approver_role: 有权接受该风险的角色
decision: ACCEPT_RISK
quote: 明确接受哪项风险的原文
timestamp: 含时区
version: 产物 URL/commit/version
scope: 接受范围与排除范围
owner: 整改责任人
due: 到期时间
approval_evidence_id: 指向证据账本中 OBSERVED 的签名工单/审批记录
verified_by: 与作者和批准者不同的核验人
verified_at: 独立核验时间，含时区
verification_attestation: DECISION_AND_QUOTE_CONSISTENT
```

`approval_evidence_id` 指向的证据必须同时是 `OBSERVED + approval_record`，其结构化 gate、decision、version、scope、approver、approver_role 与 quote SHA-256 必须匹配；证据采集时间不早于批准时间且不晚于核验时间。缺任一字段或关系即不完整，决定为 HOLD。

`quote` 必须明确写出对应 Q-Gate ID，`decision` 必须是 `ACCEPT_RISK`；普通“收到”“继续”“尽快上线”不构成风险接受，明显含“拒绝/不接受/block release”等冲突语义也拒绝。结构化 decision 是机器判定依据，核验人对其他语言和上下文的语义一致性负责。时间使用有效 ISO-8601 与时区，`due` 晚于本轮 `audit_time`，记录版本与范围必须和审计完全一致。产物作者不能批准自己的最终发布，批准人也不能核验自己的记录。脚本验证记录关系，不承担身份、权限或签名系统的真实性证明。

Q-G12 是最终发布必过项；监测、回滚或责任人缺失时保持 HOLD，不允许用 P1 风险接受变成 CONDITIONAL-GO。

## 决策表

| 条件 | 决定 |
|---|---|
| ≥1 个 P0 FAIL | NO-GO |
| ≥1 个 P0 UNKNOWN | HOLD |
| ≥1 个未接受的 P1 FAIL | HOLD |
| ≥1 个 P1 UNKNOWN | HOLD |
| 仅有已完整接受的 P1 FAIL | CONDITIONAL-GO |
| 无 P0/P1 FAIL 或 UNKNOWN | GO |

作品竞争力分数不参与此决策表。
