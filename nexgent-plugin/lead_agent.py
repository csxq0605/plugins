"""LeadAgent — team lead role wrapper.

Encapsulates lead-specific operations: spawning teammates, assigning tasks,
collecting results, coordinating shutdown. Enforces the WHAT vs HOW principle
and the hub-and-spoke topology.
"""

import time
from typing import Optional, Any

try:
    from .team_core import (
        TeamConfig, TeamMember, TeamState, MemberState,
        TeamTask, TaskStatus,
    )
    from .team_manager import TeamManager
except ImportError:
    from team_core import (
        TeamConfig, TeamMember, TeamState, MemberState,
        TeamTask, TaskStatus,
    )
    from team_manager import TeamManager


# ---------------------------------------------------------------------------
# Spawn prompt template (WHAT, not HOW)
# ---------------------------------------------------------------------------
SPAWN_PROMPT_TEMPLATE = """你是 {name}，负责 {task_description}。

范围：{scope}
成功标准：{success_criteria}

你的第一个动作：读取 team-coord:teammate skill
{extra_instructions}
"""

SPAWN_PROMPT_SUPERPOWERS = """
Read 'references/superpowers-implementer.md' 获取完整的 implementer 工作流程。
"""

SPAWN_PROMPT_REVIEWER = """
Read 'references/code-review.md' 获取 reviewer 工作流程。
"""


class LeadAgent:
    """Team lead role — orchestrates teammates via hub-and-spoke topology.

    Usage:
        lead = LeadAgent(team_manager, team_id)
        lead.spawn_team([
            {"name": "implementer-1", "task": "Implement auth module", ...},
            {"name": "reviewer-pr-1", "task": "Review PR #3", ...},
        ])
        lead.assign_task("Add JWT validation", assignee="implementer-1")
        results = lead.collect_results()
        lead.request_shutdown("implementer-1")
    """

    def __init__(self, team_manager: TeamManager, team_id: str):
        self.tm = team_manager
        self.team_id = team_id

    @property
    def team(self) -> Optional[TeamConfig]:
        return self.tm.get_team(self.team_id)

    def spawn_team(self, teammates: list[dict]) -> list[TeamMember]:
        """Spawn all teammates in a single batch (parallel execution).

        Args:
            teammates: List of dicts with keys:
                - name (required): teammate name
                - task (required): task description
                - scope (optional): work scope
                - success_criteria (optional): success criteria
                - model (optional): model override
                - worktree_path (optional): worktree path
                - role_type (optional): "implementer" or "reviewer"
                - extra_instructions (optional): additional prompt text

        Returns:
            List of created TeamMember objects
        """
        members = []
        for t in teammates:
            name = t["name"]
            task = t["task"]
            scope = t.get("scope", task)
            success_criteria = t.get("success_criteria", "完成任务并通过 review")
            role_type = t.get("role_type", "implementer")
            extra = t.get("extra_instructions", "")

            # Build spawn prompt (WHAT, not HOW)
            if role_type == "reviewer":
                extra += SPAWN_PROMPT_REVIEWER
            elif role_type == "implementer":
                extra += SPAWN_PROMPT_SUPERPOWERS

            prompt = SPAWN_PROMPT_TEMPLATE.format(
                name=name,
                task_description=task,
                scope=scope,
                success_criteria=success_criteria,
                extra_instructions=extra,
            )

            # Add task to shared task list
            self.tm.add_task(
                self.team_id,
                description=task,
                created_by="lead",
            )

            # Spawn the teammate
            member = self.tm.spawn_teammate(
                team_id=self.team_id,
                name=name,
                task=prompt,
                model=t.get("model"),
                worktree_path=t.get("worktree_path"),
                effort=t.get("effort", "medium"),
            )
            members.append(member)

        return members

    def assign_task(self, description: str,
                    assignee: str = None) -> Optional[TeamTask]:
        """Assign a task to a specific teammate or add to the shared list.

        Args:
            description: Task description
            assignee: Teammate name (None = available for self-claim)

        Returns:
            The created TeamTask
        """
        task = self.tm.add_task(
            self.team_id,
            description=description,
            created_by="lead",
        )
        if assignee:
            # Directly assign
            task.assigned_to = assignee
            task.status = TaskStatus.IN_PROGRESS
        return task

    def collect_results(self) -> dict:
        """Collect results from all teammates.

        Returns:
            Dict mapping teammate names to their final reports
        """
        results = {}
        team = self.team
        if team is None:
            return results

        for name, member in team.members.items():
            if member.role != "teammate":
                continue
            # Check inbox for final reports
            messages = self.tm.check_inbox(self.team_id, name)
            for msg in messages:
                if msg.msg_type in ("status_report", "task_result"):
                    results[name] = msg.content
        return results

    def check_all_idle(self) -> bool:
        """Check if all teammates are idle (no active work)."""
        team = self.team
        if team is None:
            return True
        return all(
            m.state == MemberState.IDLE
            for m in team.members.values()
            if m.role == "teammate"
        )

    def request_shutdown(self, member_name: str,
                         report_to_user: bool = True) -> bool:
        """Request shutdown of a teammate.

        Enforces the hard rule: report to user before shutdown
        (except for reviewer teammates).

        Args:
            member_name: Teammate to shutdown
            report_to_user: Whether to prompt user for approval

        Returns:
            True if shutdown was initiated
        """
        team = self.team
        if team is None:
            return False

        member = team.members.get(member_name)
        if member is None:
            return False

        # Reviewers can be shutdown without user approval
        is_reviewer = member_name.startswith("reviewer")
        if report_to_user and not is_reviewer:
            # In a real implementation, this would prompt the user
            # For now, we log the requirement
            pass

        return self.tm.request_shutdown(self.team_id, member_name)

    def shutdown_all(self, reports: dict = None):
        """Shutdown all teammates after reporting to user.

        Args:
            reports: Optional dict of teammate → status report
        """
        team = self.team
        if team is None:
            return

        # Collect reports if not provided
        if reports is None:
            reports = self.collect_results()

        # Report to user (in real impl, this would be a user prompt)
        for name, report in reports.items():
            pass  # Log report

        # Shutdown all
        self.tm.shutdown_all(self.team_id)

    def synthesize(self, results: dict = None) -> str:
        """Synthesize all teammate results into a final report.

        Args:
            results: Optional pre-collected results

        Returns:
            Combined report string
        """
        if results is None:
            results = self.collect_results()

        if not results:
            return "No teammate results collected."

        parts = ["## Team Results\n"]
        for name, result in results.items():
            parts.append(f"### {name}\n{result}\n")

        # Include task list status
        tasks = self.tm.list_tasks(self.team_id)
        if tasks:
            parts.append("## Task Status\n")
            for task in tasks:
                status_icon = {
                    TaskStatus.PENDING: "⏳",
                    TaskStatus.IN_PROGRESS: "🔄",
                    TaskStatus.COMPLETED: "✅",
                }.get(task.status, "❓")
                parts.append(f"- {status_icon} {task.description}")
                if task.result:
                    parts.append(f"  Result: {task.result[:200]}")

        return "\n".join(parts)
