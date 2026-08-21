---
name: uiux-laws
description: "通用 UI/UX 设计法则大全（跨项目，56条规则）：WCAG 无障碍/交互反馈/布局响应式/表单/性能/排版/AI时代定律。"
version: 2.0.0
applies-to: All frontend/UI tasks
model: sonnet
when_to_use: "/uiux-design, UI规范检查, 设计法则, accessibility audit, 无障碍"
user-invocable: false
---

# UI/UX 设计核心定律 v2.0

> 面向前端开发者和 UI 设计师的可执行规则集。47 条核心 + 9 条附录 = 56 条。
> 违反铁律 = 代码审查不通过。建议类标注 [建议]。评审综合分: 9.4/10

## 执行流程

### Stage 0: 读取项目 Manifest

读取 `<local path>`，提取 UI/UX 相关字段：
- `design_system` → 决定 Stage 2 扫描基准（`see-ds-v2` 用 SEE Design System token，`tailwind-default` 用 Tailwind 标准）
- `i18n` → 决定是否检查多语言合规
- `tech_stack.framework` → 决定组件库适配（nextjs → RSC 边界检查，react-vite → CSR 模式）
- `custom.notification_channels` → 决定通知组件是否需要多渠道适配


### Stage 1: 任务识别与模块加载

根据前端任务类型选择加载哪些模块，不全量加载。

| 模块 | 文件 | 内容 | 适用场景 |
|------|------|------|---------|
| 一 | `contexts/uiux/a11y.md` | 无障碍铁律（11 条） | 任何 UI 变更必加载 |
| 二+三 | `contexts/uiux/interaction-layout.md` | 交互反馈 + 布局响应式（13 条） | 新组件/交互设计 |
| 四+五 | `contexts/uiux/forms-perf.md` | 表单 + 性能（11 条） | 表单/数据输入场景 |
| 六+七+八 | `contexts/uiux/visual-typo-anti.md` | 视觉 + 排版 + 反模式（20 条） | 视觉审查/设计评审 |
| 九+十+十一 | `contexts/uiux/vitals-ai-stats.md` | Web 性能 + 状态同步 + AI 时代 + 统计 | 性能优化/AI 界面 |
| 附录 | `contexts/uiux/appendix-refs.md` | 折叠屏/空间计算/对话式 UI + 参考来源 | 特殊设备适配 |

**Gate**：已按任务类型确定加载模块列表 ∧ a11y.md 必须加载（任何 UI 变更必需）

---

### Stage 2: 规则合规扫描

对当前 UI 变更文件执行 12 维度合规扫描（dev-quality.md 设计体系合规门控）。

扫描维度优先级：
1. **高违规率维度**（L10 热层，优先检查）：颜色硬编码、按钮语义类、三态覆盖
2. **中频违规维度**：圆角等级、间距规范、图表色板
3. **低频验证维度**：图标大小、分隔线、交互过渡

**Gate**：12 维度全部扫描完毕 ∧ 热层高违规维度零违规 ∧ 发现违规已当场修复

---

### Stage 3: 加载规则应用与记录

将已加载模块中的规则应用于当前任务，并记录违规模式用于 L10 热度更新。

违规记录格式（内部，不输出给用户）：
```
{"ts":"ISO8601","rule_id":"a11y-03","file":"component.tsx","violation":"缺失 aria-label","fixed":true}
```

**Gate**：所有发现的违规已修复 ∧ 无新引入违规 ∧ 违规记录已写入（如有）

---

### Stage 4: 跨模块规则一致性验证

检查组件是否同时满足多模块交叉规则，常见冲突点：

| 冲突场景 | 检查内容 |
|---------|---------|
| 表单 + 无障碍 | input 有 label ∧ error 态有 role=alert |
| 性能 + 交互 | 动画不阻塞 CLS ∧ 过渡 ≤150ms |
| 视觉 + 排版 | 色彩对比度 ≥4.5:1 ∧ 字号不低于 11px |

**Gate**：跨模块冲突点全部验证通过 ∧ WCAG AA 对比度达标

---

### Stage 5: 产出与热度更新

输出本次合规扫描结果，并更新 L10 规则热度数据（高频违规规则升权，低频规则降温）。

**Gate**：扫描报告已输出（含违规数/修复数/模块覆盖率）∧ 热度数据更新（如有 ≥3 次同规则违规）

---

## SEE Layer Map

| Step | SEE Layer | Role |
|------|------------|------|
| 模块按需加载 | **L9 表观遗传** | 按前端任务类型条件激活对应模块（a11y/交互/表单等），非前端项目自动沉默 |
| 规则热度追踪 | **L10 时间记忆** | 高频违反的规则升为热层，低频规则降温，审计时优先检查热层规则 |

## SEE 三条自问

- ① **自注册**：新 UI 规则模块（a11y/交互/表单等）加入 contexts/uiux/ 后，按需加载机制自动发现并整合
- ② **自优化**：高频违反规则通过 L10 热度追踪自动升权，低频规则自动降温，无需人工排序
- ③ **自扩展**：审计发现新违反模式时自动提议新增规则条目或新增检测维度

## 三阶段观测

- T0：UI 组件变更即刻扫描 12 维度合规门控（dev-quality.md 设计体系合规门控）
- T1：48h 内验证违规率未回升（watchlist 自动调度）
- T2：7 天周期统计各模块违规频率，热层/冷层自动重分级

## DocSync 检查

执行后验证相关文档引用一致性：CLAUDE.md `/uiux-design` 触发词、dev-quality.md 设计体系合规门控 12 维度对齐。

## 数据文件

| 文件 | 用途 | 读/写 |
|------|------|-------|
| `contexts/uiux/a11y.md` | 无障碍铁律（11 条） | 读 |
| `contexts/uiux/interaction-layout.md` | 交互反馈 + 布局响应式（13 条） | 读 |
| `contexts/uiux/forms-perf.md` | 表单 + 性能（11 条） | 读 |
| `contexts/uiux/visual-typo-anti.md` | 视觉 + 排版 + 反模式（20 条） | 读 |
| `contexts/uiux/vitals-ai-stats.md` | Web 性能 + 状态同步 + AI 时代 + 统计 | 读 |

## 变更日志

| 版本 | 变更 | 日期 |
|------|------|------|
| 1.0.0 | 初始版本 + SEE 合规模板注入 | 2026-03-26 |
