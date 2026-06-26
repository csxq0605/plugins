"""
project-onboarding Nexgent Plugin
Auto-scan project structure, tech stack, build system, test framework, CI/CD, code style.
"""

from .onboarding_tools import get_tools, get_permissions, call_tool

__all__ = ["get_tools", "get_permissions", "call_tool"]
