# Awwwards 证据基线

访问日期：2026-07-20

## 使用规则

把材料分成三层：

1. **官方事实**：Awwwards、W3C、web.dev 的直接说明；
2. **样本归纳**：从获奖项目页面提取的重复模式，不代表 Awwwards 官方规定；
3. **项目决策**：团队为特定受众、品牌和约束作出的选择。

不得把后两层写成官方规则。涉及当前奖项政策、评委、价格或趋势时重新联网核验。

## 官方事实

| 事实 | 核验结果 | 来源 |
|---|---|---|
| 平台性质 | Awwwards 自述为表彰全球网页设计师、开发者与机构的奖项与专业社区；它不是单一设计公司。 | https://www.awwwards.com/about-us/ |
| 主评审维度 | Design 40%、Usability 30%、Creativity 20%、Content 10%。 | https://www.awwwards.com/about-evaluation/ |
| 评审过程 | 官方称每个通过初审的网站至少发送给 18 名评委，去掉距离平均值最远的 3 个分数，投票通常持续 5 天。 | https://www.awwwards.com/about-evaluation/ |
| Honorable Mention | Evaluation 页面写 Jury 分数达到 6.5；FAQ 进一步写 Jury 与 Users 两边都需达到 6.5。两页存在口径差异，报告应披露并采用更严格口径，不能只写单一门槛。 | https://www.awwwards.com/about-evaluation/ 与 https://www.awwwards.com/faqs/ |
| Site of the Day | 官方没有公布固定分数线，只说明由高分项目竞争每日唯一名额。不得发明 SOTD 阈值。 | https://www.awwwards.com/about-evaluation/ |
| Developer Award | 官方称 SOTD 项目进入开发者评审，得分高于 7 可获 Developer Award；目标包括跨现代浏览器/设备的质量代码、移动优化、无障碍与包容性。 | https://www.awwwards.com/about-evaluation/ 与 https://www.awwwards.com/developer-award/ |
| 开发者维度 | 当前项目页可见 Semantics/SEO、Animations/Transitions、Accessibility、WPO、Responsive Design、Markup/Meta-data 六维。官方链接的旧版指南含历史权重，但文档版本陈旧；不要把旧权重当作当前确定规则。 | https://www.awwwards.com/sites/glitch-grit 与 https://www.awwwards.com/developer-award/ |

### 门槛声明模板

> 本报告按 Awwwards 公布的四维权重做内部预评，不代表 Awwwards 官方评审或获奖保证。Honorable Mention 的官方页面存在口径差异；本报告采用更严格的“双 6.5”解释。SOTD 没有公开固定分数线。

## 2026 样本观察

以下项目用于证明“获奖级”不是单一皮肤。标签、分数与描述来自各项目官方页面。

| 项目 | 官方页面呈现 | 可迁移观察，不是官方规则 |
|---|---|---|
| Glitch&Grit，SOTD 7.17 | 两色；Typography、Video、Transitions、Portfolio；开发者评分 6.67，Accessibility 5.8。 | 简洁调色与强内容框架也可获奖；SOTD 不等于技术与无障碍完美，因此发布门禁必须独立。 |
| IZANAMI，SOTD 7.19 + DEV | 两色；Scrolling、Typography、Storytelling、Copy design、WebGL、GSAP。 | 高技术表达与文案/叙事共同构成概念，技术不是孤立装饰。 |
| CoffeeTech，SOTD 7.18 + DEV | Clean、Minimal、Transitions、360、3D；商业技术产品。 | 工业产品可用克制布局配合单一产品展示机制，不必默认暗黑或艺术站。 |
| PP Neue Montreal，SOTD 7.41 + DEV | Experimental、Animation、Clean、Colorful、Fullscreen、Graphic design、Motion。 | 字体产品把产品本身变成叙事和交互媒介；“干净”与“实验”可以并存。 |
| Brunello Cucinelli AI E-com，SOTD 7.19 + DEV | Luxury、Clean、Unusual Navigation、Interaction Design；突出移动行为、视觉搜索与产品页。 | 商业创新要落在发现、搜索和购买任务，而不是只做展示性动效。 |
| MONOLOG，SOTD 7.43 + DEV + Typography Honors | Clean、Flat Design、Typography、GSAP、Three.js；强调 statement hero 与 storytelling。 | 签名表达可以来自排版与叙事，3D 只需承担局部概念角色。 |

直接来源：

- https://www.awwwards.com/sites/glitch-grit
- https://www.awwwards.com/sites/izanami
- https://www.awwwards.com/sites/coffeetech-r
- https://www.awwwards.com/sites/pp-neue-montreal
- https://www.awwwards.com/sites/brunello-cucinelli-ai-e-com
- https://www.awwwards.com/sites/monolog
- 当前 SOTD 列表：https://www.awwwards.com/websites/sites_of_the_day/

## 官方专题页提供的边界

- Awwwards 的 Minimal 专题把 balance、alignment、contrast 视为极简设计基础，而不是把极简等同于空白或灰色：https://www.awwwards.com/websites/minimal/
- UI Design 专题明确关联 user-centered design、information architecture、prototyping、research、user testing 与 usability：https://www.awwwards.com/websites/ui-design/
- Animation 专题认为动效可突出界面并提升互动，但这不是要求每个项目使用动画：https://www.awwwards.com/websites/animation/
- E-commerce 专题强调商品展示、购物车、客服与结账等完整购买体验：https://www.awwwards.com/websites/e-commerce/

## 外部发布标准

| 领域 | 默认门槛 | 一手来源 |
|---|---|---|
| Core Web Vitals | 以真实用户第 75 百分位、移动端与桌面端分别评估：LCP ≤2.5s、INP ≤200ms、CLS ≤0.1。实验室数据只作诊断，不能冒充真实用户数据。 | https://web.dev/articles/vitals |
| WCAG | 默认以 WCAG 2.2 AA 为发布目标；普通文字对比度至少 4.5:1，大文字至少 3:1；所有功能可键盘操作；焦点可见且不被遮挡。 | https://www.w3.org/TR/WCAG22/ |
| 自动运动 | 自动开始、持续超过 5 秒且与其他内容并行的运动内容，需要暂停、停止或隐藏机制。 | https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html |
| 交互动效 | 非必要交互动效应能关闭或响应 `prefers-reduced-motion`。WCAG 2.2 的 Animation from Interactions 是 AAA；本 Skill 把它作为更严格的项目门禁，不冒充 AA 最低要求。 | https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html |
| 目标尺寸 | WCAG 2.2 AA 最低目标为 24×24 CSS px 或满足间距例外；44×44 是更严格的 AAA/易用性目标，引用时要区分等级。 | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum 与 https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced |

## 不确定性处理

- 页面、截图或原型只能支持视觉与部分交互判断，不能证明真实性能、语义结构或辅助技术兼容性。
- Lighthouse 单次实验室分数不能证明 Core Web Vitals 通过。
- 第三方标签或团队自述不能证明可用性与原创性。
- 没有用户研究时，用“启发式判断”而不是“用户已验证”。
- 没有 Awwwards 官方结果时，用“内部预评”“候选方向”，不用“达到 SOTD”或“会获奖”。
