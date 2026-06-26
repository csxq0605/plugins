"""Migrator — Framework Migration Assistant plugin for Nexgent.

Analyze codebase, generate migration plans, execute step by step with verification.
"""

try:
    from .migrator_tools import get_tools, get_permissions, call_tool
except ImportError:
    from migrator_tools import get_tools, get_permissions, call_tool

__all__ = ["get_tools", "get_permissions", "call_tool"]
