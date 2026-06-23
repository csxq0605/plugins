"""Inbox sync protocol — file-based messaging between teammates.

Implements the inbox sync protocol from team-coord:
- File-based inbox per team member
- Atomic write (write to temp + rename)
- check_and_drain() for the "read to check, not to act" pattern
- Two trigger points: after each step, before SendMessage

The inbox is a JSON file at ~/.nexgent/teams/{team_id}/inbox/{member_name}.json.
Messages are appended atomically; drain reads and clears in one operation.
"""

import json
import os
import time
import uuid
import threading
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class InboxMessage:
    """A single message in a teammate's inbox."""
    msg_id: str
    sender: str
    content: str
    msg_type: str  # "message", "status_report", "task_result", "shutdown_request"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "msg_id": self.msg_id,
            "sender": self.sender,
            "content": self.content,
            "msg_type": self.msg_type,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InboxMessage":
        return cls(
            msg_id=data["msg_id"],
            sender=data["sender"],
            content=data["content"],
            msg_type=data.get("msg_type", "message"),
            timestamp=data.get("timestamp", 0),
        )


class TeamInbox:
    """File-based inbox for a team member.

    Supports the inbox sync protocol:
    - send(): atomic write to target's inbox file
    - check_and_drain(): read all pending messages and clear the file
    - has_messages(): non-blocking check for pending messages

    Thread-safe: all operations use a per-instance lock.
    Atomic writes: write to temp file + rename to prevent partial reads.
    """

    def __init__(self, team_id: str, member_name: str,
                 teams_dir: str = None):
        self.team_id = team_id
        self.member_name = member_name
        base = teams_dir or os.path.join(os.path.expanduser("~"), ".nexgent", "teams")
        self._inbox_path = os.path.join(base, team_id, "inbox",
                                        f"{member_name}.json")
        self._lock = threading.Lock()
        # Ensure inbox directory exists
        os.makedirs(os.path.dirname(self._inbox_path), exist_ok=True)
        # Initialize empty inbox if not exists
        if not os.path.exists(self._inbox_path):
            self._write_file([])

    def _read_file(self) -> list[dict]:
        """Read inbox file (caller must hold lock or be in init)."""
        try:
            with open(self._inbox_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_file(self, messages: list[dict]):
        """Atomic write: write to temp + rename."""
        tmp_path = self._inbox_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        # Atomic rename (on most OSes)
        if os.path.exists(self._inbox_path):
            os.replace(tmp_path, self._inbox_path)
        else:
            os.rename(tmp_path, self._inbox_path)

    def send(self, sender: str, content: str,
             msg_type: str = "message") -> InboxMessage:
        """Send a message to this inbox (atomic write).

        Args:
            sender: Name of the sending agent
            content: Message content
            msg_type: Type of message (message, status_report, etc.)

        Returns:
            The created InboxMessage
        """
        msg = InboxMessage(
            msg_id=str(uuid.uuid4())[:8],
            sender=sender,
            content=content,
            msg_type=msg_type,
        )
        with self._lock:
            messages = self._read_file()
            messages.append(msg.to_dict())
            self._write_file(messages)
        return msg

    def check_and_drain(self) -> list[InboxMessage]:
        """Check and drain all pending messages.

        This is the core of the inbox sync protocol:
        - Read all pending messages
        - Clear the inbox file atomically
        - Return the messages for processing

        "Read to check, not to act" — caller should collect messages
        first, then process them one by one.

        Returns:
            List of pending InboxMessage objects (empty if none).
        """
        with self._lock:
            raw_messages = self._read_file()
            if not raw_messages:
                return []
            # Clear inbox atomically
            self._write_file([])
            return [InboxMessage.from_dict(m) for m in raw_messages]

    def has_messages(self) -> bool:
        """Non-blocking check for pending messages.

        Returns:
            True if there are pending messages.
        """
        with self._lock:
            messages = self._read_file()
            return len(messages) > 0

    def peek(self) -> Optional[InboxMessage]:
        """Peek at the next message without removing it.

        Returns:
            The next InboxMessage, or None if empty.
        """
        with self._lock:
            messages = self._read_file()
            if messages:
                return InboxMessage.from_dict(messages[0])
        return None

    def message_count(self) -> int:
        """Count pending messages."""
        with self._lock:
            return len(self._read_file())

    def clear(self):
        """Clear all messages without reading."""
        with self._lock:
            self._write_file([])


class InboxManager:
    """Manages inboxes for all members of a team.

    Provides a centralized way to:
    - Get or create an inbox for a team member
    - Send messages between team members
    - List all inboxes in a team
    """

    def __init__(self, team_id: str, teams_dir: str = None):
        self.team_id = team_id
        self._teams_dir = teams_dir
        self._inboxes: dict[str, TeamInbox] = {}
        self._lock = threading.Lock()

    def get_inbox(self, member_name: str) -> TeamInbox:
        """Get or create an inbox for a team member."""
        with self._lock:
            if member_name not in self._inboxes:
                self._inboxes[member_name] = TeamInbox(
                    team_id=self.team_id,
                    member_name=member_name,
                    teams_dir=self._teams_dir,
                )
            return self._inboxes[member_name]

    def send_to(self, sender: str, recipient: str, content: str,
                msg_type: str = "message") -> InboxMessage:
        """Send a message from one team member to another.

        Args:
            sender: Name of the sending agent
            recipient: Name of the receiving agent
            content: Message content
            msg_type: Type of message

        Returns:
            The created InboxMessage
        """
        inbox = self.get_inbox(recipient)
        return inbox.send(sender, content, msg_type)

    def drain_all(self, member_name: str) -> list[InboxMessage]:
        """Drain all messages for a specific member."""
        inbox = self.get_inbox(member_name)
        return inbox.check_and_drain()

    def get_all_member_names(self) -> list[str]:
        """Get all member names that have inboxes."""
        inbox_dir = os.path.join(
            self._teams_dir or os.path.join(os.path.expanduser("~"), ".nexgent", "teams"),
            self.team_id, "inbox"
        )
        if not os.path.exists(inbox_dir):
            return []
        return [
            f.replace(".json", "")
            for f in os.listdir(inbox_dir)
            if f.endswith(".json") and not f.startswith(".")
        ]
