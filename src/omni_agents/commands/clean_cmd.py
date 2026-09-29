#!/usr/bin/env python3
"""
Cleanup command handlers for omni-agents.
Supports headless workspace cleanup and global tool unlinking via CLI flags.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from omni_agents.core.config import save_app_config
from omni_agents.env_paths import is_default_or_system_path
from omni_agents.i18n import t
from omni_agents.targets import (
    get_all_targets,
    get_available_target_ids,
    get_target,
    load_workspace_state,
    save_workspace_state,
)


def clean_global_cli(
    target_tool: str | None,
    app_config: dict[str, Any],
    repo_root: Path,
    omni_docs_dir: Path | None,
    current_lang: str = "en",
) -> None:
    """Executes global configuration cleanup via CLI flags."""
    tools = (
        [
            get_target(t_id)
            for t_id in [
                x.strip().lower()
                for x in target_tool.replace(";", ",").split(",")
                if x.strip()
            ]
        ]
        if target_tool and target_tool != "all"
        else [target for target in get_all_targets() if target.supports_global]
    )
    for target in tools:
        if target:
            target.clean_global(lang=current_lang)
    app_config["global_rules"] = []
    save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)
    print("\n[OK] Global clean completed.")


def clean_workspace_cli(
    target_path: Path,
    target_tool: str | None,
    assume_yes: bool,
    current_lang: str = "en",
) -> None:
    """Removes tool configurations from workspace directory via CLI flags."""
    if is_default_or_system_path(target_path) and not assume_yes:
        print(f"\n{t('default_path_cli_warning', current_lang, path=target_path)}")
        try:
            confirm = (
                input(t("default_path_cli_prompt", current_lang, path=target_path))
                .strip()
                .lower()
            )
        except (EOFError, KeyboardInterrupt):
            sys.exit(1)
        if confirm not in ("s", "y", "sim", "yes"):
            print("[!] Aborted.")
            sys.exit(1)

    state = load_workspace_state(target_path)
    tool_ids = (
        [
            x.strip().lower()
            for x in target_tool.replace(";", ",").split(",")
            if x.strip()
        ]
        if target_tool and target_tool != "all"
        else get_available_target_ids()
    )
    for tid in tool_ids:
        adapter = get_target(tid)
        if adapter:
            adapter.clean_workspace(target_path, lang=current_lang)
            if tid in state.get("active_targets", []):
                state["active_targets"].remove(tid)
    save_workspace_state(target_path, state)
    print("\n[OK] Clean completed.")
