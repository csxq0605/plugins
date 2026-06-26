"""Incident Response Nexgent Plugin — Structured incident handling tools.

Triage, diagnose, fix, verify, postmortem. Timeline tracking, root cause analysis,
and automated postmortem generation.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Tool definitions
TOOL_DEFS = []
PERMISSIONS = {}

def _register(name, description, parameters, permission_desc):
    TOOL_DEFS.append({
        "name": name,
        "description": description,
        "parameters": parameters,
    })
    PERMISSIONS[name] = permission_desc


# ============================================================
# Severity definitions
# ============================================================

SEVERITY_LEVELS = {
    "P0": {"name": "Critical", "description": "Complete outage, all users affected", "response": "Immediate"},
    "P1": {"name": "Major", "description": "Major feature broken, most users affected", "response": "< 1 hour"},
    "P2": {"name": "Significant", "description": "Minor feature broken, some users affected", "response": "< 4 hours"},
    "P3": {"name": "Minor", "description": "Edge case issue, few users affected", "response": "< 24 hours"},
    "P4": {"name": "Low", "description": "Cosmetic or low-impact issue", "response": "Next sprint"},
}

STATUS_VALUES = ["open", "investigating", "fixing", "verifying", "closed"]


# ============================================================
# Helpers
# ============================================================

def _get_incidents_dir(root: Path = None) -> Path:
    """Get the incidents directory relative to project root."""
    base = root if root else Path.cwd()
    return (base / ".incidents").resolve()


def _ensure_incidents_dir(root: Path = None) -> Path:
    """Ensure incidents directory exists."""
    incidents_dir = _get_incidents_dir(root)
    incidents_dir.mkdir(parents=True, exist_ok=True)
    return incidents_dir


def _load_index(incidents_dir: Path) -> dict:
    """Load the incident index."""
    index_file = incidents_dir / "index.json"
    if index_file.exists():
        try:
            return json.loads(index_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"incidents": [], "next_id": 1}


def _save_index(incidents_dir: Path, index: dict):
    """Save the incident index."""
    (incidents_dir / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def _generate_incident_id(index: dict) -> str:
    """Generate a new incident ID."""
    inc_id = f"INC-{index['next_id']:03d}"
    index["next_id"] += 1
    return inc_id


def _load_incident(incidents_dir: Path, inc_id: str) -> dict | None:
    """Load an incident record."""
    inc_dir = incidents_dir / inc_id
    inc_file = inc_dir / "incident.json"
    if inc_file.exists():
        try:
            return json.loads(inc_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def _save_incident(incidents_dir: Path, inc_id: str, incident: dict):
    """Save an incident record."""
    inc_dir = incidents_dir / inc_id
    inc_dir.mkdir(parents=True, exist_ok=True)
    (inc_dir / "incident.json").write_text(
        json.dumps(incident, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def _load_timeline(incidents_dir: Path, inc_id: str) -> list:
    """Load timeline events."""
    inc_dir = incidents_dir / inc_id
    timeline_file = inc_dir / "timeline.json"
    if timeline_file.exists():
        try:
            return json.loads(timeline_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _save_timeline(incidents_dir: Path, inc_id: str, timeline: list):
    """Save timeline events."""
    inc_dir = incidents_dir / inc_id
    inc_dir.mkdir(parents=True, exist_ok=True)
    (inc_dir / "timeline.json").write_text(
        json.dumps(timeline, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def _now_iso() -> str:
    """Get current time in ISO format."""
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# Tool: ir_start
# ============================================================

_register(
    name="ir_start",
    description="Create a new incident record and begin triage.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project root path. Incidents will be stored in <path>/.incidents/",
            },
            "title": {
                "type": "string",
                "description": "Brief description of the incident.",
            },
            "severity": {
                "type": "string",
                "enum": ["P0", "P1", "P2", "P3", "P4"],
                "description": "Initial severity classification. Default: P2 (will be refined during triage).",
            },
            "affected_services": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of affected services/components.",
            },
        },
        "required": ["title"],
    },
    permission_desc="Create incident record in .incidents/ directory.",
)


def _ir_start(args: dict) -> dict:
    """Create a new incident."""
    root = Path(args.get("path", ".")).resolve()
    incidents_dir = _ensure_incidents_dir(root)
    index = _load_index(incidents_dir)

    inc_id = _generate_incident_id(index)
    now = _now_iso()

    incident = {
        "id": inc_id,
        "title": args["title"],
        "severity": args.get("severity", "P2"),
        "status": "open",
        "created_at": now,
        "closed_at": None,
        "affected_services": args.get("affected_services", []),
        "diagnosis": {
            "root_cause": None,
            "contributing_factors": [],
            "investigation_notes": [],
        },
        "fixes": [],
        "verification": [],
        "action_items": [],
    }

    # Add initial timeline event
    timeline = [{
        "timestamp": now,
        "event": f"Incident created: {args['title']}",
        "type": "detection",
        "details": f"Severity: {incident['severity']}",
    }]

    _save_incident(incidents_dir, inc_id, incident)
    _save_timeline(incidents_dir, inc_id, timeline)

    # Update index
    index["incidents"].append({
        "id": inc_id,
        "title": args["title"],
        "severity": incident["severity"],
        "status": "open",
        "created_at": now,
    })
    _save_index(incidents_dir, index)

    return {
        "incident_id": inc_id,
        "title": args["title"],
        "severity": incident["severity"],
        "status": "open",
        "message": f"Incident {inc_id} created. Use ir_triage to classify severity and ir_timeline to track events.",
    }


# ============================================================
# Tool: ir_triage
# ============================================================

_register(
    name="ir_triage",
    description="Classify incident severity and gather initial context.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project root path. Data will be stored in <path>/.incidents/",
            },
            "incident_id": {
                "type": "string",
                "description": "Incident ID (e.g., INC-001). If not provided, uses the most recent open incident.",
            },
            "severity": {
                "type": "string",
                "enum": ["P0", "P1", "P2", "P3", "P4"],
                "description": "Updated severity classification.",
            },
            "affected_services": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of affected services/components.",
            },
            "notes": {
                "type": "string",
                "description": "Triage notes or observations.",
            },
        },
        "required": [],
    },
    permission_desc="Update incident record with triage information.",
)


def _ir_triage(args: dict) -> dict:
    """Triage an incident."""
    incidents_dir = _ensure_incidents_dir(Path(args.get("path", ".")).resolve())
    inc_id = args.get("incident_id")

    # Find incident
    if not inc_id:
        # Find most recent open incident
        index = _load_index(incidents_dir)
        open_incidents = [i for i in index["incidents"] if i["status"] != "closed"]
        if not open_incidents:
            return {"error": "No open incidents found. Use ir_start to create one."}
        inc_id = open_incidents[-1]["id"]

    incident = _load_incident(incidents_dir, inc_id)
    if not incident:
        return {"error": f"Incident {inc_id} not found."}

    # Update severity if provided
    if "severity" in args:
        incident["severity"] = args["severity"]

    # Update affected services if provided
    if "affected_services" in args:
        incident["affected_services"] = args["affected_services"]

    # Update status
    incident["status"] = "investigating"

    _save_incident(incidents_dir, inc_id, incident)

    # Add timeline event
    timeline = _load_timeline(incidents_dir, inc_id)
    timeline.append({
        "timestamp": _now_iso(),
        "event": "Triage completed",
        "type": "triage",
        "details": f"Severity: {incident['severity']}, Services: {', '.join(incident['affected_services']) or 'unknown'}",
    })
    if "notes" in args:
        timeline.append({
            "timestamp": _now_iso(),
            "event": "Triage notes",
            "type": "note",
            "details": args["notes"],
        })
    _save_timeline(incidents_dir, inc_id, timeline)

    # Update index
    index = _load_index(incidents_dir)
    for inc in index["incidents"]:
        if inc["id"] == inc_id:
            inc["severity"] = incident["severity"]
            inc["status"] = incident["status"]
            break
    _save_index(incidents_dir, index)

    return {
        "incident_id": inc_id,
        "severity": incident["severity"],
        "status": incident["status"],
        "affected_services": incident["affected_services"],
        "response_time": SEVERITY_LEVELS[incident["severity"]]["response"],
    }


# ============================================================
# Tool: ir_timeline
# ============================================================

_register(
    name="ir_timeline",
    description="Add an event to the incident timeline.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project root path. Data will be stored in <path>/.incidents/",
            },
            "incident_id": {
                "type": "string",
                "description": "Incident ID. If not provided, uses the most recent open incident.",
            },
            "event": {
                "type": "string",
                "description": "Description of the event.",
            },
            "type": {
                "type": "string",
                "enum": ["detection", "triage", "investigation", "fix", "verification", "note", "update"],
                "description": "Event type. Default: update.",
            },
        },
        "required": ["event"],
    },
    permission_desc="Add event to incident timeline.",
)


def _ir_timeline(args: dict) -> dict:
    """Add a timeline event."""
    incidents_dir = _ensure_incidents_dir(Path(args.get("path", ".")).resolve())
    inc_id = args.get("incident_id")

    if not inc_id:
        index = _load_index(incidents_dir)
        open_incidents = [i for i in index["incidents"] if i["status"] != "closed"]
        if not open_incidents:
            return {"error": "No open incidents found."}
        inc_id = open_incidents[-1]["id"]

    incident = _load_incident(incidents_dir, inc_id)
    if not incident:
        return {"error": f"Incident {inc_id} not found."}

    timeline = _load_timeline(incidents_dir, inc_id)
    timeline.append({
        "timestamp": _now_iso(),
        "event": args["event"],
        "type": args.get("type", "update"),
    })
    _save_timeline(incidents_dir, inc_id, timeline)

    return {
        "incident_id": inc_id,
        "timeline_length": len(timeline),
        "event_added": args["event"],
    }


# ============================================================
# Tool: ir_diagnose
# ============================================================

_register(
    name="ir_diagnose",
    description="Perform root cause analysis on an incident.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project root path. Data will be stored in <path>/.incidents/",
            },
            "incident_id": {
                "type": "string",
                "description": "Incident ID. If not provided, uses the most recent open incident.",
            },
            "root_cause": {
                "type": "string",
                "description": "Identified root cause.",
            },
            "contributing_factors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Contributing factors to the incident.",
            },
            "notes": {
                "type": "string",
                "description": "Investigation notes.",
            },
        },
        "required": [],
    },
    permission_desc="Update incident with diagnosis information.",
)


def _ir_diagnose(args: dict) -> dict:
    """Diagnose an incident."""
    incidents_dir = _ensure_incidents_dir(Path(args.get("path", ".")).resolve())
    inc_id = args.get("incident_id")

    if not inc_id:
        index = _load_index(incidents_dir)
        open_incidents = [i for i in index["incidents"] if i["status"] != "closed"]
        if not open_incidents:
            return {"error": "No open incidents found."}
        inc_id = open_incidents[-1]["id"]

    incident = _load_incident(incidents_dir, inc_id)
    if not incident:
        return {"error": f"Incident {inc_id} not found."}

    # Update diagnosis
    if "root_cause" in args:
        incident["diagnosis"]["root_cause"] = args["root_cause"]
    if "contributing_factors" in args:
        incident["diagnosis"]["contributing_factors"] = args["contributing_factors"]
    if "notes" in args:
        incident["diagnosis"]["investigation_notes"].append(args["notes"])

    # Update status
    incident["status"] = "fixing"

    _save_incident(incidents_dir, inc_id, incident)

    # Add timeline event
    timeline = _load_timeline(incidents_dir, inc_id)
    timeline.append({
        "timestamp": _now_iso(),
        "event": "Diagnosis completed",
        "type": "investigation",
        "details": f"Root cause: {args.get('root_cause', 'Not yet identified')}",
    })
    _save_timeline(incidents_dir, inc_id, timeline)

    # Save diagnosis report
    inc_dir = incidents_dir / inc_id
    diagnosis_md = [
        "# Root Cause Analysis",
        "",
        f"**Incident:** {inc_id}",
        f"**Title:** {incident['title']}",
        f"**Severity:** {incident['severity']}",
        "",
        "## Root Cause",
        "",
        incident["diagnosis"]["root_cause"] or "Not yet identified",
        "",
        "## Contributing Factors",
        "",
    ]
    for factor in incident["diagnosis"]["contributing_factors"]:
        diagnosis_md.append(f"- {factor}")
    if not incident["diagnosis"]["contributing_factors"]:
        diagnosis_md.append("- None identified yet")

    diagnosis_md.extend(["", "## Investigation Notes", ""])
    for note in incident["diagnosis"]["investigation_notes"]:
        diagnosis_md.append(f"- {note}")

    (inc_dir / "diagnosis.md").write_text("\n".join(diagnosis_md), encoding="utf-8")

    return {
        "incident_id": inc_id,
        "root_cause": incident["diagnosis"]["root_cause"],
        "contributing_factors": incident["diagnosis"]["contributing_factors"],
        "status": incident["status"],
    }


# ============================================================
# Tool: ir_fix
# ============================================================

_register(
    name="ir_fix",
    description="Record a fix action for an incident.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project root path. Data will be stored in <path>/.incidents/",
            },
            "incident_id": {
                "type": "string",
                "description": "Incident ID. If not provided, uses the most recent open incident.",
            },
            "action": {
                "type": "string",
                "description": "Description of the fix action.",
            },
            "rollback": {
                "type": "string",
                "description": "Rollback plan if the fix fails.",
            },
        },
        "required": ["action"],
    },
    permission_desc="Record fix action in incident record.",
)


def _ir_fix(args: dict) -> dict:
    """Record a fix action."""
    incidents_dir = _ensure_incidents_dir(Path(args.get("path", ".")).resolve())
    inc_id = args.get("incident_id")

    if not inc_id:
        index = _load_index(incidents_dir)
        open_incidents = [i for i in index["incidents"] if i["status"] != "closed"]
        if not open_incidents:
            return {"error": "No open incidents found."}
        inc_id = open_incidents[-1]["id"]

    incident = _load_incident(incidents_dir, inc_id)
    if not incident:
        return {"error": f"Incident {inc_id} not found."}

    fix = {
        "timestamp": _now_iso(),
        "action": args["action"],
        "rollback": args.get("rollback"),
    }
    incident["fixes"].append(fix)

    _save_incident(incidents_dir, inc_id, incident)

    # Add timeline event
    timeline = _load_timeline(incidents_dir, inc_id)
    timeline.append({
        "timestamp": _now_iso(),
        "event": f"Fix applied: {args['action']}",
        "type": "fix",
        "details": f"Rollback: {args.get('rollback', 'None specified')}",
    })
    _save_timeline(incidents_dir, inc_id, timeline)

    return {
        "incident_id": inc_id,
        "fixes_count": len(incident["fixes"]),
        "action_recorded": args["action"],
    }


# ============================================================
# Tool: ir_verify
# ============================================================

_register(
    name="ir_verify",
    description="Record verification that a fix works.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project root path. Data will be stored in <path>/.incidents/",
            },
            "incident_id": {
                "type": "string",
                "description": "Incident ID. If not provided, uses the most recent open incident.",
            },
            "check": {
                "type": "string",
                "description": "Verification check performed.",
            },
            "result": {
                "type": "string",
                "enum": ["pass", "fail", "partial"],
                "description": "Verification result. Default: pass.",
            },
        },
        "required": ["check"],
    },
    permission_desc="Record verification in incident record.",
)


def _ir_verify(args: dict) -> dict:
    """Record verification."""
    incidents_dir = _ensure_incidents_dir(Path(args.get("path", ".")).resolve())
    inc_id = args.get("incident_id")

    if not inc_id:
        index = _load_index(incidents_dir)
        open_incidents = [i for i in index["incidents"] if i["status"] != "closed"]
        if not open_incidents:
            return {"error": "No open incidents found."}
        inc_id = open_incidents[-1]["id"]

    incident = _load_incident(incidents_dir, inc_id)
    if not incident:
        return {"error": f"Incident {inc_id} not found."}

    verification = {
        "timestamp": _now_iso(),
        "check": args["check"],
        "result": args.get("result", "pass"),
    }
    incident["verification"].append(verification)

    # Update status
    incident["status"] = "verifying"

    _save_incident(incidents_dir, inc_id, incident)

    # Update index
    index = _load_index(incidents_dir)
    for inc in index["incidents"]:
        if inc["id"] == inc_id:
            inc["status"] = "verifying"
            break
    _save_index(incidents_dir, index)

    # Add timeline event
    timeline = _load_timeline(incidents_dir, inc_id)
    timeline.append({
        "timestamp": _now_iso(),
        "event": f"Verification: {args['check']}",
        "type": "verification",
        "details": f"Result: {args.get('result', 'pass')}",
    })
    _save_timeline(incidents_dir, inc_id, timeline)

    return {
        "incident_id": inc_id,
        "verification_count": len(incident["verification"]),
        "check_recorded": args["check"],
        "result": args.get("result", "pass"),
    }


# ============================================================
# Tool: ir_close
# ============================================================

_register(
    name="ir_close",
    description="Close an incident and trigger postmortem generation.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project root path. Data will be stored in <path>/.incidents/",
            },
            "incident_id": {
                "type": "string",
                "description": "Incident ID. If not provided, uses the most recent open incident.",
            },
            "resolution": {
                "type": "string",
                "description": "Summary of how the incident was resolved.",
            },
        },
        "required": [],
    },
    permission_desc="Close incident and update index.",
)


def _ir_close(args: dict) -> dict:
    """Close an incident."""
    incidents_dir = _ensure_incidents_dir(Path(args.get("path", ".")).resolve())
    inc_id = args.get("incident_id")

    if not inc_id:
        index = _load_index(incidents_dir)
        open_incidents = [i for i in index["incidents"] if i["status"] != "closed"]
        if not open_incidents:
            return {"error": "No open incidents found."}
        inc_id = open_incidents[-1]["id"]

    incident = _load_incident(incidents_dir, inc_id)
    if not incident:
        return {"error": f"Incident {inc_id} not found."}

    now = _now_iso()
    incident["status"] = "closed"
    incident["closed_at"] = now

    if "resolution" in args:
        incident["resolution"] = args["resolution"]

    _save_incident(incidents_dir, inc_id, incident)

    # Add timeline event
    timeline = _load_timeline(incidents_dir, inc_id)
    timeline.append({
        "timestamp": now,
        "event": "Incident closed",
        "type": "update",
        "details": args.get("resolution", "Resolved"),
    })
    _save_timeline(incidents_dir, inc_id, timeline)

    # Update index
    index = _load_index(incidents_dir)
    for inc in index["incidents"]:
        if inc["id"] == inc_id:
            inc["status"] = "closed"
            break
    _save_index(incidents_dir, index)

    # Calculate duration
    created = datetime.fromisoformat(incident["created_at"])
    closed = datetime.fromisoformat(now)
    duration = closed - created

    return {
        "incident_id": inc_id,
        "status": "closed",
        "duration_hours": round(duration.total_seconds() / 3600, 2),
        "message": f"Incident {inc_id} closed. Use ir_postmortem to generate report.",
    }


# ============================================================
# Tool: ir_postmortem
# ============================================================

_register(
    name="ir_postmortem",
    description="Generate a postmortem report from incident data.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project root path. Data will be stored in <path>/.incidents/",
            },
            "incident_id": {
                "type": "string",
                "description": "Incident ID. If not provided, uses the most recent closed incident.",
            },
            "action_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "owner": {"type": "string"},
                        "due_date": {"type": "string"},
                    },
                    "required": ["action"],
                },
                "description": "Action items to prevent recurrence.",
            },
            "lessons": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lessons learned from this incident.",
            },
        },
        "required": [],
    },
    permission_desc="Generate postmortem report in incident directory.",
)


def _ir_postmortem(args: dict) -> dict:
    """Generate a postmortem report."""
    incidents_dir = _ensure_incidents_dir(Path(args.get("path", ".")).resolve())
    inc_id = args.get("incident_id")

    if not inc_id:
        # Find most recent closed incident
        index = _load_index(incidents_dir)
        closed_incidents = [i for i in index["incidents"] if i["status"] == "closed"]
        if not closed_incidents:
            # Try open incidents too
            if index["incidents"]:
                inc_id = index["incidents"][-1]["id"]
            else:
                return {"error": "No incidents found."}
        else:
            inc_id = closed_incidents[-1]["id"]

    incident = _load_incident(incidents_dir, inc_id)
    if not incident:
        return {"error": f"Incident {inc_id} not found."}

    timeline = _load_timeline(incidents_dir, inc_id)

    # Add action items if provided
    if "action_items" in args:
        incident["action_items"] = args["action_items"]
        _save_incident(incidents_dir, inc_id, incident)

    # Add lessons if provided
    if "lessons" in args:
        incident["lessons"] = args["lessons"]
        _save_incident(incidents_dir, inc_id, incident)

    # Generate postmortem markdown
    lines = [
        f"# Postmortem: {incident['title']}",
        "",
        f"**Incident ID:** {inc_id}",
        f"**Severity:** {incident['severity']} ({SEVERITY_LEVELS[incident['severity']]['name']})",
        f"**Status:** {incident['status']}",
        f"**Created:** {incident['created_at']}",
        f"**Closed:** {incident.get('closed_at', 'N/A')}",
        "",
        "## Executive Summary",
        "",
        f"{incident['title']}. ",
        f"This was a {SEVERITY_LEVELS[incident['severity']]['name'].lower()} severity incident ",
        f"that affected {', '.join(incident.get('affected_services', ['unknown services']))}.",
        "",
        "## Timeline",
        "",
        "| Timestamp | Event | Type |",
        "|-----------|-------|------|",
    ]

    for event in timeline:
        ts = event["timestamp"][:19].replace("T", " ")
        lines.append(f"| {ts} | {event['event']} | {event['type']} |")

    lines.extend([
        "",
        "## Root Cause Analysis",
        "",
        "### Root Cause",
        "",
        incident["diagnosis"].get("root_cause") or "Not identified",
        "",
        "### Contributing Factors",
        "",
    ])
    for factor in incident["diagnosis"].get("contributing_factors", []):
        lines.append(f"- {factor}")
    if not incident["diagnosis"].get("contributing_factors"):
        lines.append("- None identified")

    lines.extend([
        "",
        "## Impact Assessment",
        "",
        f"- **Affected Services:** {', '.join(incident.get('affected_services', ['Unknown']))}",
        f"- **Severity:** {incident['severity']}",
        "",
        "## Fix Actions",
        "",
    ])
    for fix in incident.get("fixes", []):
        lines.append(f"- {fix['action']}")
        if fix.get("rollback"):
            lines.append(f"  - Rollback: {fix['rollback']}")
    if not incident.get("fixes"):
        lines.append("- No fixes recorded")

    lines.extend([
        "",
        "## Verification",
        "",
    ])
    for ver in incident.get("verification", []):
        lines.append(f"- [{ver['result'].upper()}] {ver['check']}")
    if not incident.get("verification"):
        lines.append("- No verification recorded")

    lines.extend([
        "",
        "## Action Items",
        "",
        "| Action | Owner | Due Date |",
        "|--------|-------|----------|",
    ])
    for item in incident.get("action_items", []):
        lines.append(f"| {item['action']} | {item.get('owner', 'TBD')} | {item.get('due_date', 'TBD')} |")
    if not incident.get("action_items"):
        lines.append("| No action items | - | - |")

    lines.extend([
        "",
        "## Lessons Learned",
        "",
    ])
    for lesson in incident.get("lessons", []):
        lines.append(f"- {lesson}")
    if not incident.get("lessons"):
        lines.append("- To be filled during postmortem meeting")

    lines.extend([
        "",
        "---",
        "",
        f"*Generated on {_now_iso()[:19]}*",
    ])

    # Save postmortem
    inc_dir = incidents_dir / inc_id
    postmortem_path = inc_dir / "postmortem.md"
    postmortem_path.write_text("\n".join(lines), encoding="utf-8")

    # Also save fixes
    fixes_md = ["# Fix Actions", ""]
    for fix in incident.get("fixes", []):
        fixes_md.append(f"## {fix['timestamp'][:19]}")
        fixes_md.append(f"- **Action:** {fix['action']}")
        if fix.get("rollback"):
            fixes_md.append(f"- **Rollback:** {fix['rollback']}")
        fixes_md.append("")
    (inc_dir / "fixes.md").write_text("\n".join(fixes_md), encoding="utf-8")

    return {
        "incident_id": inc_id,
        "postmortem_path": str(postmortem_path),
        "timeline_events": len(timeline),
        "fixes_count": len(incident.get("fixes", [])),
        "action_items_count": len(incident.get("action_items", [])),
    }


# ============================================================
# Tool: ir_list
# ============================================================

_register(
    name="ir_list",
    description="List all incidents with optional filters.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project root path. Data will be stored in <path>/.incidents/",
            },
            "status": {
                "type": "string",
                "enum": ["open", "investigating", "fixing", "verifying", "closed"],
                "description": "Filter by status.",
            },
            "severity": {
                "type": "string",
                "enum": ["P0", "P1", "P2", "P3", "P4"],
                "description": "Filter by severity.",
            },
        },
        "required": [],
    },
    permission_desc="Read incident index.",
)


def _ir_list(args: dict) -> dict:
    """List incidents."""
    incidents_dir = _ensure_incidents_dir(Path(args.get("path", ".")).resolve())
    index = _load_index(incidents_dir)

    incidents = index["incidents"]

    # Apply filters
    if "status" in args:
        incidents = [i for i in incidents if i["status"] == args["status"]]
    if "severity" in args:
        incidents = [i for i in incidents if i["severity"] == args["severity"]]

    return {
        "total": len(incidents),
        "incidents": incidents,
    }


# ============================================================
# Tool dispatch
# ============================================================

def get_tools() -> list[dict]:
    """Return all registered tool definitions."""
    return TOOL_DEFS


def get_permissions() -> dict:
    """Return tool permission descriptions."""
    return PERMISSIONS


def call_tool(name: str, args: dict) -> Any:
    """Dispatch a tool call."""
    dispatch = {
        "ir_start": _ir_start,
        "ir_triage": _ir_triage,
        "ir_timeline": _ir_timeline,
        "ir_diagnose": _ir_diagnose,
        "ir_fix": _ir_fix,
        "ir_verify": _ir_verify,
        "ir_close": _ir_close,
        "ir_postmortem": _ir_postmortem,
        "ir_list": _ir_list,
    }

    if name in dispatch:
        return dispatch[name](args)
    else:
        return {"error": f"Unknown tool: {name}"}
