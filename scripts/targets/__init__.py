#!/usr/bin/env python3
"""
Central registry of supported targets and adapters for the omni-agent system.
"""

from __future__ import annotations

from .antigravity import AntigravityTarget
from .base import BaseTarget, load_workspace_state, save_workspace_state
from .claude import ClaudeTarget
from .copilot import CopilotTarget
from .cursor import CursorTarget
from .universal import (
    CodexTarget,
    KiroTarget,
    OpenCodeTarget,
    UniversalTarget,
)

TARGET_REGISTRY: dict[str, BaseTarget] = {
    "antigravity": AntigravityTarget(),
    "claude": ClaudeTarget(),
    "cursor": CursorTarget(),
    "copilot": CopilotTarget(),
    "universal": UniversalTarget(),
    "kiro": KiroTarget(),
    "opencode": OpenCodeTarget(),
    "codex": CodexTarget(),
}


def get_target(target_id: str) -> BaseTarget | None:
    """Returns the adapter instance for the given identifier."""
    return TARGET_REGISTRY.get(target_id.lower().strip())


def get_all_targets() -> list[BaseTarget]:
    """Returns all available adapter instances in recommended order."""
    return list(TARGET_REGISTRY.values())


def get_available_target_ids() -> list[str]:
    """Returns the list of registered adapter IDs."""
    return list(TARGET_REGISTRY.keys())


__all__ = [
    "TARGET_REGISTRY",
    "BaseTarget",
    "get_all_targets",
    "get_available_target_ids",
    "get_target",
    "load_workspace_state",
    "save_workspace_state",
]
