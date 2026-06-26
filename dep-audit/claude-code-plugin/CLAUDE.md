# dep-audit — 贡献者指南

## 如果你是 AI Agent

在提交 PR 之前，你**必须**完成以下 4 项检查：

1. **理解设计原则**：阅读下方的"设计原则"部分，确认你的改动符合依赖审计和漏洞查询的设计。
2. **不破坏 OSV API 调用**：API 查询逻辑是核心，改动需验证返回结果的正确性。
3. **测试**：用已知有漏洞的包测试查询结果，提供 before/after 行为证据。
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

### OSV 数据库优先

使用 OSV (Open Source Vulnerability) API 作为漏洞数据源。它是免费的、跨生态系统的、无需 API key。

### 多生态系统支持

支持 npm, PyPI, crates.io, Go, RubyGems, Packagist, Maven。依赖文件解析器必须准确，不能误报。

### 健康评分

评分公式：`100 - (Critical×25 + High×10 + Medium×3 + Low×1)`。权重反映实际安全影响。

### 可执行的修复

每个漏洞报告必须包含具体的修复命令（如 `npm install pkg@version`），不能只说"升级"。

### Skill vs Reference

- **SKILL.md**：审计流程和检查清单（always loaded）
- **references/vuln-severity.md**：严重程度评分标准（on-demand reference）
- **references/team-coord-guide.md**：并行审计策略（on-demand reference）
