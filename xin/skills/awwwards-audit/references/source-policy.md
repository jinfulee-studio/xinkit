# 来源与事实政策

访问日期：2026-07-20。规则可能更新；涉及“最新”、正式参赛或上线审批时重新访问原始页面。

## 来源优先级

按以下顺序处理事实：

1. 指定作品的当前官方结果页；
2. 当前、主题明确的 Awwwards 官方规则页；
3. 当前官方 FAQ 或概览页；
4. Awwwards 当前页面仍链接、但自身标注较旧的指南；
5. W3C、web.dev 等标准制定者或官方技术文档；
6. 评审者从案例归纳的模式；
7. 二手文章、社交内容和未核实陈述。

高优先级来源也可能互相冲突。遇到冲突时：

- 保留两个版本与 URL；
- 标 `CONFLICT`，不替用户偷偷选真相；
- 内部发布决策采用更保守规则；
- 正式提交、合同或公开声明前由人类向官方复核。

## Awwwards 当前官方事实

### 主评分权重

当前 Evaluation 页面公布：

- Design 40%
- Usability 30%
- Creativity 20%
- Content 10%

来源：

- https://www.awwwards.com/about-evaluation/
- https://www.awwwards.com/about-us/

### 评审流程

Evaluation 页面称每个项目由至少 18 位评审评分，去掉 3 个偏离整体均值最远的分数，并开放 5 天投票。内部 1–3 人审计只是预评和质量控制，不得称为官方复刻。

来源：https://www.awwwards.com/about-evaluation/

### Honorable Mention 冲突

- Evaluation 页面描述为 Jury score 达到至少 6.5；
- FAQ 描述为 Jury 与 Users score 都达到至少 6.5。

因此内部可把 6.5 用作保守比较线，但不得声称已经满足官方 HM 条件。

来源：

- https://www.awwwards.com/about-evaluation/
- https://www.awwwards.com/faqs/
- https://www.awwwards.com/about-status/

### Site of the Day

官方没有公开固定 SOTD 分数线。不得发明“≥7.0/7.5 即 SOTD”之类规则，也不得承诺获奖。

来源：

- https://www.awwwards.com/about-status/
- https://www.awwwards.com/websites/sites_of_the_day/

### Developer Award

当前 Evaluation 页面称，SOTD 项目会再次接受技术评审，技术分高于 7 才可获得 Developer Award；Developer Award 页面描述其代码质量、跨浏览器/设备、移动与无障碍目标。当前结果页常见技术维度包括 Semantics/SEO、Animations/Transitions、Accessibility、WPO、Responsive Design、Markup/Meta-data。

来源：

- https://www.awwwards.com/about-evaluation/
- https://www.awwwards.com/developer-award/
- Awwwards 当前获奖项目结果页

当前页面仍链接的 Developer Guideline 包含历史权重：

`WPO 20% + Responsive 20% + Markup 15% + Semantics 20% + Animation 15% + Accessibility 10%`

该文档内部修订信息较旧，技术检查也包含过时内容。只能标为 `OFFICIAL-LEGACY / IN-TRANSITION` 的代理模型，不得当作当前 Web 标准或正式获奖判定器。

## 当前案例如何使用

案例用于发现“允许哪些表达路径”，不能变成复制清单。2026 样本显示获奖作品可以是：

- 强叙事、滚动与动态排版；
- 克制、简洁、以产品或 360° 媒体为中心；
- 彩色实验排版与全屏动效；
- 奢侈品电商中的非常规导航和内容揭示；
- 平面化、排版主导的品牌体验。

案例也显示作品获得 SOTD 并不代表每个技术维度都完美。因此必须把作品竞争力分与发布门禁分开。

参考结果页：

- https://www.awwwards.com/sites/glitch-grit
- https://www.awwwards.com/sites/izanami
- https://www.awwwards.com/sites/coffeetech-r
- https://www.awwwards.com/sites/pp-neue-montreal
- https://www.awwwards.com/sites/brunello-cucinelli-ai-e-com
- https://www.awwwards.com/sites/monolog

## 外部发布标准

### WCAG 2.2

默认发布门禁使用 WCAG 2.2 A/AA，而不是旧获奖指南中的简化检查。

关键事实：

- 普通文字最低对比度 4.5:1，大文字 3:1；
- AA 目标尺寸最低 24×24 CSS px，或满足标准规定的间距/例外；
- 44×44 属于更高等级目标，可作为项目最佳实践，不能误写成 AA 必须；
- 自动开始、持续超过 5 秒且与其他内容并行的运动需要暂停、停止或隐藏机制；
- 交互触发的非必要动效应可关闭，并支持 `prefers-reduced-motion`。WCAG 2.2 的 Animation from Interactions 属于 AAA；本套件将它作为更严格的项目质量门禁，不冒充 AA 最低要求。

来源：

- https://www.w3.org/TR/WCAG22/
- https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html
- https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html
- https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html

### Core Web Vitals

真实用户字段数据在移动端与桌面端分别看第 75 百分位：

- LCP ≤2.5 秒；
- INP ≤200 毫秒；
- CLS ≤0.1。

预发布实验室测试不能宣称已通过真实用户 Core Web Vitals。

来源：https://web.dev/articles/vitals

## 事实标签

| 标签 | 可以写什么 | 禁止写什么 |
|---|---|---|
| `OFFICIAL-CURRENT` | 当前官方页面明确陈述 | 推断出的隐藏评审偏好 |
| `OFFICIAL-LEGACY` | 历史模型及其局限 | “这就是当前规则” |
| `EXTERNAL-STANDARD` | 规范的实际要求 | 把最佳实践冒充最低合规 |
| `PROJECT-EVIDENCE` | 对冻结版本的测量/观察 | 扩大到未测页面或生产环境 |
| `HEURISTIC` | 内部子权重、优先级模型 | 冒充 Awwwards 官方模型 |
| `INFERENCE` | 明示推理链与不确定性 | 写成事实 |
| `UNKNOWN` | 缺什么、如何补证据 | 默认为 PASS 或 FAIL |
| `CONFLICT` | 两个来源及保守处理 | 静默删除不方便的来源 |

## 声明规则

始终使用这些表述：

- “Awwwards 级/获奖级的内部质量代理”
- “保守内部 HM 比较线”
- “发布门禁决定”
- “基于当前证据的预测/区间”

禁止：

- “Awwwards 官方审计”
- “保证 SOTD/HM/Developer Award”
- “达到固定 SOTD 分数线”
- “照此修改即可获奖”
