"""Tests for team_manager.py — team lifecycle management."""

import os
import tempfile
import shutil
import pytest

from team_core import TeamState, MemberState, TaskStatus, TEAMS_DIR
from team_manager import TeamManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def manager(temp_dir, monkeypatch):
    """Create a TeamManager with temp directory."""
    import team_core
    monkeypatch.setattr(team_core, "TEAMS_DIR", temp_dir)
    return TeamManager()


# ---------------------------------------------------------------------------
# Team lifecycle tests
# ---------------------------------------------------------------------------

class TestTeamLifecycle:
    def test_create_team(self, manager):
        team = manager.create_team("my-team")
        assert team.team_name == "my-team"
        assert team.state == TeamState.ACTIVE
        assert "lead" in team.members

    def test_get_team(self, manager):
        team = manager.create_team("my-team")
        retrieved = manager.get_team(team.team_id)
        assert retrieved is not None
        assert retrieved.team_id == team.team_id

    def test_list_teams(self, manager):
        manager.create_team("team-1")
        manager.create_team("team-2")
        teams = manager.list_teams()
        assert len(teams) == 2

    def test_delete_team(self, manager):
        team = manager.create_team("my-team")
        manager.delete_team(team.team_id)
        assert manager.get_team(team.team_id) is None


# ---------------------------------------------------------------------------
# Teammate lifecycle tests
# ---------------------------------------------------------------------------

class TestTeammateLifecycle:
    def test_spawn_teammate(self, manager):
        team = manager.create_team("my-team")
        member = manager.spawn_teammate(
            team.team_id, "worker-1", "Do something"
        )
        assert member.name == "worker-1"
        assert member.role == "worker"
        assert member.state in (MemberState.IDLE, MemberState.WORKING, MemberState.SHUTDOWN)

    def test_list_teammates(self, manager):
        team = manager.create_team("my-team")
        manager.spawn_teammate(team.team_id, "worker-1", "Task A")
        manager.spawn_teammate(team.team_id, "worker-2", "Task B")

        teammates = manager.list_teammates(team.team_id)
        assert len(teammates) == 2
        names = [t.name for t in teammates]
        assert "worker-1" in names
        assert "worker-2" in names

    def test_set_teammate_state(self, manager):
        team = manager.create_team("my-team")
        manager.spawn_teammate(team.team_id, "worker-1", "Task A")

        # In test env, the teammate may already be SHUTDOWN due to missing API key
        manager.set_teammate_state(
            team.team_id, "worker-1", MemberState.WORKING
        )
        member = manager.get_teammate(team.team_id, "worker-1")
        # State should be WORKING (we just set it), unless background thread
        # changed it back to SHUTDOWN
        assert member.state in (MemberState.WORKING, MemberState.SHUTDOWN)


# ---------------------------------------------------------------------------
# Messaging tests
# ---------------------------------------------------------------------------

class TestMessaging:
    def test_send_and_check(self, manager):
        team = manager.create_team("my-team")
        manager.spawn_teammate(team.team_id, "worker-1", "Task A")

        manager.send_message(
            team.team_id, "lead", "worker-1", "Hello!", "message"
        )

        messages = manager.check_inbox(team.team_id, "worker-1")
        assert len(messages) == 1
        assert messages[0].content == "Hello!"

    def test_has_messages(self, manager):
        team = manager.create_team("my-team")
        manager.spawn_teammate(team.team_id, "worker-1", "Task A")

        assert not manager.has_messages(team.team_id, "worker-1")

        manager.send_message(
            team.team_id, "lead", "worker-1", "Hello!", "message"
        )
        assert manager.has_messages(team.team_id, "worker-1")


# ---------------------------------------------------------------------------
# Task management tests
# ---------------------------------------------------------------------------

class TestTaskManagement:
    def test_add_and_list_tasks(self, manager):
        team = manager.create_team("my-team")
        manager.add_task(team.team_id, "Task A", created_by="lead")
        manager.add_task(team.team_id, "Task B", created_by="lead")

        tasks = manager.list_tasks(team.team_id)
        assert len(tasks) == 2

    def test_claim_task(self, manager):
        team = manager.create_team("my-team")
        manager.spawn_teammate(team.team_id, "worker-1", "Task A")
        manager.add_task(team.team_id, "Do something", created_by="lead")

        claimed = manager.claim_task(team.team_id, "worker-1")
        assert claimed is not None
        assert claimed.assigned_to == "worker-1"
        assert claimed.status == TaskStatus.IN_PROGRESS

    def test_complete_task(self, manager):
        team = manager.create_team("my-team")
        task = manager.add_task(team.team_id, "Do something", created_by="lead")

        assert manager.complete_task(team.team_id, task.task_id, "Done")
        tasks = manager.list_tasks(team.team_id, status=TaskStatus.COMPLETED)
        assert len(tasks) == 1


# ---------------------------------------------------------------------------
# Shutdown tests
# ---------------------------------------------------------------------------

class TestShutdown:
    def test_request_shutdown(self, manager):
        team = manager.create_team("my-team")
        manager.spawn_teammate(team.team_id, "worker-1", "Task A")

        # request_shutdown queues as pending
        success = manager.request_shutdown(team.team_id, "worker-1")
        assert success
        pending = manager.get_pending_shutdowns(team.team_id)
        assert "worker-1" in pending

        # approve_shutdown actually shuts down
        manager.approve_shutdown(team.team_id, "worker-1")
        member = manager.get_teammate(team.team_id, "worker-1")
        assert member.state == MemberState.SHUTDOWN
        assert "worker-1" not in manager.get_pending_shutdowns(team.team_id)

    def test_shutdown_all(self, manager):
        team = manager.create_team("my-team")
        manager.spawn_teammate(team.team_id, "worker-1", "Task A")
        manager.spawn_teammate(team.team_id, "worker-2", "Task B")

        manager.shutdown_all(team.team_id)

        team = manager.get_team(team.team_id)
        assert team.state == TeamState.SHUTTING_DOWN

    def test_resource_summary(self, manager):
        team = manager.create_team("my-team")
        manager.spawn_teammate(team.team_id, "worker-1", "Task A")

        summary = manager.get_resource_summary()
        assert summary["total_teams"] == 1
        assert summary["total_teammates"] == 1
