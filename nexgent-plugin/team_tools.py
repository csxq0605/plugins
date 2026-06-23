"""Team tools — Nexgent ToolRegistry integration.

Architecture:
- Only the LEAD can call team_create / team_spawn / team_shutdown / team_close
- All teammates have: inbox, tasks, report, request_subordinate
- Any teammate can request subordinates; lead decides whether to approve
"""

import json
from typing import Any


# Lazy-loaded TeamManager singleton — stored on the function itself
# so it persists across different module instances (plugin loaded from
# both project-level and user-level directories).
_lead_caller_id = "lead"


def _get_team_manager():
    if not hasattr(_get_team_manager, '_instance') or _get_team_manager._instance is None:
        try:
            from .team_manager import TeamManager
        except ImportError:
            from team_manager import TeamManager
        _get_team_manager._instance = TeamManager()
    return _get_team_manager._instance


def _set_team_manager(tm):
    _get_team_manager._instance = tm


# ---------------------------------------------------------------------------
# Permission check: only lead can create/spawn
# ---------------------------------------------------------------------------

def _is_lead(params: dict) -> bool:
    """Check if the caller is the lead.

    team_create and team_spawn are ONLY callable by the lead.
    Managers must use team_request_subordinate instead.
    """
    caller = params.get("_caller_role", "lead")
    return caller == "lead"


# ---------------------------------------------------------------------------
# Tool handlers — LEAD ONLY
# ---------------------------------------------------------------------------

def _team_create(params: dict) -> str:
    """Create a new agent team. ONLY callable by the lead."""
    if not _is_lead(params):
        return json.dumps({
            "error": "Permission denied: only the lead can create teams. "
                     "Use team_request_subordinate to ask the lead to create one."
        })

    tm = _get_team_manager()
    name = params.get("name")
    team = tm.create_team(name)
    return json.dumps({
        "team_id": team.team_id,
        "team_name": team.team_name,
        "message": f"Team '{team.team_name}' created with ID {team.team_id}",
    })


def _team_spawn(params: dict) -> str:
    """Spawn a teammate. ONLY callable by the lead."""
    if not _is_lead(params):
        return json.dumps({
            "error": "Permission denied: only the lead can spawn teammates. "
                     "Use team_request_subordinate to ask the lead to spawn someone."
        })

    tm = _get_team_manager()
    team_id = params.get("team_id", "")
    name = params.get("name", "")
    task = params.get("task", "")
    role = params.get("role", "worker")
    model = params.get("model")
    worktree_path = params.get("worktree_path")
    effort = params.get("effort", "medium")

    if not team_id or not name or not task:
        return json.dumps({"error": "team_id, name, and task are required"})

    try:
        member = tm.spawn_teammate(
            team_id=team_id,
            name=name,
            task=task,
            role=role,
            model=model,
            worktree_path=worktree_path,
            effort=effort,
        )
        return json.dumps({
            "name": member.name,
            "agent_id": member.agent_id,
            "role": role,
            "state": member.state.value,
            "message": f"Teammate '{name}' (role={role}) spawned in team {team_id}",
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# Tool handlers — ANYONE (task-level operations)
# ---------------------------------------------------------------------------

def _team_send_message(params: dict) -> str:
    """Send a message to a team member. Callable by anyone."""
    tm = _get_team_manager()
    team_id = params.get("team_id", "")
    sender = params.get("sender", "lead")
    recipient = params.get("recipient", "")
    content = params.get("content", "")
    msg_type = params.get("msg_type", "message")

    if not team_id or not recipient or not content:
        return json.dumps({"error": "team_id, recipient, and content are required"})

    try:
        msg = tm.send_message(team_id, sender, recipient, content, msg_type)
        return json.dumps({
            "msg_id": msg.msg_id,
            "sender": sender,
            "recipient": recipient,
            "message": f"Message sent from {sender} to {recipient}",
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def _team_check_inbox(params: dict) -> str:
    """Check and drain a team member's inbox. Callable by anyone."""
    tm = _get_team_manager()
    team_id = params.get("team_id", "")
    member_name = params.get("member_name", "")

    if not team_id or not member_name:
        return json.dumps({"error": "team_id and member_name are required"})

    try:
        messages = tm.check_inbox(team_id, member_name)
        return json.dumps({
            "count": len(messages),
            "messages": [
                {
                    "msg_id": m.msg_id,
                    "sender": m.sender,
                    "content": m.content,
                    "msg_type": m.msg_type,
                    "timestamp": m.timestamp,
                }
                for m in messages
            ],
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def _team_add_task(params: dict) -> str:
    """Add a task to the shared task list. Callable by anyone."""
    tm = _get_team_manager()
    team_id = params.get("team_id", "")
    description = params.get("description", "")
    created_by = params.get("created_by", "lead")
    depends_on = params.get("depends_on", [])

    if not team_id or not description:
        return json.dumps({"error": "team_id and description are required"})

    try:
        task = tm.add_task(team_id, description, created_by, depends_on)
        return json.dumps({
            "task_id": task.task_id,
            "description": task.description,
            "message": f"Task added: {task.task_id}",
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def _team_list_tasks(params: dict) -> str:
    """List tasks. Callable by anyone."""
    tm = _get_team_manager()
    team_id = params.get("team_id", "")
    status_filter = params.get("status")

    if not team_id:
        return json.dumps({"error": "team_id is required"})

    try:
        from team_core import TaskStatus
        status = TaskStatus(status_filter) if status_filter else None
        tasks = tm.list_tasks(team_id, status=status)
        return json.dumps({
            "count": len(tasks),
            "tasks": [t.to_dict() for t in tasks],
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def _team_claim_task(params: dict) -> str:
    """Claim the next available task. Callable by anyone."""
    tm = _get_team_manager()
    team_id = params.get("team_id", "")
    claimer = params.get("claimer", "")

    if not team_id or not claimer:
        return json.dumps({"error": "team_id and claimer are required"})

    try:
        task = tm.claim_task(team_id, claimer)
        if task:
            return json.dumps({
                "task_id": task.task_id,
                "description": task.description,
                "status": task.status.value,
                "message": f"Task claimed by {claimer}",
            })
        return json.dumps({"task_id": None, "message": "No available tasks"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _team_complete_task(params: dict) -> str:
    """Mark a task as completed. Callable by anyone."""
    tm = _get_team_manager()
    team_id = params.get("team_id", "")
    task_id = params.get("task_id", "")
    result = params.get("result")

    if not team_id or not task_id:
        return json.dumps({"error": "team_id and task_id are required"})

    try:
        success = tm.complete_task(team_id, task_id, result)
        if success:
            return json.dumps({"task_id": task_id, "message": "Task completed"})
        return json.dumps({"error": f"Task not found: {task_id}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _team_report_status(params: dict) -> str:
    """Report status to the lead. Callable by anyone."""
    tm = _get_team_manager()
    team_id = params.get("team_id", "")
    sender = params.get("sender", "")
    content = params.get("content", "")

    if not team_id or not sender or not content:
        return json.dumps({"error": "team_id, sender, and content are required"})

    try:
        msg = tm.send_message(team_id, sender, "lead", content, "status_report")
        return json.dumps({"msg_id": msg.msg_id, "message": "Status reported to lead"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# Tool handler — MANAGER ONLY (request, not execute)
# ---------------------------------------------------------------------------

def _team_tool_search(params: dict) -> str:
    """Search for available team tools and return their schemas.

    Equivalent to Claude Code's ToolSearch — lets teammates discover
    what team coordination tools are available and how to use them.
    """
    tm = _get_team_manager()
    select = params.get("select", "")
    max_results = params.get("max_results", 10)

    # Get all available tools
    try:
        try:
            from .team_tools import get_tools
        except ImportError:
            from team_tools import get_tools
        all_tools = get_tools()
    except Exception:
        all_tools = []

    # Filter by select criteria if provided
    if select:
        selected_names = [s.strip() for s in select.split(",")]
        tools = [t for t in all_tools if t.name in selected_names]
    else:
        tools = all_tools

    tools = tools[:max_results]

    # Build result
    result = []
    for t in tools:
        if hasattr(t, 'name'):  # ToolDef object
            result.append({
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters if hasattr(t, 'parameters') else {},
            })
        elif isinstance(t, dict):  # Raw dict
            result.append({
                "name": t.get("name", ""),
                "description": t.get("description", ""),
                "parameters": t.get("parameters", {}),
            })

    return json.dumps({
        "count": len(result),
        "tools": result,
    })


def _team_request_subordinate(params: dict) -> str:
    """Request the lead to spawn a subordinate.

    This is the ONLY way a manager can get more team members.
    The lead evaluates the request and decides whether to approve.

    Callable by: managers (teammates with role="manager")
    """
    tm = _get_team_manager()
    team_id = params.get("team_id", "")
    requester = params.get("requester", "")
    requested_role = params.get("requested_role", "worker")
    requested_name = params.get("requested_name", "")
    task = params.get("task", "")
    reason = params.get("reason", "")

    if not team_id or not requester or not task:
        return json.dumps({"error": "team_id, requester, and task are required"})

    # Send request to lead via inbox
    request_content = json.dumps({
        "type": "subordinate_request",
        "requester": requester,
        "requested_name": requested_name,
        "requested_role": requested_role,
        "task": task,
        "reason": reason,
    }, ensure_ascii=False)

    tm.send_message(team_id, requester, "lead", request_content,
                    msg_type="subordinate_request")

    return json.dumps({
        "message": f"Subordinate request sent to lead. "
                   f"Waiting for approval. Requested: {requested_name or 'auto'} "
                   f"({requested_role}) for: {task[:100]}",
    })


def _team_shutdown(params: dict) -> str:
    """Shutdown a teammate. Callable by lead only."""
    if not _is_lead(params):
        return json.dumps({
            "error": "Permission denied: only the lead can shutdown teammates."
        })

    tm = _get_team_manager()
    team_id = params.get("team_id", "")
    member_name = params.get("member_name", "")

    if not team_id or not member_name:
        return json.dumps({"error": "team_id and member_name are required"})

    try:
        success = tm.request_shutdown(team_id, member_name)
        if success:
            return json.dumps({"member_name": member_name, "message": f"Shutdown requested for {member_name}"})
        return json.dumps({"error": f"Cannot shutdown {member_name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _team_close(params: dict) -> str:
    """Properly close a team: summarize, archive, cleanup.

    The lead calls this when all work is done:
    1. Collects final status from all teammates
    2. Archives important messages to ~/.nexgent/memory/
    3. Saves team summary
    4. Cleans up team directory
    """
    if not _is_lead(params):
        return json.dumps({
            "error": "Permission denied: only the lead can close teams."
        })

    tm = _get_team_manager()
    team_id = params.get("team_id", "")
    summary = params.get("summary")

    if not team_id:
        return json.dumps({"error": "team_id is required"})

    try:
        result = tm.close_team(team_id, summary)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})




# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

def get_tools() -> list:
    """Return team tool definitions for Nexgent's ToolRegistry."""
    try:
        from nexgent.tools.registry import ToolDef
        from nexgent.permissions import Permission
        _has_tooldef = True
    except ImportError:
        _has_tooldef = False

    tools_raw = [
        # ── LEAD ONLY ──────────────────────────────────────────────
        {
            "name": "team_close",
            "description": (
                "[LEAD ONLY] Properly close a team when all work is done. "
                "Summarizes results, archives important messages to memory, "
                "cleans up team directory."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "summary": {"type": "string", "description": "Summary of what the team accomplished"},
                },
                "required": ["team_id"],
            },
            "handler": _team_close,
            "permission": "write",
        },
        {
            "name": "team_create",
            "description": (
                "[LEAD ONLY] Create a new agent team. "
                "Only the lead agent can call this. "
                "Call when a task benefits from parallel agents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Team name"},
                },
            },
            "handler": _team_create,
            "permission": "write",
        },
        {
            "name": "team_spawn",
            "description": (
                "[LEAD ONLY] Spawn a teammate. You decide the role based on task complexity: "
                "'worker' for execution, 'manager' for coordination with subordinates."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "name": {"type": "string", "description": "Teammate name"},
                    "task": {"type": "string", "description": "Task (WHAT, not HOW)"},
                    "role": {"type": "string", "enum": ["worker", "manager"], "description": "worker=execute, manager=coordinate"},
                    "model": {"type": "string"},
                    "worktree_path": {"type": "string"},
                    "effort": {"type": "string"},
                },
                "required": ["team_id", "name", "task"],
            },
            "handler": _team_spawn,
            "permission": "write",
        },
        {
            "name": "team_shutdown",
            "description": "[LEAD ONLY] Request shutdown of a teammate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "member_name": {"type": "string"},
                },
                "required": ["team_id", "member_name"],
            },
            "handler": _team_shutdown,
            "permission": "write",
        },
        # ── ANYONE — coordination ─────────────────────────────────
        {
            "name": "team_tool_search",
            "description": (
                "Search for available team tools and return their schemas. "
                "Call this at startup to discover what team coordination tools "
                "are available and how to use them. Equivalent to ToolSearch."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "select": {"type": "string", "description": "Comma-separated tool names to look up (empty = all)"},
                    "max_results": {"type": "integer", "description": "Max tools to return (default 10)"},
                },
            },
            "handler": _team_tool_search,
            "permission": "read",
        },
        # ── ANYONE — messaging ────────────────────────────────────
        {
            "name": "team_send_message",
            "description": "Send a message to a team member. Callable by anyone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "sender": {"type": "string", "description": "Sender name"},
                    "recipient": {"type": "string", "description": "Recipient name"},
                    "content": {"type": "string"},
                    "msg_type": {"type": "string", "description": "message/status_report/task_result/shutdown_request"},
                },
                "required": ["team_id", "recipient", "content"],
            },
            "handler": _team_send_message,
            "permission": "write",
        },
        {
            "name": "team_check_inbox",
            "description": "Check and drain a team member's inbox. Callable by anyone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "member_name": {"type": "string"},
                },
                "required": ["team_id", "member_name"],
            },
            "handler": _team_check_inbox,
            "permission": "read",
        },
        {
            "name": "team_add_task",
            "description": "Add a task to the shared task list. Callable by anyone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "description": {"type": "string"},
                    "created_by": {"type": "string"},
                    "depends_on": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["team_id", "description"],
            },
            "handler": _team_add_task,
            "permission": "write",
        },
        {
            "name": "team_list_tasks",
            "description": "List tasks. Callable by anyone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "status": {"type": "string", "description": "pending/in_progress/completed"},
                },
                "required": ["team_id"],
            },
            "handler": _team_list_tasks,
            "permission": "read",
        },
        {
            "name": "team_claim_task",
            "description": "Claim the next available task. Callable by anyone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "claimer": {"type": "string"},
                },
                "required": ["team_id", "claimer"],
            },
            "handler": _team_claim_task,
            "permission": "write",
        },
        {
            "name": "team_complete_task",
            "description": "Mark a task as completed. Callable by anyone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "task_id": {"type": "string"},
                    "result": {"type": "string"},
                },
                "required": ["team_id", "task_id"],
            },
            "handler": _team_complete_task,
            "permission": "write",
        },
        {
            "name": "team_report_status",
            "description": "Report status to the lead. Callable by anyone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "sender": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["team_id", "sender", "content"],
            },
            "handler": _team_report_status,
            "permission": "write",
        },
        # ── MANAGER ONLY ───────────────────────────────────────────
        {
            "name": "team_request_subordinate",
            "description": (
                "Request the lead to spawn a subordinate worker for you. "
                "The lead evaluates the request and decides whether to approve. "
                "Use this when your task is too complex for you alone."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "requester": {"type": "string", "description": "Your name"},
                    "requested_name": {"type": "string", "description": "Suggested name for the subordinate"},
                    "requested_role": {"type": "string", "enum": ["worker", "manager"], "description": "Role for the subordinate"},
                    "task": {"type": "string", "description": "Task for the subordinate"},
                    "reason": {"type": "string", "description": "Why you need this subordinate"},
                },
                "required": ["team_id", "requester", "task"],
            },
            "handler": _team_request_subordinate,
            "permission": "write",
        },
    ]

    if _has_tooldef:
        perm_map = {"read": Permission.READ, "write": Permission.WRITE}
        return [
            ToolDef(
                name=t["name"],
                description=t["description"],
                parameters=t["parameters"],
                handler=t["handler"],
                permission=perm_map.get(t["permission"], Permission.WRITE),
                is_read_only=(t["permission"] == "read"),
                is_concurrency_safe=False,
            )
            for t in tools_raw
        ]

    return tools_raw


def get_lead_tools() -> list:
    """Return only the tools that the lead should have.

    When spawning a teammate, register ONLY the non-lead tools
    so teammates cannot call team_create/team_spawn/team_shutdown/team_delete.
    """
    all_tools = get_tools()
    lead_only = {"team_create", "team_spawn", "team_shutdown", "team_close"}
    return [t for t in all_tools if t.name not in lead_only]


def get_teammate_tools() -> list:
    """Return tools available to ALL teammates.

    Includes: inbox, tasks, report, request_subordinate.
    Excludes: lead-only (create, spawn, shutdown, delete).
    """
    all_tools = get_tools()
    lead_only = {"team_create", "team_spawn", "team_shutdown", "team_close"}
    return [t for t in all_tools if t.name not in lead_only]
