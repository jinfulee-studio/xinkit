---
name: conventional-commit
description: "手动提交入口（Conventional Commits 格式），用于 WIP/文档/非自动交付场景"
version: 2.0.0
when_to_use: "/commit, 手动提交, WIP commit, 文档提交, conventional commit"
applies-to: all projects
model: sonnet
user-invocable: false
---

# /commit Skill — 手动提交入口

## 适用场景（10% 手动场景）

- WIP 提交（功能未完成，需要保存进度）
- 纯文档修改（不触发 lint/test 流程）
- 配置调整（不走自动交付流程）
- 用户明确要求"手动 commit"时

> 90% 场景由 `dev-quality.md` 自动交付流程覆盖（CLAUDE_AUTO_COMMIT=true），开发完成自动 commit+push，无需手动触发。

## 与自动交付的关系

| 维度 | 自动交付路径 | /commit 路径 |
|------|------------|------------|
| 触发方式 | 开发完成后自动触发 | 用户手动执行 `/commit` |
| 包含流程 | lint + test + commit + push + verify 全链路 | 仅 commit，不含 lint/test/verify |
| 适用场景 | 功能开发的标准交付 | WIP / 文档 / 非标准场景 |
| Push | 自动 push | 提示用户确认，默认不 push |
| Co-Authored-By | 自动附加 | 自动附加（同签名格式） |

## 执行步骤

### Stage 1: 查看变更

```bash
git status
git diff --stat
```

分析变更范围，确认需要提交的文件。

**Gate**：`git status` 输出非空（存在已修改或已暂存的文件），且无 `key/`、`.env`、`*.pem` 等敏感文件出现在变更列表中。

### Stage 2: 生成 Conventional Commits 消息

格式：`<type>(<scope>): <description>`

**type 选择：**

| type | 适用场景 |
|------|---------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档变更 |
| `style` | 格式调整（不影响逻辑） |
| `refactor` | 重构（不是 feat 也不是 fix） |
| `test` | 测试相关 |
| `chore` | 构建/工具/依赖更新 |
| `build` | 构建系统变更 |
| `ci` | CI 配置变更 |
| `perf` | 性能优化 |

**scope 规则：**
- 可选，填变更涉及的模块/目录/文件（无括号时省略）
- 示例：`feat(auth): add OAuth2 login` / `docs: update README`

**description 规则：**
- 用英文或中文，与项目风格一致
- 动词开头，首字母小写（英文）
- 不加句号

**Gate**：commit 消息格式符合 `<type>(<scope>): <description>` 模式，type 在允许列表内，description 非空且不含句号结尾。

### Stage 3: 精确 add（禁止 git add -A）

```bash
# 逐个添加，避免泄露敏感文件
git add <file1> <file2> ...

# 或按目录添加（确认无敏感文件）
git add <directory>/
```

禁止 `git add -A` / `git add .` — 可能包含 .env、key/ 等敏感文件。

**Gate**：`git diff --cached --name-only` 返回非空，且列表中不含 `key/`、`.env`、`*.pem`、`*.key` 等敏感路径模式。

### Stage 4: 提交（含 Co-Authored-By 签名）

```bash
git commit -m "<type>(<scope>): <description>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

签名格式见  attribution 字段（行 16-17）。

### Stage 5：确认是否 push

默认不 push（与自动交付路径区分）。提示用户：

```
Commit 完成：<commit hash> <message>
是否现在 push？（默认否，自动交付场景会自动处理）
```

如用户确认 push：
```bash
git push
# 无 upstream 时：
git push -u origin HEAD
```

**Gate**：`git log --oneline -1` 输出含本次 commit hash 和 Co-Authored-By 签名行，`git log --format="%B" -1 | grep -q "Co-Authored-By"` 返回 0。

### Stage 6: pm-trigger hook

commit 完成后，pm-trigger hook 自动激活（与自动交付路径共享），无需手动触发。


## 注意事项

- 提交前检查 `key/`、`.env`、`*.pem` 等敏感文件未被 add
- WIP 提交建议在 description 中注明 `[WIP]`：`feat(auth): [WIP] add OAuth2 login`
- 手动 commit 不替代自动交付流程的 lint/test 验证，功能完成时仍需走完整链路

## SEE 三条自问

- ① **自注册**：pm-trigger hook 自动触发，commit 完成后无需人工记忆调用后续流程
- ② **自优化**：与自动交付路径共享 Co-Authored-By 签名格式，保持一致性无需额外配置
- ③ **自扩展**：新增 type 类型时，Conventional Commits 解析自动适配，不需要修改 Skill

## 三阶段观测

- T0：commit 完成即刻确认 hash 和 Co-Authored-By 签名存在
- T1：48h 内验证 pm-trigger hook 正常激活（watchlist 自动调度）
- T2：7 天周期统计手动 commit 占比，若 >10% 则排查自动交付流程异常

## DocSync 检查

执行后验证相关文档引用一致性：dev-quality.md 自动交付流程、CLAUDE.md Co-Authored-By 签名格式对齐。

## 数据文件

| 文件 | 用途 | 读/写 |
|------|------|-------|
|  | Co-Authored-By 签名格式（attribution 字段） | 读 |
| Git 提交历史 | 验证 commit 存在和签名格式 | 读 |

## 变更日志

| 版本 | 变更 | 日期 |
|------|------|------|
| 1.0.0 | 初始版本 + SEE 合规模板注入 | 2026-03-26 |
