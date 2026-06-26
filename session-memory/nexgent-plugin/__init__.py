"""
session-memory Nexgent Plugin
Persistent cross-session memory — save and restore context, decisions, findings, handoffs.
"""

try:
    from .memory_tools import get_tools, get_permissions, call_tool
except ImportError:
    from memory_tools import get_tools, get_permissions, call_tool

__all__ = ["get_tools", "get_permissions", "call_tool"]
