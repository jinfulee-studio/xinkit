---
name: artifact-ship
description: 验证 Artifact 单文件 5 维硬约束 + 剪贴板复制 src/artifact.jsx 到剪贴板 + 打开 claude.ai 粘贴粘贴指引。 dev 跑通后部署到 claude.ai 验证真实 window.claude 工作。
user-invocable: false
type: operation
---

# /artifact-deploy — Artifact 部署到 claude.ai Skill

## 触发场景

-  Artifact 项目目录说「部署」/「发布到 claude.ai」
- `/artifact-init` 完成本地 dev 后链式调用
- 想验证最新代码在真实沙箱的表现

## 工作流程

### 1. 当前目录校验

```bash
PROJECT_DIR="$PWD"
# 必须在 ~/Desktop/artifacts/*/ 下
[[ "$PROJECT_DIR" == */Desktop/artifacts/* ]] || { echo "❌ 不在 Artifact 项目目录"; exit 1; }
test -f "$PROJECT_DIR/src/artifact.jsx" || { echo "❌ src/artifact.jsx 不存在"; exit 1; }
```

### 2. spawn artifact-validator agent 校验 5 维约束

```bash
# 调 artifact-validator agent
# 输出：通过 / 警告 / 错误清单
```

任一错误 → 中止部署 + 提示修复。

### 3. 剪贴板复制 复制到剪贴板

```bash
# macOS: pbcopy < "$PROJECT_DIR/src/artifact.jsx"
# Linux: xclip -sel clip < "$PROJECT_DIR/src/artifact.jsx"
# Windows: clip < "$PROJECT_DIR/src/artifact.jsx"
echo "✓ 已复制 src/artifact.jsx 到剪贴板（$(wc -l < $PROJECT_DIR/src/artifact.jsx) 行）"
```

### 4. 打开 claude.ai + 粘贴指引

```bash
# macOS: open | Linux: xdg-open | Windows: start
open "https://claude.ai/new"
echo ""
echo "下一步："
echo "1. claude.ai 已打开"
echo "2. 在 chat 框新建 Artifact 或粘贴到现有 Artifact"
echo "3. Cmd+V 粘贴"
echo "4. 等待 Babel 转换 + 加载"
echo "5. 测试 window.claude.complete 真实工作"
```

## 验收

- ✅ artifact-validator 5 维校验通过
- ✅ 剪贴板复制 0 错误（剪贴板含 artifact.jsx 全文）
- ✅ claude.ai 在浏览器打开

## 关联

-  — 5 维校验 agent
- [[feedback_artifact_dev_baseline]] — 5 维硬约束 + 部署流程
- [[feedback_artifact_domain_positioning]] — Artifact 定位
