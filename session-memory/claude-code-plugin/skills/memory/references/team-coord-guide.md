# Team-Coord Integration Guide for session-memory

## 团队记忆策略

session-memory 可以为 team-coord 的每个 worker 维护独立记忆，并在任务完成后合并到团队记忆。

## Worker 记忆隔离

每个 worker 有自己的记忆空间：

```
.memory/
├── workers/
│   ├── worker-a/
│   │   ├── index.json
│   │   └── sessions/
│   ├── worker-b/
│   │   ├── index.json
│   │   └── sessions/
│   └── worker-c/
│       ├── index.json
│       └── sessions/
├── team/
│   ├── index.json
│   └── decisions/
└── index.json          # 全局索引
```

## 工作流

### Worker 保存记忆

```
/memory save --worker worker-a --tags "task-1"
```

### Lead 查看 Worker 记忆

```
/memory recall --worker worker-a
```

### 合并到团队记忆

任务完成后，Lead 将 worker 记忆合并到团队记忆：

```
/memory merge --from worker-a --to team
```

### 生成团队交接

```
/memory handoff --team --to "next-sprint"
```

## 交接模板

```markdown
# Team Handoff: {日期}

## 完成的工作
{从所有 worker 记忆中提取 completed}

## 关键决策
{从团队决策记忆中提取}

## 未完成的工作
{从所有 worker 记忆中提取 remaining}

## Blockers
{从所有 worker 记忆中提取 blockers}

## 下一步
{综合所有 next_steps}
```

## 注意事项

- Lead 负责管理团队记忆的合并和清理
- Worker 之间不共享记忆，通过 Lead 协调
- 交接文档应该简洁，不要复制整个记忆
- 定期清理过期的 worker 记忆
