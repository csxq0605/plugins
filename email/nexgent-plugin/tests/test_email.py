"""Tests for email tools."""

import pytest
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import directly from the module file
import importlib.util
spec = importlib.util.spec_from_file_location("email_tools", os.path.join(parent_dir, "email_tools.py"))
email_tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(email_tools)

email_is_configured = email_tools.email_is_configured
email_get_presets = email_tools.email_get_presets
email_setup = email_tools.email_setup
email_test = email_tools.email_test
email_get_config = email_tools.email_get_config
email_send = email_tools.email_send
email_list = email_tools.email_list
email_read = email_tools.email_read
email_search = email_tools.email_search


class TestEmailConfig:
    """Test email configuration functions."""

    def test_email_is_configured(self):
        """Test email_is_configured function."""
        result = email_is_configured()
        assert "configured" in result
        assert isinstance(result["configured"], bool)

    def test_email_get_presets(self):
        """Test email_get_presets function."""
        result = email_get_presets()
        assert result["success"] is True
        assert "presets" in result
        assert "pku" in result["presets"]
        assert "gmail" in result["presets"]
        assert "outlook" in result["presets"]
        assert "qq" in result["presets"]
        assert "163" in result["presets"]

    def test_email_get_config(self):
        """Test email_get_config function."""
        result = email_get_config()
        # May or may not be configured
        assert "success" in result


class TestEmailSend:
    """Test email sending functions."""

    def test_send_dry_run(self):
        """Test email send with dry run."""
        result = email_send(
            to="test@example.com",
            subject="Test Subject",
            body="Test body",
            dry_run=True
        )
        assert result["success"] is True
        assert result["dry_run"] is True
        assert "preview" in result

    def test_send_real_email(self):
        """Test sending real email to self."""
        # Check if configured
        config_check = email_is_configured()
        if not config_check["configured"]:
            pytest.skip("Email not configured, skipping real send test")

        # Get config to know our email
        config = email_get_config()
        my_email = config["config"]["email"]

        # Send to self
        result = email_send(
            to=my_email,
            subject="Outreach Plugin Self-Test",
            body="This is an automated self-test from Outreach Plugin.\n\nIf you receive this, email sending is working correctly!"
        )

        assert result["success"] is True
        assert result["details"]["to"] == my_email
        assert result["details"]["subject"] == "Outreach Plugin Self-Test"

    def test_send_and_verify_receipt(self):
        """Test sending email and verifying receipt."""
        # Check if configured
        config_check = email_is_configured()
        if not config_check["configured"]:
            pytest.skip("Email not configured, skipping send/receive test")

        # Get config
        config = email_get_config()
        my_email = config["config"]["email"]

        # Send unique email
        import time
        unique_id = str(int(time.time()))
        subject = f"Self-Test {unique_id}"
        body = f"Unique ID: {unique_id}\n\nSent at: {time.strftime('%Y-%m-%d %H:%M:%S')}"

        send_result = email_send(
            to=my_email,
            subject=subject,
            body=body
        )

        assert send_result["success"] is True

        # Wait a bit for email to arrive
        time.sleep(3)

        # Check inbox for the email
        list_result = email_list(folder="INBOX", limit=10)
        assert list_result["success"] is True

        # Search for our email
        found = False
        for e in list_result.get("emails", []):
            if subject in e.get("subject", ""):
                found = True
                break

        assert found, f"Sent email with subject '{subject}' not found in inbox"


class TestEmailReceive:
    """Test email receiving functions."""

    def test_list_inbox(self):
        """Test listing inbox."""
        # Check if configured
        config_check = email_is_configured()
        if not config_check["configured"]:
            pytest.skip("Email not configured, skipping list test")

        result = email_list(folder="INBOX", limit=5)
        assert result["success"] is True
        assert "count" in result
        assert "emails" in result

    def test_list_unread(self):
        """Test listing unread emails."""
        config_check = email_is_configured()
        if not config_check["configured"]:
            pytest.skip("Email not configured, skipping unread test")

        result = email_list(folder="INBOX", unread_only=True, limit=5)
        assert result["success"] is True

    def test_search_emails(self):
        """Test searching emails."""
        config_check = email_is_configured()
        if not config_check["configured"]:
            pytest.skip("Email not configured, skipping search test")

        result = email_search(query="test", folder="INBOX", limit=5)
        assert result["success"] is True
        assert "count" in result

    def test_read_email(self):
        """Test reading specific email."""
        config_check = email_is_configured()
        if not config_check["configured"]:
            pytest.skip("Email not configured, skipping read test")

        # First list to get an email ID
        list_result = email_list(folder="INBOX", limit=1)
        if list_result["success"] and list_result["count"] > 0:
            email_id = list_result["emails"][0]["id"]
            read_result = email_read(email_id=email_id, folder="INBOX")
            assert read_result["success"] is True
            assert "email" in read_result
        else:
            pytest.skip("No emails in inbox to read")


class TestEmailConnection:
    """Test email connection."""

    def test_connection(self):
        """Test email connection."""
        config_check = email_is_configured()
        if not config_check["configured"]:
            pytest.skip("Email not configured, skipping connection test")

        result = email_test()
        assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
