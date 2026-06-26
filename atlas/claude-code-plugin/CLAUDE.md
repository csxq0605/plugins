# Atlas Plugin — Contributor Guide

## Design Principles

1. **多 Agent 并行探索** — Lead Agent 协调，Explorer Agents 并行执行，不串行
2. **只读不改** — Atlas 永远不修改源代码，只生成知识文档
3. **增量更新** — 重复运行只更新变化的部分
4. **上下文高效** — Explorer 写 raw findings，Lead 只读摘要

## Architecture

```
Lead Agent (SKILL.md)
├── /atlas explore → 调用 5 个并行 Explorer
├── /atlas map → 从 raw/ 生成 docs/
├── /atlas query → 搜索知识库回答问题
└── /atlas diff → 比较两个代码库
```

## File Structure

```
atlas/
├── claude-code-plugin/        # Claude Code 版本
│   ├── .claude-plugin/plugin.json
│   ├── CLAUDE.md
│   ├── README.md
│   └── skills/atlas/
│       ├── SKILL.md
│       └── references/
└── nexgent-plugin/            # Nexgent 版本
    ├── plugin.json
    ├── __init__.py
    ├── atlas_tools.py
    ├── skills/atlas/SKILL.md
    ├── references/
    └── tests/
```

## PR Checklist

- [ ] SKILL.md 中的命令与 atlas_tools.py 中的工具名一致
- [ ] 测试全部通过
- [ ] README 安装命令正确
- [ ] 不引入外部依赖（标准库优先）
