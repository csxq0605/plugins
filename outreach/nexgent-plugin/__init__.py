"""
Outreach Plugin for Nexgent
学术套磁全流程自动化（含邮件功能）
"""

from .outreach_tools import (
    outreach_parse_materials,
    outreach_list_profiles,
    outreach_research_professor,
    outreach_get_research,
    outreach_generate_report,
    outreach_generate_email,
    outreach_list_professors
)

from .email_tools import (
    email_setup,
    email_get_config,
    email_send,
    email_send_batch,
    email_list,
    email_read,
    email_search
)

__all__ = [
    # Outreach tools
    "outreach_parse_materials",
    "outreach_list_profiles",
    "outreach_research_professor",
    "outreach_get_research",
    "outreach_generate_report",
    "outreach_generate_email",
    "outreach_list_professors",
    # Email tools
    "email_setup",
    "email_get_config",
    "email_send",
    "email_send_batch",
    "email_list",
    "email_read",
    "email_search"
]
