# lit-review — 贡献者指南

## 如果你是 AI Agent

在提交 PR 之前，你**必须**完成以下 4 项检查：

1. **理解设计原则**：阅读下方的"设计原则"部分，确认你的改动符合多源搜索和结构化调研的设计。
2. **不破坏 API 兼容性**：`bin/lit-search.py` 的 CLI 接口是稳定的，改动不能破坏已有命令。
3. **测试**：用实际搜索查询测试，提供 before/after 行为证据。
4. **不扩大 scope**：不要在 skill 改动中夹带不相关的内容。

## Pull Request 要求

- 一个 PR 解决一个 issue
- 必须描述问题和解决方案
- 需要人类 review

## 不会被接受的改动

- 合规性重写（没有行为变化的格式调整）
- 推测性修复（没有复现步骤的"修复"）
- 第三方依赖引入（lit-search.py 必须保持零依赖）
- 批量 PR（多个不相关改动合并）
- 捏造内容（虚假的测试结果或文档）

## 设计原则

### 零外部依赖

`lit-search.py` 只使用 Python 标准库（urllib, json, xml）。这是硬约束——Claude Code 环境不能保证有第三方包。

### 双源搜索

arXiv + Semantic Scholar 互补：
- arXiv：预印本，覆盖最新研究
- Semantic Scholar：引用网络，提供影响力指标

搜索结果去重后按引用数排序。

### 配置共享

`~/.lit-review/config.json` 在 Claude Code 和 Nexgent 版本之间共享。API key 只需要设置一次。

### 三个技能分离

- **search**：搜索和发现（Bash 调用 lit-search.py）
- **analyze**：深度分析单篇论文（LLM 推理）
- **synthesize**：综合多篇论文生成综述（LLM 推理）

### Skill vs Reference

- **SKILL.md**：搜索/分析/综合的流程（always loaded）
- **bin/lit-search.py**：API 调用工具（Bash 执行）
- **references/**：team-coord 集成指南（on-demand）
