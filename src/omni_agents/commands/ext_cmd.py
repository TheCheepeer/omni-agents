#!/usr/bin/env python3
"""
Remote extension CLI command handlers for omni-agents.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from omni_agents.remote_sync import (
    check_ext_updates,
    fetch_remote_tree,
    install_remote_component,
    load_manifest,
    save_manifest,
)


def list_extensions(ext_dir: Path | None) -> None:
    """Lists installed remote extensions in ext/."""
    manifest = load_manifest(ext_dir) if ext_dir else {}
    installed = manifest.get("installed", {})
    print("\nInstalled Remote Extensions:")
    if not installed:
        print("  (No extensions currently installed in ext/)")
    for k, v in installed.items():
        print(f"  * {k:<32} (sha: {v.get('sha', '')[:7]})")


def install_extension(
    ext_item: str,
    app_config: dict[str, Any],
    ext_dir: Path | None,
) -> bool:
    """Installs a remote extension from catalog (e.g. 'agents/code-reviewer.md' or 'skills/testing/pytest')."""
    if not ext_dir:
        print("[x] Error: Personal documents directory is not available.")
        return False

    raw_target = ext_item.replace("\\", "/").strip("/")
    parts = raw_target.split("/")
    comp_type = parts[0] if parts[0] in ("agents", "rules", "skills") else None
    comp_id = parts[-1]
    cat = parts[1] if comp_type == "skills" and len(parts) > 2 else None

    if not comp_type:
        tree = fetch_remote_tree(app_config, timeout=5.0)
        if tree:
            if any(a["id"].lower() == comp_id.lower() for a in tree.get("agents", [])):
                comp_type = "agents"
            elif any(r["id"].lower() == comp_id.lower() for r in tree.get("rules", [])):
                comp_type = "rules"
            else:
                for c_name, c_skills in tree.get("skills_by_category", {}).items():
                    if any(s["id"].lower() == comp_id.lower() for s in c_skills):
                        comp_type = "skills"
                        cat = c_name
                        break

    if not comp_type:
        print(f"[x] Error: Could not identify component type for '{ext_item}'.")
        print("    Use format: 'agents/<id>.md', 'rules/<id>', or 'skills/<cat>/<id>'")
        return False

    print(f"-> Installing remote {comp_type}: {comp_id}...")
    ok = install_remote_component(comp_type, comp_id, app_config, ext_dir, category=cat)
    if ok:
        print(f"[OK] Successfully installed {comp_type}/{comp_id} in ext/")
        return True
    else:
        print(f"[x] Failed to install {comp_type}/{comp_id}.")
        return False


def update_extensions(
    app_config: dict[str, Any],
    ext_dir: Path | None,
) -> bool:
    """Checks and updates all installed remote extensions in ext/."""
    if not ext_dir:
        print("[x] Error: Personal documents directory is not available.")
        return False

    print("-> Checking for remote extension updates...")
    updates = check_ext_updates(ext_dir, app_config, timeout=5.0)
    if not updates:
        print("[OK] All extensions in ext/ are up to date.")
        return True

    print(f"-> Found {len(updates)} update(s). Applying...")
    tree = fetch_remote_tree(app_config, timeout=5.0)
    for u in updates:
        install_remote_component(
            u["type"],
            u["id"],
            app_config,
            ext_dir,
            category=u.get("category"),
            tree_data=tree,
        )
    print("[OK] Extensions updated successfully.")
    return True


def remove_extension(
    key: str,
    ext_dir: Path | None,
) -> bool:
    """Removes an installed remote extension by key."""
    if not ext_dir:
        print("[x] Error: Personal documents directory is not available.")
        return False

    manifest = load_manifest(ext_dir)
    installed = manifest.get("installed", {})
    key_to_del = next((k for k in installed if k.lower() == key.lower()), None)
    if not key_to_del:
        print(f"[x] Error: Extension '{key}' not found in installed extensions.")
        return False

    del installed[key_to_del]
    save_manifest(ext_dir, manifest)
    target_file = ext_dir / key_to_del
    if target_file.is_dir():
        shutil.rmtree(target_file, ignore_errors=True)
    elif target_file.is_file():
        target_file.unlink(missing_ok=True)
    print(f"[OK] Removed extension: {key_to_del}")
    return True
