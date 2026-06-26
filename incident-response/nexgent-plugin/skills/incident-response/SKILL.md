---
name: incident-response
description: >
  Structured incident response workflow. Guides through triage → diagnose → fix → verify → postmortem.
  Timeline tracking, root cause analysis, and automated postmortem generation.
---

# Incident Response (Nexgent)

Structured incident handling from detection to postmortem.

## Tools

| Tool | Description |
|------|-------------|
| `ir_start` | Create a new incident record |
| `ir_triage` | Classify severity, gather context |
| `ir_timeline` | Add event to timeline |
| `ir_diagnose` | Root cause analysis |
| `ir_fix` | Record fix action |
| `ir_verify` | Record verification |
| `ir_close` | Close incident |
| `ir_postmortem` | Generate postmortem report |
| `ir_list` | List all incidents |

## Workflow

```
1. ir_start {"title": "..."}          → Create incident
2. ir_triage {"severity": "P1"}       → Classify severity
3. ir_timeline {"event": "..."}       → Track events
4. ir_diagnose {"root_cause": "..."}  → Root cause analysis
5. ir_fix {"action": "..."}           → Record fix
6. ir_verify {"check": "..."}         → Verify fix
7. ir_close {"resolution": "..."}     → Close incident
8. ir_postmortem {"lessons": [...]}   → Generate report
```

## Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| P0 | Complete outage | Immediate |
| P1 | Major feature broken | < 1 hour |
| P2 | Minor feature broken | < 4 hours |
| P3 | Edge case issue | < 24 hours |
| P4 | Low impact | Next sprint |

## Output Structure

```
.incidents/
├── INC-001/
│   ├── incident.json
│   ├── timeline.json
│   ├── diagnosis.md
│   ├── fixes.md
│   └── postmortem.md
└── index.json
```

## Integration with Team Coordination

Works with `team-coord` for multi-agent incident response:
- **Lead agent** coordinates the response
- **Worker agents** handle diagnosis, fix, and verification in parallel
