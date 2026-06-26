"""Tests for outreach tools."""

import pytest
import sys
import tempfile
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import directly from the module file
import importlib.util
spec = importlib.util.spec_from_file_location("outreach_tools", os.path.join(parent_dir, "outreach_tools.py"))
outreach_tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(outreach_tools)

outreach_parse_materials = outreach_tools.outreach_parse_materials
outreach_list_profiles = outreach_tools.outreach_list_profiles
outreach_research_professor = outreach_tools.outreach_research_professor
outreach_get_research = outreach_tools.outreach_get_research
outreach_generate_report = outreach_tools.outreach_generate_report
outreach_generate_email = outreach_tools.outreach_generate_email
outreach_list_professors = outreach_tools.outreach_list_professors

# Import email tools for sending test
email_spec = importlib.util.spec_from_file_location("email_tools", os.path.join(parent_dir, "email_tools.py"))
email_tools = importlib.util.module_from_spec(email_spec)
email_spec.loader.exec_module(email_tools)

email_is_configured = email_tools.email_is_configured
email_setup = email_tools.email_setup
email_send = email_tools.email_send
email_list = email_tools.email_list


class TestMaterialParsing:
    """Test material parsing functions."""

    def test_parse_materials_md(self):
        """Test parsing markdown materials."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("# John Doe\n\nEmail: john@example.com\nSchool: MIT\nGPA: 3.9/4.0\n\nResearch: machine learning")
            tmpfile = f.name

        try:
            result = outreach_parse_materials(file_path=tmpfile)
            assert result["success"] is True
            assert "extracted_info" in result
            assert result["extracted_info"]["GPA"] == "3.9/4.0"
        finally:
            os.unlink(tmpfile)

    def test_list_profiles(self):
        """Test listing profiles."""
        result = outreach_list_profiles()
        assert result["success"] is True
        assert "count" in result
        assert "profiles" in result


class TestProfessorResearch:
    """Test professor research functions."""

    def test_research_professor(self):
        """Test researching a professor."""
        result = outreach_research_professor(
            name="Test Professor",
            school="TestSchool",
            dept="CS",
            homepage="https://example.com",
            email="prof@example.com",
            research_keywords="AI, ML"
        )
        assert result["success"] is True
        assert "research_path" in result

    def test_get_research(self):
        """Test getting research report."""
        # First create a research
        outreach_research_professor(
            name="Get Test Prof",
            school="GetTest",
            dept="CS"
        )

        result = outreach_get_research(school="GetTest", dept="CS", professor="Get Test Prof")
        assert result["success"] is True
        assert "content" in result

    def test_list_professors(self):
        """Test listing professors."""
        result = outreach_list_professors()
        assert result["success"] is True
        assert "count" in result
        assert "professors" in result


class TestReportGeneration:
    """Test report generation functions."""

    def test_generate_report(self):
        """Test generating HTML report."""
        # First create a research
        outreach_research_professor(
            name="Report Test Prof",
            school="ReportTest",
            dept="CS"
        )

        result = outreach_generate_report(school="ReportTest", dept="CS")
        assert result["success"] is True
        assert "report_path" in result


class TestEmailGeneration:
    """Test email generation functions."""

    def test_generate_email(self):
        """Test generating email draft."""
        # First create a research
        outreach_research_professor(
            name="Email Test Prof",
            school="EmailTest",
            dept="CS"
        )

        result = outreach_generate_email(school="EmailTest", dept="CS", professor="Email Test Prof")
        assert result["success"] is True
        assert "email_path" in result
        assert "template" in result


class TestFullWorkflow:
    """Test full outreach workflow with real email."""

    def test_full_workflow_with_email(self):
        """Test complete workflow: parse -> research -> report -> email -> send."""
        # Check email config
        config_check = email_is_configured()
        if not config_check["configured"]:
            pytest.skip("Email not configured, skipping full workflow test")

        import time
        unique_id = str(int(time.time()))

        # 1. Parse materials
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(f"# Test User {unique_id}\n\nEmail: wsu0605@stu.pku.edu.cn\nSchool: PKU\nGPA: 3.8/4.0\n\nResearch: NLP, LLM")
            tmpfile = f.name

        try:
            parse_result = outreach_parse_materials(file_path=tmpfile)
            assert parse_result["success"] is True
        finally:
            os.unlink(tmpfile)

        # 2. Research professor
        research_result = outreach_research_professor(
            name=f"Workflow Test Prof {unique_id}",
            school="WorkflowTest",
            dept="CS",
            homepage="https://example.com",
            email="prof@example.com",
            research_keywords="NLP, Transformers"
        )
        assert research_result["success"] is True

        # 3. Generate report
        report_result = outreach_generate_report(school="WorkflowTest", dept="CS")
        assert report_result["success"] is True

        # 4. Generate email
        email_result = outreach_generate_email(
            school="WorkflowTest",
            dept="CS",
            professor=f"Workflow Test Prof {unique_id}"
        )
        assert email_result["success"] is True

        # 5. Send test email to self
        subject = f"Workflow Self-Test {unique_id}"
        body = f"This is a workflow self-test.\n\nUnique ID: {unique_id}\n\nProfessor: Workflow Test Prof {unique_id}\n\nSent at: {time.strftime('%Y-%m-%d %H:%M:%S')}"

        send_result = email_send(
            to="wsu0605@stu.pku.edu.cn",
            subject=subject,
            body=body
        )
        assert send_result["success"] is True

        # 6. Verify receipt
        time.sleep(3)
        list_result = email_list(folder="INBOX", limit=10)
        assert list_result["success"] is True

        found = False
        for e in list_result.get("emails", []):
            if subject in e.get("subject", ""):
                found = True
                break

        assert found, f"Sent email with subject '{subject}' not found in inbox"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
