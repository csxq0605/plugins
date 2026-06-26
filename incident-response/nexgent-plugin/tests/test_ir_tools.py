"""Tests for incident-response Nexgent plugin."""
import json
import pytest
import os
import shutil
from pathlib import Path

# Adjust path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ir_tools import get_tools, get_permissions, call_tool


@pytest.fixture(autouse=True)
def cleanup_incidents():
    """Clean up .incidents directory after each test."""
    yield
    incidents_dir = Path(".incidents").resolve()
    if incidents_dir.exists():
        shutil.rmtree(incidents_dir)


class TestToolRegistration:
    def test_get_tools_returns_list(self):
        tools = get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 9

    def test_tool_names(self):
        tools = get_tools()
        names = set()
        for t in tools:
            if hasattr(t, "name"):
                names.add(t.name)
            elif isinstance(t, dict):
                names.add(t["name"])
        expected = {
            "ir_start", "ir_triage", "ir_timeline", "ir_diagnose",
            "ir_fix", "ir_verify", "ir_close", "ir_postmortem", "ir_list",
        }
        assert names == expected

    def test_get_permissions(self):
        perms = get_permissions()
        assert isinstance(perms, dict)
        assert len(perms) == 9


class TestStart:
    def test_start_creates_incident(self):
        result = call_tool("ir_start", {"title": "Test incident"})
        assert "incident_id" in result
        assert result["incident_id"].startswith("INC-")
        assert result["status"] == "open"
        assert result["severity"] == "P2"  # default

    def test_start_with_severity(self):
        result = call_tool("ir_start", {
            "title": "Critical outage",
            "severity": "P0",
            "affected_services": ["api", "db"],
        })
        assert result["severity"] == "P0"

    def test_start_increments_id(self):
        r1 = call_tool("ir_start", {"title": "First"})
        r2 = call_tool("ir_start", {"title": "Second"})
        assert r1["incident_id"] != r2["incident_id"]
        # IDs should be sequential
        id1 = int(r1["incident_id"].split("-")[1])
        id2 = int(r2["incident_id"].split("-")[1])
        assert id2 == id1 + 1


class TestTriage:
    def test_triage_updates_severity(self):
        start = call_tool("ir_start", {"title": "Test"})
        result = call_tool("ir_triage", {
            "incident_id": start["incident_id"],
            "severity": "P1",
            "affected_services": ["web"],
        })
        assert result["severity"] == "P1"
        assert result["status"] == "investigating"

    def test_triage_latest_incident(self):
        call_tool("ir_start", {"title": "Old incident"})
        call_tool("ir_start", {"title": "New incident"})
        result = call_tool("ir_triage", {"severity": "P0"})
        assert result["severity"] == "P0"

    def test_triage_nonexistent(self):
        result = call_tool("ir_triage", {"incident_id": "INC-999"})
        assert "error" in result


class TestTimeline:
    def test_timeline_adds_event(self):
        start = call_tool("ir_start", {"title": "Test"})
        result = call_tool("ir_timeline", {
            "incident_id": start["incident_id"],
            "event": "Investigating database",
        })
        assert result["timeline_length"] == 2  # initial + new

    def test_timeline_multiple_events(self):
        start = call_tool("ir_start", {"title": "Test"})
        call_tool("ir_timeline", {"incident_id": start["incident_id"], "event": "Event 1"})
        call_tool("ir_timeline", {"incident_id": start["incident_id"], "event": "Event 2"})
        result = call_tool("ir_timeline", {
            "incident_id": start["incident_id"],
            "event": "Event 3",
        })
        assert result["timeline_length"] == 4  # initial + 3

    def test_timeline_no_open_incident(self):
        result = call_tool("ir_timeline", {"event": "Test"})
        assert "error" in result


class TestDiagnose:
    def test_diagnose_records_root_cause(self):
        start = call_tool("ir_start", {"title": "Test"})
        result = call_tool("ir_diagnose", {
            "incident_id": start["incident_id"],
            "root_cause": "Connection pool exhaustion",
            "contributing_factors": ["High traffic", "No connection limits"],
        })
        assert result["root_cause"] == "Connection pool exhaustion"
        assert len(result["contributing_factors"]) == 2
        assert result["status"] == "fixing"

    def test_diagnose_creates_file(self):
        start = call_tool("ir_start", {"title": "Test"})
        call_tool("ir_diagnose", {
            "incident_id": start["incident_id"],
            "root_cause": "Test cause",
        })
        diag_file = Path(".incidents").resolve() / start["incident_id"] / "diagnosis.md"
        assert diag_file.exists()
        content = diag_file.read_text(encoding="utf-8")
        assert "Test cause" in content


class TestFix:
    def test_fix_records_action(self):
        start = call_tool("ir_start", {"title": "Test"})
        result = call_tool("ir_fix", {
            "incident_id": start["incident_id"],
            "action": "Increased pool size to 100",
            "rollback": "Revert to 10",
        })
        assert result["fixes_count"] == 1

    def test_fix_multiple_actions(self):
        start = call_tool("ir_start", {"title": "Test"})
        call_tool("ir_fix", {"incident_id": start["incident_id"], "action": "Fix 1"})
        result = call_tool("ir_fix", {
            "incident_id": start["incident_id"],
            "action": "Fix 2",
        })
        assert result["fixes_count"] == 2


class TestVerify:
    def test_verify_records_check(self):
        start = call_tool("ir_start", {"title": "Test"})
        result = call_tool("ir_verify", {
            "incident_id": start["incident_id"],
            "check": "Error rate back to normal",
            "result": "pass",
        })
        assert result["verification_count"] == 1
        assert result["result"] == "pass"

    def test_verify_updates_status(self):
        start = call_tool("ir_start", {"title": "Test"})
        call_tool("ir_verify", {
            "incident_id": start["incident_id"],
            "check": "Health checks passing",
        })
        # Check incident status
        index_file = Path(".incidents").resolve() / "index.json"
        index = json.loads(index_file.read_text(encoding="utf-8"))
        inc = [i for i in index["incidents"] if i["id"] == start["incident_id"]][0]
        assert inc["status"] == "verifying"


class TestClose:
    def test_close_incident(self):
        start = call_tool("ir_start", {"title": "Test"})
        result = call_tool("ir_close", {
            "incident_id": start["incident_id"],
            "resolution": "Fixed by increasing pool size",
        })
        assert result["status"] == "closed"
        assert "duration_hours" in result

    def test_close_updates_index(self):
        start = call_tool("ir_start", {"title": "Test"})
        call_tool("ir_close", {"incident_id": start["incident_id"]})
        index_file = Path(".incidents").resolve() / "index.json"
        index = json.loads(index_file.read_text(encoding="utf-8"))
        inc = [i for i in index["incidents"] if i["id"] == start["incident_id"]][0]
        assert inc["status"] == "closed"


class TestPostmortem:
    def test_postmortem_generates_report(self):
        start = call_tool("ir_start", {"title": "API outage"})
        call_tool("ir_diagnose", {
            "incident_id": start["incident_id"],
            "root_cause": "DB connection leak",
        })
        call_tool("ir_fix", {
            "incident_id": start["incident_id"],
            "action": "Fixed connection handling",
        })
        call_tool("ir_close", {
            "incident_id": start["incident_id"],
            "resolution": "Deployed hotfix",
        })
        result = call_tool("ir_postmortem", {
            "incident_id": start["incident_id"],
            "action_items": [{"action": "Add connection monitoring", "owner": "SRE"}],
            "lessons": ["Need better connection pool monitoring"],
        })
        assert result["incident_id"] == start["incident_id"]
        assert result["timeline_events"] > 0

        # Check file exists
        pm_file = Path(".incidents").resolve() / start["incident_id"] / "postmortem.md"
        assert pm_file.exists()
        content = pm_file.read_text(encoding="utf-8")
        assert "API outage" in content
        assert "DB connection leak" in content

    def test_postmortem_latest_closed(self):
        start = call_tool("ir_start", {"title": "Test"})
        call_tool("ir_close", {"incident_id": start["incident_id"]})
        result = call_tool("ir_postmortem", {})
        assert result["incident_id"] == start["incident_id"]


class TestList:
    def test_list_all(self):
        call_tool("ir_start", {"title": "Incident 1"})
        call_tool("ir_start", {"title": "Incident 2"})
        result = call_tool("ir_list", {})
        assert result["total"] == 2

    def test_list_filter_status(self):
        r1 = call_tool("ir_start", {"title": "Open"})
        call_tool("ir_start", {"title": "To close"})
        call_tool("ir_close", {"incident_id": r1["incident_id"]})

        result = call_tool("ir_list", {"status": "open"})
        assert result["total"] == 1

    def test_list_filter_severity(self):
        call_tool("ir_start", {"title": "P0", "severity": "P0"})
        call_tool("ir_start", {"title": "P2"})
        result = call_tool("ir_list", {"severity": "P0"})
        assert result["total"] == 1

    def test_list_empty(self):
        result = call_tool("ir_list", {})
        assert result["total"] == 0


class TestFullWorkflow:
    def test_complete_incident_workflow(self):
        """Test the complete triage → diagnose → fix → verify → close → postmortem workflow."""
        # Start
        start = call_tool("ir_start", {
            "title": "Payment service returning 503",
            "severity": "P1",
            "affected_services": ["payment", "checkout"],
        })
        inc_id = start["incident_id"]

        # Triage
        triage = call_tool("ir_triage", {
            "incident_id": inc_id,
            "severity": "P0",
            "notes": "All payment processing stopped",
        })
        assert triage["severity"] == "P0"

        # Timeline events
        call_tool("ir_timeline", {"incident_id": inc_id, "event": "Investigating database"})
        call_tool("ir_timeline", {"incident_id": inc_id, "event": "Found connection pool exhaustion"})

        # Diagnose
        diag = call_tool("ir_diagnose", {
            "incident_id": inc_id,
            "root_cause": "Database connection pool exhaustion due to connection leak in payment service",
            "contributing_factors": [
                "Connection not properly closed in error path",
                "No connection pool monitoring",
            ],
        })
        assert diag["root_cause"] is not None

        # Fix
        fix = call_tool("ir_fix", {
            "incident_id": inc_id,
            "action": "Increased pool size and fixed connection leak",
            "rollback": "Revert to previous version",
        })
        assert fix["fixes_count"] == 1

        # Verify
        verify = call_tool("ir_verify", {
            "incident_id": inc_id,
            "check": "Payment success rate back to 99.9%",
            "result": "pass",
        })
        assert verify["result"] == "pass"

        # Close
        close = call_tool("ir_close", {
            "incident_id": inc_id,
            "resolution": "Deployed hotfix v2.3.2 with connection leak fix",
        })
        assert close["status"] == "closed"

        # Postmortem
        pm = call_tool("ir_postmortem", {
            "incident_id": inc_id,
            "action_items": [
                {"action": "Add connection pool monitoring", "owner": "SRE", "due_date": "2026-07-15"},
                {"action": "Add connection leak detection", "owner": "Backend", "due_date": "2026-07-30"},
            ],
            "lessons": [
                "Connection pool monitoring is critical",
                "Error paths must properly close resources",
            ],
        })
        assert pm["timeline_events"] >= 5
        assert pm["action_items_count"] == 2

        # Verify postmortem content
        pm_file = Path(".incidents").resolve() / inc_id / "postmortem.md"
        content = pm_file.read_text(encoding="utf-8")
        assert "Payment service returning 503" in content
        assert "connection pool" in content.lower()
