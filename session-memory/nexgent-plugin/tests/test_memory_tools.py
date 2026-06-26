"""Tests for session-memory Nexgent plugin."""
import pytest
from memory_tools import get_tools, get_permissions, call_tool


class TestToolRegistration:
    def test_get_tools_returns_list(self):
        tools = get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 9

    def test_tool_names(self):
        tools = get_tools()
        names = {t["name"] for t in tools}
        expected = {
            "memory_save_session", "memory_save_decision", "memory_save_finding",
            "memory_save_handoff", "memory_recall", "memory_list",
            "memory_delete", "memory_cleanup", "memory_generate_handoff",
        }
        assert names == expected

    def test_get_permissions(self):
        perms = get_permissions()
        assert isinstance(perms, dict)
        assert len(perms) == 9


class TestMemoryOperations:
    def test_save_and_recall_session(self, tmp_path):
        result = call_tool("memory_save_session", {
            "path": str(tmp_path),
            "summary": "Test session",
            "tags": ["test"],
        })
        assert "id" in result
        assert result["status"] == "saved"

        memories = call_tool("memory_recall", {"path": str(tmp_path), "tags": ["test"]})
        assert len(memories) == 1
        assert memories[0]["summary"] == "Test session"

    def test_save_decision(self, tmp_path):
        result = call_tool("memory_save_decision", {
            "path": str(tmp_path),
            "title": "Use PostgreSQL",
            "rationale": "ACID compliance",
            "tags": ["database"],
        })
        assert "id" in result

    def test_list_memories(self, tmp_path):
        call_tool("memory_save_session", {"path": str(tmp_path), "summary": "A"})
        call_tool("memory_save_session", {"path": str(tmp_path), "summary": "B"})
        result = call_tool("memory_list", {"path": str(tmp_path)})
        assert len(result) == 2

    def test_delete_memory(self, tmp_path):
        saved = call_tool("memory_save_session", {"path": str(tmp_path), "summary": "ToDelete"})
        result = call_tool("memory_delete", {"path": str(tmp_path), "id": saved["id"]})
        assert "deleted" in result

    def test_generate_handoff(self, tmp_path):
        call_tool("memory_save_session", {
            "path": str(tmp_path),
            "summary": "Fixed auth bug",
            "next_steps": ["Write tests"],
        })
        result = call_tool("memory_generate_handoff", {"path": str(tmp_path), "to_role": "frontend"})
        assert "Handoff Document" in result

    def test_cleanup(self, tmp_path):
        result = call_tool("memory_cleanup", {"path": str(tmp_path)})
        assert "removed" in result
        assert "remaining" in result

    def test_unknown_tool(self):
        result = call_tool("nonexistent_tool", {})
        assert "error" in result
