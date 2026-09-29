#!/usr/bin/env python3
"""
Application configuration persistence for omni-agents.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from omni_agents.env_paths import is_dev_mode, save_omni_config


def load_app_config(
    repo_root: Path, omni_docs_dir: Path | None = None
) -> dict[str, Any]:
    """Loads persistent application preferences from Documents or repo root."""
    if omni_docs_dir:
        cfg_file = omni_docs_dir / "config.json"
        if cfg_file.exists():
            try:
                return json.loads(cfg_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
    cfg_file = repo_root / "config.json"
    if cfg_file.exists():
        try:
            return json.loads(cfg_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_app_config(
    repo_root: Path,
    config: dict[str, Any],
    omni_docs_dir: Path | None = None,
) -> None:
    """Persists application preferences to Documents/omni-agents/config.json and repo root."""
    if omni_docs_dir:
        save_omni_config(config)
    if is_dev_mode(repo_root):
        cfg_file = repo_root / "config.json"
        try:
            cfg_file.write_text(
                json.dumps(config, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except OSError:
            pass
