# Migrator Plugin — Contributor Guide

## Design Principles

1. **逐步验证** — 每一步迁移后都验证，不跳步
2. **可回滚** — 每一步都有回滚方案
3. **风险评估** — 分析阶段识别风险，规划阶段制定缓解措施
4. **进度追踪** — 实时显示迁移进度

## Architecture

```
migrator/
├── claude-code-plugin/        # Claude Code 版本
│   ├── .claude-plugin/plugin.json
│   ├── CLAUDE.md
│   ├── README.md
│   └── skills/migrator/
│       ├── SKILL.md
│       └── references/
└── nexgent-plugin/            # Nexgent 版本
    ├── plugin.json
    ├── __init__.py
    ├── migrator_tools.py
    ├── skills/migrator/SKILL.md
    ├── references/
    └── tests/
```

## PR Checklist

- [ ] SKILL.md 中的命令与 migrator_tools.py 中的工具名一致
- [ ] 测试全部通过
- [ ] README 安装命令正确
- [ ] 迁移计划格式正确
- [ ] 验证检查点定义完整
