# project-onboarding (Claude Code Plugin)

项目自动入门 — 纯 SKILL.md 实现，引导 LLM 扫描项目并生成入门文档。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/project-onboarding/claude-code-plugin
```

## 使用

```
/onboarding                              # 完整扫描
/onboarding --quick                      # 快速概览
/onboarding --focus tech-stack           # 聚焦技术栈
/onboarding --focus build                # 聚焦构建系统
/onboarding --focus test                 # 聚焦测试
/onboarding --focus ci                   # 聚焦 CI/CD
/onboarding --focus code-style           # 聚焦代码风格
```

## 目录结构

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # 插件清单
├── skills/onboarding/
│   ├── SKILL.md                     # 主技能文件（7 阶段扫描流程）
│   └── references/
│       ├── detection-patterns.md    # 语言/框架/CI/风格检测模式
│       └── team-coord-guide.md      # team-coord 集成指南
└── README.md
```

## 依赖

无。纯 SKILL.md 指令。

## License

MIT
