"""Literature Review plugin for Nexgent.

Multi-source academic search, citation network analysis,
and structured literature review synthesis.
"""

try:
    from .lit_tools import get_tools, get_permissions, call_tool
except ImportError:
    from lit_tools import get_tools, get_permissions, call_tool

__all__ = ["get_tools", "get_permissions", "call_tool"]
