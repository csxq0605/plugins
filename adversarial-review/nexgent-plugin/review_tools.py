"""Adversarial Review tools — Nexgent ToolRegistry integration.

Provides multi-perspective code review with 6 analysis lenses,
unified findings format, health scoring, and iterative fix loop.
"""

import json
import os
import re
from typing import Any
from datetime import datetime


# ---------------------------------------------------------------------------
# Review state management
# ---------------------------------------------------------------------------

class ReviewSession:
    """Manages a single review session with findings and scoring."""

    def __init__(self, session_id: str, target: str, perspectives: list):
        self.session_id = session_id
        self.target = target
        self.perspectives = perspectives
        self.findings = []
        self.health_scores = {}
        self.started_at = datetime.now().isoformat()

    def add_finding(self, finding: dict):
        """Add a validated finding to the session."""
        required = ["id", "perspective", "severity", "title", "file", "risk", "fix"]
        if not all(k in finding for k in required):
            return False
        if finding.get("confidence", 0) < 70:
            return False
        self.findings.append(finding)
        return True

    def calculate_health_score(self) -> dict:
        """Calculate health scores per perspective and overall."""
        severity_weights = {"critical": 15, "warning": 5, "suggestion": 1}
        perspective_scores = {}

        for perspective in self.perspectives:
            p_findings = [f for f in self.findings if f.get("perspective") == perspective]
            deduction = sum(severity_weights.get(f["severity"], 0) for f in p_findings)
            perspective_scores[perspective] = max(0, 100 - deduction)

        if perspective_scores:
            overall = sum(perspective_scores.values()) / len(perspective_scores)
        else:
            overall = 100

        self.health_scores = {
            "overall": round(overall, 1),
            "perspectives": perspective_scores,
            "counts": {
                "critical": len([f for f in self.findings if f["severity"] == "critical"]),
                "warning": len([f for f in self.findings if f["severity"] == "warning"]),
                "suggestion": len([f for f in self.findings if f["severity"] == "suggestion"]),
            }
        }
        return self.health_scores

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "target": self.target,
            "perspectives": self.perspectives,
            "started_at": self.started_at,
            "findings_count": len(self.findings),
            "health_scores": self.health_scores,
            "findings": self.findings,
        }


# Global session store
_sessions: dict[str, ReviewSession] = {}
_session_counter = 0


def _get_next_session_id() -> str:
    global _session_counter
    _session_counter += 1
    return f"review-{_session_counter:04d}"


# ---------------------------------------------------------------------------
# Security patterns loader
# ---------------------------------------------------------------------------

def _load_security_patterns() -> list:
    """Load security patterns from patterns JSON file."""
    patterns_file = os.path.join(os.path.dirname(__file__), "patterns", "security_patterns.json")
    if os.path.exists(patterns_file):
        with open(patterns_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

def _review_start(params: dict) -> str:
    """Start a new review session."""
    target = params.get("target", "")
    perspectives_param = params.get("perspectives", "all")
    mode = params.get("mode", "quick")

    all_perspectives = ["security", "performance", "architecture", "quality", "test", "api"]

    if perspectives_param == "all":
        perspectives = all_perspectives
    else:
        perspectives = [p.strip() for p in perspectives_param.split(",")]
        perspectives = [p for p in perspectives if p in all_perspectives]

    if not perspectives:
        return json.dumps({"error": f"Invalid perspectives. Use: {', '.join(all_perspectives)}"})

    session_id = _get_next_session_id()
    session = ReviewSession(session_id, target, perspectives)
    _sessions[session_id] = session

    return json.dumps({
        "session_id": session_id,
        "target": target,
        "perspectives": perspectives,
        "mode": mode,
        "message": f"Review session {session_id} started. Use review_add_finding to add findings, then review_health_score to get scores.",
    })


def _review_add_finding(params: dict) -> str:
    """Add a finding to a review session."""
    session_id = params.get("session_id", "")
    if session_id not in _sessions:
        return json.dumps({"error": f"Session not found: {session_id}"})

    session = _sessions[session_id]
    finding = {
        "id": params.get("id", ""),
        "perspective": params.get("perspective", ""),
        "severity": params.get("severity", "warning"),
        "title": params.get("title", ""),
        "file": params.get("file", ""),
        "line": params.get("line", 0),
        "evidence": params.get("evidence", ""),
        "risk": params.get("risk", ""),
        "fix": params.get("fix", ""),
        "confidence": params.get("confidence", 80),
        "ref": params.get("ref", ""),
    }

    if session.add_finding(finding):
        return json.dumps({
            "session_id": session_id,
            "finding_id": finding["id"],
            "total_findings": len(session.findings),
            "message": f"Finding {finding['id']} added.",
        })
    return json.dumps({"error": "Finding rejected (missing required fields or low confidence)"})


def _review_get_findings(params: dict) -> str:
    """Get findings from a review session with optional filters."""
    session_id = params.get("session_id", "")
    if session_id not in _sessions:
        return json.dumps({"error": f"Session not found: {session_id}"})

    session = _sessions[session_id]
    findings = session.findings

    # Filter by perspective
    perspective = params.get("perspective", "")
    if perspective:
        findings = [f for f in findings if f["perspective"] == perspective]

    # Filter by severity
    severity = params.get("severity", "")
    if severity:
        findings = [f for f in findings if f["severity"] == severity]

    return json.dumps({
        "session_id": session_id,
        "count": len(findings),
        "findings": findings,
    })


def _review_health_score(params: dict) -> str:
    """Calculate and return health scores for a review session."""
    session_id = params.get("session_id", "")
    if session_id not in _sessions:
        return json.dumps({"error": f"Session not found: {session_id}"})

    session = _sessions[session_id]
    scores = session.calculate_health_score()

    # Determine grade
    overall = scores["overall"]
    if overall >= 90:
        grade = "Excellent"
    elif overall >= 70:
        grade = "Good"
    elif overall >= 50:
        grade = "Needs Improvement"
    else:
        grade = "Critical Issues"

    return json.dumps({
        "session_id": session_id,
        "health_score": scores["overall"],
        "grade": grade,
        "perspective_scores": scores["perspectives"],
        "findings_count": scores["counts"],
    })


def _review_export(params: dict) -> str:
    """Export review results in specified format."""
    session_id = params.get("session_id", "")
    if session_id not in _sessions:
        return json.dumps({"error": f"Session not found: {session_id}"})

    session = _sessions[session_id]
    session.calculate_health_score()
    fmt = params.get("format", "json")

    if fmt == "json":
        return json.dumps(session.to_dict(), ensure_ascii=False, indent=2)

    elif fmt == "markdown":
        scores = session.health_scores
        counts = scores.get("counts", {})

        lines = [
            "# Adversarial Review Report",
            "",
            f"**Session**: {session_id}",
            f"**Target**: {session.target}",
            f"**Health Score**: {scores.get('overall', 0)}/100",
            f"**Findings**: {counts.get('critical', 0)} Critical, "
            f"{counts.get('warning', 0)} Warning, "
            f"{counts.get('suggestion', 0)} Suggestion",
            "",
            "## Perspective Scores",
            "",
            "| Perspective | Score | Critical | Warning | Suggestion |",
            "|-------------|-------|----------|---------|------------|",
        ]

        for p, score in scores.get("perspectives", {}).items():
            p_findings = [f for f in session.findings if f["perspective"] == p]
            c = len([f for f in p_findings if f["severity"] == "critical"])
            w = len([f for f in p_findings if f["severity"] == "warning"])
            s = len([f for f in p_findings if f["severity"] == "suggestion"])
            lines.append(f"| {p.title()} | {score} | {c} | {w} | {s} |")

        lines.append("")

        for severity in ["critical", "warning", "suggestion"]:
            sev_findings = [f for f in session.findings if f["severity"] == severity]
            if sev_findings:
                lines.append(f"## {severity.title()} Issues")
                lines.append("")
                for f in sev_findings:
                    lines.append(f"### [{f['id']}] {f['title']}")
                    lines.append(f"- **File**: {f['file']}:{f.get('line', 0)}")
                    if f.get("evidence"):
                        lines.append(f"- **Evidence**: `{f['evidence']}`")
                    lines.append(f"- **Risk**: {f['risk']}")
                    lines.append(f"- **Fix**: {f['fix']}")
                    if f.get("ref"):
                        lines.append(f"- **Ref**: {f['ref']}")
                    lines.append("")

        return "\n".join(lines)

    elif fmt == "sarif":
        # SARIF 2.1.0 format for GitHub Code Scanning
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "adversarial-review",
                        "version": "1.0.0",
                        "informationUri": "https://github.com/csxq0605/plugins/tree/master/adversarial-review",
                    }
                },
                "results": []
            }]
        }

        for f in session.findings:
            result = {
                "ruleId": f["id"],
                "level": {"critical": "error", "warning": "warning", "suggestion": "note"}.get(f["severity"], "warning"),
                "message": {"text": f["title"]},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": f["file"]},
                        "region": {"startLine": f.get("line", 1)},
                    }
                }],
            }
            sarif["runs"][0]["results"].append(result)

        return json.dumps(sarif, ensure_ascii=False, indent=2)

    return json.dumps({"error": f"Unsupported format: {fmt}. Use: json, markdown, sarif"})


def _review_list_sessions(params: dict) -> str:
    """List all review sessions."""
    sessions_info = []
    for sid, session in _sessions.items():
        sessions_info.append({
            "session_id": sid,
            "target": session.target,
            "perspectives": session.perspectives,
            "findings_count": len(session.findings),
            "started_at": session.started_at,
        })

    return json.dumps({
        "count": len(sessions_info),
        "sessions": sessions_info,
    })


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

def get_tools() -> list:
    """Return review tool definitions for Nexgent's ToolRegistry."""
    try:
        from nexgent.tools.registry import ToolDef
        from nexgent.permissions import Permission
        _has_tooldef = True
    except ImportError:
        _has_tooldef = False

    tools_raw = [
        {
            "name": "review_start",
            "description": (
                "Start a new adversarial review session with multiple perspectives. "
                "Perspectives: security, performance, architecture, quality, test, api. "
                "Use 'all' for comprehensive review or comma-separated for specific ones."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Files or directory to review"},
                    "perspectives": {"type": "string", "description": "Comma-separated perspectives or 'all' (default: all)"},
                    "mode": {"type": "string", "enum": ["quick", "deep", "fix"], "description": "Review mode (default: quick)"},
                },
                "required": ["target"],
            },
            "handler": _review_start,
            "permission": "write",
        },
        {
            "name": "review_add_finding",
            "description": (
                "Add a finding to a review session. Each finding must have: "
                "id, perspective, severity, title, file, risk, fix. "
                "Confidence must be >= 70."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "id": {"type": "string", "description": "Finding ID (e.g., SEC-001)"},
                    "perspective": {"type": "string", "enum": ["security", "performance", "architecture", "quality", "test", "api"]},
                    "severity": {"type": "string", "enum": ["critical", "warning", "suggestion"]},
                    "title": {"type": "string"},
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                    "evidence": {"type": "string", "description": "Code snippet evidence"},
                    "risk": {"type": "string", "description": "Risk description"},
                    "fix": {"type": "string", "description": "Fix suggestion"},
                    "confidence": {"type": "integer", "description": "Confidence 0-100 (must be >= 70)"},
                    "ref": {"type": "string", "description": "Reference (CWE, OWASP, book)"},
                },
                "required": ["session_id", "id", "perspective", "severity", "title", "file", "risk", "fix"],
            },
            "handler": _review_add_finding,
            "permission": "write",
        },
        {
            "name": "review_get_findings",
            "description": "Get findings from a review session with optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "perspective": {"type": "string", "description": "Filter by perspective"},
                    "severity": {"type": "string", "description": "Filter by severity"},
                },
                "required": ["session_id"],
            },
            "handler": _review_get_findings,
            "permission": "read",
        },
        {
            "name": "review_health_score",
            "description": "Calculate and return health scores for a review session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                },
                "required": ["session_id"],
            },
            "handler": _review_health_score,
            "permission": "read",
        },
        {
            "name": "review_export",
            "description": "Export review results in json, markdown, or sarif format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "format": {"type": "string", "enum": ["json", "markdown", "sarif"], "description": "Export format (default: json)"},
                },
                "required": ["session_id"],
            },
            "handler": _review_export,
            "permission": "read",
        },
        {
            "name": "review_list_sessions",
            "description": "List all active review sessions.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
            "handler": _review_list_sessions,
            "permission": "read",
        },
    ]

    if _has_tooldef:
        perm_map = {"read": Permission.READ, "write": Permission.WRITE}
        return [
            ToolDef(
                name=t["name"],
                description=t["description"],
                parameters=t["parameters"],
                handler=t["handler"],
                permission=perm_map.get(t["permission"], Permission.WRITE),
                is_read_only=(t["permission"] == "read"),
                is_concurrency_safe=False,
            )
            for t in tools_raw
        ]

    return tools_raw
