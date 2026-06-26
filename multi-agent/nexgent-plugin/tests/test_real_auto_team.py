"""Real test: lead creates team and delegates work.

Run from Nexgent directory:
    cd D:/tasks/project/Nexgent/nexgent
    python D:/tasks/project/multi-agent/nexgent-plugin/tests/test_real_auto_team.py

Cleanup: removes all test artifacts (teams, memory, outputs, generated docs).
"""

import os
import sys
import time
import shutil

# Fix Windows console encoding for emoji/unicode
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path("D:/tasks/project/Nexgent/nexgent/.env"))

sys.path.insert(0, "D:/tasks/project/Nexgent/nexgent")
sys.path.insert(0, "D:/tasks/project/multi-agent/nexgent-plugin")

from nexgent.agent import NexgentAgent
from nexgent.context import Session
from team_manager import TeamManager
from team_tools import _set_team_manager, get_tools


def cleanup():
    """Remove all test artifacts."""
    cwd = os.getcwd()
    home = os.path.expanduser("~")

    # Remove ~/.nexgent/teams/ (where teams are stored)
    teams_dir = os.path.join(home, ".nexgent", "teams")
    if os.path.exists(teams_dir):
        shutil.rmtree(teams_dir, ignore_errors=True)

    # Remove ~/.nexgent/memory/ (inbox archives)
    memory_dir = os.path.join(home, ".nexgent", "memory")
    if os.path.exists(memory_dir):
        shutil.rmtree(memory_dir, ignore_errors=True)

    # Remove project-level .nexgent/ (legacy leftovers)
    local_nexgent = os.path.join(cwd, ".nexgent")
    if os.path.exists(local_nexgent):
        shutil.rmtree(local_nexgent, ignore_errors=True)

    # Remove generated md files from test runs
    for f in os.listdir(cwd):
        if f.endswith(".md") and f != "README.md" and f.startswith(("Python_313", "python_313")):
            try:
                os.remove(os.path.join(cwd, f))
            except OSError:
                pass


def main():
    print("=" * 60)
    print("Real Test: Agent Team")
    print("=" * 60)

    # 1. Create lead agent
    print("\n[1] Creating lead agent...")
    lead_agent = NexgentAgent(
        auto_approve=True,
        max_steps=0,
        stream=True,
        effort="low",
    )

    # 2. Register team tools
    print("[2] Registering team tools...")
    tm = TeamManager(parent_harness=lead_agent)
    _set_team_manager(tm)
    team_tools = get_tools()
    lead_agent.registry.register_many(team_tools)
    print(f"    Registered {len([t for t in lead_agent.registry.list_all() if 'team_' in t.name])} team tools")

    # 3. Task
    print("\n[3] Task: research Python 3.13 features\n")
    print("-" * 60)

    task = """调研 Python 3.13 的新特性，写一份中文总结。

你有 team 工具。"""

    session = Session(
        session_id="lead-001",
        working_dir=os.getcwd(),
    )

    # 4. Run
    print("[4] Running lead agent...\n")
    result = lead_agent.run(task, session)

    print("\n" + "=" * 60)
    print("[5] Lead's final response:")
    print("=" * 60)
    print(result[:3000] if result else "(empty)")

    # 6. Team status
    print("\n" + "=" * 60)
    print("[6] Team Status:")
    print("=" * 60)
    summary = tm.get_resource_summary()
    print(f"  Teams: {summary['total_teams']}")
    print(f"  Total members: {summary['total_teammates']}")
    print(f"  Active: {summary['active_teammates']}")

    for team in tm.list_teams():
        print(f"\n  Team: {team.team_name} ({team.team_id})")
        for name, member in team.members.items():
            print(f"    {name}: role={member.role}, state={member.state.value}")

    # 7. Lead closes team (summarize → archive → cleanup)
    print("\n" + "=" * 60)
    print("[7] Lead closing team...")
    print("=" * 60)

    for team in tm.list_teams():
        tm.shutdown_all(team.team_id)
        result = tm.close_team(team.team_id, summary=result[:500] if result else None)
        print(f"  Team {team.team_id} closed:")
        print(f"    Tasks: {result.get('tasks_completed', 0)}/{result.get('tasks_total', 0)}")
        print(f"    Messages archived: {result.get('archived_messages', 0)}")

    # Safety net: clean any remaining artifacts
    cleanup()
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
