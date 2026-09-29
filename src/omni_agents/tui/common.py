#!/usr/bin/env python3
"""
Common terminal rendering and interaction utilities for omni-agents TUI.
"""

from __future__ import annotations

import os
import sys

from omni_agents.i18n import t
from omni_agents.tui.theme import COLOR_WARNING, console


def clear_screen() -> None:
    """Cross-platform terminal screen cleaner."""
    os.system("cls" if sys.platform.startswith("win") else "clear")


def confirm_exit_unsaved(lang: str = "en") -> bool:
    """Prompts the user whether to discard unsaved changes using a styled warning prompt."""
    try:
        warning_text = t("unsaved_changes_warning", lang)
        arrow = f"[bold {COLOR_WARNING}]![/bold {COLOR_WARNING}] "
        console.print(f"\n{arrow}[white]{warning_text}[/white]", end="")
        resp = input().strip().lower()
        return resp in ("s", "sim", "y", "yes", "si", "sí")
    except (EOFError, KeyboardInterrupt):
        return True
