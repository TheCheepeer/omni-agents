#!/usr/bin/env python3
"""
Diagnostics and updater command handlers for omni-agents.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.i18n import t
from omni_agents.updater import (
    __version__,
    check_for_updates,
    prompt_and_upgrade,
)


def show_info(
    repo_root: Path,
    omni_docs_dir: Path,
    app_config: dict[str, Any],
    is_dev: bool,
) -> None:
    """Displays system paths, active configuration, and runtime mode."""
    print("\nomni-agents Diagnostic Info:")
    print(f"  CLI Version:      v{__version__}")
    print(
        f"  Execution Mode:   {'Local Dev Mode (Repository)' if is_dev else 'Global Mode (Documents)'}"
    )
    print(f"  Repo Root:        {repo_root}")
    print(f"  Documents Dir:    {omni_docs_dir}")
    print(f"  Configured Repo:  {app_config.get('repository', {}).get('url', 'N/A')}")
    print(f"  Default Language: {app_config.get('language', 'en')}")


def run_update(is_dev: bool, current_lang: str) -> None:
    """Checks for newer releases and executes self-upgrade."""
    print(f"\n{t('update_checking', current_lang, version=__version__)}")
    up_info = check_for_updates(current_version=__version__, is_dev=is_dev, timeout=3.0)
    if up_info:
        prompt_and_upgrade(up_info, lang=current_lang)
    else:
        print(f"\n{t('update_up_to_date', current_lang)}")
