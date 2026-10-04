#!/usr/bin/env python3
"""
Migration and legacy cleanup module for omni-agents.
Detects and safely removes deprecated global junctions, relative symlinks,
and orphaned machine configurations from legacy versions (v1.0.2 and earlier),
ensuring a seamless transition to the 100% workspace-centric model in v1.0.3.
"""

from __future__ import annotations

import os
from pathlib import Path

from omni_agents.core.config import load_app_config, save_app_config
from omni_agents.i18n import t
from omni_agents.targets.base import (
    is_link,
    remove_dir_link,
    safe_remove_dir_if_empty,
    safe_remove_file,
)


def cleanup_legacy_global_environment(
    omni_docs_dir: Path | None = None,
    repo_root: Path | None = None,
    lang: str = "en",
    verbose: bool = True,
) -> list[str]:
    """
    Scans the system user environment for legacy global junctions and files
    created by omni-agents v1.0.2 or earlier, and safely unlinks them.

    Target legacy artifacts:
      - ~/.gemini/config/agents (junction or symlink)
      - ~/.gemini/config/skills (junction or symlink)
      - ~/.gemini/config/rules (junction, symlink, or legacy rule files)
      - ~/.claude/CLAUDE.md (if containing omni-agents markers)
      - App config: clears obsolete 'global_rules' property

    Returns a list of removed artifact paths.
    """
    removed: list[str] = []
    home = Path.home()

    # 1. Google Antigravity legacy global targets
    gemini_config = home / ".gemini" / "config"
    if os.path.lexists(gemini_config):
        for name in ("agents", "skills", "rules"):
            target = gemini_config / name
            if os.path.lexists(target):
                if is_link(target):
                    try:
                        remove_dir_link(target)
                        removed.append(str(target))
                    except OSError:
                        pass
                elif name == "rules" and target.is_dir():
                    try:
                        for item in list(target.iterdir()):
                            if item.is_file() and item.suffix == ".md":
                                item.unlink()
                        safe_remove_dir_if_empty(target)
                        if not os.path.lexists(target):
                            removed.append(str(target))
                    except OSError:
                        pass

    # 2. Claude Code legacy global instructions
    claude_global = home / ".claude" / "CLAUDE.md"
    if claude_global.exists():
        try:
            content = claude_global.read_text(encoding="utf-8", errors="ignore")
            if "omni-agents" in content or "Claude Global Guidelines" in content:
                safe_remove_file(claude_global)
                removed.append(str(claude_global))
                safe_remove_dir_if_empty(claude_global.parent)
        except OSError:
            pass

    # 3. Clean legacy config keys in user Documents/omni-agents/config.json
    if omni_docs_dir or repo_root:
        try:
            root = repo_root or Path.cwd()
            cfg = load_app_config(root, omni_docs_dir=omni_docs_dir)
            changed = False
            if "global_rules" in cfg:
                del cfg["global_rules"]
                changed = True
            if cfg.get("version") != "1.0.3":
                cfg["version"] = "1.0.3"
                changed = True
            if not cfg.get("legacy_global_cleaned"):
                cfg["legacy_global_cleaned"] = True
                changed = True
            if changed:
                save_app_config(root, cfg, omni_docs_dir=omni_docs_dir)
        except OSError:
            pass

    if removed and verbose:
        print(f"\n[i] {t('legacy_cleanup_detected', lang)}")
        for item in removed:
            print(f"  [-] {t('legacy_cleanup_item', lang, path=item)}")
        print(f"[OK] {t('legacy_cleanup_completed', lang)}\n")

    return removed
