# project-onboarding — 贡献者指南

## 如果你是 AI Agent

在提交 PR 之前，你**必须**完成以下 4 项检查：

1. **理解设计原则**：阅读下方的"设计原则"部分，确认你的改动符合自动扫描和结构化输出的设计。
2. **不破坏检测模式**：新增检测模式时，确保不影响已有检测的准确性。
3. **测试**：用实际项目测试扫描结果，提供 before/after 行为证据。
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

### 扫描优先于猜测

所有检测必须通过工具验证（文件存在性、内容解析），不要根据目录名猜测技术栈。

### 7 阶段流水线

扫描流程分为 7 个独立阶段，可以并行执行：
1. 项目身份 → 2. 目录结构 → 3. 技术栈 → 4. 构建系统 → 5. 测试框架 → 6. CI/CD → 7. 代码风格

### 可执行的命令

输出中所有命令必须是可直接复制执行的，不要只说"用 npm"，要给出 `npm install && npm run dev`。

### 检测模式库

`references/detection-patterns.md` 是所有检测模式的权威来源。新增框架/工具时，必须同时更新该文件。

### Skill vs Reference

- **SKILL.md**：扫描流程和输出格式（always loaded）
- **references/detection-patterns.md**：检测模式库（on-demand reference）
- **references/team-coord-guide.md**：并行扫描策略（on-demand reference）
