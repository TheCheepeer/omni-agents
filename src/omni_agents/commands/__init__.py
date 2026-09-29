"""
Headless commands and action handlers for omni-agents CLI.
"""

from __future__ import annotations

from omni_agents.commands.clean_cmd import (
    clean_global_cli,
    clean_workspace_cli,
)
from omni_agents.commands.diagnostics import run_update, show_info
from omni_agents.commands.ext_cmd import (
    install_extension,
    list_extensions,
    remove_extension,
    update_extensions,
)
from omni_agents.commands.list_cmd import (
    list_agents,
    list_rules,
    list_skills,
    list_tools,
)
from omni_agents.commands.sync_cmd import configure_global_cli, sync_workspace_cli

__all__ = [
    "clean_global_cli",
    "clean_workspace_cli",
    "configure_global_cli",
    "install_extension",
    "list_agents",
    "list_extensions",
    "list_rules",
    "list_skills",
    "list_tools",
    "remove_extension",
    "run_update",
    "show_info",
    "sync_workspace_cli",
    "update_extensions",
]
