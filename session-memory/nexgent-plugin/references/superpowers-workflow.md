# Superpowers Workflow — session-memory 集成

当用户要求使用 superpowers 工作流时，session-memory 在以下阶段被调用：

## Step 1: Brainstorming 阶段

回忆之前的决策和发现，避免重复讨论已解决的问题。

## Step 2: Writing-plans 阶段

参考之前的实现计划和经验教训。

## Step 10: Merge + Cleanup 阶段

保存本次开发的决策、发现和交接文档。

### 调用方式

```
# 回忆之前的决策
memory_recall(tags=["architecture", "decision"])

# 保存本次决策
memory_save_decision(title="Use Event Sourcing", rationale="...", tags=["architecture"])

# 保存会话摘要
memory_save_session(summary="Implemented auth module", tags=["auth"], next_steps=["Write tests"])

# 生成交接文档
memory_generate_handoff(to_role="frontend")
```

### 与 team-coord 集成

每个 worker 有独立记忆空间：
- Worker 完成任务后自动保存记忆
- Lead 合并 worker 记忆到团队记忆
- Lead 生成团队交接文档

### 记忆用途

- **避免重复讨论** — 已有的决策不需要重新讨论
- **传承经验教训** — 之前的发现和教训可以指导新开发
- **团队交接** — 新成员可以通过记忆快速了解项目历史
