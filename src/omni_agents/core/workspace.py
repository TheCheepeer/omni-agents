#!/usr/bin/env python3
"""
Workspace resolution and path validation utilities for omni-agents.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from omni_agents.env_paths import is_default_or_system_path
from omni_agents.i18n import t


def clear_screen() -> None:
    """Cross-platform terminal screen cleaner."""
    os.system("cls" if sys.platform.startswith("win") else "clear")


def has_graphical_display() -> bool:
    """Checks if a graphical display environment is available."""
    if sys.platform.startswith("win") or sys.platform.startswith("darwin"):
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def is_gui_available() -> bool:
    """Checks if both graphical display and Tkinter module are available."""
    if not has_graphical_display():
        return False
    return importlib.util.find_spec("tkinter") is not None


def pick_directory_gui(
    title: str = "Select Project Repository Directory",
) -> str | None:
    """Opens native GUI file dialog (Tkinter) for directory selection."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return None

    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", True)
        root.update()
        root.focus_force()
        selected_path = filedialog.askdirectory(parent=root, title=title)
        root.destroy()
        return selected_path if selected_path else None
    except (tk.TclError, RuntimeError, OSError):
        return None


def resolve_workspace(current_target: Path | None, lang: str = "en") -> Path | None:
    """Prompts for target workspace path, opening native GUI dialog if available."""
    if current_target and current_target.exists() and current_target.is_dir():
        return current_target

    clear_screen()
    print("\n" + "=" * 65)
    print(f"  {t('target_workspace', lang).upper()}")
    print("=" * 65)

    if is_gui_available():
        gui_path = pick_directory_gui(title=t("workspace_selector_title", lang))
        if gui_path:
            p = Path(gui_path).resolve()
            if p.exists() and p.is_dir():
                print(f"[OK] {t('path_selected', lang, path=p)}")
                return p

    while True:
        try:
            val = input(f"\n{t('prompt_path', lang)}").strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if val.lower() in ("v", "voltar", "volver", ""):
            return None

        clean_val = val.strip("\"'")
        p = Path(clean_val).resolve()
        if p.exists() and p.is_dir():
            return p
        print(f"[x] {t('path_invalid', lang, path=p)}")


def confirm_or_choose_project_workspace(
    target_path: Path | None, lang: str = "en"
) -> Path | None:
    """
    If the current workspace target is a default user home or system directory,
    warns the user and prompts them to pick an actual project folder.
    """
    if not is_default_or_system_path(target_path):
        return target_path

    print(f"\n{t('default_path_confirm_prompt', lang, path=target_path)}", end="")
    try:
        ans = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        return target_path

    if ans in ("", "s", "y", "sim", "yes"):
        chosen = resolve_workspace(None, lang=lang)
        if chosen:
            return chosen
    return target_path
