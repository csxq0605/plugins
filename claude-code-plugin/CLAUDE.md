# team-coord — 贡献者指南

## 如果你是 AI Agent

在提交 PR 之前，你**必须**完成以下 4 项检查：

1. **理解设计原则**：阅读下方的"设计原则"部分，确认你的改动符合 lead/teammate 分离和 skill vs reference doc 的设计。
2. **不破坏 WHAT vs HOW 原则**：确保 lead skill 不重述 teammate skill 的执行细节。
3. **测试**：在真实的多 agent session 中测试你的改动，提供 before/after 行为证据。
4. **不扩大 scope**：不要在 skill 改动中夹带 superpowers workflow 的改动（反之亦然）。

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

### Lead vs Teammate 分离

两者的 first actions 和 ongoing protocols **不重叠**。混进一个 skill 会让任一角色读到 500+ 行无关内容。

### Skill vs Reference Doc

- **Skill**：team primitive（lead/teammate 的协调协议）
- **Reference doc**：superpowers workflow（一种使用模式）

把 workflow 作为 reference doc 而非独立 skill，意味着"不用时上下文成本为零，用时内容完整"。

### ToolSearch over Restating

使用 `ToolSearch` 加载工具的实时 schema，而不是在 skill 中重述工具参数。

### Bookend Skill/Tool Listing Pattern

每个 reference doc 在开头列出它要 invoke 的 skill/tool，不是可选项——经验上 Claude 在工作压力下倾向跳过 `Skill(...)` 调用。
