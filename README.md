# Claude Code & Nexgent Plugins

8 个插件覆盖真实开发场景。不碎片化，不制造伪需求。

> **设计原则：** 每个插件解决一个完整的工作流，而不是一个原子操作。真实开发场景是一个 PR 流程里你需要 audit + review + changelog + ADR，不是一个一个手动调。

## 插件总览

| 插件 | 领域 | Claude Code | Nexgent |
|------|------|-------------|---------|
| [dev-flow](#dev-flow) | 开发工作流 | ✅ | ✅ |
| [research](#research) | 学术研究 | ✅ | ✅ |
| [outreach](#outreach) | 学术套磁 | ✅ | ✅ |
| [email](#email) | 邮件收发 | ✅ | ✅ |
| [multi-agent](#multi-agent) | 多 Agent 协调 | ✅ | ✅ |
| [atlas](#atlas) | 代码库知识图谱 | ✅ | ✅ |
| [incident-response](#incident-response) | 生产事故响应 | ✅ | ✅ |
| [migrator](#migrator) | 框架迁移助手 | ✅ | ✅ |

---

## 插件详情

### dev-flow

一站式开发工作流。一个插件覆盖：项目入门 → 依赖审计 → 代码审查（6 视角）→ 变更日志 → 架构决策记录 → 跨会话记忆。

**命令：**
- `/dev-flow onboard` — 项目扫描和入门
- `/dev-flow audit` — 依赖健康审计
- `/dev-flow review` — 6 视角代码审查（安全、性能、架构、质量、测试、API）
- `/dev-flow changelog` — 基于 Conventional Commits 生成变更日志
- `/dev-flow adr` — 创建架构决策记录
- `/dev-flow remember` — 跨会话记忆持久化

**路径：**
- Claude Code: `dev-flow/claude-code-plugin/`
- Nexgent: `dev-flow/nexgent-plugin/`

---

### research

学术研究工作流。多源文献搜索（arXiv, Semantic Scholar）、引用网络分析、子主题分解、结构化综述合成。

**命令：**
- `/research search <query>` — 多源文献搜索
- `/research cite <paper>` — 引用网络分析
- `/research decompose <topic>` — 子主题分解
- `/research synthesize` — 结构化综述合成

**路径：**
- Claude Code: `lit-review/claude-code-plugin/`
- Nexgent: `lit-review/nexgent-plugin/`

---

### outreach

学术套磁全流程自动化。材料解析、教授调研、可视化报告、个性化邮件生成、邮件收发。

**命令：**
- `/outreach "配置邮箱"` — 配置邮箱（首次使用）
- `/outreach "这是我的CV"` — 上传材料
- `/outreach "调研 MIT CS"` — 教授调研
- `/outreach "生成报告 MIT CS"` — 生成可视化报告
- `/outreach "生成邮件 MIT CS"` — 生成套磁邮件
- `/outreach "发送邮件给 MIT CS Professor"` — 发送邮件

**路径：**
- Claude Code: `outreach/claude-code-plugin/`
- Nexgent: `outreach/nexgent-plugin/`

---

### email

独立邮件收发插件。基于 IMAP/SMTP 协议，支持多种邮箱服务器（PKU、清华、Gmail、Outlook、QQ、163），配置后自动测试连接。

**命令：**
- `/email "配置邮箱"` — 配置邮箱
- `/email "查看收件箱"` — 查看邮件
- `/email "发送邮件给 xxx@example.com"` — 发送邮件
- `/email "搜索邮件 keyword"` — 搜索邮件

**路径：**
- Claude Code: `email/claude-code-plugin/`
- Nexgent: `email/nexgent-plugin/`

---

### multi-agent

多 agent 团队协调层。Lead 纯协调、Teammate 引导执行、统一报告生成。

**核心概念：**
- **Lead Agent** — 纯协调，从不做实际工作
- **Teammate Agent** — 执行任务，返回原始发现
- **Inbox Sync** — 基于文件的异步消息协议
- **Two-step Shutdown** — request_shutdown → approve_shutdown（需要用户批准）

**路径：**
- Claude Code: `multi-agent/claude-code-plugin/`
- Nexgent: `multi-agent/nexgent-plugin/`

---

### atlas

代码库知识图谱。多 Agent 并行探索代码库，生成架构文档、数据流图、依赖分析，构建活的知识地图。

**命令：**
- `/atlas explore [path]` — 并行探索代码库（5 个维度）
- `/atlas map [path]` — 生成结构化文档
- `/atlas query <question>` — 基于知识库回答问题
- `/atlas diff [path1] [path2]` — 比较两个代码库

**探索维度：** 架构、依赖、数据流、入口点、编码模式

**路径：**
- Claude Code: `atlas/claude-code-plugin/`
- Nexgent: `atlas/nexgent-plugin/`

---

### incident-response

生产事故响应。结构化事故处理：分诊 → 定位 → 修复 → 验证 → 复盘。时间线追踪、根因分析、事后报告自动生成。

**命令：**
- `/ir start <desc>` — 创建事故记录
- `/ir triage [id]` — 严重性分级 (P0-P4)
- `/ir timeline <event>` — 添加时间线事件
- `/ir diagnose [id]` — 根因分析
- `/ir fix <action>` — 记录修复动作
- `/ir verify <check>` — 验证修复效果
- `/ir close [id]` — 关闭事故
- `/ir postmortem [id]` — 生成复盘报告

**路径：**
- Claude Code: `incident-response/claude-code-plugin/`
- Nexgent: `incident-response/nexgent-plugin/`

---

### migrator

框架/库迁移助手。分析代码库 → 识别所有触点 → 生成迁移计划 → 逐步执行 → 每步验证。处理 breaking changes 和废弃 API。

**命令：**
- `/migrator analyze <src> → <target>` — 分析迁移目标
- `/migrator plan` — 生成迁移计划
- `/migrator execute [step]` — 执行迁移步骤
- `/migrator verify [step]` — 验证迁移步骤
- `/migrator status` — 查看迁移进度
- `/migrator rollback [step]` — 回滚迁移步骤

**已知迁移模式：** React 17→18, Express 4→5, Python 3.9→3.12, Lodash 4→odash

**路径：**
- Claude Code: `migrator/claude-code-plugin/`
- Nexgent: `migrator/nexgent-plugin/`

---

## 安装

### Claude Code

添加插件市场：

```bash
/plugin marketplace add csxq0605/plugins
```

之后可以在 `/plugin > Discover` 里浏览，或直接安装某个插件：

```bash
/plugin install dev-flow@csxq0605-plugins
/plugin install research@csxq0605-plugins
/plugin install outreach@csxq0605-plugins
/plugin install email@csxq0605-plugins
/plugin install multi-agent@csxq0605-plugins
/plugin install atlas@csxq0605-plugins
/plugin install incident-response@csxq0605-plugins
/plugin install migrator@csxq0605-plugins
```

### Nexgent

```bash
# 一站式开发工作流
/plugin install https://github.com/csxq0605/plugins/tree/master/dev-flow/nexgent-plugin

# 学术研究
/plugin install https://github.com/csxq0605/plugins/tree/master/lit-review/nexgent-plugin

# 学术套磁
/plugin install https://github.com/csxq0605/plugins/tree/master/outreach/nexgent-plugin

# 邮件收发
/plugin install https://github.com/csxq0605/plugins/tree/master/email/nexgent-plugin

# 多 agent 协调
/plugin install https://github.com/csxq0605/plugins/tree/master/multi-agent/nexgent-plugin

# 代码库知识图谱
/plugin install https://github.com/csxq0605/plugins/tree/master/atlas/nexgent-plugin

# 生产事故响应
/plugin install https://github.com/csxq0605/plugins/tree/master/incident-response/nexgent-plugin

# 框架迁移助手
/plugin install https://github.com/csxq0605/plugins/tree/master/migrator/nexgent-plugin
```

---

## 设计理念

### 为什么是 8 个而不是更多？

之前的结构：project-onboarding, dep-audit, adversarial-review, changelog-gen, adr-generator, session-memory, lit-review, team-coord — 8 个碎片插件。

**问题是：** 真实开发场景是一个 PR 流程里你需要 audit + review + changelog + ADR，不是一个一个手动调。碎片化插件创造的是伪需求。

**现在的结构：**

| 插件 | 覆盖场景 |
|------|---------|
| **dev-flow** | 6 合 1（onboard + audit + review + changelog + adr + memory） |
| **research** | 独立的学术研究场景 |
| **outreach** | 独立的学术套磁场景（含邮件功能） |
| **email** | 独立的邮件收发场景（供其他场景复用） |
| **multi-agent** | 协调层，被其他插件复用 |
| **atlas** | 代码库理解（新人入职、重构前分析、架构文档） |
| **incident-response** | 生产事故处理（分诊、定位、修复、复盘） |
| **migrator** | 框架现代化（分析、计划、执行、验证） |

### 双版本架构

每个插件遵循双版本结构：

```
plugin-name/
├── claude-code-plugin/        # Claude Code 版本
│   ├── .claude-plugin/
│   │   └── plugin.json        # 插件元数据
│   ├── CLAUDE.md              # 贡献者指南
│   ├── README.md              # 中文文档
│   ├── README.en.md           # 英文文档
│   └── skills/
│       └── <skill-name>/
│           ├── SKILL.md       # 核心技能定义
│           └── references/    # 参考文档
└── nexgent-plugin/            # Nexgent 版本
    ├── plugin.json            # 插件元数据
    ├── __init__.py            # 入口
    ├── <name>_tools.py        # Python 工具实现
    ├── README.md              # 文档
    ├── pytest.ini             # 测试配置
    ├── skills/
    │   └── <skill-name>/
    │       └── SKILL.md       # 技能定义
    ├── references/            # 参考文档
    └── tests/
        ├── __init__.py
        └── test_<name>_tools.py  # 测试
```

### 与 Superpowers 工作流集成

所有插件遵循 Superpowers 工作流模式：
- **Lead Agent** 协调 — 从不做实际工作
- **Worker Agents** 执行 — 并行处理任务
- **阶段化流程** — 每个阶段有明确的输入输出
- **验证检查点** — 每步之后验证，不跳步

---

## Semantic Scholar API

research 插件支持 Semantic Scholar 进行论文搜索和引用分析。

```bash
# Claude Code
python bin/lit-search.py set-key YOUR_API_KEY

# Nexgent
export SEMANTIC_SCHOLAR_API_KEY=YOUR_API_KEY
```

配置存储在 `~/.lit-review/config.json`，两个版本共享。

---

## 开发

### 运行测试

```bash
# 单个插件
cd dev-flow/nexgent-plugin && python -m pytest tests/ -v

# 全部插件
python -m pytest dev-flow/nexgent-plugin/tests/ -v
python -m pytest multi-agent/nexgent-plugin/tests/ -v
python -m pytest atlas/nexgent-plugin/tests/ -v
python -m pytest incident-response/nexgent-plugin/tests/ -v
python -m pytest migrator/nexgent-plugin/tests/ -v
python -m pytest email/nexgent-plugin/tests/ -v
python -m pytest outreach/nexgent-plugin/tests/ -v
```

### 测试覆盖率

| 插件 | 测试数 | 状态 |
|------|--------|------|
| dev-flow | 16 | ✅ |
| multi-agent | 49 | ✅ |
| atlas | 20 | ✅ |
| incident-response | 27 | ✅ |
| migrator | 22 | ✅ |
| email | 11 | ✅ |
| outreach | 8 | ✅ |
| **总计** | **153** | **全部通过** |

---

## License

MIT
