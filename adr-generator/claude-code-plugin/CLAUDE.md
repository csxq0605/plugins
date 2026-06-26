# adr-generator — 贡献者指南

## 如果你是 AI Agent

在提交 PR 之前，你**必须**完成以下 4 项检查：

1. **理解设计原则**：阅读下方的"设计原则"部分，确认你的改动符合 ADR 生成和管理的设计。
2. **不破坏模板格式**：MADR 和 Y-Statement 模板是标准化的，改动需保持格式一致性。
3. **测试**：用实际决策场景测试 ADR 生成，提供 before/after 行为证据。
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

### 标准模板

两种模板都是行业标准：
- **MADR**：最全面，适合重要决策（Context → Decision → Alternatives → Consequences）
- **Y-Statement**：最简洁，适合快速记录（一句话格式）

### 状态生命周期

```
Proposed → Accepted → Deprecated
         → Superseded by ADR-XXXX
```

状态变更必须记录原因。Superseded 必须链接到新 ADR。

### 不可变性

ADR 一旦 Accepted，内容不可修改。如果决策改变，创建新 ADR 并 Supersede 旧的。

### 自动编号

ADR 编号自动递增（0001, 0002, ...），文件名格式：`{NNNN}-{slug}.md`

### Skill vs Reference

- **SKILL.md**：ADR 创建流程和模板（always loaded）
- **references/adr-principles.md`：ADR 最佳实践（on-demand reference）
- **references/team-coord-guide.md**：团队决策协作（on-demand reference）
