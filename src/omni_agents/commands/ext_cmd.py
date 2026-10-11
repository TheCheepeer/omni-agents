#!/usr/bin/env python3
"""
Remote extension CLI command handlers for omni-agents.
Manages listing, installing (catalog and external Git repos), checking, and updating extensions.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

from omni_agents.i18n import t
from omni_agents.remote_sync import (
    check_all_extensions_updates,
    fetch_remote_tree,
    install_external_git_component,
    install_remote_component,
    load_manifest,
    save_manifest,
)


def list_extensions(ext_dir: Path | None, lang: str = "en") -> None:
    """Lists installed remote extensions in ext/."""
    manifest = load_manifest(ext_dir) if ext_dir else {}
    installed = manifest.get("installed", {})
    print(f"\n{t('ext_installed_list_title', lang)}")
    if not installed:
        print(f"  ({t('ext_none_installed', lang)})")
        return

    for k, v in installed.items():
        src_type = v.get("source_type", "catalog")
        sha = v.get("sha", "")[:7] or "unknown"
        src_info = f"[{src_type}]" if src_type == "git" else "[catalog]"
        print(f"  * {k:<36} {src_info:<10} (sha: {sha})")


def check_extensions(
    app_config: dict[str, Any],
    ext_dir: Path | None,
    lang: str = "en",
) -> bool:
    """
    Checks for extension updates and displays a status table without modifying files.
    """
    if not ext_dir:
        print("[x] Error: Personal documents directory is not available.")
        return False

    manifest = load_manifest(ext_dir)
    installed = manifest.get("installed", {})
    if not installed:
        print(f"\n[i] {t('ext_none_installed', lang)}")
        return True

    print(f"\n-> {t('ext_checking_updates', lang)}")
    all_statuses, updates = check_all_extensions_updates(ext_dir, app_config, timeout=4.0)

    print("\n" + "=" * 80)
    print(f"  {'Extension':<30} {'Type':<10} {'Current':<10} {'Remote':<10} {'Status'}")
    print("-" * 80)

    for item in all_statuses:
        key = item["key"]
        comp_type = item["type"]
        cur_sha = (item["current_sha"] or "")[:7] or "---"
        new_sha = (item["new_sha"] or "")[:7] or "---"
        status_str = "[!] Update available" if item["has_update"] else "[OK] Up to date"
        print(f"  {key:<30} {comp_type:<10} {cur_sha:<10} {new_sha:<10} {status_str}")

    print("=" * 80)

    if updates:
        print(f"\n-> {len(updates)} update(s) available.")
        print("   To update, run: omni --ext-update\n")
    else:
        print(f"\n[OK] {t('ext_up_to_date', lang)}\n")

    return True


def add_external_extension(
    source: str,
    ext_dir: Path | None,
    skill_name: str | None = None,
    category: str = "community",
    lang: str = "en",
) -> bool:
    """Installs a skill or agent directly from an external Git repository."""
    if not ext_dir:
        print("[x] Error: Personal documents directory is not available.")
        return False

    print(f"\n-> Fetching external component from: {source}...")
    result = install_external_git_component(
        source=source,
        ext_dir=ext_dir,
        skill_id=skill_name,
        category=category,
        timeout=30.0,
    )

    if result:
        comp_type = result["type"]
        comp_id = result["id"]
        key = result["key"]
        sha = result.get("sha", "")[:7]
        print(f"[OK] Successfully installed {comp_type}: '{comp_id}' in ext/{key} (sha: {sha})")
        print("     Origin saved in ext/manifest.json. Available for all workspaces.")
        return True
    else:
        print(f"[x] Error: Failed to clone or install external component from '{source}'.")
        print("    Ensure the repository URL is public, accessible, and contains SKILL.md.")
        return False


def install_extension(
    ext_item: str,
    app_config: dict[str, Any],
    ext_dir: Path | None,
    skill_name: str | None = None,
    category: str | None = None,
    lang: str = "en",
) -> bool:
    """
    Installs an extension. Intelligently routes Git URLs/slugs to the external installer
    and catalog identifiers to the catalog installer.
    """
    if not ext_dir:
        print("[x] Error: Personal documents directory is not available.")
        return False

    raw_target = ext_item.strip()

    # Detect if user provided a Git URL or GitHub repository shorthand
    is_url = raw_target.startswith(("http://", "https://", "git@", "ssh://", "github.com/"))
    is_gh_slug = (
        not is_url
        and "/" in raw_target
        and not raw_target.startswith(("agents/", "rules/", "skills/"))
        and not raw_target.endswith((".md", ".json"))
    )

    if is_url or is_gh_slug:
        cat = category or "community"
        return add_external_extension(
            source=raw_target,
            ext_dir=ext_dir,
            skill_name=skill_name,
            category=cat,
            lang=lang,
        )

    clean_target = raw_target.replace("\\", "/").strip("/")
    parts = clean_target.split("/")
    comp_type = parts[0] if parts[0] in ("agents", "rules", "skills") else None
    comp_id = parts[-1]
    cat = parts[1] if comp_type == "skills" and len(parts) > 2 else category

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
        print("    Use format: 'agents/<id>.md', 'rules/<id>', 'skills/<cat>/<id>', or Git URL.")
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
    assume_yes: bool = False,
    lang: str = "en",
) -> bool:
    """
    Checks and updates installed extensions in ext/.
    Prompts for confirmation before applying updates unless assume_yes is True.
    """
    if not ext_dir:
        print("[x] Error: Personal documents directory is not available.")
        return False

    print(f"-> {t('ext_checking_updates', lang)}")
    _all_statuses, updates = check_all_extensions_updates(ext_dir, app_config, timeout=5.0)

    if not updates:
        print(f"[OK] {t('ext_up_to_date', lang)}")
        return True

    print(f"\n[!] {len(updates)} update(s) available for installed extensions:")
    for u in updates:
        print(f"    * {u['name']} ({u['key']}): {u['current_sha'][:7]} -> {u['new_sha'][:7]}")

    # Prompt user for confirmation before applying updates
    if not assume_yes:
        if sys.stdin.isatty():
            try:
                ans = input(f"\n[?] Do you want to update these {len(updates)} extension(s)? [y/N]: ").strip().lower()
                if ans not in ("y", "yes", "s", "sim", "si", "sí"):
                    print("[i] Update cancelled by user.")
                    return True
            except (EOFError, KeyboardInterrupt):
                print("\n[i] Update cancelled.")
                return False
        else:
            print("[!] Running non-interactively. Pass --yes to apply updates automatically.")
            return False

    print(f"\n-> Applying {len(updates)} update(s)...")
    tree = fetch_remote_tree(app_config, timeout=5.0)

    success_count = 0
    for u in updates:
        source_type = u.get("source_type", "catalog")
        if source_type == "git":
            res = install_external_git_component(
                source=u["source_url"],
                ext_dir=ext_dir,
                skill_id=u["id"],
                category=u.get("category", "community"),
            )
            if res:
                success_count += 1
                print(f"  [+] Updated git extension: {u['name']} ({u['key']})")
        else:
            ok = install_remote_component(
                u["type"],
                u["id"],
                app_config,
                ext_dir,
                category=u.get("category"),
                tree_data=tree,
            )
            if ok:
                success_count += 1
                print(f"  [+] Updated catalog extension: {u['name']} ({u['key']})")

    print(f"[OK] Finished updating extensions ({success_count}/{len(updates)} updated successfully).")
    return True


def remove_extension(
    key: str,
    ext_dir: Path | None,
    lang: str = "en",
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
