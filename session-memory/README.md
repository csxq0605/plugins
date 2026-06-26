# session-memory — 跨会话持久化记忆

在多个 Claude Code/Nexgent 会话之间保持上下文连续性。保存决策、发现、交接文档，支持标签搜索和自动过期。

## 安装

### Claude Code

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/session-memory/claude-code-plugin
```

### Nexgent

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/session-memory/nexgent-plugin
```

## 使用

```
/memory save                             # 保存当前会话摘要
/memory save --tags "auth,refactor"      # 带标签保存
/memory recall                           # 显示最近记忆
/memory recall --query "auth"            # 搜索记忆
/memory recall --tags "bug"              # 按标签过滤
/memory list                             # 列出所有记忆
/memory delete <id>                      # 删除记忆
/memory clear --older-than 30d           # 清理过期记忆
/memory handoff                          # 生成交接文档
/memory resume                           # 恢复上次会话上下文
```

## 4 种记忆类型

| 类型 | 用途 | 过期时间 |
|------|------|----------|
| session | 会话摘要 — 修改了什么、做了什么决策 | 30 天 |
| decision | 架构决策 — 为什么选这个方案 | 永不过期 |
| finding | 发现/洞察 — 性能瓶颈、代码异味 | 90 天 |
| handoff | 交接文档 — 给下一个开发者/团队 | 7 天 |

## 存储结构

```
.memory/
├── index.json           # 记忆索引
├── sessions/            # 会话摘要
├── decisions/           # 关键决策
├── findings/            # 发现和洞察
└── handoffs/            # 交接文档
```

## team-coord 集成

每个 worker 有独立记忆空间，Lead 负责合并到团队记忆。参见 `references/team-coord-guide.md`。

## License

MIT
