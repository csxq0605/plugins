# adversarial-review (Claude Code Plugin)

多视角对抗式代码审查 — 纯 SKILL.md 实现，无需额外依赖。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/adversarial-review/claude-code-plugin
```

## 使用

```
/adversarial-review                          # 快速模式
/adversarial-review --deep                   # 深度模式
/adversarial-review --fix                    # 修复模式
/adversarial-review src/api                  # 指定路径
/adversarial-review --perspective security   # 单视角
```

## 目录结构

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # 插件清单
├── skills/adversarial-review/
│   ├── SKILL.md                     # 主技能文件（6 视角审查流程）
│   └── references/
│       ├── patterns.md              # 200+ 安全检测正则模式
│       ├── risk-dimensions.md       # 6 个衰减风险维度
│       └── team-coord-guide.md      # team-coord 集成指南
└── README.md
```

## 依赖

无。纯 SKILL.md 指令，由 Claude Code LLM 执行。

## License

MIT
