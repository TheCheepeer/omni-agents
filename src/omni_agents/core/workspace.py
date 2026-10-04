#!/usr/bin/env python3
"""
Workspace resolution and path validation utilities for omni-agents.
"""

from __future__ import annotations

import contextlib
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from omni_agents.env_paths import get_omni_documents_dir, is_default_or_system_path
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


def get_workspaces_registry_file(omni_docs_dir: Path | None = None) -> Path:
    """Returns the central workspaces registry path in Documents/omni-agents/workspaces.json."""
    base_dir = omni_docs_dir or get_omni_documents_dir()
    return base_dir / "workspaces.json"


def load_tracked_workspaces(omni_docs_dir: Path | None = None) -> list[dict[str, Any]]:
    """
    Loads all tracked workspaces from Documents/omni-agents/workspaces.json.
    Automatically prunes entries whose directories no longer exist on disk.
    """
    reg_file = get_workspaces_registry_file(omni_docs_dir)
    if not reg_file.exists():
        return []

    try:
        data = json.loads(reg_file.read_text(encoding="utf-8"))
        entries = data.get("workspaces", []) if isinstance(data, dict) else []
    except (json.JSONDecodeError, OSError):
        return []

    valid_entries: list[dict[str, Any]] = []
    has_pruned = False

    for entry in entries:
        raw_path = entry.get("path")
        if not raw_path:
            has_pruned = True
            continue
        p = Path(raw_path)
        if p.exists() and p.is_dir() and not is_default_or_system_path(p):
            valid_entries.append(entry)
        else:
            has_pruned = True

    if has_pruned:
        with contextlib.suppress(OSError):
            reg_file.write_text(
                json.dumps({"workspaces": valid_entries}, indent=2, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )

    return valid_entries


def add_tracked_workspace(
    target_path: Path,
    active_tools: list[str] | None = None,
    omni_docs_dir: Path | None = None,
) -> None:
    """Registers or updates a workspace in Documents/omni-agents/workspaces.json."""
    if is_default_or_system_path(target_path):
        return

    resolved_path = str(target_path.resolve())
    reg_file = get_workspaces_registry_file(omni_docs_dir)
    reg_file.parent.mkdir(parents=True, exist_ok=True)

    entries = load_tracked_workspaces(omni_docs_dir)
    now_iso = datetime.now(timezone.utc).isoformat()

    found = False
    for item in entries:
        if item.get("path") == resolved_path:
            if active_tools is not None:
                item["active_tools"] = sorted(active_tools)
            item["updated_at"] = now_iso
            found = True
            break

    if not found:
        entries.append(
            {
                "path": resolved_path,
                "active_tools": sorted(active_tools or []),
                "updated_at": now_iso,
            }
        )

    with contextlib.suppress(OSError):
        reg_file.write_text(
            json.dumps({"workspaces": entries}, indent=2, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )


def remove_tracked_workspace(
    target_path: Path, omni_docs_dir: Path | None = None
) -> None:
    """Removes a workspace from Documents/omni-agents/workspaces.json."""
    resolved_path = str(target_path.resolve())
    reg_file = get_workspaces_registry_file(omni_docs_dir)
    if not reg_file.exists():
        return

    entries = load_tracked_workspaces(omni_docs_dir)
    filtered = [item for item in entries if item.get("path") != resolved_path]

    if len(filtered) != len(entries):
        with contextlib.suppress(OSError):
            reg_file.write_text(
                json.dumps({"workspaces": filtered}, indent=2, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )


def resolve_workspace(
    current_target: Path | None,
    lang: str = "en",
    omni_docs_dir: Path | None = None,
    force_prompt: bool = False,
) -> Path | None:
    """Prompts for target workspace path, displaying tracked recent projects or opening native GUI dialog."""
    if (
        not force_prompt
        and current_target
        and current_target.exists()
        and current_target.is_dir()
        and not is_default_or_system_path(current_target)
    ):
        return current_target

    clear_screen()
    print("\n" + "=" * 65)
    print(f"  {t('target_workspace', lang).upper()}")
    print("=" * 65)

    tracked = load_tracked_workspaces(omni_docs_dir)
    quick_map: dict[str, str] = {}

    if tracked:
        recent_title = t("tracked_workspaces_title", lang)
        print(f"\n{recent_title}:")
        for idx, item in enumerate(tracked[:9], start=1):
            tools_str = (
                f" ({', '.join(item.get('active_tools', []))})"
                if item.get("active_tools")
                else ""
            )
            print(f"  [{idx}] {item['path']}{tools_str}")
            quick_map[str(idx)] = item["path"]
        print("-" * 65)

    if is_gui_available():
        gui_path = pick_directory_gui(title=t("workspace_selector_title", lang))
        if gui_path:
            p = Path(gui_path).resolve()
            if p.exists() and p.is_dir() and not is_default_or_system_path(p):
                print(f"[OK] {t('path_selected', lang, path=p)}")
                return p

    while True:
        try:
            val = input(f"\n{t('prompt_path', lang)}").strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if val.lower() in ("v", "voltar", "volver", ""):
            return None

        if val in quick_map:
            p = Path(quick_map[val]).resolve()
            if p.exists() and p.is_dir():
                return p

        clean_val = val.strip("\"'")
        p = Path(clean_val).resolve()
        if p.exists() and p.is_dir():
            return p
        print(f"[x] {t('path_invalid', lang, path=p)}")


def confirm_or_choose_project_workspace(
    target_path: Path | None,
    lang: str = "en",
    omni_docs_dir: Path | None = None,
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
        chosen = resolve_workspace(None, lang=lang, omni_docs_dir=omni_docs_dir)
        if chosen:
            return chosen
    return target_path
