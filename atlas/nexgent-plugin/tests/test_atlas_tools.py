"""Tests for atlas Nexgent plugin."""
import json
import pytest
import os
from pathlib import Path

# Adjust path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from atlas_tools import get_tools, get_permissions, call_tool


class TestToolRegistration:
    def test_get_tools_returns_list(self):
        tools = get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 4

    def test_tool_names(self):
        tools = get_tools()
        names = set()
        for t in tools:
            if hasattr(t, "name"):
                names.add(t.name)
            elif isinstance(t, dict):
                names.add(t["name"])
        expected = {"atlas_explore", "atlas_map", "atlas_query", "atlas_diff"}
        assert names == expected

    def test_get_permissions(self):
        perms = get_permissions()
        assert isinstance(perms, dict)
        assert len(perms) == 4


class TestExplore:
    def test_explore_current_dir(self):
        result = call_tool("atlas_explore", {"path": ".", "depth": "quick"})
        assert "path" in result
        assert "dimensions" in result
        assert "architecture" in result["dimensions"]

    def test_explore_nonexistent(self):
        result = call_tool("atlas_explore", {"path": "/nonexistent/path"})
        assert "error" in result

    def test_explore_specific_dimensions(self):
        result = call_tool("atlas_explore", {
            "path": ".",
            "depth": "quick",
            "dimensions": ["architecture", "dependencies"],
        })
        assert "architecture" in result["dimensions"]
        assert "dependencies" in result["dimensions"]
        assert "data_flow" not in result["dimensions"]

    def test_explore_architecture(self):
        result = call_tool("atlas_explore", {"path": ".", "depth": "quick"})
        arch = result["dimensions"]["architecture"]
        assert "languages" in arch
        assert "modules" in arch
        assert "total_files" in arch


class TestMap:
    def test_map_creates_atlas_dir(self, tmp_path):
        # Create a simple project
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "utils.py").write_text("def helper(): pass")

        result = call_tool("atlas_map", {"path": str(tmp_path)})
        assert result["status"] == "success"

        atlas_dir = tmp_path / ".atlas"
        assert atlas_dir.exists()
        assert (atlas_dir / "SUMMARY.md").exists()
        assert (atlas_dir / "index.md").exists()
        assert (atlas_dir / "docs" / "architecture.md").exists()
        assert (atlas_dir / "docs" / "dependencies.md").exists()

    def test_map_generates_docs(self, tmp_path):
        # Create a Node.js project
        (tmp_path / "package.json").write_text(json.dumps({
            "name": "test-project",
            "dependencies": {"express": "^4.0.0"},
        }))
        (tmp_path / "index.js").write_text("const express = require('express');")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "api.js").write_text("module.exports = {};")

        result = call_tool("atlas_map", {"path": str(tmp_path)})
        assert result["status"] == "success"
        assert "architecture.md" in result["docs_generated"]

    def test_map_nonexistent(self):
        result = call_tool("atlas_map", {"path": "/nonexistent/path"})
        assert "error" in result


class TestQuery:
    def test_query_without_atlas(self, tmp_path):
        result = call_tool("atlas_query", {
            "path": str(tmp_path),
            "question": "What is this project?",
        })
        assert "error" in result

    def test_query_with_atlas(self, tmp_path):
        # Create project and generate atlas
        (tmp_path / "main.py").write_text("def authenticate(): pass")
        (tmp_path / "auth.py").write_text("class Auth: pass")

        call_tool("atlas_map", {"path": str(tmp_path)})

        result = call_tool("atlas_query", {
            "path": str(tmp_path),
            "question": "authentication",
        })
        assert "question" in result
        assert "results" in result

    def test_query_requires_question(self, tmp_path):
        result = call_tool("atlas_query", {"path": str(tmp_path)})
        assert "error" in result


class TestDiff:
    def test_diff_two_projects(self, tmp_path):
        # Create two projects
        proj1 = tmp_path / "proj1"
        proj1.mkdir()
        (proj1 / "main.py").write_text("print('v1')")
        (proj1 / "package.json").write_text(json.dumps({"name": "proj1", "dependencies": {"lodash": "^4.0.0"}}))

        proj2 = tmp_path / "proj2"
        proj2.mkdir()
        (proj2 / "main.py").write_text("print('v2')")
        (proj2 / "index.js").write_text("console.log('v2')")
        (proj2 / "package.json").write_text(json.dumps({"name": "proj2", "dependencies": {"express": "^4.0.0"}}))

        result = call_tool("atlas_diff", {
            "path1": str(proj1),
            "path2": str(proj2),
        })
        assert "languages" in result
        assert "dependencies" in result
        assert "file_count" in result

    def test_diff_nonexistent(self):
        result = call_tool("atlas_diff", {
            "path1": "/nonexistent1",
            "path2": "/nonexistent2",
        })
        assert "error" in result


class TestHelpers:
    def test_count_files_by_lang(self):
        from atlas_tools import _count_files_by_lang
        result = _count_files_by_lang(Path("."))
        assert isinstance(result, dict)

    def test_detect_project_type(self):
        from atlas_tools import _detect_project_type
        result = _detect_project_type(Path("."))
        assert isinstance(result, list)

    def test_find_entry_points(self):
        from atlas_tools import _find_entry_points
        result = _find_entry_points(Path("."))
        assert isinstance(result, dict)

    def test_analyze_dependencies(self):
        from atlas_tools import _analyze_dependencies
        result = _analyze_dependencies(Path("."))
        assert "external" in result
        assert "dev" in result

    def test_detect_patterns(self):
        from atlas_tools import _detect_patterns
        result = _detect_patterns(Path("."))
        assert "naming" in result
        assert "testing" in result
