---
name: artifact-mocks
description: Artifact 项目的 window.claude.complete mock 响应库管理。生成 / 切换 / 校验 mock JSON 与真实 AI 输出 schema 一致性，防 prompt 调试时 schema drift。
user-invocable: false
type: operation
---

# /artifact-mock-fixtures — Mock 响应库管理 Skill

## 触发场景

- 「mock 数据」/「生成 mock fixture」
- prompt 调试需要确定性输入输出
- 怀疑 mock 与真实 AI schema drift

## 3 子命令

### 1. generate — 生成 mock fixture

```bash
/artifact-mock-fixtures generate {fixture-name} {prompt-key}
```

输入：fixture 名 + 对应 prompt 的 key（与 src/artifact.jsx 中 prompt 字符串关联）
工作：根据 prompt 中声明的 JSON schema 生成符合的假数据 → 写 `mocks/{fixture-name}.json`

### 2. switch — 切换 mock 模式

```bash
/artifact-mock-fixtures switch mock     # VITE_AI_MODE=mock（默认）
/artifact-mock-fixtures switch real     # VITE_AI_MODE=real（需 .env API key）
```

工作：写 `.env.local` 或 export 环境变量

### 3. verify — 校验 schema 一致性

```bash
/artifact-mock-fixtures verify
```

工作：
- 用 real 模式调一次真实 AI 拿响应
- 与 mocks/ 现有 fixture 对比 schema（字段名/类型/嵌套）
- drift 警告输出（哪些字段不一致）

## 验收

- ✅ generate: mocks/{name}.json 存在 + 符合 prompt 声明 schema
- ✅ switch: .env.local 或 shell env 正确切换
- ✅ verify: 输出 diff 报告（无 drift / drift 字段清单）

## 关联

- [[feedback_artifact_dev_baseline]] — mock 双模式（VITE_AI_MODE）
-  — mock 实现
