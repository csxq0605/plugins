"""Atlas — Codebase Knowledge Atlas plugin for Nexgent.

Multi-agent parallel exploration of codebases. Generates architecture docs,
data flow maps, dependency analysis, and living knowledge maps.
"""

try:
    from .atlas_tools import get_tools, get_permissions, call_tool
except ImportError:
    from atlas_tools import get_tools, get_permissions, call_tool

__all__ = ["get_tools", "get_permissions", "call_tool"]
