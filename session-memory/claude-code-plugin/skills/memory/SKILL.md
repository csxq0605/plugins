---
name: memory
description: "Persistent cross-session memory — saves and restores conversation context, key decisions, findings, and progress. Supports tagging, search, auto-expiry, and team-coord handoff. Trigger on: 'remember this', 'save context', 'recall', 'what did we do', 'session summary', 'handoff', 'resume work'."
user-invocable: true
---

# memory — 跨会话持久化记忆

你是记忆管理专家。帮助用户在多个 Claude Code 会话之间保持上下文连续性。

## 铁律

1. **结构化存储。** 不要存原始对话，提取关键信息。
2. **及时清理。** 过期的记忆比没有记忆更危险。
3. **搜索优先。** 存之前先查是否已有相关记忆。
4. **最小权限。** 只存用户明确要求或工作必需的信息。

## 调用方式

```
/memory save                             # 保存当前会话摘要
/memory save --tags "auth,refactor"      # 带标签保存
/memory recall                           # 显示最近记忆
/memory recall --query "auth"            # 搜索记忆
/memory recall --tags "bug"              # 按标签过滤
/memory list                             # 列出所有记忆
/memory delete <id>                      # 删除记忆
/memory clear --older-than 30d           # 清理 30 天前的记忆
/memory handoff                          # 生成交接文档
/memory resume                           # 恢复上次会话上下文
```

## 存储结构

记忆存储在项目的 `.memory/` 目录下：

```
.memory/
├── index.json           # 记忆索引（ID、标签、时间戳、摘要）
├── sessions/            # 会话摘要
│   ├── 2024-01-15-001.json
│   ├── 2024-01-15-002.json
│   └── ...
├── decisions/           # 关键决策
│   ├── 2024-01-15-use-postgres.json
│   └── ...
├── findings/            # 发现和洞察
│   ├── 2024-01-15-perf-bottleneck.json
│   └── ...
└── handoffs/            # 交接文档
    ├── 2024-01-15-to-frontend.json
    └── ...
```

## 记忆格式

### 会话摘要

```json
{
  "id": "session-2024-01-15-001",
  "type": "session",
  "timestamp": "2024-01-15T10:30:00Z",
  "tags": ["auth", "api", "bug-fix"],
  "summary": "修复了 JWT token 过期后不刷新的 bug",
  "context": {
    "files_modified": ["src/auth/jwt.ts", "src/api/middleware.ts"],
    "decisions": ["使用 refresh token 机制", "token 过期时间设为 15 分钟"],
    "blockers": ["需要前端配合更新 token 刷新逻辑"],
    "next_steps": ["测试 token 刷新流程", "更新 API 文档"]
  },
  "key_findings": [
    "JWT 过期时间原来设的 24 小时，太长了",
    "中间件没有处理 token 过期的 401 响应"
  ]
}
```

### 决策记录

```json
{
  "id": "decision-2024-01-15-001",
  "type": "decision",
  "timestamp": "2024-01-15T11:00:00Z",
  "tags": ["auth", "architecture"],
  "title": "使用 refresh token 机制",
  "rationale": "Access token 15 分钟过期 + refresh token 7 天过期，平衡安全性和用户体验",
  "alternatives_considered": [
    "Session-based auth — 不适合微服务",
    "Long-lived token — 安全风险高"
  ],
  "impact": ["需要前端实现 token 自动刷新", "需要新增 refresh token 存储"]
}
```

### 交接文档

```json
{
  "id": "handoff-2024-01-15-001",
  "type": "handoff",
  "timestamp": "2024-01-15T17:00:00Z",
  "from_session": "session-2024-01-15-001",
  "to_role": "frontend",
  "summary": "后端 JWT refresh token 机制已完成，需要前端配合",
  "completed": [
    "JWT access token 过期时间改为 15 分钟",
    "新增 refresh token API (/api/auth/refresh)",
    "中间件支持 401 + token-expired 错误码"
  ],
  "remaining": [
    "前端实现 token 自动刷新拦截器",
    "前端处理 401 token-expired 响应",
    "测试完整刷新流程"
  ],
  "context": {
    "api_changes": "新增 POST /api/auth/refresh，请求体 {refresh_token: string}",
    "error_codes": {"token_expired": "access token 已过期，需要刷新", "token_invalid": "token 无效，需要重新登录"}
  }
}
```

## 工作流

### 1. 保存会话

在会话结束前：

```
/memory save --tags "feature-x,api"
```

自动提取：
- 修改的文件列表
- 做出的决策
- 遇到的问题
- 下一步计划

### 2. 恢复上下文

在新会话开始时：

```
/memory resume
```

显示：
- 最近 3 个会话的摘要
- 未完成的任务
- 活跃的 blocker

### 3. 搜索记忆

```
/memory recall --query "JWT"
```

返回所有包含 "JWT" 的记忆，按相关性排序。

### 4. 生成交接

```
/memory handoff --to frontend
```

生成面向前端开发者的交接文档，包含：
- 已完成的工作
- 需要配合的工作
- API 变更详情
- 错误码说明

## 自动记忆

以下情况自动触发记忆保存：

1. **会话超过 1 小时** — 提醒用户保存
2. **做出重要决策时** — 自动记录决策
3. **遇到 blocker 时** — 自动记录问题
4. **切换任务时** — 保存当前任务状态

## team-coord 集成

当检测到 team-coord 环境时：

```
# Lead 可以查看所有 worker 的记忆
/memory recall --worker "worker-a"

# Worker 完成后自动保存记忆
/memory save --tags "worker-a,task-1"

# Lead 生成团队交接
/memory handoff --team
```

## 参考文件

- `references/memory-structure.md` — 记忆结构详解
- `references/team-coord-guide.md` — team-coord 集成指南
