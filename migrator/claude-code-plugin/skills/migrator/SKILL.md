---
name: migrator
description: >
  Framework and library migration assistant. Analyzes codebases for migration targets,
  generates step-by-step migration plans, executes with verification at each step.
  Handles breaking changes, deprecated APIs, version upgrades, and framework transitions.
  Use when: upgrading dependencies, migrating frameworks, handling deprecation warnings,
  or planning a major version upgrade. Triggers: "migrate", "upgrade", "breaking changes",
  "deprecated", "version upgrade", "迁移", "升级".
---

# Migrator — Framework Migration Assistant

Structured migration workflow: Analyze → Plan → Execute → Verify. Every step is verified before moving forward.

## Architecture

```
User: /migrator analyze react 17→18
         │
    Analysis Agent
    ├── Scan codebase for affected files
    ├── Identify deprecated APIs
    ├── Map breaking changes
    └── Estimate effort
         │
    Planning Agent
    ├── Generate migration steps
    ├── Identify risks and mitigations
    ├── Define verification checkpoints
    └── Create rollback plan
         │
    Execution Agent (per step)
    ├── Apply changes
    ├── Run tests
    ├── Verify behavior
    └── Record progress
         │
    Verification Agent
    ├── Full test suite
    ├── Integration checks
    ├── Performance comparison
    └── Sign-off
```

## Commands

### `/migrator analyze <source> → <target>`

Analyze codebase for migration targets.

**What it does:**
1. Scans for affected files and APIs
2. Identifies deprecated usage
3. Maps breaking changes
4. Estimates effort and risk

**Usage:**
```bash
/migrator analyze react 17→18
/migrator analyze python 3.9→3.12
/migrator analyze express 4→5
/migrator analyze lodash 4→odash
```

**Output:**
- Affected files count
- Deprecated API usage list
- Breaking change inventory
- Risk assessment (low/medium/high)
- Estimated effort (hours)

### `/migrator plan`

Generate a step-by-step migration plan.

**What it does:**
1. Creates ordered migration steps
2. Groups related changes
3. Defines verification checkpoints
4. Identifies rollback points

**Usage:**
```bash
/migrator plan                    # Plan from last analysis
/migrator plan --incremental      # Small, safe steps
/migrator plan --big-bang         # All at once
```

**Plan structure:**
```json
{
  "steps": [
    {
      "id": 1,
      "name": "Update import statements",
      "files": ["src/hooks/*.js"],
      "changes": ["useEffect cleanup → useEffect with return"],
      "verification": "npm test -- --grep hooks",
      "rollback": "git checkout src/hooks/"
    }
  ]
}
```

### `/migrator execute [step-id]`

Execute a migration step.

**What it does:**
1. Applies changes for the specified step
2. Runs verification tests
3. Records progress
4. Stops on failure (doesn't proceed to next step)

**Usage:**
```bash
/migrator execute 1            # Execute step 1
/migrator execute --continue   # Continue from last successful step
/migrator execute --retry      # Retry last failed step
```

### `/migrator verify [step-id]`

Verify that a migration step was successful.

**What it does:**
1. Runs full test suite
2. Checks for regressions
3. Compares behavior with baseline
4. Records verification result

**Usage:**
```bash
/migrator verify 1             # Verify step 1
/migrator verify --full        # Full verification suite
```

### `/migrator status`

Check migration progress.

**Usage:**
```bash
/migrator status               # Show current progress
/migrator status --detailed    # Show per-step details
```

**Output:**
```
Migration: React 17 → 18
Progress: 3/7 steps completed (43%)
Current: Step 4 - Update useEffect hooks
Status: In Progress

Steps:
✅ 1. Update import statements
✅ 2. Replace ReactDOM.render
✅ 3. Update Strict Mode
🔄 4. Update useEffect hooks
⬜ 5. Update Suspense boundaries
⬜ 6. Update Error Boundaries
⬜ 7. Final verification
```

### `/migrator rollback [step-id]`

Rollback a migration step.

**Usage:**
```bash
/migrator rollback 3           # Rollback step 3
/migrator rollback --all       # Rollback everything
```

## Output Structure

```
.migrations/
├── react-17-to-18/
│   ├── analysis.json         # Analysis results
│   ├── plan.json             # Migration plan
│   ├── progress.json         # Step progress tracking
│   ├── verification.json     # Verification results
│   └── steps/
│       ├── step-1.md         # Step details
│       ├── step-2.md
│       └── ...
└── index.json                # Migration index
```

## Migration Types

| Type | Example | Complexity |
|------|---------|------------|
| Patch | 4.17.15 → 4.17.21 | Low |
| Minor | 4.17 → 4.18 | Low-Medium |
| Major | 4.x → 5.x | Medium-High |
| Framework | React → Preact | High |
| Language | Python 2 → 3 | Very High |

## Integration with Superpowers

Migrator follows the Superpowers workflow:
- **Analysis Agent** — Scans and identifies targets
- **Planning Agent** — Generates structured plan
- **Execution Agent** — Applies changes step by step
- **Verification Agent** — Validates each step

When used with `team-coord`, different agents can handle different migration steps in parallel.

## Quick Start

```bash
# 1. Analyze the migration target
/migrator analyze express 4→5

# 2. Generate migration plan
/migrator plan

# 3. Execute step by step
/migrator execute 1
/migrator verify 1
/migrator execute 2
/migrator verify 2

# 4. Check status
/migrator status
```

## When to Use

- **Dependency upgrade** — Major version bump with breaking changes
- **Framework migration** — Switching frameworks or libraries
- **Deprecation handling** — APIs being removed in next version
- **Language upgrade** — Python 2→3, Node.js 14→18
- **API migration** — REST → GraphQL, v1 → v2 API
