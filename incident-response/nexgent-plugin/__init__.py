"""Incident Response plugin for Nexgent.

Structured incident handling: triage, diagnose, fix, verify, postmortem.
Timeline tracking, root cause analysis, and automated postmortem generation.
"""

try:
    from .ir_tools import get_tools, get_permissions, call_tool
except ImportError:
    from ir_tools import get_tools, get_permissions, call_tool

__all__ = ["get_tools", "get_permissions", "call_tool"]
