"""Real integration test — spawns actual agents with API calls.

Run from the Nexgent project directory so .env and models.json are found:
    cd D:/tasks/project/Nexgent/nexgent
    python -m pytest D:/tasks/project/multi-agent/nexgent-plugin/tests/test_real_team.py -v -s
"""

import os
import sys
import time
import tempfile
import shutil
import threading

# Ensure Nexgent's .env is loaded
from pathlib import Path
from dotenv import load_dotenv

# Load .env from Nexgent project
_nexgent_env = Path("D:/tasks/project/Nexgent/nexgent/.env")
if _nexgent_env.exists():
    load_dotenv(_nexgent_env)

# Add Nexgent to path
sys.path.insert(0, "D:/tasks/project/Nexgent/nexgent")

# Add plugin to path
sys.path.insert(0, "D:/tasks/project/multi-agent/nexgent-plugin")

from team_core import TeamConfig, TeamMember, TeamState, MemberState, TEAMS_DIR
from team_manager import TeamManager
from inbox import TeamInbox, InboxManager


def test_real_inbox_communication():
    """Test real inbox send/receive between two agents."""
    temp_dir = tempfile.mkdtemp()
    try:
        # Create inbox manager
        manager = InboxManager("test-real-team", temp_dir)

        # Agent A sends to Agent B
        msg1 = manager.send_to("agent-a", "agent-b", "Hello from A!", "message")
        msg2 = manager.send_to("agent-a", "agent-b", "Task complete", "task_result")
        msg3 = manager.send_to("agent-b", "agent-a", "Acknowledged", "message")

        # Agent B checks inbox
        b_inbox = manager.get_inbox("agent-b")
        assert b_inbox.has_messages()

        messages = b_inbox.check_and_drain()
        assert len(messages) == 2
        assert messages[0].content == "Hello from A!"
        assert messages[1].content == "Task complete"

        # Agent A checks inbox
        a_inbox = manager.get_inbox("agent-a")
        messages = a_inbox.check_and_drain()
        assert len(messages) == 1
        assert messages[0].content == "Acknowledged"

        # Both inboxes now empty
        assert not b_inbox.has_messages()
        assert not a_inbox.has_messages()

        print("[PASS] Real inbox communication works")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_real_team_create_and_tasks():
    """Test real team creation and task management."""
    temp_dir = tempfile.mkdtemp()
    try:
        import team_core
        original_dir = team_core.TEAMS_DIR
        team_core.TEAMS_DIR = temp_dir

        manager = TeamManager()

        # Create team
        team = manager.create_team("real-test-team")
        assert team.state == TeamState.ACTIVE
        print(f"[PASS] Team created: {team.team_id}")

        # Add tasks
        t1 = manager.add_task(team.team_id, "Research topic A", created_by="lead")
        t2 = manager.add_task(team.team_id, "Write document B", created_by="lead",
                              depends_on=[t1.task_id])
        t3 = manager.add_task(team.team_id, "Review output", created_by="lead")
        print(f"[PASS] Tasks added: {t1.task_id}, {t2.task_id}, {t3.task_id}")

        # Spawn teammates (without actually running agents)
        m1 = manager.spawn_teammate(team.team_id, "researcher", "Research topic A")
        m2 = manager.spawn_teammate(team.team_id, "writer", "Write document B")
        print(f"[PASS] Teammates spawned: {m1.name}, {m2.name}")

        # Researcher claims task
        claimed = manager.claim_task(team.team_id, "researcher")
        assert claimed is not None
        assert claimed.task_id == t1.task_id
        print(f"[PASS] Researcher claimed: {claimed.description}")

        # Writer claims t3 (no dependencies, t2 is blocked by t1)
        claimed_w = manager.claim_task(team.team_id, "writer")
        assert claimed_w is not None
        assert claimed_w.task_id == t3.task_id  # t3 has no deps
        print(f"[PASS] Writer claimed: {claimed_w.description}")

        # No more tasks available (t2 still blocked by t1)
        no_task = manager.claim_task(team.team_id, "researcher")
        assert no_task is None
        print("[PASS] No more tasks available (t2 blocked)")

        tasks = manager.list_tasks(team.team_id)
        for t in tasks:
            print(f"  Task: {t.task_id[:8]}... status={t.status.value} deps={t.depends_on}")

        # Complete t1
        manager.complete_task(team.team_id, t1.task_id, "Research done")
        print("[PASS] Task 1 completed")

        # Now t2 is unblocked
        claimed_w = manager.claim_task(team.team_id, "writer")
        assert claimed_w is not None
        assert claimed_w.task_id == t2.task_id
        print(f"[PASS] Writer claimed unblocked task: {claimed_w.description}")

        # Send messages between teammates
        manager.send_message(team.team_id, "researcher", "writer",
                             "Here's my research: Topic A is about X", "message")
        manager.send_message(team.team_id, "lead", "researcher",
                             "Good work, now help with review", "message")

        # Check inboxes
        writer_msgs = manager.check_inbox(team.team_id, "writer")
        assert len(writer_msgs) == 1
        assert "research" in writer_msgs[0].content.lower()
        print(f"[PASS] Writer received message: {writer_msgs[0].content[:50]}")

        researcher_msgs = manager.check_inbox(team.team_id, "researcher")
        assert len(researcher_msgs) == 1
        assert "review" in researcher_msgs[0].content.lower()
        print(f"[PASS] Researcher received message: {researcher_msgs[0].content[:50]}")

        # Shutdown
        manager.request_shutdown(team.team_id, "researcher")
        manager.request_shutdown(team.team_id, "writer")
        print("[PASS] Shutdown requested")

        # Verify teammate states
        r = manager.get_teammate(team.team_id, "researcher")
        w = manager.get_teammate(team.team_id, "writer")
        assert r.state == MemberState.SHUTDOWN
        assert w.state == MemberState.SHUTDOWN
        print("[PASS] Both teammates in SHUTDOWN state")

        manager.delete_team(team.team_id)
        print("[PASS] Team deleted")

        team_core.TEAMS_DIR = original_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_real_agent_team_with_api():
    """Test with actual API calls — spawns a real NexgentAgent as teammate.

    This test requires a valid API key in the Nexgent .env file.
    """
    try:
        from nexgent.agent import NexgentAgent
        from nexgent.context import Session
    except ImportError:
        print("[SKIP] Nexgent not importable, skipping API test")
        return

    temp_dir = tempfile.mkdtemp()
    try:
        import team_core
        original_dir = team_core.TEAMS_DIR
        team_core.TEAMS_DIR = temp_dir

        manager = TeamManager()

        # Create team
        team = manager.create_team("api-test-team")
        print(f"\n[TEAM] Created: {team.team_id}")

        # Create a real NexgentAgent
        agent = NexgentAgent(
            auto_approve=True,
            max_steps=5,
            stream=False,
            bare=True,
            effort="low",
        )

        # Run a simple task as a "teammate"
        session = Session(
            session_id="test-teammate-1",
            working_dir=os.getcwd(),
        )

        # Register as teammate
        manager.spawn_teammate(team.team_id, "test-worker", "Say hello")

        # Send a message to the teammate via inbox
        manager.send_message(team.team_id, "lead", "test-worker",
                             "Welcome to the team!", "message")

        # Run the agent with a simple task
        task = """You are a teammate in a team. Your task is simple:
1. Read your inbox file to check for messages
2. Respond with "Hello team! I received your message."
3. That's it - just respond with text, no tools needed.

Respond now with a greeting."""

        print("[AGENT] Running real agent...")
        result = agent.run(task, session)
        print(f"[AGENT] Result: {result[:200] if result else '(empty)'}")

        # Verify the agent produced output
        assert result is not None
        assert len(result) > 0
        print("[PASS] Real agent produced output")

        # Check inbox
        messages = manager.check_inbox(team.team_id, "test-worker")
        print(f"[INBOX] Messages for test-worker: {len(messages)}")
        for msg in messages:
            print(f"  - {msg.sender}: {msg.content[:50]}")

        # Cleanup
        manager.delete_team(team.team_id)
        print("[PASS] Real agent team test complete")

        team_core.TEAMS_DIR = original_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("=" * 60)
    print("Agent Team Real Integration Tests")
    print("=" * 60)

    test_real_inbox_communication()
    print()
    test_real_team_create_and_tasks()
    print()
    test_real_agent_team_with_api()

    print()
    print("=" * 60)
    print("All tests complete!")
    print("=" * 60)
