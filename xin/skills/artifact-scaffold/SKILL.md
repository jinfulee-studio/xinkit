---
name: artifact-scaffold
description: 一键创建 claude.ai Artifact 类项目脚手架。触发场景：「心，artifact 它：XX」/「做个 AI 工具帮我 XX」/ 心 3 问澄清判定 Artifact 路径后。1h 内 能在 claude.ai 跑起来。
user-invocable: false
type: operation
---

# /artifact-init — Artifact 项目脚手架 Skill

## 触发场景

信号（任一）→ 心识别为 Artifact 路径 → 启动本 skill：
- 明示：「心，artifact 它：{描述}」/「artifact 化这个想法」
- 隐含自用：「做个 AI 工具帮我 {功能}」（满足 3 问澄清条件）
- 快速验证：「想验证下这个想法」/「做个原型给我用一周」

前置：心已完成 3 问澄清（feedback_artifact_vs_saas_routing L4）— 数据存哪 ✅ / 谁用 ✅ / 要不要 AI ✅。

## 工作流程

### 1. 接收参数

- `name`: 项目名（kebab-case，如 `shopping-tracker` / `mood-journal`）
- `description`: 一句话描述（如「每日消费追踪 + AI 营养分析」）

### 2. 创建目录 + cp template

```bash
PROJECT_DIR="$HOME/Desktop/artifacts/${name}"
mkdir -p "$PROJECT_DIR"
cp -R "<local path>" "$PROJECT_DIR/"
cd "$PROJECT_DIR"
```

### 3. 初始化 git + npm install

```bash
git init -q
git add . && git commit -q -m "feat: ${name} 项目初始化 from artifact-skeleton template

Co-Authored-By: 心 <noreply@anthropic.com>"
npm install --silent
```

### 4. 替换 src/artifact.jsx 占位 → 基础骨架

template 默认 src/artifact.jsx 是通用骨架，本 skill 根据 description 生成更贴近需求的骨架（含基础组件 + window.claude.complete 调用示例 + mock 响应）。

### 5. 输出 下一步命令

```
✅ Artifact 项目 ${name} 创建完成

📁 路径：~/Desktop/artifacts/${name}/

下一步：
  cd ~/Desktop/artifacts/${name}/
  npm run dev                              # 本地 mock 跑通（默认）
  VITE_AI_MODE=real npm run dev            # 用真实 AI 验证 prompt（需 .env VITE_ANTHROPIC_API_KEY）
  /artifact-deploy                         # 部署到 claude.ai
```

## 验收（声称完成前心自检）

- ✅ `~/Desktop/artifacts/${name}/` 目录存在 + 含 template 8 文件
- ✅ `npm install` 0 错误
- ✅ `npm run dev` 浏览器看到基础页面（VITE_AI_MODE=mock 默认）
- ✅ 点击 demo 按钮 → mock window.claude.complete 返回 JSON

## 关联

- [[feedback_artifact_domain_positioning]] — Artifact 双标准定位
- [[feedback_artifact_vs_saas_routing]] — 3 问澄清前置
- [[feedback_artifact_dev_baseline]] — 5 维硬约束 + 开发工作流
-  — 项目模板
- `/artifact-deploy` — 后续部署 skill
