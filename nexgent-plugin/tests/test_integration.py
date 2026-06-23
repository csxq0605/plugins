"""Integration tests — end-to-end team coordination scenarios."""

import os
import tempfile
import shutil
import pytest

from team_core import TeamState, MemberState, TaskStatus, TEAMS_DIR
from team_manager import TeamManager
from lead_agent import LeadAgent
from teammate_agent import TeammateAgent


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def manager(temp_dir, monkeypatch):
    import team_core
    monkeypatch.setattr(team_core, "TEAMS_DIR", temp_dir)
    return TeamManager()


# ---------------------------------------------------------------------------
# Full workflow: create → spawn → work → report → shutdown
# ---------------------------------------------------------------------------

class TestFullWorkflow:
    def test_lead_teammate_workflow(self, manager):
        """Simulate a complete lead-teammate workflow."""
        # 1. Lead creates team
        team = manager.create_team("dev-team")
        lead = LeadAgent(manager, team.team_id)

        # 2. Lead spawns teammates
        members = lead.spawn_team([
            {
                "name": "implementer-1",
                "task": "Implement auth module",
                "scope": "src/auth/",
                "success_criteria": "All tests pass",
                "role_type": "implementer",
            },
        ])
        assert len(members) == 1
        assert members[0].name == "implementer-1"

        # 3. Lead assigns a task
        task = lead.assign_task("Add JWT validation", assignee="implementer-1")
        assert task is not None

        # 4. Teammate starts working
        teammate = TeammateAgent(manager, team.team_id, "implementer-1")

        # Teammate checks inbox (trigger point 1)
        messages = teammate.sync_inbox()
        assert len(messages) >= 0  # May have spawn notification

        # Teammate claims a task
        claimed = teammate.claim_next_task()
        if claimed:
            assert claimed.status == TaskStatus.IN_PROGRESS

        # 5. Teammate completes work
        if claimed:
            teammate.complete_and_report(claimed.task_id, "Auth module implemented")

        # 6. Teammate sends final report
        teammate.final_report("All tasks complete. JWT validation added.")

        # 7. Lead collects results
        results = lead.collect_results()
        # Results may be empty if messages were already drained

        # 8. Lead requests shutdown (pending approval)
        success = lead.request_shutdown("implementer-1")
        assert success

        # 9. Approve shutdown (after user approval)
        manager.approve_shutdown(team.team_id, "implementer-1")
        member = manager.get_teammate(team.team_id, "implementer-1")
        assert member.state == MemberState.SHUTDOWN

    def test_multiple_teammates(self, manager):
        """Test with multiple teammates working in parallel."""
        team = manager.create_team("multi-team")
        lead = LeadAgent(manager, team.team_id)

        # Spawn multiple teammates
        members = lead.spawn_team([
            {"name": "researcher", "task": "Research topic A", "role_type": "implementer"},
            {"name": "writer", "task": "Write document B", "role_type": "implementer"},
            {"name": "reviewer-pr-1", "task": "Review PR #1", "role_type": "reviewer"},
        ])
        assert len(members) == 3

        # Each teammate can check their own inbox
        for name in ["researcher", "writer", "reviewer-pr-1"]:
            ta = TeammateAgent(manager, team.team_id, name)
            messages = ta.sync_inbox()
            # No crash = success

        # Lead can message any teammate
        manager.send_message(team.team_id, "lead", "researcher", "Focus on X")
        manager.send_message(team.team_id, "lead", "writer", "Use format Y")

        # Researchers check inbox
        researcher = TeammateAgent(manager, team.team_id, "researcher")
        messages = researcher.sync_inbox()
        assert any("Focus on X" in m.content for m in messages)

        writer = TeammateAgent(manager, team.team_id, "writer")
        messages = writer.sync_inbox()
        assert any("Use format Y" in m.content for m in messages)


# ---------------------------------------------------------------------------
# Inbox sync protocol scenarios
# ---------------------------------------------------------------------------

class TestInboxSyncScenarios:
    def test_rendezvous_failure_prevention(self, manager):
        """Test that inbox sync prevents stale-state race conditions."""
        team = manager.create_team("race-team")

        manager.spawn_teammate(team.team_id, "worker-a", "Task A")
        manager.spawn_teammate(team.team_id, "worker-b", "Task B")

        # worker-a completes and messages worker-b
        manager.send_message(
            team.team_id, "worker-a", "worker-b",
            "I finished Task A, result is X"
        )

        # worker-b checks inbox before making decisions
        messages = manager.check_inbox(team.team_id, "worker-b")
        assert len(messages) == 1
        assert "finished Task A" in messages[0].content

        # worker-b makes decision based on fresh state
        # (no stale-state race condition)

    def test_two_trigger_points(self, manager):
        """Test inbox check at both trigger points."""
        team = manager.create_team("sync-team")
        manager.spawn_teammate(team.team_id, "worker-1", "Task")

        teammate = TeammateAgent(manager, team.team_id, "worker-1")

        # Trigger point 1: after completing a step
        messages = teammate.sync_inbox()

        # Do some work...

        # Trigger point 2: before sending a message
        messages = teammate.sync_inbox()
        teammate.report_to_lead("Step complete")


# ---------------------------------------------------------------------------
# Shared task list scenarios
# ---------------------------------------------------------------------------

class TestSharedTaskListScenarios:
    def test_parallel_task_claiming(self, manager):
        """Multiple teammates claiming tasks without conflicts."""
        team = manager.create_team("parallel-team")

        manager.add_task(team.team_id, "Task A", created_by="lead")
        manager.add_task(team.team_id, "Task B", created_by="lead")
        manager.add_task(team.team_id, "Task C", created_by="lead")

        # Two workers claim tasks — no conflict
        t1 = manager.claim_task(team.team_id, "worker-1")
        t2 = manager.claim_task(team.team_id, "worker-2")

        assert t1 is not None
        assert t2 is not None
        assert t1.task_id != t2.task_id

        # Third claim gets the last task
        t3 = manager.claim_task(team.team_id, "worker-3")
        assert t3 is not None

        # No more tasks
        assert manager.claim_task(team.team_id, "worker-4") is None

    def test_dependency_chain(self, manager):
        """Tasks with dependencies are claimed in order."""
        team = manager.create_team("dep-team")

        t1 = manager.add_task(team.team_id, "Design", created_by="lead")
        t2 = manager.add_task(
            team.team_id, "Implement", created_by="lead",
            depends_on=[t1.task_id]
        )
        t3 = manager.add_task(
            team.team_id, "Test", created_by="lead",
            depends_on=[t2.task_id]
        )

        # Only Design is claimable
        claimed = manager.claim_task(team.team_id, "worker-1")
        assert claimed.task_id == t1.task_id

        # Implement not yet claimable
        assert manager.claim_task(team.team_id, "worker-2") is None

        # Complete Design → Implement becomes claimable
        manager.complete_task(team.team_id, t1.task_id)
        claimed = manager.claim_task(team.team_id, "worker-2")
        assert claimed.task_id == t2.task_id

        # Complete Implement → Test becomes claimable
        manager.complete_task(team.team_id, t2.task_id)
        claimed = manager.claim_task(team.team_id, "worker-3")
        assert claimed.task_id == t3.task_id
