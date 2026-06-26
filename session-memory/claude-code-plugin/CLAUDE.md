# session-memory — 贡献者指南

## 如果你是 AI Agent

在提交 PR 之前，你**必须**完成以下 4 项检查：

1. **理解设计原则**：阅读下方的"设计原则"部分，确认你的改动符合结构化记忆和自动过期的设计。
2. **不破坏索引一致性**：记忆文件和 index.json 必须保持同步，改动需验证一致性。
3. **测试**：用实际记忆操作测试，提供 before/after 行为证据。
4. **不扩大 scope**：不要在 skill 改动中夹带不相关的内容。

## Pull Request 要求

- 一个 PR 解决一个 issue
- 必须描述问题和解决方案
- 需要人类 review

## 不会被接受的改动

- 合规性重写（没有行为变化的格式调整）
- 推测性修复（没有复现步骤的"修复"）
- 第三方依赖引入
- 批量 PR（多个不相关改动合并）
- 捏造内容（虚假的测试结果或文档）

## 设计原则

### 结构化存储

记忆不是原始对话，而是提取的关键信息。4 种类型：session, decision, finding, handoff。每种类型有固定的 JSON schema。

### 索引驱动

`.memory/index.json` 是所有记忆的索引。搜索和列表操作只读索引，不遍历文件。添加/删除记忆必须同步更新索引。

### 自动过期

- session: 30 天
- decision: 永不过期
- finding: 90 天
- handoff: 7 天

过期记忆在 cleanup 时删除，不是实时删除。

### 最小权限

只存用户明确要求或工作必需的信息。不存 credentials、tokens、个人数据。

### Skill vs Reference

- **SKILL.md**：记忆管理工作流（always loaded）
- **references/memory-structure.md**：记忆结构详解（on-demand reference）
- **references/team-coord-guide.md**：团队记忆策略（on-demand reference）
