# Migrator — Framework Migration Assistant

Analyze codebase → identify all touchpoints → generate migration plan → execute step by step → verify at each step. Handles breaking changes and deprecated APIs.

## Install

```bash
claude install-plugin github:csxq0605/plugins
```

## Commands

| Command | Description |
|---------|-------------|
| `/migrator analyze <src> → <target>` | Analyze migration target |
| `/migrator plan` | Generate migration plan |
| `/migrator execute [step]` | Execute migration step |
| `/migrator verify [step]` | Verify migration step |
| `/migrator status` | Check migration progress |
| `/migrator rollback [step]` | Rollback migration step |

## Output

```
.migrations/
├── react-17-to-18/
│   ├── analysis.json     # Analysis results
│   ├── plan.json         # Migration plan
│   ├── progress.json     # Progress tracking
│   └── steps/            # Step details
└── index.json            # Migration index
```

## Use Cases

- Dependency upgrades (e.g., React 17→18)
- Framework migrations (e.g., Express 4→5)
- Deprecated API handling
- Language version upgrades (e.g., Python 3.9→3.12)
