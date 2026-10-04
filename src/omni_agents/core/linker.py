#!/usr/bin/env python3
"""
Linker module for omni-agents.
Coordinates applying rules, agents, and skills across workspace and global targets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.i18n import t
from omni_agents.targets import get_target, save_workspace_state


def apply_workspace_to_targets(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    active_target_ids: list[str],
    selected_agent_ids: list[str],
    selected_rule_ids: list[str],
    selected_skills_dict: dict[str, list[str] | set[str]],
    lang: str = "en",
) -> bool:
    """Applies rules, agents, and skills across all active target tools."""
    if not active_target_ids:
        print(f"  [!] {t('no_active_tools', lang)}")
        return False

    agents_map = {a["id"]: a for a in scanned["agents"]}
    rules_map = {r["id"]: r for r in scanned["rules"]}

    normalized_rule_ids = []
    for rid in selected_rule_ids:
        if rid in rules_map:
            normalized_rule_ids.append(rid)
        elif rid == "AGENTS.md" and rules_map:
            fallback = (
                "pt-br-dev"
                if "pt-br-dev" in rules_map
                else next(iter(rules_map.keys()))
            )
            normalized_rule_ids.append(fallback)

    active_agents = [agents_map[aid] for aid in selected_agent_ids if aid in agents_map]
    active_rules = [rules_map[rid] for rid in normalized_rule_ids if rid in rules_map]

    skills_by_cat: dict[str, set[str]] = {
        k: set(v) for k, v in selected_skills_dict.items() if v
    }
    # Always bundle omni-tune as the mandatory built-in driver skill
    skills_by_cat.setdefault("meta", set()).add("omni-tune")

    print(f"\n-> {t('applying_configs', lang, count=len(active_target_ids))}")
    for t_id in active_target_ids:
        adapter = get_target(t_id)
        if adapter:
            print(
                f"\n  [{t('processing', lang)}] {adapter.display_name} ({adapter.target_id})..."
            )
            try:
                adapter.configure_workspace(
                    target_path=target_path,
                    repo_root=repo_root,
                    scanned=scanned,
                    agents=active_agents,
                    rules=active_rules,
                    skills_by_cat=skills_by_cat,
                    lang=lang,
                )
            except (OSError, RuntimeError, ValueError, KeyError) as e:
                print(
                    f"  [x] {t('error_applying', lang, target=adapter.display_name, error=e)}"
                )

    state_to_save = {
        "language": lang,
        "active_targets": active_target_ids,
        "selected_agents": selected_agent_ids,
        "selected_rules": selected_rule_ids,
        "selected_skills": {k: sorted(v) for k, v in skills_by_cat.items()},
    }
    save_workspace_state(target_path, state_to_save)
    return True


def apply_global_rules_to_targets(
    repo_root: Path,
    scanned: dict[str, Any],
    selected_global_rule_ids: list[str],
    lang: str = "en",
) -> None:
    """Applies global rules to all tools that support global configurations (Antigravity, Claude)."""
    rules_map = {r["id"]: r for r in scanned.get("rules", [])}
    active_global_rules = [
        rules_map[rid] for rid in selected_global_rule_ids if rid in rules_map
    ]

    # 1. Google Antigravity
    ag_target = get_target("antigravity")
    if ag_target and hasattr(ag_target, "apply_global_rules"):
        rules_dst = Path.home() / ".gemini" / "config" / "rules"
        ag_target.apply_global_rules(rules_dst, active_global_rules, lang=lang)

    # 2. Claude Code
    claude_target = get_target("claude")
    if claude_target:
        claude_target.configure_global(
            repo_root=repo_root,
            lang=lang,
            selected_rules=active_global_rules,
        )
