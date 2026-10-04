#!/usr/bin/env python3
"""
List and discovery command handlers for omni-agents.
"""

from __future__ import annotations

from typing import Any

from omni_agents.targets import get_all_targets


def list_tools() -> None:
    """Lists all supported AI coding tool adapters."""
    print("\nSupported Tools:")
    for target in get_all_targets():
        supports_glob = (
            "[Global + Workspace]" if target.supports_global else "[Workspace]"
        )
        print(f"  * {target.target_id:<14} - {target.display_name:<24} {supports_glob}")


def list_agents(scanned: dict[str, Any]) -> None:
    """Lists available subagents."""
    agents = scanned.get("agents", [])
    print("\nAvailable Subagents:")
    if not agents:
        print("  (None found)")
    for a in agents:
        desc = a.get("description", "")
        desc_str = f" - {desc[:70]}..." if desc else ""
        print(f"  * {a['id']:<28}{desc_str}")


def list_rules(scanned: dict[str, Any]) -> None:
    """Lists available rule profiles."""
    rules = scanned.get("rules", [])
    print("\nAvailable Rules:")
    if not rules:
        print("  (None found)")
    for r in rules:
        desc = r.get("description", "")
        desc_str = f" - {desc[:70]}..." if desc else ""
        print(f"  * {r['id']:<24}{desc_str}")


def list_skills(scanned: dict[str, Any]) -> None:
    """Lists available modular skills by category."""
    skills_cat = scanned.get("skills_by_category", {})
    print("\nAvailable Modular Skills by Category:")
    if not skills_cat:
        print("  (None found)")
    for cat, items in sorted(skills_cat.items()):
        print(f"\n  [{cat}] ({len(items)} skills):")
        for item in items:
            desc = item.get("description", "")
            desc_str = f" - {desc[:60]}..." if desc else ""
            print(f"    * {item['id']:<24}{desc_str}")


def list_workspaces(omni_docs_dir: Any = None, lang: str = "en") -> None:
    """Lists all tracked workspaces and their configured AI tools."""
    from omni_agents.core.workspace import load_tracked_workspaces
    from omni_agents.i18n import t

    workspaces = load_tracked_workspaces(omni_docs_dir)
    print(f"\n{t('tracked_workspaces_title', lang)}:")
    if not workspaces:
        print(f"  {t('no_tracked_workspaces', lang)}")
        return

    for item in workspaces:
        p = item.get("path", "")
        tools = item.get("active_tools", [])
        tools_str = f" [{', '.join(tools)}]" if tools else " [no active tools]"
        print(f"  * {p:<50}{tools_str}")
