---
name: incident-response
description: >
  Structured incident response workflow. Guides through triage → diagnose → fix → verify → postmortem.
  Tracks timeline events, performs root cause analysis, and generates postmortem reports.
  Use when: production incident occurs, service is down, users report errors, alerts fire,
  or post-incident review is needed. Triggers: "incident", "outage", "production down",
  "postmortem", "root cause", "事故", "故障", "复盘".
---

# Incident Response

Structured incident handling from detection to postmortem. Every step is tracked on a timeline for accountability and learning.

## Architecture

```
User: /ir start "API returning 500 errors"
         │
    Triage Agent
    ├── Classify severity (P0-P4)
    ├── Create incident record
    └── Identify affected services
         │
    Diagnose Agent
    ├── Timeline tracking
    ├── Root cause investigation
    └── Impact assessment
         │
    Fix Agent
    ├── Track fix actions
    ├── Verification steps
    └── Rollback plan
         │
    Postmortem Agent
    ├── Timeline reconstruction
    ├── Root cause analysis
    ├── Action items
    └── Lessons learned
```

## Commands

### `/ir start <description>`

Create a new incident and begin triage.

**What it does:**
1. Creates incident record in `.incidents/<id>/`
2. Classifies severity (P0-P4)
3. Identifies affected services/components
4. Starts timeline tracking

**Usage:**
```bash
/ir start "API returning 500 errors for all users"
/ir start "Database connection pool exhausted"
/ir start "Payment processing failing intermittently"
```

### `/ir triage [incident-id]`

Classify severity and gather initial context.

**Severity levels:**
| Level | Description | Response Time |
|-------|-------------|---------------|
| P0 | Complete outage, all users affected | Immediate |
| P1 | Major feature broken, most users affected | < 1 hour |
| P2 | Minor feature broken, some users affected | < 4 hours |
| P3 | Edge case issue, few users affected | < 24 hours |
| P4 | Cosmetic or low-impact issue | Next sprint |

**Usage:**
```bash
/ir triage              # Triage current incident
/ir triage INC-001      # Triage specific incident
```

### `/ir timeline <event>`

Add an event to the incident timeline.

**Usage:**
```bash
/ir timeline "Deployed v2.3.1 to production"
/ir timeline "Rolled back to v2.3.0"
/ir timeline "Confirmed fix — error rate back to normal"
```

### `/ir diagnose [incident-id]`

Perform root cause analysis.

**What it does:**
1. Reviews timeline events
2. Analyzes logs, metrics, traces
3. Identifies contributing factors
4. Determines root cause
5. Documents findings

**Usage:**
```bash
/ir diagnose            # Diagnose current incident
/ir diagnose INC-001    # Diagnose specific incident
```

### `/ir fix <action>`

Record a fix action and its verification.

**Usage:**
```bash
/ir fix "Increased connection pool from 10 to 50"
/ir fix "Added retry logic for transient failures"
/ir fix "Deployed hotfix v2.3.2"
```

### `/ir verify <check>`

Record verification that the fix works.

**Usage:**
```bash
/ir verify "Error rate returned to baseline (<0.1%)"
/ir verify "All health checks passing"
/ir verify "Customer confirmations received"
```

### `/ir close [incident-id]`

Close the incident and trigger postmortem generation.

**Usage:**
```bash
/ir close               # Close current incident
/ir close INC-001       # Close specific incident
```

### `/ir postmortem [incident-id]`

Generate postmortem report from incident data.

**What it generates:**
1. Executive summary
2. Timeline reconstruction
3. Root cause analysis
4. Impact assessment
5. Action items with owners
6. Lessons learned

**Usage:**
```bash
/ir postmortem          # Generate for current incident
/ir postmortem INC-001  # Generate for specific incident
```

### `/ir list`

List all incidents.

**Usage:**
```bash
/ir list                # List all incidents
/ir list --open         # List only open incidents
/ir list --severity P0  # List by severity
```

## Output Structure

```
.incidents/
├── INC-001/
│   ├── incident.json     # Incident metadata
│   ├── timeline.json     # Timeline events
│   ├── diagnosis.md      # Root cause analysis
│   ├── fixes.md          # Fix actions taken
│   └── postmortem.md     # Generated postmortem
├── INC-002/
│   └── ...
└── index.json            # Incident index
```

## Incident Record Schema

```json
{
  "id": "INC-001",
  "title": "API returning 500 errors",
  "severity": "P1",
  "status": "open",
  "created_at": "2026-06-27T10:30:00Z",
  "closed_at": null,
  "affected_services": ["api-gateway", "user-service"],
  "timeline": [
    {
      "timestamp": "2026-06-27T10:30:00Z",
      "event": "Incident detected",
      "type": "detection"
    }
  ],
  "diagnosis": {
    "root_cause": null,
    "contributing_factors": [],
    "investigation_notes": []
  },
  "fixes": [],
  "verification": [],
  "action_items": []
}
```

## Integration with Superpowers

Incident response follows the Superpowers workflow:
- **Triage Agent** — Quick classification, context gathering
- **Diagnose Agent** — Deep investigation, root cause analysis
- **Fix Agent** — Track remediation, verify effectiveness
- **Postmortem Agent** — Generate structured report

When used with `team-coord`, different team members can handle different phases.

## Quick Start

```bash
# 1. Start incident response
/ir start "Payment service returning 503"

# 2. Triage
/ir triage

# 3. Track timeline
/ir timeline "Investigating database connections"
/ir timeline "Found connection pool exhaustion"

# 4. Diagnose
/ir diagnose

# 5. Apply fix
/ir fix "Increased pool size to 100"

# 6. Verify
/ir verify "Payment success rate back to 99.9%"

# 7. Close and generate postmortem
/ir close
/ir postmortem
```

## When to Use

- **Production outage** — Service is down or degraded
- **User-reported errors** — Multiple users reporting issues
- **Alert fires** — Monitoring alerts triggered
- **Post-incident review** — Generate postmortem after resolution
- **Incident drill** — Practice incident response process
