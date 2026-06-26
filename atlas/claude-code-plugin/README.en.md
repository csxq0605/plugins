# Atlas — Codebase Knowledge Atlas

Multi-agent parallel exploration of codebases. Generates architecture docs, data flow maps, dependency analysis, and living knowledge maps.

## Install

```bash
claude install-plugin github:csxq0605/plugins
```

## Commands

| Command | Description |
|---------|-------------|
| `/atlas explore [path]` | Parallel exploration of the codebase |
| `/atlas map [path]` | Generate structured docs from exploration |
| `/atlas query <question>` | Answer questions using the knowledge base |
| `/atlas diff [path1] [path2]` | Compare two codebases structurally |

## Output

```
.atlas/
├── SUMMARY.md          # Executive summary
├── index.md            # Master index
├── raw/                # Raw exploration findings
└── docs/               # Generated documentation
```

## Use Cases

- **Onboarding** — Understand a codebase fast
- **Pre-refactor** — Know the impact before changing
- **Architecture review** — Auto-generate docs
- **API docs** — Extract public API surface
