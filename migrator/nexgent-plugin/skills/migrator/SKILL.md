---
name: migrator
description: >
  Framework and library migration assistant. Analyzes codebases for migration targets,
  generates step-by-step plans, executes with verification at each step.
---

# Migrator — Framework Migration Assistant (Nexgent)

Structured migration workflow: Analyze → Plan → Execute → Verify.

## Tools

| Tool | Description |
|------|-------------|
| `migrator_analyze` | Analyze migration targets |
| `migrator_plan` | Generate migration plan |
| `migrator_execute` | Execute migration step |
| `migrator_verify` | Verify migration step |
| `migrator_status` | Check migration progress |
| `migrator_rollback` | Rollback migration step |

## Workflow

```
1. migrator_analyze {"path": ".", "source": "react", "source_version": "17", "target_version": "18"}
2. migrator_plan {"path": "."}
3. migrator_execute {"path": ".", "step_id": 1}
4. migrator_verify {"path": ".", "step_id": 1, "result": "pass"}
5. migrator_status {"path": "."}
```

## Migration Types

| Type | Example | Complexity |
|------|---------|------------|
| Patch | 4.17.15 → 4.17.21 | Low |
| Minor | 4.17 → 4.18 | Low-Medium |
| Major | 4.x → 5.x | Medium-High |
| Framework | React → Preact | High |

## Output Structure

```
.migrations/
├── react-17-to-18/
│   ├── analysis.json
│   ├── plan.json
│   ├── progress.json
│   ├── verification.json
│   └── steps/
└── index.json
```

## Integration with Team Coordination

Works with `team-coord` for multi-agent migration:
- **Lead agent** coordinates the migration
- **Worker agents** handle different migration steps in parallel
