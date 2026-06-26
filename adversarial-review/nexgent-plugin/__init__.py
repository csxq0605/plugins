"""Adversarial Review plugin for Nexgent.

Multi-perspective code review with 6 analysis lenses,
unified findings format, health scoring, and iterative fix loop.
"""

try:
    from .review_tools import get_tools
except ImportError:
    from review_tools import get_tools

__all__ = ["get_tools"]
