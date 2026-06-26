"""Tests for project-onboarding Nexgent plugin."""
import pytest
from onboarding_tools import get_tools, get_permissions, call_tool


class TestToolRegistration:
    def test_get_tools_returns_list(self):
        tools = get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 7

    def test_tool_names(self):
        tools = get_tools()
        names = {t["name"] for t in tools}
        expected = {
            "onboarding_scan", "onboarding_detect_languages",
            "onboarding_detect_frameworks", "onboarding_detect_ci",
            "onboarding_detect_code_style", "onboarding_get_tree",
            "onboarding_generate",
        }
        assert names == expected

    def test_get_permissions(self):
        perms = get_permissions()
        assert isinstance(perms, dict)
        assert len(perms) == 7


class TestScan:
    def test_scan_current_dir(self):
        result = call_tool("onboarding_scan", {"path": ".", "depth": 1})
        assert "name" in result
        assert "languages" in result

    def test_detect_languages(self):
        result = call_tool("onboarding_detect_languages", {"path": "."})
        assert "languages" in result

    def test_detect_frameworks(self):
        result = call_tool("onboarding_detect_frameworks", {"path": "."})
        assert "frameworks" in result

    def test_detect_ci(self):
        result = call_tool("onboarding_detect_ci", {"path": "."})
        assert "ci" in result

    def test_detect_code_style(self):
        result = call_tool("onboarding_detect_code_style", {"path": "."})
        assert "code_style" in result

    def test_get_tree(self):
        result = call_tool("onboarding_get_tree", {"path": ".", "depth": 2})
        assert "tree" in result
        assert isinstance(result["tree"], str)

    def test_generate(self):
        result = call_tool("onboarding_generate", {"path": ".", "depth": 1})
        assert isinstance(result, str)
        assert "# Project Onboarding" in result

    def test_unknown_tool(self):
        result = call_tool("nonexistent_tool", {})
        assert "error" in result
