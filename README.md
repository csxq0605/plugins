# Claude Code & Nexgent Plugins

7 个插件覆盖真实开发场景。不碎片化，不制造伪需求。

## Plugins

### dev-flow
一站式开发工作流。一个插件覆盖：项目入门 → 依赖审计 → 代码审查（6 视角）→ 变更日志 → 架构决策记录 → 跨会话记忆。

- **Claude Code**: `dev-flow/claude-code-plugin/`
- **Nexgent**: `dev-flow/nexgent-plugin/`

### research
学术研究工作流。多源文献搜索（arXiv, Semantic Scholar）、引用网络分析、子主题分解、结构化综述合成。

- **Claude Code**: `lit-review/claude-code-plugin/`
- **Nexgent**: `lit-review/nexgent-plugin/`

### outreach
学术套磁全流程自动化。材料解析、教授调研、可视化报告、个性化邮件生成。

- **Claude Code**: `outreach/claude-code-plugin/`
- **Nexgent**: `outreach/nexgent-plugin/`

### multi-agent
多 agent 团队协调层。Lead 纯协调、Teammate 引导执行、统一报告生成。

- **Claude Code**: `multi-agent/claude-code-plugin/`
- **Nexgent**: `multi-agent/nexgent-plugin/`

### atlas
代码库知识图谱。多 Agent 并行探索代码库，生成架构文档、数据流图、依赖分析，构建活的知识地图。

- **Claude Code**: `atlas/claude-code-plugin/`
- **Nexgent**: `atlas/nexgent-plugin/`

### incident-response
生产事故响应。结构化事故处理：分诊 → 定位 → 修复 → 验证 → 复盘。时间线追踪、根因分析、事后报告自动生成。

- **Claude Code**: `incident-response/claude-code-plugin/`
- **Nexgent**: `incident-response/nexgent-plugin/`

### migrator
框架/库迁移助手。分析代码库 → 识别所有触点 → 生成迁移计划 → 逐步执行 → 每步验证。处理 breaking changes 和废弃 API。

- **Claude Code**: `migrator/claude-code-plugin/`
- **Nexgent**: `migrator/nexgent-plugin/`

## 安装

### Claude Code

```bash
# 安装全部插件
claude install-plugin github:csxq0605/plugins
```

### Nexgent

```bash
# 一站式开发工作流
/plugin install https://github.com/csxq0605/plugins/tree/master/dev-flow/nexgent-plugin

# 学术研究
/plugin install https://github.com/csxq0605/plugins/tree/master/lit-review/nexgent-plugin

# 学术套磁
/plugin install https://github.com/csxq0605/plugins/tree/master/outreach/nexgent-plugin

# 多 agent 协调
/plugin install https://github.com/csxq0605/plugins/tree/master/multi-agent/nexgent-plugin

# 代码库知识图谱
/plugin install https://github.com/csxq0605/plugins/tree/master/atlas/nexgent-plugin

# 生产事故响应
/plugin install https://github.com/csxq0605/plugins/tree/master/incident-response/nexgent-plugin

# 框架迁移助手
/plugin install https://github.com/csxq0605/plugins/tree/master/migrator/nexgent-plugin
```

## 设计理念

之前的结构：project-onboarding, dep-audit, adversarial-review, changelog-gen, adr-generator, session-memory, lit-review, team-coord — 8 个碎片插件。

问题是：真实开发场景是一个 PR 流程里你需要 audit + review + changelog + ADR，不是一个一个手动调。碎片化插件创造的是伪需求。

现在的结构：
- **dev-flow** = 6 合 1（onboard + audit + review + changelog + adr + memory）
- **research** = 独立的学术研究场景
- **outreach** = 独立的学术套磁场景
- **multi-agent** = 协调层
- **atlas** = 代码库知识图谱（新人入职、重构前分析、架构文档）
- **incident-response** = 生产事故响应（分诊、定位、修复、复盘）
- **migrator** = 框架迁移助手（分析、计划、执行、验证）

## Semantic Scholar API

research 插件支持 Semantic Scholar 进行论文搜索和引用分析。

```bash
# Claude Code
python bin/lit-search.py set-key YOUR_API_KEY

# Nexgent
export SEMANTIC_SCHOLAR_API_KEY=YOUR_API_KEY
```

配置存储在 `~/.lit-review/config.json`，两个版本共享。

## 开发

每个插件遵循双版本结构：
- `plugin-name/claude-code-plugin/` — 纯 SKILL.md 文件
- `plugin-name/nexgent-plugin/` — Python 工具 + SKILL.md
