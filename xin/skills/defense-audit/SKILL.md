---
name: dprl-defense-audit
description: 使用 DPRL 四层框架（Detection→Prevention→Recovery→Learning）+ H/A/C 三类分层评估任何 Agent 系统或模块的防线完整性
user-invocable: false
---

# DPRL 防线审计 Skill

## 框架来源
SEE 原创框架，综合安全工程 Defense-in-Depth 模型（Schneier 2000）与 NIST AI RMF 的 DETECT→PROTECT→RESPOND→RECOVER 职能映射，适配至 LLM Agent 系统的运行时防线场景。

## 使用方法
对目标系统/模块执行以下分析：

### Step 1: 失败模式枚举
列出目标的所有已知失败模式（参考 Naive Agent 四大失败模式：One-shot / Context 丢失 / 状态污染 / 假完成 + 领域特定模式）。

### Step 2: DPRL 四层映射
对每个失败模式，逐层枚举防线：

| 层 | 定义 | 问题 |
|----|------|------|
| D-检测 | 发现问题的机制 | 怎么知道这个失败模式正在发生？ |
| P-预防 | 阻止问题的机制 | 怎么在发生前拦截？ |
| R-恢复 | 事后止损的机制 | 发生后怎么最小化损失？ |
| L-学习 | 防止再犯的机制 | 怎么确保同类问题不再发生？ |

### Step 3: H/A/C 分类
每个防线按可靠性分类：
- **H（硬防线）**：hook/script 系统层强制，agent 无法绕过
- **A（架构防线）**：架构设计保障，非单点可绕
- **C（认知防线）**：prompt/rules 约束，依赖 LLM 遵从度

### Step 4: 覆盖率计算
- 等权硬覆盖率 = H / (H + A + C)
- 等权有效覆盖率 = (H + A) / (H + A + C)
- 加权覆盖率 = (H×3 + A×2 + C×1) / ((H+A+C)×3)

### Step 5: 残余风险 + 硬化路径
识别每个模式的残余风险，评估 C→H 升级可行性和 ROI。

### Step 6: DPRL 层级投资优先级
L（学习，复利×3）> P（预防，×2）> R（恢复，×1.5）> D（检测，×1）。
新建防线时优先投 L 层（复利效应最大），等权用于存量评估。

## 输出格式
覆盖率矩阵表 + 残余风险优先级表 + C→H 升级行动清单 + Before/After/ROI

## 参考

