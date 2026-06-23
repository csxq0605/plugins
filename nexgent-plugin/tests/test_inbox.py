"""Tests for inbox.py — inbox sync protocol."""

import os
import tempfile
import shutil
import threading
import pytest

from inbox import TeamInbox, InboxManager, InboxMessage


@pytest.fixture
def temp_teams_dir():
    """Create a temporary teams directory."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def inbox(temp_teams_dir):
    """Create a test inbox."""
    return TeamInbox(
        team_id="test-team",
        member_name="worker-1",
        teams_dir=temp_teams_dir,
    )


# ---------------------------------------------------------------------------
# TeamInbox tests
# ---------------------------------------------------------------------------

class TestTeamInbox:
    def test_send_and_drain(self, inbox):
        msg = inbox.send("lead", "Hello!", "message")
        assert msg.sender == "lead"
        assert msg.content == "Hello!"

        messages = inbox.check_and_drain()
        assert len(messages) == 1
        assert messages[0].content == "Hello!"

        # Inbox should be empty after drain
        assert inbox.check_and_drain() == []

    def test_multiple_messages(self, inbox):
        inbox.send("lead", "Msg 1", "message")
        inbox.send("lead", "Msg 2", "message")
        inbox.send("lead", "Msg 3", "status_report")

        messages = inbox.check_and_drain()
        assert len(messages) == 3
        assert [m.content for m in messages] == ["Msg 1", "Msg 2", "Msg 3"]

    def test_has_messages(self, inbox):
        assert not inbox.has_messages()

        inbox.send("lead", "Hello!", "message")
        assert inbox.has_messages()

        inbox.check_and_drain()
        assert not inbox.has_messages()

    def test_peek(self, inbox):
        assert inbox.peek() is None

        inbox.send("lead", "Hello!", "message")
        peeked = inbox.peek()
        assert peeked is not None
        assert peeked.content == "Hello!"

        # Peek doesn't remove
        assert inbox.has_messages()

    def test_message_count(self, inbox):
        assert inbox.message_count() == 0

        inbox.send("lead", "Msg 1", "message")
        inbox.send("lead", "Msg 2", "message")
        assert inbox.message_count() == 2

        inbox.check_and_drain()
        assert inbox.message_count() == 0

    def test_clear(self, inbox):
        inbox.send("lead", "Msg 1", "message")
        inbox.send("lead", "Msg 2", "message")

        inbox.clear()
        assert inbox.message_count() == 0
        assert inbox.check_and_drain() == []

    def test_persistence(self, temp_teams_dir):
        """Inbox should persist across instances."""
        inbox1 = TeamInbox("test-team", "worker-1", temp_teams_dir)
        inbox1.send("lead", "Persistent msg", "message")

        # Create new instance — should load from disk
        inbox2 = TeamInbox("test-team", "worker-1", temp_teams_dir)
        messages = inbox2.check_and_drain()
        assert len(messages) == 1
        assert messages[0].content == "Persistent msg"

    def test_separate_inboxes(self, temp_teams_dir):
        """Different members have separate inboxes."""
        inbox_a = TeamInbox("test-team", "worker-a", temp_teams_dir)
        inbox_b = TeamInbox("test-team", "worker-b", temp_teams_dir)

        inbox_a.send("lead", "For A", "message")
        inbox_b.send("lead", "For B", "message")

        msgs_a = inbox_a.check_and_drain()
        msgs_b = inbox_b.check_and_drain()

        assert len(msgs_a) == 1
        assert msgs_a[0].content == "For A"
        assert len(msgs_b) == 1
        assert msgs_b[0].content == "For B"

    def test_concurrent_sends(self, inbox):
        """Multiple threads sending concurrently should not lose messages."""
        def send_messages(sender, count):
            for i in range(count):
                inbox.send(sender, f"{sender}-msg-{i}", "message")

        threads = [
            threading.Thread(target=send_messages, args=("sender-1", 10)),
            threading.Thread(target=send_messages, args=("sender-2", 10)),
            threading.Thread(target=send_messages, args=("sender-3", 10)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        messages = inbox.check_and_drain()
        assert len(messages) == 30


# ---------------------------------------------------------------------------
# InboxMessage tests
# ---------------------------------------------------------------------------

class TestInboxMessage:
    def test_to_dict_roundtrip(self):
        msg = InboxMessage(
            msg_id="test-001",
            sender="lead",
            content="Hello!",
            msg_type="message",
            timestamp=1234567890.0,
        )
        d = msg.to_dict()
        assert d["msg_id"] == "test-001"
        assert d["sender"] == "lead"

        restored = InboxMessage.from_dict(d)
        assert restored.msg_id == "test-001"
        assert restored.content == "Hello!"


# ---------------------------------------------------------------------------
# InboxManager tests
# ---------------------------------------------------------------------------

class TestInboxManager:
    def test_send_to(self, temp_teams_dir):
        manager = InboxManager("test-team", temp_teams_dir)
        msg = manager.send_to("lead", "worker-1", "Hello!", "message")
        assert msg.sender == "lead"

        messages = manager.drain_all("worker-1")
        assert len(messages) == 1
        assert messages[0].content == "Hello!"

    def test_get_inbox_reuses(self, temp_teams_dir):
        manager = InboxManager("test-team", temp_teams_dir)
        inbox1 = manager.get_inbox("worker-1")
        inbox2 = manager.get_inbox("worker-1")
        assert inbox1 is inbox2  # Same instance

    def test_get_all_member_names(self, temp_teams_dir):
        manager = InboxManager("test-team", temp_teams_dir)
        manager.get_inbox("worker-1")
        manager.get_inbox("worker-2")

        names = manager.get_all_member_names()
        assert "worker-1" in names
        assert "worker-2" in names
