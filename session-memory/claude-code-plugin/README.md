# session-memory (Claude Code Plugin)

跨会话持久化记忆 — 纯 SKILL.md 实现，引导 LLM 管理 `.memory/` 目录。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/session-memory/claude-code-plugin
```

## 使用

```
/memory save                             # 保存当前会话摘要
/memory save --tags "auth,refactor"      # 带标签保存
/memory recall                           # 显示最近记忆
/memory recall --query "auth"            # 搜索记忆
/memory list                             # 列出所有记忆
/memory delete <id>                      # 删除记忆
/memory handoff                          # 生成交接文档
/memory resume                           # 恢复上次会话上下文
```

## 目录结构

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # 插件清单
├── skills/memory/
│   ├── SKILL.md                     # 主技能文件（记忆管理工作流）
│   └── references/
│       ├── memory-structure.md      # 记忆结构详解
│       └── team-coord-guide.md      # team-coord 集成指南
└── README.md
```

## 依赖

无。纯 SKILL.md 指令，读写 `.memory/` 目录。

## License

MIT
