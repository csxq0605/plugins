"""TeamManager — lifecycle management for agent teams.

Design principles (following Fomalhaut647's original approach):
- Spawn prompt is minimal: identity + task + skill reference (WHAT, not HOW)
- Protocol lives in skills, not in prompts
- Inbox is ephemeral: cleaned on drain, important content saved to memory
- Shutdown requires user approval (hard rule)
"""

import os
import json
import time
import uuid
import shutil
import threading
from typing import Optional, Any

try:
    from .team_core import (
        TeamConfig, TeamMember, TeamState, MemberState,
        SharedTaskList, TeamTask, TaskStatus, create_team_id, get_teams_dir,
    )
    from .inbox import InboxManager, InboxMessage
except ImportError:
    from team_core import (
        TeamConfig, TeamMember, TeamState, MemberState,
        SharedTaskList, TeamTask, TaskStatus, create_team_id, get_teams_dir,
    )
    from inbox import InboxManager, InboxMessage


# ---------------------------------------------------------------------------
# Role identity prompts — kept minimal, protocol lives in skill
# ---------------------------------------------------------------------------

ROLE_PROMPTS = {
    "lead": "你是团队的 **lead**。只做协调，不做实际工作。",
    "manager": "你是团队的 **manager**。协调子任务，向 lead 汇报。",
    "worker": "你是团队的 **worker**。执行任务，向 lead 汇报结果。",
}


class TeamManager:
    """Manages team lifecycle: create → spawn → coordinate → shutdown → delete.

    Key design:
    - Spawn prompt = role identity + task + "read the skill" (WHAT only)
    - Protocol in skill file, not in prompt
    - Inbox ephemeral: cleaned on drain, important messages saved to memory
    - Shutdown requires user approval
    """

    def __init__(self, parent_harness: Any = None, logger: Any = None):
        self._parent = parent_harness
        self._logger = logger
        self._teams: dict[str, TeamConfig] = {}
        self._task_lists: dict[str, SharedTaskList] = {}
        self._inbox_managers: dict[str, InboxManager] = {}
        self._teammate_agents: dict[str, Any] = {}
        self._teammate_threads: dict[str, threading.Thread] = {}
        self._teammate_sessions: dict[str, Any] = {}
        self._shutdown_events: dict[str, threading.Event] = {}
        self._lock = threading.Lock()
        # Pending shutdown requests waiting for user approval
        self._pending_shutdowns: dict[str, list[str]] = {}  # team_id → [member_names]

    def _log(self, level: str, msg: str):
        if self._logger:
            getattr(self._logger, level, self._logger.info)(msg)

    def _agent_key(self, team_id: str, name: str) -> str:
        return f"{team_id}:{name}"

    # ------------------------------------------------------------------
    # Team lifecycle
    # ------------------------------------------------------------------

    def create_team(self, name: str = None) -> TeamConfig:
        team_id = create_team_id()
        team = TeamConfig(
            team_id=team_id,
            team_name=name or team_id,
            lead_session_id="lead",
        )
        team.members["lead"] = TeamMember(
            name="lead", agent_id="lead", session_id="lead",
            role="lead", state=MemberState.IDLE,
        )
        team.save()
        os.makedirs(os.path.join(team.config_dir, "inbox"), exist_ok=True)
        with self._lock:
            self._teams[team_id] = team
            self._task_lists[team_id] = SharedTaskList(team)
            self._inbox_managers[team_id] = InboxManager(team_id)
            self._pending_shutdowns[team_id] = []
        self._log("info", f"Team created: {team_id} ({team.team_name})")
        return team

    def get_team(self, team_id: str) -> Optional[TeamConfig]:
        with self._lock:
            if team_id in self._teams:
                return self._teams[team_id]
        team = TeamConfig.load(team_id)
        if team:
            with self._lock:
                self._teams[team_id] = team
                self._task_lists[team_id] = SharedTaskList(team)
                self._inbox_managers[team_id] = InboxManager(team_id)
        return team

    def list_teams(self) -> list[TeamConfig]:
        teams = []
        teams_dir = get_teams_dir()
        if os.path.exists(teams_dir):
            for name in os.listdir(teams_dir):
                team = self.get_team(name)
                if team and team.state == TeamState.ACTIVE:
                    teams.append(team)
        return teams

    def close_team(self, team_id: str, summary: str = None) -> dict:
        """Lead calls this to properly end a team.

        Flow:
        1. Collect final status from all teammates
        2. Archive important messages (status reports, task results) to memory
        3. Generate a summary of what was accomplished
        4. Clean up team directory (inbox, config)

        Args:
            team_id: Team to close
            summary: Optional lead-provided summary of the team's work

        Returns:
            Dict with team summary and archived message count
        """
        team = self.get_team(team_id)
        if team is None:
            return {"error": "Team not found"}

        # 1. Collect final status from all teammates
        final_status = {}
        for name, member in team.members.items():
            if member.role == "lead":
                continue
            messages = self.check_inbox(team_id, name)
            final_status[name] = {
                "role": member.role,
                "state": member.state.value,
                "last_active": member.last_active,
                "pending_messages": len(messages),
            }

        # 2. Archive important messages to memory
        archived_count = self._archive_team_messages(team_id)

        # 3. Collect task results
        tasks = self.list_tasks(team_id)
        completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        task_results = {t.task_id: t.result for t in completed_tasks if t.result}

        # 4. Build team summary
        team_summary = {
            "team_id": team_id,
            "team_name": team.team_name,
            "members": final_status,
            "tasks_completed": len(completed_tasks),
            "tasks_total": len(tasks),
            "task_results": task_results,
            "archived_messages": archived_count,
            "lead_summary": summary,
        }

        # 5. Save summary to memory
        try:
            memory_dir = os.path.join(os.path.expanduser("~"), ".nexgent", "memory")
            os.makedirs(memory_dir, exist_ok=True)
            summary_path = os.path.join(memory_dir, f"team-{team_id}-summary.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(team_summary, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._log("warning", f"Failed to save team summary: {e}")

        # 6. Clean up
        team.state = TeamState.CLOSED
        team.delete()

        with self._lock:
            self._teams.pop(team_id, None)
            self._task_lists.pop(team_id, None)
            self._inbox_managers.pop(team_id, None)
            self._pending_shutdowns.pop(team_id, None)
            to_remove = [k for k in self._teammate_agents if k.startswith(f"{team_id}:")]
            for k in to_remove:
                self._teammate_agents.pop(k, None)
                self._teammate_threads.pop(k, None)
                self._teammate_sessions.pop(k, None)
                self._shutdown_events.pop(k, None)

        self._log("info", f"Team closed: {team_id} ({len(completed_tasks)} tasks, {archived_count} messages archived)")
        return team_summary

    def delete_team(self, team_id: str):
        """Delete team without summary (for cleanup/error cases)."""
        team = self.get_team(team_id)
        if team is None:
            return
        self._archive_team_messages(team_id)
        team.state = TeamState.CLOSED
        team.delete()
        with self._lock:
            self._teams.pop(team_id, None)
            self._task_lists.pop(team_id, None)
            self._inbox_managers.pop(team_id, None)
            self._pending_shutdowns.pop(team_id, None)
            to_remove = [k for k in self._teammate_agents if k.startswith(f"{team_id}:")]
            for k in to_remove:
                self._teammate_agents.pop(k, None)
                self._teammate_threads.pop(k, None)
                self._teammate_sessions.pop(k, None)
                self._shutdown_events.pop(k, None)

        self._log("info", f"Team deleted: {team_id}")

    def _archive_team_messages(self, team_id: str):
        """Archive important messages to Nexgent memory before cleanup.

        Saves status reports and task results to .nexgent/memory/ for
        future reference. Inbox files themselves are deleted.
        """
        try:
            memory_dir = os.path.join(os.getcwd(), ".nexgent", "memory")
            os.makedirs(memory_dir, exist_ok=True)

            manager = self._get_inbox_manager(team_id)
            member_names = manager.get_all_member_names()

            archived = []
            for name in member_names:
                inbox = manager.get_inbox(name)
                messages = inbox.check_and_drain()
                for msg in messages:
                    if msg.msg_type in ("status_report", "task_result"):
                        archived.append({
                            "from": msg.sender,
                            "to": name,
                            "type": msg.msg_type,
                            "content": msg.content,
                            "time": msg.timestamp,
                        })

            if archived:
                archive_path = os.path.join(memory_dir, f"team-{team_id}-archive.json")
                with open(archive_path, "w", encoding="utf-8") as f:
                    json.dump(archived, f, indent=2, ensure_ascii=False)
                self._log("info", f"Archived {len(archived)} messages from team {team_id}")
        except Exception as e:
            self._log("warning", f"Failed to archive messages for {team_id}: {e}")

    # ------------------------------------------------------------------
    # Teammate lifecycle
    # ------------------------------------------------------------------

    def spawn_teammate(
        self,
        team_id: str,
        name: str,
        task: str,
        role: str = "worker",
        model: str = None,
        worktree_path: str = None,
        max_steps: int = 0,
        effort: str = "medium",
        auto_approve: bool = True,
    ) -> TeamMember:
        """Spawn a new teammate.

        Spawn prompt is minimal (WHAT only):
        - Role identity (short)
        - Task description
        - "Read the teammate skill" instruction
        - No protocol details (they're in the skill)
        """
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team not found: {team_id}")

        agent_id = str(uuid.uuid4())[:8]
        session_id = f"teammate-{agent_id}"

        member = TeamMember(
            name=name, agent_id=agent_id, session_id=session_id,
            role=role, state=MemberState.IDLE,
            worktree_path=worktree_path,
        )
        team.members[name] = member
        team.save()

        agent_key = self._agent_key(team_id, name)
        shutdown_event = threading.Event()
        with self._lock:
            self._shutdown_events[agent_key] = shutdown_event

        # Minimal spawn prompt (WHAT only)
        full_task = self._build_spawn_prompt(
            name=name, task=task, role=role,
            team_id=team_id, worktree_path=worktree_path,
        )

        ready_event = threading.Event()

        def _run_teammate():
            try:
                try:
                    from .agent import NexgentAgent
                    from .context import Session
                except ImportError:
                    from nexgent.agent import NexgentAgent
                    from nexgent.context import Session

                agent = NexgentAgent(
                    model=model or (self._parent.model if self._parent else None),
                    auto_approve=auto_approve,
                    max_steps=max_steps,
                    effort=effort,
                    stream=False,
                    bare=False,
                )
                if self._parent and hasattr(self._parent, '_hook_runner'):
                    agent._hook_runner = self._parent._hook_runner

                # Add team coordination tools
                try:
                    try:
                        from .team_tools import get_teammate_tools, _set_team_manager
                    except ImportError:
                        from team_tools import get_teammate_tools, _set_team_manager
                    _set_team_manager(self)
                    tools = get_teammate_tools()
                    if tools:
                        agent.registry.register_many(tools)
                        agent._system_prompt_cache = None
                except Exception as e:
                    self._log("warning", f"Failed to register team tools for {name}: {e}")

                session = Session(session_id=session_id, working_dir=os.getcwd())
                with self._lock:
                    self._teammate_agents[agent_key] = agent
                    self._teammate_sessions[agent_key] = session

                ready_event.set()
                member.state = MemberState.WORKING
                team.save()

                result = agent.run(full_task, session)

                if not shutdown_event.is_set():
                    member.state = MemberState.IDLE
                    team.save()
            except Exception as e:
                ready_event.set()
                self._log("error", f"Teammate {name} failed: {e}")
                member.state = MemberState.SHUTDOWN
                team.save()

        thread = threading.Thread(
            target=_run_teammate, name=f"teammate-{name}", daemon=True,
        )
        with self._lock:
            self._teammate_threads[agent_key] = thread
        thread.start()
        ready_event.wait(timeout=10)

        self._log("info", f"Teammate spawned: {name} (role={role}) in team {team_id}")
        return member

    def _build_spawn_prompt(
        self, name: str, task: str, role: str,
        team_id: str, worktree_path: str = None,
    ) -> str:
        """Build minimal spawn prompt (WHAT only).

        The prompt contains:
        1. Role identity (short, focused)
        2. Task description
        3. "Read the skill" instruction

        The prompt does NOT contain:
        - Inbox sync protocol details
        - Tool usage instructions
        - Workflow steps
        These live in the teammate skill.
        """
        role_prompt = ROLE_PROMPTS.get(role, ROLE_PROMPTS["worker"])

        inbox_path = os.path.join(get_teams_dir(), team_id, "inbox", f"{name}.json")
        config_path = os.path.join(get_teams_dir(), team_id, "config.json")

        return f"""{role_prompt}

你是团队 '{team_id}' 中的 '{name}'。

第一个动作：调用 `team_tool_search` 加载 team 工具 schema，然后读取 teammate skill 了解协调协议。

任务：{task}
依赖：无
"""

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    def send_message(self, team_id: str, sender: str, recipient: str,
                     content: str, msg_type: str = "message") -> InboxMessage:
        manager = self._get_inbox_manager(team_id)
        msg = manager.send_to(sender, recipient, content, msg_type)
        team = self.get_team(team_id)
        if team and sender in team.members:
            team.members[sender].last_active = time.time()
            team.save()
        return msg

    def check_inbox(self, team_id: str, member_name: str) -> list[InboxMessage]:
        """Check and drain inbox. Messages are removed from file after read."""
        return self._get_inbox_manager(team_id).drain_all(member_name)

    def has_messages(self, team_id: str, member_name: str) -> bool:
        return self._get_inbox_manager(team_id).get_inbox(member_name).has_messages()

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def add_task(self, team_id: str, description: str,
                 created_by: str = "lead", depends_on: list[str] = None) -> TeamTask:
        return self._get_task_list(team_id).add_task(description, created_by, depends_on)

    def claim_task(self, team_id: str, claimer: str) -> Optional[TeamTask]:
        return self._get_task_list(team_id).claim_task(claimer)

    def complete_task(self, team_id: str, task_id: str, result: str = None) -> bool:
        return self._get_task_list(team_id).complete_task(task_id, result)

    def list_tasks(self, team_id: str, status: TaskStatus = None) -> list[TeamTask]:
        return self._get_task_list(team_id).list_tasks(status=status)

    # ------------------------------------------------------------------
    # Shutdown — requires user approval (hard rule)
    # ------------------------------------------------------------------

    def request_shutdown(self, team_id: str, member_name: str) -> bool:
        """Request shutdown of a teammate.

        The shutdown is queued as pending. The lead must call
        approve_shutdown() after reporting to the user.
        """
        team = self.get_team(team_id)
        if team is None:
            return False
        member = team.members.get(member_name)
        if member is None or member.role == "lead":
            return False

        with self._lock:
            if team_id not in self._pending_shutdowns:
                self._pending_shutdowns[team_id] = []
            self._pending_shutdowns[team_id].append(member_name)

        # Notify teammate
        self.send_message(team_id, "lead", member_name,
                          "Shutdown requested. Complete in-flight work and report.",
                          msg_type="shutdown_request")

        self._log("info", f"Shutdown pending for {member_name} in team {team_id} (awaiting user approval)")
        return True

    def approve_shutdown(self, team_id: str, member_name: str) -> bool:
        """Approve a pending shutdown. Called after user approval."""
        team = self.get_team(team_id)
        if team is None:
            return False
        member = team.members.get(member_name)
        if member is None:
            return False

        member.state = MemberState.SHUTDOWN
        team.save()

        agent_key = self._agent_key(team_id, member_name)
        with self._lock:
            event = self._shutdown_events.get(agent_key)
            if event:
                event.set()
            agent = self._teammate_agents.get(agent_key)
            if agent and hasattr(agent, 'graceful_abort'):
                agent.graceful_abort.request()
            # Remove from pending
            if team_id in self._pending_shutdowns:
                self._pending_shutdowns[team_id] = [
                    n for n in self._pending_shutdowns[team_id] if n != member_name
                ]

        self._log("info", f"Shutdown approved for {member_name} in team {team_id}")
        return True

    def get_pending_shutdowns(self, team_id: str) -> list[str]:
        """Get list of teammates pending shutdown approval."""
        with self._lock:
            return list(self._pending_shutdowns.get(team_id, []))

    def shutdown_all(self, team_id: str):
        """Shutdown all teammates. Bypasses approval for cleanup."""
        team = self.get_team(team_id)
        if team is None:
            return
        team.state = TeamState.SHUTTING_DOWN
        team.save()
        for name, member in team.members.items():
            if member.role != "lead" and member.state != MemberState.SHUTDOWN:
                self.approve_shutdown(team_id, name)

    def set_teammate_state(self, team_id: str, name: str, state: MemberState):
        team = self.get_team(team_id)
        if team is None:
            return
        member = team.members.get(name)
        if member:
            member.state = state
            member.last_active = time.time()
            team.save()

    def get_teammate(self, team_id: str, name: str) -> Optional[TeamMember]:
        team = self.get_team(team_id)
        if team is None:
            return None
        return team.members.get(name)

    def list_teammates(self, team_id: str) -> list[TeamMember]:
        team = self.get_team(team_id)
        if team is None:
            return []
        return [m for m in team.members.values() if m.role != "lead"]

    def wait_for_teammate(self, team_id: str, name: str, timeout: float = None) -> bool:
        agent_key = self._agent_key(team_id, name)
        with self._lock:
            thread = self._teammate_threads.get(agent_key)
        if thread:
            thread.join(timeout=timeout)
            return not thread.is_alive()
        return True

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_inbox_manager(self, team_id: str) -> InboxManager:
        with self._lock:
            if team_id not in self._inbox_managers:
                self._inbox_managers[team_id] = InboxManager(team_id)
            return self._inbox_managers[team_id]

    def _get_task_list(self, team_id: str) -> SharedTaskList:
        with self._lock:
            if team_id not in self._task_lists:
                team = self.get_team(team_id)
                if team is None:
                    raise ValueError(f"Team not found: {team_id}")
                self._task_lists[team_id] = SharedTaskList(team)
            return self._task_lists[team_id]

    def get_resource_summary(self) -> dict:
        with self._lock:
            return {
                "total_teams": len(self._teams),
                "total_teammates": sum(
                    sum(1 for m in t.members.values() if m.role != "lead")
                    for t in self._teams.values()
                ),
                "active_teammates": sum(
                    sum(1 for m in t.members.values()
                        if m.role != "lead" and m.state == MemberState.WORKING)
                    for t in self._teams.values()
                ),
            }
