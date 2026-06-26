---
name: atlas
description: >
  Codebase knowledge atlas — multi-agent parallel exploration to map architecture,
  data flows, dependencies, entry points, and coding patterns. Generates living
  documentation that stays in sync with code. Use when: onboarding to a new codebase,
  generating architecture docs, understanding data flows, mapping dependencies,
  answering "how does X work?", or building a knowledge base before a major refactor.
  Triggers: "atlas explore", "atlas map", "atlas query", "map this codebase",
  "generate architecture docs", "how does this project work", "代码库地图",
  "架构文档", "项目分析".
---

# Atlas — Codebase Knowledge Atlas

Build a living knowledge map of any codebase through multi-agent parallel exploration. Atlas answers the question every developer asks on day one: *"How does this thing actually work?"*

## Architecture: Lead Agent + Parallel Explorers

```
User: /atlas explore ./src
         │
    Lead Agent (this skill)
         │
    ┌────┼────┬────────┬──────────┐
    │    │    │        │        Explorer ×5 (parallel)
    │    │    │        │        - Architecture mapper
    │    │    │        │        - Dependency analyzer
    │    │    │        │        - Data flow tracer
    │    │    │        │        - Entry point finder
    │    │    │        │        - Pattern recognizer
    │    │    │        │
    └────┴────┴────────┴──────────┘
         │
    Synthesis → .atlas/ directory
```

**Context efficiency:** Each explorer writes findings to `.atlas/raw/`. Lead agent reads distilled summaries, not raw exploration output.

## Commands

### `/atlas explore [path]`

Launches parallel exploration of a codebase. Default path: current directory.

**What it does:**
1. Creates `.atlas/` directory structure
2. Spawns 5 parallel explorer agents, each investigating a different dimension
3. Each explorer writes findings to `.atlas/raw/<dimension>.md`
4. Lead agent synthesizes findings into `.atlas/SUMMARY.md`

**Explorer dimensions:**
- **Architecture** — Module structure, layering, key abstractions, design patterns
- **Dependencies** — Internal module graph, external deps, version constraints, circular deps
- **Data Flows** — How data moves through the system, transformations, persistence
- **Entry Points** — Main paths, CLI commands, API endpoints, event handlers
- **Patterns** — Coding conventions, naming, error handling, testing patterns

**Usage:**
```bash
/atlas explore                # Explore current directory
/atlas explore ./src          # Explore specific directory
/atlas explore --depth deep   # Deep exploration (more agents, slower)
```

### `/atlas map [path]`

Generates structured architecture documentation from exploration results.

**What it does:**
1. Reads `.atlas/raw/` exploration results
2. Generates structured docs in `.atlas/docs/`:
   - `architecture.md` — Module overview, layer diagram, key abstractions
   - `data-flow.md` — Data movement, transformations, storage
   - `dependencies.md` — Dependency graph, version matrix, health
   - `entry-points.md` — All entry points with call chains
   - `patterns.md` — Coding conventions, anti-patterns, style guide
   - `api-surface.md` — Public API inventory (if applicable)
3. Generates `.atlas/index.md` — Master index linking all docs

**Usage:**
```bash
/atlas map                    # Generate from existing exploration
/atlas map --fresh            # Re-explore then generate
```

### `/atlas query <question>`

Answers questions about the codebase using the generated knowledge.

**What it does:**
1. Loads `.atlas/` knowledge base
2. Searches across all dimensions for relevant information
3. Synthesizes an answer with file references

**Usage:**
```bash
/atlas query "How does authentication work?"
/atlas query "What happens when a user makes a request?"
/atlas query "Where is the database connection configured?"
```

### `/atlas diff [path1] [path2]`

Compares two codebases or snapshots.

**What it does:**
1. Runs exploration on both targets
2. Compares architecture, dependencies, patterns
3. Generates `.atlas/diff.md` with structural changes

**Usage:**
```bash
/atlas diff ./old ./new        # Compare two directories
/atlas diff HEAD~10 HEAD       # Compare git snapshots
```

## Output Structure

```
.atlas/
├── SUMMARY.md              # Executive summary
├── index.md                # Master index
├── raw/                    # Raw exploration findings
│   ├── architecture.md
│   ├── dependencies.md
│   ├── data-flow.md
│   ├── entry-points.md
│   └── patterns.md
└── docs/                   # Generated documentation
    ├── architecture.md
    ├── data-flow.md
    ├── dependencies.md
    ├── entry-points.md
    ├── patterns.md
    └── api-surface.md
```

## Exploration Depth

| Depth | Agents | Time | Detail |
|-------|--------|------|--------|
| `quick` | 3 | ~1 min | High-level overview, top-level modules only |
| `normal` | 5 | ~3 min | Standard exploration, all modules (default) |
| `deep` | 8 | ~8 min | Deep dive, includes implementation details |

## Integration with Superpowers

Atlas follows the Superpowers workflow pattern:
- **Lead Agent** coordinates (this skill) — never does raw exploration
- **Explorer Agents** do the actual work — each writes to `.atlas/raw/`
- **Synthesis** happens in the lead context — distills, doesn't duplicate

When used with `team-coord`, atlas can be run by a lead agent with worker agents as explorers.

## Guardrails

- **Read-only:** Atlas never modifies source code
- **Incremental:** Re-running `explore` updates only changed areas
- **Git-friendly:** `.atlas/` can be committed for team knowledge sharing
- **Privacy:** No data leaves the local environment

## Quick Start

```bash
# 1. Explore the codebase
/atlas explore

# 2. Generate documentation
/atlas map

# 3. Ask questions
/atlas query "What are the main entry points?"

# 4. Review the knowledge base
cat .atlas/SUMMARY.md
```

## When to Use

- **New team member onboarding** — Build understanding fast
- **Pre-refactor analysis** — Know what you're changing before you change it
- **Architecture review** — Generate structured documentation
- **Dependency audit** — Map the dependency graph
- **API documentation** — Auto-generate API surface docs
- **Code review context** — Understand the area around a change
