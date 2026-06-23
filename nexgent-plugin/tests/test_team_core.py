"""Tests for team_core.py — data structures and shared task list."""

import os
import json
import tempfile
import shutil
import pytest

from team_core import (
    TeamConfig, TeamMember, TeamState, MemberState,
    SharedTaskList, TeamTask, TaskStatus, create_team_id,
)


@pytest.fixture
def temp_teams_dir():
    """Create a temporary teams directory."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def team_config(temp_teams_dir, monkeypatch):
    """Create a test team config with temp directory."""
    monkeypatch.setattr("team_core.TEAMS_DIR", temp_teams_dir)
    team = TeamConfig(
        team_id="test-team-001",
        team_name="Test Team",
        lead_session_id="lead-session",
    )
    team.members["lead"] = TeamMember(
        name="lead",
        agent_id="lead-001",
        session_id="lead-session",
        role="lead",
        state=MemberState.IDLE,
    )
    # Persist to disk so SharedTaskList can find it
    team.save()
    return team


# ---------------------------------------------------------------------------
# TeamConfig tests
# ---------------------------------------------------------------------------

class TestTeamConfig:
    def test_create_team_id(self):
        tid = create_team_id()
        assert tid.startswith("team-")
        assert len(tid) == 13  # "team-" + 8 hex chars

    def test_to_dict_roundtrip(self, team_config):
        d = team_config.to_dict()
        assert d["team_id"] == "test-team-001"
        assert d["team_name"] == "Test Team"
        assert d["state"] == "active"
        assert "lead" in d["members"]

        restored = TeamConfig.from_dict(d)
        assert restored.team_id == team_config.team_id
        assert restored.team_name == team_config.team_name
        assert "lead" in restored.members

    def test_member_to_dict_roundtrip(self):
        member = TeamMember(
            name="worker-1",
            agent_id="a-001",
            session_id="s-001",
            role="teammate",
            state=MemberState.WORKING,
        )
        d = member.to_dict()
        assert d["name"] == "worker-1"
        assert d["state"] == "working"

        restored = TeamMember.from_dict(d)
        assert restored.name == "worker-1"
        assert restored.state == MemberState.WORKING

    def test_save_and_load(self, team_config, temp_teams_dir, monkeypatch):
        monkeypatch.setattr("team_core.TEAMS_DIR", temp_teams_dir)
        team_config.save()

        loaded = TeamConfig.load("test-team-001")
        assert loaded is not None
        assert loaded.team_id == "test-team-001"
        assert "lead" in loaded.members


# ---------------------------------------------------------------------------
# SharedTaskList tests
# ---------------------------------------------------------------------------

class TestSharedTaskList:
    def test_add_and_list(self, team_config):
        tl = SharedTaskList(team_config)
        t1 = tl.add_task("Task A", created_by="lead")
        t2 = tl.add_task("Task B", created_by="lead")

        assert t1.task_id != t2.task_id
        tasks = tl.list_tasks()
        assert len(tasks) == 2

    def test_claim_task(self, team_config):
        tl = SharedTaskList(team_config)
        tl.add_task("Task A", created_by="lead")

        claimed = tl.claim_task("worker-1")
        assert claimed is not None
        assert claimed.assigned_to == "worker-1"
        assert claimed.status == TaskStatus.IN_PROGRESS

        # No more tasks to claim
        assert tl.claim_task("worker-2") is None

    def test_complete_task(self, team_config):
        tl = SharedTaskList(team_config)
        task = tl.add_task("Task A", created_by="lead")
        tl.claim_task("worker-1")

        assert tl.complete_task(task.task_id, result="Done")
        assert tl.all_completed()

    def test_dependency_resolution(self, team_config):
        tl = SharedTaskList(team_config)
        t1 = tl.add_task("Task A", created_by="lead")
        t2 = tl.add_task("Task B", created_by="lead", depends_on=[t1.task_id])

        # t2 depends on t1, so only t1 is claimable
        claimed = tl.claim_task("worker-1")
        assert claimed.task_id == t1.task_id

        # t2 still not claimable (t1 not completed)
        assert tl.claim_task("worker-2") is None

        # Complete t1, now t2 is claimable
        tl.complete_task(t1.task_id)
        claimed = tl.claim_task("worker-2")
        assert claimed.task_id == t2.task_id

    def test_persistence(self, team_config):
        tl1 = SharedTaskList(team_config)
        tl1.add_task("Task A", created_by="lead")
        tl1.add_task("Task B", created_by="lead")

        # Create a new instance — should load from disk
        tl2 = SharedTaskList(team_config)
        tasks = tl2.list_tasks()
        assert len(tasks) == 2

    def test_pending_count(self, team_config):
        tl = SharedTaskList(team_config)
        tl.add_task("Task A", created_by="lead")
        tl.add_task("Task B", created_by="lead")

        assert tl.get_pending_count() == 2

        tl.claim_task("worker-1")
        assert tl.get_pending_count() == 1
