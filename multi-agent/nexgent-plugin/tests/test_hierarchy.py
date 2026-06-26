"""Test multi-level hierarchy — managers can create sub-teams.

Run from the Nexgent project directory:
    cd D:/tasks/project/Nexgent/nexgent
    python -m pytest D:/tasks/project/multi-agent/nexgent-plugin/tests/test_hierarchy.py -v -s
"""

import os
import sys
import time
import tempfile
import shutil

# Load .env from Nexgent project
from pathlib import Path
from dotenv import load_dotenv
_nexgent_env = Path("D:/tasks/project/Nexgent/nexgent/.env")
if _nexgent_env.exists():
    load_dotenv(_nexgent_env)

sys.path.insert(0, "D:/tasks/project/Nexgent/nexgent")
sys.path.insert(0, "D:/tasks/project/multi-agent/nexgent-plugin")

from team_core import TeamConfig, TeamMember, TeamState, MemberState, TEAMS_DIR
from team_manager import TeamManager


def test_manager_creates_subteam():
    """Test that a manager role can create its own sub-team."""
    temp_dir = tempfile.mkdtemp()
    try:
        import team_core
        original_dir = team_core.TEAMS_DIR
        team_core.TEAMS_DIR = temp_dir

        manager = TeamManager()

        # Create top-level team
        top_team = manager.create_team("project-alpha")
        print(f"\n[LEVEL 0] Created team: {top_team.team_id}")

        # Add high-level tasks
        t1 = manager.add_task(top_team.team_id, "Build entire feature X", created_by="lead")
        t2 = manager.add_task(top_team.team_id, "Write documentation", created_by="lead")
        print(f"[LEVEL 0] Added {2} tasks")

        # Spawn a manager (not just a worker)
        mgr = manager.spawn_teammate(
            top_team.team_id, "tech-lead",
            "Coordinate the implementation of feature X",
            role="manager",
        )
        print(f"[LEVEL 0] Spawned manager: {mgr.name} (state={mgr.state.value})")

        # Spawn a regular worker
        worker = manager.spawn_teammate(
            top_team.team_id, "doc-writer",
            "Write documentation for feature X",
            role="worker",
        )
        print(f"[LEVEL 0] Spawned worker: {worker.name}")

        # Verify the manager has team tools available
        agent_key = manager._agent_key(top_team.team_id, "tech-lead")
        mgr_agent = manager._teammate_agents.get(agent_key)
        if mgr_agent:
            tool_names = [t.name for t in mgr_agent.registry.list_all()]
            has_team_tools = any("team_" in t for t in tool_names)
            print(f"[MANAGER] Has team tools: {has_team_tools}")
            print(f"[MANAGER] Team tools: {[t for t in tool_names if 'team_' in t]}")
        else:
            print("[MANAGER] Agent not yet started (expected in test)")

        # Verify the manager's task prompt mentions sub-team capability
        inbox_path = os.path.join(top_team.config_dir, "inbox", "tech-lead.json")
        mgr_task = manager._build_teammate_task(
            name="tech-lead",
            task="Coordinate feature X",
            team_id=top_team.team_id,
            inbox_path=inbox_path,
            role="manager",
        )
        assert "team_create" in mgr_task
        assert "子团队" in mgr_task or "sub-team" in mgr_task.lower()
        print("[PASS] Manager task prompt includes sub-team instructions")

        # Verify worker's task prompt does NOT mention sub-teams
        worker_task = manager._build_teammate_task(
            name="doc-writer",
            task="Write docs",
            team_id=top_team.team_id,
            inbox_path=os.path.join(top_team.config_dir, "inbox", "doc-writer.json"),
            role="worker",
        )
        assert "team_create" not in worker_task
        print("[PASS] Worker task prompt does NOT include sub-team instructions")

        # Simulate what happens when the manager creates a sub-team
        # (In real usage, the manager's agent would call team_create)
        sub_team = manager.create_team(f"{top_team.team_id}-impl")
        print(f"\n[LEVEL 1] Manager created sub-team: {sub_team.team_id}")

        # Manager spawns workers in sub-team
        w1 = manager.spawn_teammate(sub_team.team_id, "frontend-dev", "Build UI components")
        w2 = manager.spawn_teammate(sub_team.team_id, "backend-dev", "Build API endpoints")
        print(f"[LEVEL 1] Spawned workers: {w1.name}, {w2.name}")

        # Sub-team tasks
        st1 = manager.add_task(sub_team.team_id, "Build React components", created_by="tech-lead")
        st2 = manager.add_task(sub_team.team_id, "Build REST API", created_by="tech-lead")
        st3 = manager.add_task(sub_team.team_id, "Integration tests", created_by="tech-lead",
                               depends_on=[st1.task_id, st2.task_id])
        print(f"[LEVEL 1] Added {3} tasks (with dependency)")

        # Workers claim tasks
        claimed1 = manager.claim_task(sub_team.team_id, "frontend-dev")
        claimed2 = manager.claim_task(sub_team.team_id, "backend-dev")
        assert claimed1 is not None
        assert claimed2 is not None
        print(f"[PASS] Workers claimed tasks: {claimed1.description}, {claimed2.description}")

        # No one can claim st3 yet (depends on st1, st2)
        no_task = manager.claim_task(sub_team.team_id, "frontend-dev")
        assert no_task is None
        print("[PASS] Dependent task correctly blocked")

        # Complete tasks
        manager.complete_task(sub_team.team_id, claimed1.task_id, "UI done")
        manager.complete_task(sub_team.team_id, claimed2.task_id, "API done")

        # Now st3 is unblocked
        claimed3 = manager.claim_task(sub_team.team_id, "frontend-dev")
        assert claimed3 is not None
        assert claimed3.task_id == st3.task_id
        print(f"[PASS] Dependent task unblocked: {claimed3.description}")

        # Communication across levels
        manager.send_message(top_team.team_id, "tech-lead", "lead",
                             "Feature X progress: 60%", "status_report")
        manager.send_message(sub_team.team_id, "frontend-dev", "backend-dev",
                             "API contract ready, check /api/types", "message")

        # Check cross-level messaging
        lead_msgs = manager.check_inbox(top_team.team_id, "lead")
        assert len(lead_msgs) == 1
        assert "60%" in lead_msgs[0].content
        print(f"[PASS] Lead received status: {lead_msgs[0].content}")

        backend_msgs = manager.check_inbox(sub_team.team_id, "backend-dev")
        assert len(backend_msgs) == 1
        assert "API contract" in backend_msgs[0].content
        print(f"[PASS] Backend received message: {backend_msgs[0].content}")

        # Show the hierarchy
        print("\n" + "=" * 50)
        print("ORGANIZATION HIERARCHY")
        print("=" * 50)
        print(f"Level 0: Team '{top_team.team_name}' ({top_team.team_id})")
        print(f"  ├── tech-lead (MANAGER)")
        print(f"  │   └── Level 1: Sub-team '{sub_team.team_name}' ({sub_team.team_id})")
        print(f"  │       ├── frontend-dev (WORKER)")
        print(f"  │       └── backend-dev (WORKER)")
        print(f"  └── doc-writer (WORKER)")
        print("=" * 50)

        # Cleanup
        manager.shutdown_all(sub_team.team_id)
        manager.shutdown_all(top_team.team_id)
        manager.delete_team(sub_team.team_id)
        manager.delete_team(top_team.team_id)
        print("\n[PASS] All teams cleaned up")

        team_core.TEAMS_DIR = original_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_auto_team_decision():
    """Test that team_* tools are available to the main agent for auto-decision."""
    from team_tools import get_tools

    tools = get_tools()
    tool_names = [t.name for t in tools]

    print(f"\n[TOOLS] Available team tools: {tool_names}")

    assert "team_create" in tool_names
    assert "team_spawn" in tool_names
    assert "team_send_message" in tool_names
    assert "team_check_inbox" in tool_names
    assert "team_add_task" in tool_names
    assert "team_claim_task" in tool_names
    assert "team_complete_task" in tool_names
    assert "team_shutdown" in tool_names
    assert "team_delete" in tool_names

    # Check that team_spawn has role parameter
    spawn_tool = next(t for t in tools if t.name == "team_spawn")
    role_param = spawn_tool.parameters["properties"].get("role")
    assert role_param is not None
    assert "manager" in role_param.get("description", "").lower() or \
           "manager" in str(role_param.get("enum", []))
    print("[PASS] team_spawn supports role='manager' for multi-level hierarchy")

    # Check that team_create has parent_team_id
    create_tool = next(t for t in tools if t.name == "team_create")
    parent_param = create_tool.parameters["properties"].get("parent_team_id")
    assert parent_param is not None
    print("[PASS] team_create supports parent_team_id for sub-teams")


if __name__ == "__main__":
    print("=" * 60)
    print("Multi-Level Hierarchy Tests")
    print("=" * 60)

    test_auto_team_decision()
    test_manager_creates_subteam()

    print("\n" + "=" * 60)
    print("All hierarchy tests passed!")
    print("=" * 60)
