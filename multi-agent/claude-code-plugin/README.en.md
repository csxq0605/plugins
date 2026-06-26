# team-coord (Claude Code Plugin)

A Claude Code plugin providing multi-agent team coordination — a **supplement** to subagent and workflow.

- **`team-coord:lead`** — Pure coordinator: spawn workers, assign tasks, collect results, shutdown approval. **Never does actual work.**
- **`team-coord:teammate`** — Actual executor: performs tasks, reports to lead. Can use all tools (web_search, subagent, etc.).

Plus optional reference docs for layering the `superpowers` development workflow on top.

## Installation

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/multi-agent/claude-code-plugin
```

## Plugin Positioning: Supplement Layer

| Task Complexity | Approach |
|---|---|
| Simple | Direct execution |
| Medium | Subagent fan-out |
| Complex | **team-coord** — lead coordinates multiple workers in parallel |

## Subskills

| Subskill | Role | Covers |
|---|---|---|
| `team-coord:lead` | Pure coordinator | Spawn, task assignment, shutdown approval, result synthesis |
| `team-coord:teammate` | Actual executor | Inbox sync, dispatch limits, completion reporting |

## Core Design

- **Lead never does actual work** — Only 5 things: analyze → spawn → wait → synthesize → close
- **WHAT vs HOW** — Lead only passes task definitions, never restates execution details
- **Inbox sync** — Two trigger points for inbox checking, prevents rendezvous failure
- **Hub-and-spoke** — Only lead can spawn/delete, teammates communicate via inbox
- **Shutdown requires user approval** — Hard rule, prevents losing in-flight work

## License

MIT
