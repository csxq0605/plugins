# Incident Response Plugin — Contributor Guide

## Design Principles

1. **结构化流程** — 每个事故遵循 triage → diagnose → fix → verify → postmortem
2. **时间线追踪** — 每个事件都记录在时间线上，可追溯
3. **根因分析** — 不只是修复，要找到根本原因
4. **自动化复盘** — 从时间线自动生成 postmortem 报告

## Architecture

```
incident-response/
├── claude-code-plugin/        # Claude Code 版本
│   ├── .claude-plugin/plugin.json
│   ├── CLAUDE.md
│   ├── README.md
│   └── skills/incident-response/
│       ├── SKILL.md
│       └── references/
└── nexgent-plugin/            # Nexgent 版本
    ├── plugin.json
    ├── __init__.py
    ├── ir_tools.py
    ├── skills/incident-response/SKILL.md
    ├── references/
    └── tests/
```

## PR Checklist

- [ ] SKILL.md 中的命令与 ir_tools.py 中的工具名一致
- [ ] 测试全部通过
- [ ] README 安装命令正确
- [ ] 时间线事件格式正确
- [ ] Postmortem 模板完整
