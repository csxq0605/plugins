"""Tests for lit-review Nexgent plugin."""
import json
import pytest
from lit_tools import get_tools, get_permissions, call_tool


def _parse(result):
    """Parse JSON string result to dict."""
    if isinstance(result, str):
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"_raw": result}
    return result


class TestToolRegistration:
    def test_get_tools_returns_list(self):
        tools = get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 14

    def test_tool_names(self):
        tools = get_tools()
        names = set()
        for t in tools:
            if hasattr(t, "name"):
                names.add(t.name)
            elif isinstance(t, dict):
                names.add(t["name"])
        expected = {
            "lit_set_key", "lit_get_config", "lit_create_workspace",
            "lit_add_paper", "lit_get_paper", "lit_list_papers",
            "lit_search_local", "lit_add_analysis", "lit_synthesize",
            "lit_list_workspaces", "lit_search_web", "lit_citations",
            "lit_references", "lit_recommend",
        }
        assert names == expected

    def test_get_permissions(self):
        perms = get_permissions()
        assert isinstance(perms, dict)
        assert len(perms) == 14


class TestWorkspace:
    def test_create_workspace(self):
        result = _parse(call_tool("lit_create_workspace", {"topic": "Test Topic"}))
        assert "workspace_id" in result

    def test_add_paper(self):
        ws = _parse(call_tool("lit_create_workspace", {"topic": "Test"}))
        result = _parse(call_tool("lit_add_paper", {
            "workspace_id": ws["workspace_id"],
            "title": "Test Paper",
            "authors": ["Author A"],
            "year": 2024,
            "abstract": "Test abstract",
            "url": "https://arxiv.org/abs/2401.00001",
            "source": "arxiv",
        }))
        assert "paper_id" in result

    def test_list_workspaces(self):
        call_tool("lit_create_workspace", {"topic": "Test"})
        result = _parse(call_tool("lit_list_workspaces", {}))
        assert "workspaces" in result
        assert len(result["workspaces"]) >= 1

    def test_synthesize(self):
        ws = _parse(call_tool("lit_create_workspace", {"topic": "Test"}))
        call_tool("lit_add_paper", {
            "workspace_id": ws["workspace_id"],
            "title": "Test Paper",
            "authors": ["Author A"],
            "year": 2024,
        })
        result = _parse(call_tool("lit_synthesize", {"workspace_id": ws["workspace_id"]}))
        assert "total_papers" in result

    def test_unknown_tool(self):
        result = call_tool("nonexistent_tool", {})
        assert "error" in result
