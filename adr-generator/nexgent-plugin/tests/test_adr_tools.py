"""Tests for adr-generator Nexgent plugin."""
import pytest
from adr_tools import get_tools, get_permissions, call_tool


class TestToolRegistration:
    def test_get_tools_returns_list(self):
        tools = get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 6

    def test_tool_names(self):
        tools = get_tools()
        names = {t["name"] for t in tools}
        expected = {"adr_create", "adr_list", "adr_show", "adr_update_status", "adr_index", "adr_search"}
        assert names == expected

    def test_get_permissions(self):
        perms = get_permissions()
        assert isinstance(perms, dict)
        assert len(perms) == 6


class TestADROperations:
    def test_create_madr(self, tmp_path):
        result = call_tool("adr_create", {
            "path": str(tmp_path),
            "title": "Use PostgreSQL",
            "template": "madr",
            "context": "Need ACID compliance",
            "decision": "Use PostgreSQL 15",
        })
        assert result["number"] == 1
        assert result["template"] == "madr"

    def test_create_y_statement(self, tmp_path):
        result = call_tool("adr_create", {
            "path": str(tmp_path),
            "title": "Use JWT",
            "template": "y-statement",
            "context": "microservices",
            "problem": "authentication",
            "decision": "use JWT tokens",
        })
        assert result["number"] == 1
        assert result["template"] == "y-statement"

    def test_list_adrs(self, tmp_path):
        call_tool("adr_create", {"path": str(tmp_path), "title": "ADR 1"})
        call_tool("adr_create", {"path": str(tmp_path), "title": "ADR 2"})
        result = call_tool("adr_list", {"path": str(tmp_path)})
        assert len(result) == 2

    def test_show_adr(self, tmp_path):
        call_tool("adr_create", {"path": str(tmp_path), "title": "Test ADR"})
        result = call_tool("adr_show", {"path": str(tmp_path), "number": 1})
        assert "content" in result
        assert result["title"] == "Test ADR"

    def test_update_status(self, tmp_path):
        call_tool("adr_create", {"path": str(tmp_path), "title": "Test"})
        result = call_tool("adr_update_status", {"path": str(tmp_path), "number": 1, "status": "accepted"})
        assert result["status"] == "accepted"

    def test_generate_index(self, tmp_path):
        call_tool("adr_create", {"path": str(tmp_path), "title": "Test"})
        result = call_tool("adr_index", {"path": str(tmp_path)})
        assert "Architecture Decision Records" in result

    def test_search_adrs(self, tmp_path):
        call_tool("adr_create", {"path": str(tmp_path), "title": "Use PostgreSQL Database"})
        call_tool("adr_create", {"path": str(tmp_path), "title": "Use JWT Auth"})
        result = call_tool("adr_search", {"path": str(tmp_path), "query": "database"})
        assert len(result) == 1

    def test_unknown_tool(self):
        result = call_tool("nonexistent_tool", {})
        assert "error" in result
