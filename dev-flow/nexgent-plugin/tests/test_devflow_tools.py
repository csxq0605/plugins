"""Tests for dev-flow Nexgent plugin."""
import json
import pytest
from devflow_tools import get_tools, get_permissions, call_tool, _parse_commit_line, _suggest_bump, ReviewSession


class TestToolRegistration:
    def test_get_tools_returns_list(self):
        tools = get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 11

    def test_tool_names(self):
        tools = get_tools()
        names = set()
        for t in tools:
            if hasattr(t, "name"):
                names.add(t.name)
            elif isinstance(t, dict):
                names.add(t["name"])
        expected = {
            "devflow_onboard", "devflow_audit",
            "devflow_review_start", "devflow_review_add_finding", "devflow_review_score", "devflow_review_export",
            "devflow_changelog", "devflow_adr_create", "devflow_adr_list",
            "devflow_memory_save", "devflow_memory_recall",
        }
        assert names == expected

    def test_get_permissions(self):
        perms = get_permissions()
        assert isinstance(perms, dict)
        assert len(perms) == 11


class TestOnboard:
    def test_onboard_current_dir(self):
        result = call_tool("devflow_onboard", {"path": ".", "depth": 1})
        assert "name" in result
        assert "languages" in result

    def test_onboard_nonexistent(self):
        result = call_tool("devflow_onboard", {"path": "/nonexistent/path"})
        assert "error" in result


class TestAudit:
    def test_audit_empty(self, tmp_path):
        result = call_tool("devflow_audit", {"path": str(tmp_path)})
        assert result["total_deps"] == 0
        assert result["health_score"] == 100

    def test_audit_with_deps(self, tmp_path):
        pkg = tmp_path / "package.json"
        pkg.write_text('{"dependencies": {"lodash": "4.17.15"}}')
        result = call_tool("devflow_audit", {"path": str(tmp_path)})
        assert result["total_deps"] == 1


class TestReview:
    def test_review_flow(self):
        r = call_tool("devflow_review_start", {"target": "."})
        sid = r["session_id"]
        call_tool("devflow_review_add_finding", {
            "session_id": sid, "id": "SEC-001", "perspective": "security",
            "severity": "critical", "title": "SQLi", "file": "db.py", "line": 10,
            "evidence": "query = f'...'", "risk": "RCE", "fix": "Use params", "confidence": 95,
        })
        score = call_tool("devflow_review_score", {"session_id": sid})
        assert score["overall"] < 100
        report = call_tool("devflow_review_export", {"session_id": sid})
        assert "Review Report" in report


class TestChangelog:
    def test_changelog_current_repo(self):
        result = call_tool("devflow_changelog", {"path": "D:/tasks/project/plugins", "from": "HEAD~5", "version": "test"})
        assert isinstance(result, str)
        assert "test" in result


class TestADR:
    def test_adr_create_and_list(self, tmp_path):
        r = call_tool("devflow_adr_create", {"path": str(tmp_path), "title": "Use PostgreSQL", "context": "Need ACID", "decision": "PostgreSQL 15"})
        assert r["number"] == 1
        adrs = call_tool("devflow_adr_list", {"path": str(tmp_path)})
        assert len(adrs) == 1
        assert adrs[0]["title"] == "Use PostgreSQL"


class TestMemory:
    def test_save_and_recall(self, tmp_path):
        call_tool("devflow_memory_save", {"path": str(tmp_path), "type": "session", "summary": "Fixed auth bug", "tags": ["auth"]})
        call_tool("devflow_memory_save", {"path": str(tmp_path), "type": "decision", "summary": "Use JWT", "title": "JWT Auth", "tags": ["auth"]})
        results = call_tool("devflow_memory_recall", {"path": str(tmp_path), "tags": ["auth"]})
        assert len(results) == 2


class TestCommitParsing:
    def test_parse_conventional(self):
        c = _parse_commit_line("abc12345|feat(auth): add login|body|Author|2024-01-01")
        assert c["type"] == "feat"
        assert c["scope"] == "auth"
        assert c["breaking"] is False

    def test_parse_breaking(self):
        c = _parse_commit_line("abc12345|feat!: redesign|BREAKING CHANGE: yes|Author|2024-01-01")
        assert c["breaking"] is True

    def test_suggest_bump(self):
        assert _suggest_bump([{"breaking": True, "type": "feat"}]) == "major"
        assert _suggest_bump([{"breaking": False, "type": "feat"}]) == "minor"
        assert _suggest_bump([{"breaking": False, "type": "fix"}]) == "patch"
        assert _suggest_bump([]) == "none"


class TestReviewSession:
    def test_health_score(self):
        s = ReviewSession("test", ".", ["security"])
        s.add_finding({"id": "S1", "perspective": "security", "severity": "critical", "title": "t", "file": "f", "risk": "r", "fix": "x", "confidence": 90})
        score = s.get_health_score()
        assert score["overall"] == 85.0

    def test_unknown_tool(self):
        result = call_tool("nonexistent", {})
        assert "error" in result
