"""Team core data structures — TeamConfig, TeamMember, SharedTaskList, TeamTask.

Defines the data model for agent team coordination. These structures are
persisted to disk under .nexgent/teams/{team_id}/ (relative to working directory)
so that all agents in the team can access inbox files.
"""

import json
import os
import time
import uuid
import threading
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# Mutable module-level variable — monkeypatch in tests, e.g.:
#   monkeypatch.setattr("team_core.TEAMS_DIR", temp_dir)
# Uses ~/.nexgent/teams/ to match Nexgent's home directory structure
TEAMS_DIR = os.path.join(os.path.expanduser("~"), ".nexgent", "teams")


def get_teams_dir() -> str:
    """Get teams directory — uses TEAMS_DIR (monkeypatchable)."""
    return TEAMS_DIR


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class TeamState(Enum):
    """Team lifecycle states."""
    ACTIVE = "active"
    SHUTTING_DOWN = "shutting_down"
    CLOSED = "closed"


class MemberState(Enum):
    """Teammate lifecycle states."""
    IDLE = "idle"
    WORKING = "working"
    SHUTDOWN = "shutdown"


class TaskStatus(Enum):
    """Shared task statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class TeamMember:
    """A member of the team (lead or teammate)."""
    name: str
    agent_id: str
    session_id: str
    role: str  # "lead" or "teammate"
    state: MemberState = MemberState.IDLE
    worktree_path: Optional[str] = None
    spawned_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "role": self.role,
            "state": self.state.value,
            "worktree_path": self.worktree_path,
            "spawned_at": self.spawned_at,
            "last_active": self.last_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TeamMember":
        return cls(
            name=data["name"],
            agent_id=data["agent_id"],
            session_id=data["session_id"],
            role=data["role"],
            state=MemberState(data["state"]),
            worktree_path=data.get("worktree_path"),
            spawned_at=data.get("spawned_at", 0),
            last_active=data.get("last_active", 0),
        )


@dataclass
class TeamTask:
    """A task in the shared task list."""
    task_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    depends_on: list[str] = field(default_factory=list)
    created_by: str = ""
    result: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "depends_on": self.depends_on,
            "created_by": self.created_by,
            "result": self.result,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TeamTask":
        return cls(
            task_id=data["task_id"],
            description=data["description"],
            status=TaskStatus(data["status"]),
            assigned_to=data.get("assigned_to"),
            depends_on=data.get("depends_on", []),
            created_by=data.get("created_by", ""),
            result=data.get("result"),
            created_at=data.get("created_at", 0),
            completed_at=data.get("completed_at"),
        )


@dataclass
class TeamConfig:
    """Team configuration and state."""
    team_id: str
    team_name: str
    lead_session_id: str
    members: dict[str, TeamMember] = field(default_factory=dict)
    state: TeamState = TeamState.ACTIVE
    created_at: float = field(default_factory=time.time)

    @property
    def config_dir(self) -> str:
        return os.path.join(get_teams_dir(), self.team_id)

    @property
    def config_path(self) -> str:
        return os.path.join(self.config_dir, "config.json")

    @property
    def tasks_path(self) -> str:
        return os.path.join(self.config_dir, "tasks.json")

    @property
    def inbox_dir(self) -> str:
        return os.path.join(self.config_dir, "inbox")

    def to_dict(self) -> dict:
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "lead_session_id": self.lead_session_id,
            "members": {name: m.to_dict() for name, m in self.members.items()},
            "state": self.state.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TeamConfig":
        members = {}
        for name, m_data in data.get("members", {}).items():
            members[name] = TeamMember.from_dict(m_data)
        return cls(
            team_id=data["team_id"],
            team_name=data["team_name"],
            lead_session_id=data["lead_session_id"],
            members=members,
            state=TeamState(data["state"]),
            created_at=data.get("created_at", 0),
        )

    def save(self):
        """Persist team config to disk."""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, team_id: str) -> Optional["TeamConfig"]:
        """Load team config from disk."""
        path = os.path.join(get_teams_dir(), team_id, "config.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def delete(self):
        """Remove team config directory from disk."""
        import shutil
        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)


class SharedTaskList:
    """Thread-safe shared task list with file persistence.

    Tasks are stored in a JSON file under the team's config directory.
    File locking prevents race conditions when multiple teammates
    try to claim the same task simultaneously.
    """

    def __init__(self, team_config: TeamConfig):
        self._config = team_config
        self._tasks: dict[str, TeamTask] = {}
        self._lock = threading.Lock()
        self._file_lock_path = os.path.join(team_config.config_dir, ".tasks.lock")
        self._load()

    def _load(self):
        """Load tasks from disk."""
        path = self._config.tasks_path
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for t_data in data.get("tasks", []):
                task = TeamTask.from_dict(t_data)
                self._tasks[task.task_id] = task

    def _save(self):
        """Persist tasks to disk."""
        os.makedirs(self._config.config_dir, exist_ok=True)
        data = {"tasks": [t.to_dict() for t in self._tasks.values()]}
        with open(self._config.tasks_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_task(self, description: str, created_by: str = "",
                 depends_on: list[str] = None) -> TeamTask:
        """Add a new task to the list."""
        task_id = str(uuid.uuid4())[:8]
        task = TeamTask(
            task_id=task_id,
            description=description,
            created_by=created_by,
            depends_on=depends_on or [],
        )
        with self._lock:
            self._tasks[task_id] = task
            self._save()
        return task

    def claim_task(self, claimer: str) -> Optional[TeamTask]:
        """Claim the next available task (atomic with file lock).

        A task is available if:
        - status is PENDING
        - assigned_to is None
        - all dependencies are COMPLETED

        Returns the claimed task, or None if no tasks are available.
        """
        with self._lock:
            for task in self._tasks.values():
                if task.status != TaskStatus.PENDING:
                    continue
                if task.assigned_to is not None:
                    continue
                # Check dependencies
                deps_met = all(
                    self._tasks.get(dep_id) is not None
                    and self._tasks[dep_id].status == TaskStatus.COMPLETED
                    for dep_id in task.depends_on
                )
                if not deps_met:
                    continue
                # Claim it
                task.assigned_to = claimer
                task.status = TaskStatus.IN_PROGRESS
                self._save()
                return task
        return None

    def complete_task(self, task_id: str, result: str = None) -> bool:
        """Mark a task as completed."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = time.time()
            self._save()
        return True

    def get_task(self, task_id: str) -> Optional[TeamTask]:
        """Get a task by ID."""
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(self, status: TaskStatus = None,
                   assigned_to: str = None) -> list[TeamTask]:
        """List tasks with optional filters."""
        with self._lock:
            tasks = list(self._tasks.values())
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        if assigned_to is not None:
            tasks = [t for t in tasks if t.assigned_to == assigned_to]
        return tasks

    def get_pending_count(self) -> int:
        """Count unblocked pending tasks."""
        with self._lock:
            return sum(
                1 for t in self._tasks.values()
                if t.status == TaskStatus.PENDING and t.assigned_to is None
            )

    def all_completed(self) -> bool:
        """Check if all tasks are completed."""
        with self._lock:
            return all(
                t.status == TaskStatus.COMPLETED
                for t in self._tasks.values()
            )


def create_team_id() -> str:
    """Generate a unique team ID."""
    return f"team-{uuid.uuid4().hex[:8]}"
