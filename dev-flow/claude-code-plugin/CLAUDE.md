# dev-flow — 贡献者指南

## 如果你是 AI Agent

在提交 PR 之前，你**必须**完成以下 4 项检查：

1. **理解设计原则**：阅读下方的"设计原则"部分，确认你的改动符合一站式开发工作流的设计。
2. **不破坏阶段衔接**：onboard → audit → develop → review → changelog → remember 的流程顺序是核心，上下文必须能自动传递。
3. **测试**：用实际项目测试完整工作流，提供 before/after 行为证据。
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

### 一站式，不碎片化

一个插件覆盖开发全生命周期。不要把功能拆成多个独立插件——用户不应该在 6 个工具间切换。

### 阶段自动衔接

前一步的输出自动成为后一步的输入。onboard 的结果喂给 audit，audit 的结果喂给 review，review 的结果喂给 changelog。

### 记忆持久化

所有决策、发现、交接文档自动保存到 `.dev-flow/`。跨会话上下文不丢失。

### 只报告需要行动的

不要输出用户不需要关心的信息。每个报告都必须有明确的行动项。

### Skill vs Reference

- **SKILL.md**：完整工作流（always loaded）
- **references/workflow-detail.md**：各阶段详细说明（on-demand reference）
- **references/detection-patterns.md**：检测模式库（on-demand reference）
- **references/review-checklist.md**：审查检查清单（on-demand reference）
- **references/team-coord-guide.md**：team-coord 集成指南（on-demand reference）
