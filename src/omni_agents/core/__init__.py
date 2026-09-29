"""
Core domain logic for omni-agents.
"""

from __future__ import annotations

from omni_agents.core.config import load_app_config, save_app_config
from omni_agents.core.linker import (
    apply_global_rules_to_targets,
    apply_workspace_to_targets,
)
from omni_agents.core.scanner import scan_component_sources, scan_repository
from omni_agents.core.workspace import (
    confirm_or_choose_project_workspace,
    has_graphical_display,
    is_gui_available,
    pick_directory_gui,
    resolve_workspace,
)

__all__ = [
    "apply_global_rules_to_targets",
    "apply_workspace_to_targets",
    "confirm_or_choose_project_workspace",
    "has_graphical_display",
    "is_gui_available",
    "load_app_config",
    "pick_directory_gui",
    "resolve_workspace",
    "save_app_config",
    "scan_component_sources",
    "scan_repository",
]
