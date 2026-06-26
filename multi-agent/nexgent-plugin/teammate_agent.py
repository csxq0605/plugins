"""TeammateAgent — teammate role wrapper.

Encapsulates teammate-specific operations: inbox sync protocol,
task claiming, completion reporting. Enforces the "read to check,
not to act" pattern and the two-trigger-point sync protocol.
"""

import time
from typing import Optional, Any

try:
    from .team_core import (
        TeamConfig, TeamMember, MemberState,
        TeamTask, TaskStatus,
    )
    from .team_manager import TeamManager
    from .inbox import InboxMessage
except ImportError:
    from team_core import (
        TeamConfig, TeamMember, MemberState,
        TeamTask, TaskStatus,
    )
    from team_manager import TeamManager
    from inbox import InboxMessage


class TeammateAgent:
    """Teammate role — works on tasks with inbox sync protocol.

    Usage:
        teammate = TeammateAgent(team_manager, team_id, "implementer-1")
        messages = teammate.sync_inbox()  # check before starting
        task = teammate.claim_next_task()
        # ... do work ...
        teammate.complete_and_report(task.task_id, "Done, here's the result")
        messages = teammate.sync_inbox()  # check before sending
        teammate.report_to_lead("All tasks complete")
    """

    def __init__(self, team_manager: TeamManager, team_id: str, name: str):
        self.tm = team_manager
        self.team_id = team_id
        self.name = name

    @property
    def member(self) -> Optional[TeamMember]:
        return self.tm.get_teammate(self.team_id, self.name)

    # ------------------------------------------------------------------
    # Inbox sync protocol (two trigger points)
    # ------------------------------------------------------------------

    def sync_inbox(self) -> list[InboxMessage]:
        """Check and drain inbox — the core of the sync protocol.

        Call this at two trigger points:
        1. After completing a work step
        2. Before initiating any SendMessage

        Returns:
            List of pending messages (may be empty).

        Note: "Read to check, not to act" — collect messages first,
        then process them one by one. Don't process inline during drain.
        """
        return self.tm.check_inbox(self.team_id, self.name)

    def has_messages(self) -> bool:
        """Non-blocking check for pending messages."""
        return self.tm.has_messages(self.team_id, self.name)

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def claim_next_task(self) -> Optional[TeamTask]:
        """Claim the next available task from the shared task list.

        A task is available if:
        - status is PENDING
        - not assigned to anyone
        - all dependencies are COMPLETED

        Returns:
            The claimed task, or None if no tasks available
        """
        self.sync_inbox()  # Sync before claiming
        task = self.tm.claim_task(self.team_id, self.name)
        if task:
            self.tm.set_teammate_state(
                self.team_id, self.name, MemberState.WORKING
            )
        return task

    def complete_task(self, task_id: str, result: str = None):
        """Mark a task as completed.

        Args:
            task_id: Task to complete
            result: Optional result description
        """
        self.tm.complete_task(self.team_id, task_id, result)
        self.tm.set_teammate_state(
            self.team_id, self.name, MemberState.IDLE
        )

    def complete_and_report(self, task_id: str, result: str = None):
        """Complete a task and report to lead in one operation.

        This is a convenience method that:
        1. Syncs inbox
        2. Marks task complete
        3. Sends result to lead
        4. Syncs inbox again (in case lead sent something while we worked)
        """
        self.sync_inbox()
        self.complete_task(task_id, result)
        self.report_to_lead(
            f"Task {task_id} completed.\nResult: {result or '(no result)'}",
            msg_type="task_result",
        )
        self.sync_inbox()

    # ------------------------------------------------------------------
    # Communication (hub-and-spoke via lead)
    # ------------------------------------------------------------------

    def report_to_lead(self, content: str,
                       msg_type: str = "status_report"):
        """Send a status report to the lead.

        Always syncs inbox before sending (trigger point 2).
        """
        self.sync_inbox()  # Trigger point 2: before SendMessage
        self.tm.send_message(
            self.team_id, self.name, "lead", content, msg_type
        )

    def send_to_teammate(self, recipient: str, content: str,
                         msg_type: str = "message"):
        """Send a message to another teammate (via lead routing).

        Note: In hub-and-spoke topology, this goes through the lead.
        For now, we send directly but the lead can intercept if needed.
        """
        self.sync_inbox()  # Trigger point 2: before SendMessage
        self.tm.send_message(
            self.team_id, self.name, recipient, content, msg_type
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def mark_idle(self):
        """Mark self as idle (after completing all tasks)."""
        self.tm.set_teammate_state(
            self.team_id, self.name, MemberState.IDLE
        )

    def mark_working(self):
        """Mark self as working."""
        self.tm.set_teammate_state(
            self.team_id, self.name, MemberState.WORKING
        )

    def is_shutdown_requested(self) -> bool:
        """Check if a shutdown request has been received."""
        messages = self.sync_inbox()
        return any(m.msg_type == "shutdown_request" for m in messages)

    def final_report(self, summary: str):
        """Send final report to lead before going idle.

        This is the last thing a teammate does before waiting for shutdown:
        1. Final inbox check
        2. Send summary to lead
        3. Mark as idle
        """
        # Final inbox check
        self.sync_inbox()

        # Send summary
        self.report_to_lead(summary, msg_type="status_report")

        # Mark idle — wait for lead to shutdown
        self.mark_idle()

    # ------------------------------------------------------------------
    # Workflow integration helpers
    # ------------------------------------------------------------------

    def get_pending_messages(self) -> list[InboxMessage]:
        """Get all pending messages without draining (for inspection)."""
        return self.sync_inbox()

    def process_messages(self, messages: list[InboxMessage]) -> list[dict]:
        """Process a list of messages and return actions needed.

        This is the "collect first, process second" pattern.
        Returns a list of action dicts for the caller to execute.
        """
        actions = []
        for msg in messages:
            if msg.msg_type == "shutdown_request":
                actions.append({
                    "type": "shutdown",
                    "sender": msg.sender,
                    "content": msg.content,
                })
            elif msg.msg_type == "task_assignment":
                actions.append({
                    "type": "task_assignment",
                    "sender": msg.sender,
                    "content": msg.content,
                })
            elif msg.msg_type == "message":
                actions.append({
                    "type": "message",
                    "sender": msg.sender,
                    "content": msg.content,
                })
            else:
                actions.append({
                    "type": msg.msg_type,
                    "sender": msg.sender,
                    "content": msg.content,
                })
        return actions
