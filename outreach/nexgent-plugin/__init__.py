"""
Outreach Plugin for Nexgent
学术套磁全流程自动化
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

__all__ = [
    "outreach_parse_materials",
    "outreach_list_profiles",
    "outreach_research_professor",
    "outreach_get_research",
    "outreach_generate_report",
    "outreach_generate_email",
    "outreach_list_professors"
]
