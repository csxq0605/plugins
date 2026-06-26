"""
Email Plugin for Nexgent
独立邮件收发插件
"""

try:
    from .email_tools import (
        email_is_configured,
        email_get_presets,
        email_setup,
        email_test,
        email_get_config,
        email_send,
        email_send_batch,
        email_list,
        email_read,
        email_search
    )
except ImportError:
    from email_tools import (
        email_is_configured,
        email_get_presets,
        email_setup,
        email_test,
        email_get_config,
        email_send,
        email_send_batch,
        email_list,
        email_read,
        email_search
    )

__all__ = [
    "email_is_configured",
    "email_get_presets",
    "email_setup",
    "email_test",
    "email_get_config",
    "email_send",
    "email_send_batch",
    "email_list",
    "email_read",
    "email_search"
]
