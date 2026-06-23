"""Agent Team plugin for Nexgent.

Provides multi-agent team coordination with lead/teammate roles,
inbox sync protocol, shared task list, and superpowers development workflow.
"""

try:
    from .team_tools import get_tools
except ImportError:
    from team_tools import get_tools

__all__ = ["get_tools"]
