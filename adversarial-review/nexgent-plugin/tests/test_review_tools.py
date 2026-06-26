"""Tests for adversarial-review Nexgent plugin."""
import json
import pytest
from review_tools import get_tools, get_permissions, call_tool


def _parse(result):
    """Parse JSON string result to dict."""
    if isinstance(result, str):
        return json.loads(result)
    return result


class TestToolRegistration:
    def test_get_tools_returns_list(self):
        tools = get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 6

    def test_tool_names(self):
        tools = get_tools()
        names = set()
        for t in tools:
            if hasattr(t, "name"):
                names.add(t.name)
            elif isinstance(t, dict):
                names.add(t["name"])
        expected = {"review_start", "review_add_finding", "review_get_findings",
                    "review_health_score", "review_export", "review_list_sessions"}
        assert names == expected

    def test_get_permissions(self):
        perms = get_permissions()
        assert isinstance(perms, dict)
        assert len(perms) == 6


class TestReviewSession:
    def test_start_session(self):
        result = _parse(call_tool("review_start", {"target": "src/", "perspectives": "all", "mode": "quick"}))
        assert "session_id" in result
        assert result["target"] == "src/"

    def test_add_finding(self):
        session = _parse(call_tool("review_start", {"target": "."}))
        sid = session["session_id"]
        result = _parse(call_tool("review_add_finding", {
            "session_id": sid,
            "id": "SEC-001",
            "perspective": "security",
            "severity": "critical",
            "title": "SQL Injection",
            "file": "src/db.py",
            "line": 42,
            "evidence": "query = f'SELECT * FROM users WHERE id={uid}'",
            "risk": "Arbitrary SQL execution",
            "fix": "Use parameterized queries",
            "confidence": 95,
            "ref": "CWE-89",
        }))
        assert "finding_id" in result

    def test_health_score(self):
        session = _parse(call_tool("review_start", {"target": "."}))
        sid = session["session_id"]
        call_tool("review_add_finding", {
            "session_id": sid, "id": "SEC-001", "perspective": "security",
            "severity": "critical", "title": "Test", "file": "a.py", "line": 1,
            "evidence": "x", "risk": "y", "fix": "z", "confidence": 90,
        })
        result = _parse(call_tool("review_health_score", {"session_id": sid}))
        assert "health_score" in result
        assert result["health_score"] < 100

    def test_export_markdown(self):
        session = _parse(call_tool("review_start", {"target": "."}))
        sid = session["session_id"]
        result = call_tool("review_export", {"session_id": sid, "format": "markdown"})
        assert isinstance(result, str)
        assert "Review Report" in result

    def test_list_sessions(self):
        call_tool("review_start", {"target": "."})
        result = _parse(call_tool("review_list_sessions", {}))
        assert "sessions" in result
        assert result["count"] >= 1

    def test_unknown_tool(self):
        result = call_tool("nonexistent_tool", {})
        assert "error" in result
