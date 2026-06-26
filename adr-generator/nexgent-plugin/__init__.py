"""
adr-generator Nexgent Plugin
Architecture Decision Record generator — create, manage, and index ADRs.
"""

from .adr_tools import get_tools, get_permissions, call_tool

__all__ = ["get_tools", "get_permissions", "call_tool"]
