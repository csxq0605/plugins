# dep-audit (Claude Code Plugin)

依赖漏洞审计 — 纯 SKILL.md 实现，引导 LLM 扫描依赖并查询 OSV 漏洞数据库。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/dep-audit/claude-code-plugin
```

## 使用

```
/audit                                   # 完整审计
/audit --quick                           # 快速扫描
/audit --focus vulnerabilities          # 聚焦漏洞
/audit --focus outdated                 # 聚焦过期依赖
/audit --focus licenses                 # 聚焦许可证
/audit --severity critical              # 只报告 Critical
```

## 目录结构

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # 插件清单
├── skills/audit/
│   ├── SKILL.md                     # 主技能文件（5 阶段审计流程）
│   └── references/
│       ├── vuln-severity.md         # 漏洞严重程度评分标准
│       └── team-coord-guide.md      # team-coord 集成指南
└── README.md
```

## 依赖

无。纯 SKILL.md 指令，使用 curl 调用 OSV API。

## License

MIT
