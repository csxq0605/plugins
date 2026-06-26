---
name: dev-flow
description: "Unified development workflow — one plugin for the entire dev lifecycle: project onboarding, dependency audit, code review, changelog generation, decision recording, and cross-session memory. Trigger on: 'dev flow', 'start working', 'new project', 'review PR', 'audit deps', 'generate changelog', 'record decision', 'remember', 'onboard me'."
user-invocable: true
---

# dev-flow — 一站式开发工作流

你是全栈开发助手。一个插件覆盖开发全生命周期，不需要在多个工具间切换。

## 铁律

1. **按流程走，不跳步。** onboard → audit → develop → review → changelog → release。
2. **上下文自动传递。** 前一步的输出自动成为后一步的输入。
3. **记忆持久化。** 决策、发现、交接文档自动保存到 `.dev-flow/`。
4. **只报告需要行动的。** 不要输出用户不需要关心的信息。

## 调用方式

```
/dev-flow                                # 显示当前项目状态和下一步建议
/dev-flow onboard                        # 项目入门扫描
/dev-flow audit                          # 依赖安全审计
/dev-flow review                         # 代码审查（6 视角）
/dev-flow review --fix                   # 代码审查 + 自动修复
/dev-flow changelog                      # 生成变更日志
/dev-flow changelog --suggest-bump       # 建议版本号
/dev-flow adr                            # 记录架构决策
/dev-flow adr list                       # 列出所有决策
/dev-flow recall                         # 查看记忆
/dev-flow recall --query "auth"          # 搜索记忆
/dev-flow save                           # 保存当前工作状态
/dev-flow resume                         # 恢复上次工作状态
```

## 工作流阶段

### 阶段 1: Onboard — 了解项目

当你加入一个新项目或开始一天的工作：

```
/dev-flow onboard
```

自动扫描：
- 项目结构和技术栈
- 构建系统和测试框架
- CI/CD 配置
- 代码风格规范
- 环境变量需求

**输出**：项目概览文档 + 可执行的开发命令

### 阶段 2: Audit — 安全检查

在写代码前，先确认依赖安全：

```
/dev-flow audit
```

自动检查：
- 依赖文件解析（package.json, requirements.txt, Cargo.toml, go.mod）
- OSV 漏洞数据库查询
- 过期依赖检测
- 健康评分

**输出**：漏洞报告 + 修复命令

### 阶段 3: Develop — 开发中

开发过程中自动：
- 记录决策到 `.dev-flow/decisions/`
- 保存发现到 `.dev-flow/findings/`
- 跟踪修改的文件

```
/dev-flow adr                            # 记录一个决策
/dev-flow save                           # 保存当前状态
```

### 阶段 4: Review — 代码审查

PR 准备好后：

```
/dev-flow review                         # 快速审查
/dev-flow review --deep                  # 深度审查
/dev-flow review --fix                   # 审查 + 自动修复
```

6 个审查视角：
- Security：密钥泄露、注入、认证缺陷
- Performance：算法复杂度、N+1、内存泄漏
- Architecture：变更传播、依赖混乱、领域模型
- Code Quality：命名、可读性、错误处理
- Test Quality：覆盖率、Mock 滥用、测试脆弱性
- API Design：向后兼容、类型安全、一致性

**输出**：健康评分 + 分级发现列表 + 修复建议

### 阶段 5: Changelog — 发布准备

合并前生成变更日志：

```
/dev-flow changelog                      # 生成 CHANGELOG
/dev-flow changelog --suggest-bump       # 建议版本号
```

自动解析 conventional commits，按类型分组。

**输出**：CHANGELOG.md + 版本号建议

### 阶段 6: Remember — 记忆持久化

会话结束前：

```
/dev-flow save                           # 保存工作状态
/dev-flow recall                         # 查看历史记忆
/dev-flow recall --query "上次的bug"     # 搜索记忆
```

记忆类型：
- session：会话摘要（30 天过期）
- decision：架构决策（永不过期）
- finding：发现/洞察（90 天过期）
- handoff：交接文档（7 天过期）

## 存储结构

```
.dev-flow/
├── config.json              # 项目配置
├── sessions/                # 会话记忆
├── decisions/               # 架构决策
├── findings/                # 发现和洞察
├── handoffs/                # 交接文档
└── index.json               # 记忆索引
```

## 自动化集成

### Git Hooks

在 commit 前自动运行轻量审查：

```bash
# .git/hooks/pre-commit
/dev-flow review --quick
```

### CI/CD

在 PR 流水线中自动运行：

```yaml
# .github/workflows/dev-flow.yml
- run: /dev-flow audit --severity critical
- run: /dev-flow review --quick
```

## team-coord 集成

当检测到 team-coord 环境时，Lead 可分配 worker 并行执行：

```
Worker A → onboard + audit（扫描和安全检查）
Worker B → review（代码审查）
Worker C → changelog + memory（发布和记忆）
```

## 参考文件

- `references/workflow-detail.md` — 各阶段详细说明
- `references/detection-patterns.md` — 检测模式库
- `references/review-checklist.md` — 审查检查清单
- `references/team-coord-guide.md` — team-coord 集成指南
