"""
dep-audit Nexgent Plugin
Dependency vulnerability audit — OSV database queries, outdated detection, license risk assessment.
"""

from .audit_tools import get_tools, get_permissions, call_tool

__all__ = ["get_tools", "get_permissions", "call_tool"]
