# Incident Response — Production Incident Handling

Structured incident handling: Triage → Diagnose → Fix → Verify → Postmortem. Timeline tracking, root cause analysis, and automated postmortem generation.

## Install

```bash
claude install-plugin github:csxq0605/plugins
```

## Commands

| Command | Description |
|---------|-------------|
| `/ir start <desc>` | Create incident record, begin triage |
| `/ir triage [id]` | Classify severity (P0-P4) |
| `/ir timeline <event>` | Add timeline event |
| `/ir diagnose [id]` | Root cause analysis |
| `/ir fix <action>` | Record fix action |
| `/ir verify <check>` | Verify fix effectiveness |
| `/ir close [id]` | Close incident |
| `/ir postmortem [id]` | Generate postmortem report |
| `/ir list` | List all incidents |

## Output

```
.incidents/
├── INC-001/
│   ├── incident.json     # Incident metadata
│   ├── timeline.json     # Timeline events
│   ├── diagnosis.md      # Root cause analysis
│   ├── fixes.md          # Fix actions
│   └── postmortem.md     # Postmortem report
└── index.json            # Incident index
```

## Use Cases

- Production outages
- User-reported errors
- Alert-triggered incidents
- Post-incident reviews
