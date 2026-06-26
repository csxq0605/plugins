"""Tests for dep-audit Nexgent plugin."""
import pytest
from audit_tools import get_tools, get_permissions, call_tool


class TestToolRegistration:
    def test_get_tools_returns_list(self):
        tools = get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 4

    def test_tool_names(self):
        tools = get_tools()
        names = {t["name"] for t in tools}
        expected = {"audit_scan_deps", "audit_check_vulns", "audit_full", "audit_generate_report"}
        assert names == expected

    def test_get_permissions(self):
        perms = get_permissions()
        assert isinstance(perms, dict)
        assert len(perms) == 4


class TestScanDeps:
    def test_scan_empty_project(self, tmp_path):
        result = call_tool("audit_scan_deps", {"path": str(tmp_path)})
        assert result["total"] == 0

    def test_scan_with_package_json(self, tmp_path):
        pkg = tmp_path / "package.json"
        pkg.write_text('{"dependencies": {"lodash": "4.17.20"}, "devDependencies": {"jest": "29.0.0"}}')
        result = call_tool("audit_scan_deps", {"path": str(tmp_path)})
        assert result["total"] == 2
        assert "npm" in result["by_ecosystem"]

    def test_scan_with_requirements(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("requests==2.25.0\nflask>=2.0\n")
        result = call_tool("audit_scan_deps", {"path": str(tmp_path)})
        assert result["total"] == 2
        assert "PyPI" in result["by_ecosystem"]


class TestHealthScore:
    def test_no_vulnerabilities(self):
        from audit_tools import _calculate_health_score
        health = _calculate_health_score([])
        assert health["score"] == 100
        assert health["grade"] == "Excellent"

    def test_critical_vulnerability(self):
        from audit_tools import _calculate_health_score
        health = _calculate_health_score([{"severity": "CRITICAL"}])
        assert health["score"] == 75
        assert health["grade"] == "Good"

    def test_unknown_tool(self):
        result = call_tool("nonexistent_tool", {})
        assert "error" in result
