"""Tests for migrator Nexgent plugin."""
import json
import pytest
import shutil
from pathlib import Path

# Adjust path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from migrator_tools import get_tools, get_permissions, call_tool


@pytest.fixture(autouse=True)
def cleanup_migrations():
    """Clean up .migrations directory after each test."""
    yield
    migrations_dir = Path(".migrations").resolve()
    if migrations_dir.exists():
        shutil.rmtree(migrations_dir)


@pytest.fixture
def sample_project(tmp_path):
    """Create a sample project for testing."""
    # Create a React-like project
    pkg = {
        "name": "test-app",
        "dependencies": {
            "react": "^17.0.2",
            "react-dom": "^17.0.2",
        },
    }
    (tmp_path / "package.json").write_text(json.dumps(pkg))

    # Create source files with deprecated APIs
    src = tmp_path / "src"
    src.mkdir()

    (src / "index.js").write_text("""
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

ReactDOM.render(<App />, document.getElementById('root'));
""")

    (src / "App.js").write_text("""
import React, { useEffect } from 'react';

function App() {
  useEffect(() => {
    // Some effect
  }, []);

  return <div>Hello</div>;
}

export default App;
""")

    return tmp_path


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
        expected = {
            "migrator_analyze", "migrator_plan", "migrator_execute",
            "migrator_verify", "migrator_status", "migrator_rollback",
        }
        assert names == expected

    def test_get_permissions(self):
        perms = get_permissions()
        assert isinstance(perms, dict)
        assert len(perms) == 6


class TestAnalyze:
    def test_analyze_react_migration(self, sample_project):
        result = call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })
        assert "source" in result
        assert result["source"] == "react"
        assert result["migration"] == "17→18"
        assert "affected_files_count" in result
        assert "breaking_changes" in result
        assert "effort" in result
        assert "risk" in result

    def test_analyze_nonexistent_path(self):
        result = call_tool("migrator_analyze", {
            "path": "/nonexistent",
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })
        assert "error" in result

    def test_analyze_with_custom_terms(self, sample_project):
        result = call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
            "custom_terms": ["ReactDOM.render"],
        })
        assert result["total_matches"] > 0

    def test_analyze_express_migration(self, tmp_path):
        # Create Express project
        (tmp_path / "package.json").write_text(json.dumps({
            "dependencies": {"express": "^4.18.0"},
        }))
        (tmp_path / "server.js").write_text("""
const express = require('express');
const app = express();

app.del('/resource', (req, res) => {
  res.json({ deleted: true }, 200);
});
""")

        result = call_tool("migrator_analyze", {
            "path": str(tmp_path),
            "source": "express",
            "source_version": "4",
            "target_version": "5",
        })
        assert result["source"] == "express"
        assert result["migration"] == "4→5"


class TestPlan:
    def test_plan_generates_steps(self, sample_project):
        # First analyze
        call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })

        # Then plan
        result = call_tool("migrator_plan", {
            "path": str(sample_project),
        })
        assert "migration_id" in result
        assert "total_steps" in result
        assert result["total_steps"] > 0
        assert "steps" in result

    def test_plan_big_bang(self, sample_project):
        call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })

        result = call_tool("migrator_plan", {
            "path": str(sample_project),
            "strategy": "big-bang",
        })
        assert result["total_steps"] == 1

    def test_plan_without_analysis(self, sample_project):
        result = call_tool("migrator_plan", {
            "path": str(sample_project),
        })
        assert "error" in result

    def test_plan_with_custom_steps(self, sample_project):
        call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })

        result = call_tool("migrator_plan", {
            "path": str(sample_project),
            "custom_steps": [
                {"name": "Custom step", "description": "Do something custom"},
            ],
        })
        # Should have generated steps + 1 custom
        assert result["total_steps"] >= 2


class TestExecute:
    def test_execute_step(self, sample_project):
        call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })
        call_tool("migrator_plan", {"path": str(sample_project)})

        result = call_tool("migrator_execute", {
            "path": str(sample_project),
            "step_id": 1,
        })
        assert result["step_id"] == 1
        assert result["status"] == "executed"
        assert "progress" in result

    def test_execute_next_step(self, sample_project):
        call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })
        call_tool("migrator_plan", {"path": str(sample_project)})

        # Execute first step
        call_tool("migrator_execute", {"path": str(sample_project), "step_id": 1})
        # Execute next step
        result = call_tool("migrator_execute", {"path": str(sample_project)})
        assert result["step_id"] == 2

    def test_execute_without_plan(self, sample_project):
        result = call_tool("migrator_execute", {"path": str(sample_project)})
        assert "error" in result


class TestVerify:
    def test_verify_pass(self, sample_project):
        call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })
        call_tool("migrator_plan", {"path": str(sample_project)})
        call_tool("migrator_execute", {"path": str(sample_project), "step_id": 1})

        result = call_tool("migrator_verify", {
            "path": str(sample_project),
            "step_id": 1,
            "result": "pass",
        })
        assert result["result"] == "pass"

    def test_verify_fail(self, sample_project):
        call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })
        call_tool("migrator_plan", {"path": str(sample_project)})
        call_tool("migrator_execute", {"path": str(sample_project), "step_id": 1})

        result = call_tool("migrator_verify", {
            "path": str(sample_project),
            "step_id": 1,
            "result": "fail",
        })
        assert result["result"] == "fail"
        assert result["status"] == "failed"


class TestStatus:
    def test_status_after_plan(self, sample_project):
        call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })
        call_tool("migrator_plan", {"path": str(sample_project)})

        result = call_tool("migrator_status", {"path": str(sample_project)})
        assert "migration_id" in result
        assert "status" in result
        assert "progress" in result

    def test_status_detailed(self, sample_project):
        call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })
        call_tool("migrator_plan", {"path": str(sample_project)})

        result = call_tool("migrator_status", {
            "path": str(sample_project),
            "detailed": True,
        })
        assert "steps" in result

    def test_status_no_migration(self):
        result = call_tool("migrator_status", {})
        assert "error" in result


class TestRollback:
    def test_rollback_step(self, sample_project):
        call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })
        call_tool("migrator_plan", {"path": str(sample_project)})
        call_tool("migrator_execute", {"path": str(sample_project), "step_id": 1})

        result = call_tool("migrator_rollback", {
            "path": str(sample_project),
            "step_id": 1,
        })
        assert result["status"] == "rolled_back"
        assert 1 in result["rolled_back_steps"]
        assert result["remaining_completed"] == 0

    def test_rollback_all(self, sample_project):
        call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })
        call_tool("migrator_plan", {"path": str(sample_project)})
        call_tool("migrator_execute", {"path": str(sample_project), "step_id": 1})
        call_tool("migrator_execute", {"path": str(sample_project), "step_id": 2})

        result = call_tool("migrator_rollback", {
            "path": str(sample_project),
            "action": "all",
        })
        assert result["status"] == "rolled_back"
        assert result["remaining_completed"] == 0


class TestFullWorkflow:
    def test_complete_migration_workflow(self, sample_project):
        """Test the complete analyze → plan → execute → verify → status workflow."""
        # Analyze
        analysis = call_tool("migrator_analyze", {
            "path": str(sample_project),
            "source": "react",
            "source_version": "17",
            "target_version": "18",
        })
        assert analysis["source"] == "react"

        # Plan
        plan = call_tool("migrator_plan", {"path": str(sample_project)})
        assert plan["total_steps"] > 0

        # Execute first step
        exec1 = call_tool("migrator_execute", {
            "path": str(sample_project),
            "step_id": 1,
        })
        assert exec1["status"] == "executed"

        # Verify first step
        verify1 = call_tool("migrator_verify", {
            "path": str(sample_project),
            "step_id": 1,
            "result": "pass",
        })
        assert verify1["result"] == "pass"

        # Check status
        status = call_tool("migrator_status", {
            "path": str(sample_project),
            "detailed": True,
        })
        assert status["completed_steps"] >= 1
        assert status["status"] == "in_progress"

        # Execute remaining steps
        for step in plan["steps"][1:]:
            call_tool("migrator_execute", {
                "path": str(sample_project),
                "step_id": step["id"],
            })
            call_tool("migrator_verify", {
                "path": str(sample_project),
                "step_id": step["id"],
                "result": "pass",
            })

        # Final status
        final_status = call_tool("migrator_status", {"path": str(sample_project)})
        assert final_status["completed_steps"] == plan["total_steps"]
