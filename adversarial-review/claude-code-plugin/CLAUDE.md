# adversarial-review — 贡献者指南

## 如果你是 AI Agent

在提交 PR 之前，你**必须**完成以下 4 项检查：

1. **理解设计原则**：阅读下方的"设计原则"部分，确认你的改动符合多视角审查和统一发现格式的设计。
2. **不破坏评分系统**：健康评分公式（100 - Critical×15 - Warning×5 - Suggestion×1）是核心，改动需验证数学正确性。
3. **测试**：用实际代码仓库测试审查流程，提供 before/after 行为证据。
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

### 6 视角独立性

每个审查视角（Security, Performance, Architecture, Quality, Test, API）独立运行，互不干扰。视角之间不共享状态，不互相依赖。

### 统一发现格式

所有视角的发现必须使用统一的 JSON 格式（id, perspective, severity, title, file, line, evidence, risk, fix, confidence, ref）。这是报告合并和评分计算的基础。

### 置信度门控

confidence < 80 的发现自动降级为 Suggestion，< 70 的不报告。这减少了误报，提高了报告的可信度。

### 健康评分

评分公式：`100 - (Critical×15 + Warning×5 + Suggestion×1)`。每个视角独立评分，综合分 = 各视角平均分。

### Pattern Reference vs Skill

- **SKILL.md**：审查流程和检查清单（always loaded）
- **references/**：检测模式库、风险维度详解（on-demand reference）
