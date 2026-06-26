---
name: atlas
description: >
  Codebase knowledge atlas — multi-agent parallel exploration to map architecture,
  data flows, dependencies, entry points, and coding patterns. Generates living
  documentation that stays in sync with code.
---

# Atlas — Codebase Knowledge Atlas (Nexgent)

Build a living knowledge map of any codebase through multi-agent parallel exploration.

## Tools

| Tool | Description |
|------|-------------|
| `atlas_explore` | Explore a codebase across 5 dimensions |
| `atlas_map` | Generate structured documentation |
| `atlas_query` | Answer questions about the codebase |
| `atlas_diff` | Compare two codebases structurally |

## Workflow

```
1. atlas_explore <path>     → Parallel exploration across 5 dimensions
2. atlas_map <path>         → Generate .atlas/ with docs
3. atlas_query <question>   → Search the knowledge base
```

## Exploration Dimensions

| Dimension | What it finds |
|-----------|---------------|
| Architecture | Modules, layers, project types, languages |
| Dependencies | External deps, internal import graph |
| Data Flow | Input points, output points, storage, transforms |
| Entry Points | Main files, CLI commands, API routes |
| Patterns | Naming conventions, testing, error handling |

## Usage

```bash
# Explore current directory
atlas_explore {"path": "."}

# Generate documentation
atlas_map {"path": "."}

# Ask a question
atlas_query {"path": ".", "question": "How does authentication work?"}

# Compare two codebases
atlas_diff {"path1": "./old", "path2": "./new"}
```

## Output Structure

```
.atlas/
├── SUMMARY.md              # Executive summary
├── index.md                # Master index
├── raw/                    # Raw exploration data
│   ├── architecture.md
│   ├── dependencies.md
│   ├── data-flow.md
│   ├── entry-points.md
│   └── patterns.md
└── docs/                   # Generated documentation
    ├── architecture.md
    ├── dependencies.md
    ├── data-flow.md
    ├── entry-points.md
    └── patterns.md
```

## Integration with Team Coordination

Atlas works with the `team-coord` plugin for multi-agent exploration:
- **Lead agent** coordinates the exploration
- **Worker agents** explore different dimensions in parallel
- Results are synthesized into the `.atlas/` knowledge base
