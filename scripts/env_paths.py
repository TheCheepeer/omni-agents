#!/usr/bin/env python3
"""
Environment and system path resolution module for omni-agent.
Manages the user configuration directory in Documents/omni-agent, development mode detection,
and hierarchical directories for customizations (custom/) and downloaded extensions (ext/).
"""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

DEFAULT_CONFIG: dict[str, Any] = {
    "version": "1.0.0",
    "language": "en",
    "repository": {
        "url": "https://github.com/TheCheepeer/omni-agent",
        "branch": "main",
        "raw_base_url": "https://raw.githubusercontent.com/TheCheepeer/omni-agent/main",
        "api_base_url": "https://api.github.com/repos/TheCheepeer/omni-agent",
    },
    "check_updates_on_launch": True,
    "active_targets": ["antigravity"],
}


def get_system_documents_dir() -> Path:
    """
    Returns the real resolved path to the user's system Documents directory.
    On Windows, queries the registry to handle redirected folders (like OneDrive).
    On Linux, parses XDG_DOCUMENTS_DIR.
    On macOS, defaults to ~/Documents.
    """
    home = Path.home()

    # Windows: query registry for exact personal shell folder
    if sys.platform.startswith("win"):
        with contextlib.suppress(OSError, ImportError, ValueError):
            import winreg

            key_path = (
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            )
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                val, _ = winreg.QueryValueEx(key, "Personal")
                expanded = os.path.expandvars(val)
                p = Path(expanded).resolve()
                if p.exists() and p.is_dir():
                    return p

        # Fallback for OneDrive if it exists
        onedrive_docs = home / "OneDrive" / "Documentos"
        if onedrive_docs.exists() and onedrive_docs.is_dir():
            return onedrive_docs
        onedrive_docs_en = home / "OneDrive" / "Documents"
        if onedrive_docs_en.exists() and onedrive_docs_en.is_dir():
            return onedrive_docs_en

        # Standard fallbacks
        for candidate in (home / "Documents", home / "Documentos"):
            if candidate.exists() and candidate.is_dir():
                return candidate
        return home / "Documents"

    # Linux: query XDG configuration
    if sys.platform.startswith("linux"):
        xdg_config = home / ".config" / "user-dirs.dirs"
        if xdg_config.exists():
            with contextlib.suppress(OSError, UnicodeDecodeError):
                for line in xdg_config.read_text(encoding="utf-8").splitlines():
                    if line.startswith("XDG_DOCUMENTS_DIR="):
                        raw = line.split("=", 1)[1].strip("\"'")
                        expanded = raw.replace("$HOME", str(home))
                        p = Path(expanded).resolve()
                        if p.exists() and p.is_dir():
                            return p
        return home / "Documents"

    # macOS and others
    return home / "Documents"


def get_omni_documents_dir() -> Path:
    """Returns the omni-agents base directory inside Documents."""
    docs = get_system_documents_dir()
    legacy_dir = docs / "omni-agent"
    modern_dir = docs / "omni-agents"
    if legacy_dir.exists() and not modern_dir.exists():
        return legacy_dir
    return modern_dir


def is_dev_mode(repo_root: Path | None = None) -> bool:
    """
    Detects if the script is running from the cloned source Git repository.
    Verifies that the root folder contains .git and the core content directories.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent

    git_dir = repo_root / ".git"
    agents_dir = repo_root / "agents"
    rules_dir = repo_root / "rules"
    skills_dir = repo_root / "skills"

    return (
        git_dir.exists()
        and agents_dir.is_dir()
        and rules_dir.is_dir()
        and skills_dir.is_dir()
    )


def ensure_omni_documents_structure() -> tuple[Path, dict[str, Any]]:
    """
    Ensures that the directory structure in Documents/omni-agent exists.
    Creates custom/ and ext/ subdirectories, README files, and config.json if needed.
    Returns the base directory path and loaded config dictionary.
    """
    base_dir = get_omni_documents_dir()
    base_dir.mkdir(parents=True, exist_ok=True)

    # Subdirectories for user custom tools
    custom_dir = base_dir / "custom"
    for sub in ("agents", "rules", "skills"):
        (custom_dir / sub).mkdir(parents=True, exist_ok=True)

    custom_readme = custom_dir / "README.md"
    if (
        not custom_readme.exists()
        or "rules/<profile_name>/AGENTS.md"
        not in custom_readme.read_text(encoding="utf-8", errors="ignore")
    ):
        custom_readme.write_text(
            "# Personal Custom Tools\n\n"
            "Place your personal subagents, rules, and skills here:\n"
            "- `agents/`: Markdown subagents (`*.md`)\n"
            "- `rules/<profile_name>/AGENTS.md`: Modular rule profiles (or standalone `*.md` rules)\n"
            "- `skills/<category>/<skill_name>/SKILL.md`: Modular skills\n\n"
            "Components placed in this directory take highest priority over core/ext layers and are never overwritten by updates.\n",
            encoding="utf-8",
        )

    # Subdirectories for downloaded extensions
    ext_dir = base_dir / "ext"
    for sub in ("agents", "rules", "skills"):
        (ext_dir / sub).mkdir(parents=True, exist_ok=True)

    ext_manifest = ext_dir / "manifest.json"
    if not ext_manifest.exists():
        try:
            ext_manifest.write_text(
                json.dumps({"installed": {}, "last_check": None}, indent=2) + "\n",
                encoding="utf-8",
            )
        except OSError:
            pass

    # Persistent configuration file
    config_file = base_dir / "config.json"
    config: dict[str, Any] = {}
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            config = {}

    # Merge default config with existing preferences
    merged_config = dict(DEFAULT_CONFIG)
    merged_config.update(config)

    # Ensure repository block integrity
    if "repository" not in merged_config or not isinstance(
        merged_config["repository"], dict
    ):
        merged_config["repository"] = dict(DEFAULT_CONFIG["repository"])
    else:
        for k, v in DEFAULT_CONFIG["repository"].items():
            if k not in merged_config["repository"]:
                merged_config["repository"][k] = v

    if not config_file.exists() or config != merged_config:
        try:
            config_file.write_text(
                json.dumps(merged_config, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except OSError:
            pass

    return base_dir, merged_config


def save_omni_config(config: dict[str, Any]) -> bool:
    """Persists configuration to Documents/omni-agent/config.json."""
    config_file = get_omni_documents_dir() / "config.json"
    try:
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return True
    except OSError:
        return False


def open_folder_in_explorer(path: Path) -> bool:
    """Opens the specified directory in the system default file manager."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
            return True
        elif sys.platform.startswith("darwin"):
            subprocess.run(["open", str(path)], check=False)
            return True
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
            return True
    except (OSError, subprocess.SubprocessError):
        return False
