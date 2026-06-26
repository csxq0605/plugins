# Superpowers Workflow — adr-generator 集成

当用户要求使用 superpowers 工作流时，adr-generator 在以下阶段被调用：

## Step 1: Brainstorming 阶段

在讨论设计方案时，创建 ADR 草稿记录候选方案。

## Step 2: Writing-plans 阶段

将确认的设计决策写入正式的 ADR。

## Step 10: Merge + Cleanup 阶段

更新 ADR 状态为 Accepted，生成 ADR 索引。

### 调用方式

```
# 创建 ADR 草稿
adr_create(title="Use PostgreSQL", template="madr", context="...", decision="...", status="proposed")

# 确认决策后更新状态
adr_update_status(number=1, status="accepted")

# 生成索引
adr_index()

# 搜索已有决策
adr_search(query="database")
```

### 与 team-coord 集成

- Worker 可创建 ADR 草稿
- Lead 审查并批准 ADR
- Lead 维护 ADR 索引

### ADR 用途

- **vision.md** — 核心技术决策的依据
- **overview.md** — 架构选择的记录
- **specs** — 设计约束的来源
- **新成员 onboarding** — 了解"为什么这样设计"
