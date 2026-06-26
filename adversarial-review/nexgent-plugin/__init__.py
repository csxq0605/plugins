"""Adversarial Review plugin for Nexgent.

Multi-perspective code review with 6 analysis lenses,
unified findings format, health scoring, and iterative fix loop.
"""

try:
    from .review_tools import get_tools, get_permissions, call_tool
except ImportError:
    from review_tools import get_tools, get_permissions, call_tool

__all__ = ["get_tools", "get_permissions", "call_tool"]
