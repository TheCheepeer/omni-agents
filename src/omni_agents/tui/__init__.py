"""
Terminal User Interface (TUI) components for omni-agents.
"""

from __future__ import annotations

from omni_agents.tui.agents_menu import handle_agents
from omni_agents.tui.common import clear_screen, confirm_exit_unsaved
from omni_agents.tui.extensions_menu import handle_remote_extensions
from omni_agents.tui.language_menu import handle_language_selection
from omni_agents.tui.menu import run_interactive_loop
from omni_agents.tui.rules_menu import handle_rules, select_global_rule_profile
from omni_agents.tui.skills_menu import handle_category_submenu, handle_skills
from omni_agents.tui.source_menu import select_component_source
from omni_agents.tui.targets_menu import (
    handle_global_configuration,
    handle_target_selection,
)

__all__ = [
    "clear_screen",
    "confirm_exit_unsaved",
    "handle_agents",
    "handle_category_submenu",
    "handle_global_configuration",
    "handle_language_selection",
    "handle_remote_extensions",
    "handle_rules",
    "handle_skills",
    "handle_target_selection",
    "run_interactive_loop",
    "select_component_source",
    "select_global_rule_profile",
]
