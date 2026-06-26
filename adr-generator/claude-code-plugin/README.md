# adr-generator (Claude Code Plugin)

架构决策记录生成器 — 纯 SKILL.md 实现，引导 LLM 创建和管理 ADR。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/adr-generator/claude-code-plugin
```

## 使用

```
/adr new                                 # 交互式创建
/adr new --template madr                 # MADR 模板
/adr new --template y-statement          # Y-Statement 模板
/adr list                                # 列出所有 ADR
/adr list --status accepted              # 按状态过滤
/adr show 0001                           # 查看详情
/adr index                               # 生成索引
/adr search "database"                   # 搜索
```

## 目录结构

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # 插件清单
├── skills/adr/
│   ├── SKILL.md                     # 主技能文件（ADR 创建流程 + 两种模板）
│   └── references/
│       ├── adr-principles.md        # ADR 最佳实践
│       └── team-coord-guide.md      # team-coord 集成指南
└── README.md
```

## 依赖

无。纯 SKILL.md 指令，读写 `docs/adr/` 目录。

## License

MIT
