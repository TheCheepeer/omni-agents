#!/usr/bin/env python3
"""
Sync and configuration command handlers for omni-agents CLI.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from omni_agents.core.config import save_app_config
from omni_agents.core.linker import apply_workspace_to_targets
from omni_agents.env_paths import is_default_or_system_path
from omni_agents.i18n import t
from omni_agents.targets import (
    get_all_targets,
    get_available_target_ids,
    get_target,
    load_workspace_state,
    save_workspace_state,
)


def configure_global_cli(
    target_tool: str | None,
    rule_profile: str | None,
    assume_yes: bool,
    app_config: dict[str, Any],
    scanned: dict[str, Any],
    repo_root: Path,
    omni_docs_dir: Path | None,
    current_lang: str = "en",
) -> None:
    """Executes global rules configuration across global-capable tools."""
    tools = (
        [
            get_target(t)
            for t in [
                x.strip().lower()
                for x in target_tool.replace(";", ",").split(",")
                if x.strip()
            ]
        ]
        if target_tool and target_tool != "all"
        else [target for target in get_all_targets() if target.supports_global]
    )
    rules = scanned.get("rules", [])
    rules_map = {r["id"]: r for r in rules}
    selected_rules = []
    if rule_profile:
        if rule_profile.lower() in ("none", "clear", "limpar"):
            selected_rules = []
        elif rule_profile.lower() in ("all", "todas"):
            selected_rules = list(rules)
        else:
            rule_tokens = [
                tok.strip()
                for tok in rule_profile.replace(";", ",").split(",")
                if tok.strip()
            ]
            for tok in rule_tokens:
                matched = next(
                    (r for r in rules if r["id"].lower() == tok.lower()), None
                )
                if matched:
                    if matched not in selected_rules:
                        selected_rules.append(matched)
                else:
                    print(f"[!] Rule profile '{tok}' not found.")
                    print(f"    Available: {', '.join(r['id'] for r in rules)}")
                    sys.exit(1)
    else:
        configured_ids = app_config.get("global_rules", [])
        selected_rules = [rules_map[rid] for rid in configured_ids if rid in rules_map]

    for target in tools:
        if target:
            print(f"\n-> {t('linking', current_lang, tool=target.display_name)}")
            target.configure_global(
                repo_root,
                lang=current_lang,
                selected_rules=selected_rules,
                assume_yes=assume_yes,
            )
    app_config["global_rules"] = [r["id"] for r in selected_rules]
    save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)


def sync_workspace_cli(
    target_path: Path,
    target_tool: str | None,
    agents_arg: str | None,
    rule_profile_arg: str | None,
    skills_arg: str | None,
    assume_yes: bool,
    scanned: dict[str, Any],
    repo_root: Path,
    current_lang: str = "en",
    app_config: dict[str, Any] | None = None,
) -> None:
    """Executes workspace configuration & sync via CLI flags."""
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
    active_tools = state.get("active_targets", [])
    if target_tool:
        if target_tool.lower() == "all":
            active_tools = get_available_target_ids()
        else:
            tool_tokens = [
                t_str.strip().lower()
                for t_str in target_tool.replace(";", ",").split(",")
                if t_str.strip()
            ]
            matched_tools = [
                t_str for t_str in tool_tokens if get_target(t_str) is not None
            ]
            if matched_tools:
                active_tools = matched_tools
            else:
                print(
                    f"[!] Warning: No recognized tools in '{target_tool}'. Supported: {', '.join(get_available_target_ids())}"
                )
    if not active_tools and app_config:
        active_tools = [
            t_id
            for t_id in app_config.get("active_targets", [])
            if get_target(t_id) is not None
        ]
    if not active_tools:
        print(f"\n[x] {t('no_tools_selected_warning', current_lang)}\n")
        sys.exit(1)

    # Agents
    if agents_arg is not None:
        if agents_arg.lower() in ("none", "clear", "limpar"):
            selected_agent_ids = []
        elif agents_arg.lower() in ("all", "todos"):
            selected_agent_ids = [a["id"] for a in scanned.get("agents", [])]
        else:
            agent_tokens = [
                tok.strip()
                for tok in agents_arg.replace(";", ",").split(",")
                if tok.strip()
            ]
            selected_agent_ids = []
            available_agents = scanned.get("agents", [])
            for tok in agent_tokens:
                matched = next(
                    (
                        a
                        for a in available_agents
                        if a["id"].lower() == tok.lower()
                        or a["id"].lower().replace(".md", "") == tok.lower()
                    ),
                    None,
                )
                if matched:
                    if matched["id"] not in selected_agent_ids:
                        selected_agent_ids.append(matched["id"])
                else:
                    print(
                        f"[!] Warning: Subagent '{tok}' not found in available agents."
                    )
    else:
        selected_agent_ids = state.get("selected_agents", [])

    # Rules
    if rule_profile_arg is not None:
        if rule_profile_arg.lower() in ("none", "clear", "limpar"):
            selected_rule_ids = []
        elif rule_profile_arg.lower() in ("all", "todas"):
            selected_rule_ids = [r["id"] for r in scanned.get("rules", [])]
        else:
            rule_tokens = [
                tok.strip()
                for tok in rule_profile_arg.replace(";", ",").split(",")
                if tok.strip()
            ]
            selected_rule_ids = []
            available_rules = scanned.get("rules", [])
            for tok in rule_tokens:
                matched = next(
                    (r for r in available_rules if r["id"].lower() == tok.lower()),
                    None,
                )
                if matched:
                    if matched["id"] not in selected_rule_ids:
                        selected_rule_ids.append(matched["id"])
                else:
                    print(f"[!] Warning: Rule '{tok}' not found in available rules.")
    else:
        selected_rule_ids = (
            state.get("selected_rules")
            if state.get("selected_rules") is not None
            else [r["id"] for r in scanned.get("rules", [])]
        )

    # Skills
    skills_by_cat = scanned.get("skills_by_category", {})
    if skills_arg is not None:
        if skills_arg.lower() in ("none", "clear", "limpar"):
            selected_skills_dict = {}
        elif skills_arg.lower() in ("all", "todas"):
            selected_skills_dict = {
                cat: [s["id"] for s in s_list] for cat, s_list in skills_by_cat.items()
            }
        else:
            selected_skills_dict = {}
            skill_tokens = [
                tok.strip()
                for tok in skills_arg.replace(";", ",").split(",")
                if tok.strip()
            ]
            for tok in skill_tokens:
                if "/" in tok:
                    c_part, s_part = tok.split("/", 1)
                    c_match = next(
                        (c for c in skills_by_cat if c.lower() == c_part.lower()),
                        None,
                    )
                    if c_match:
                        s_match = next(
                            (
                                s
                                for s in skills_by_cat[c_match]
                                if s["id"].lower() == s_part.lower()
                            ),
                            None,
                        )
                        if s_match:
                            selected_skills_dict.setdefault(c_match, set()).add(
                                s_match["id"]
                            )
                        else:
                            print(
                                f"[!] Warning: Skill '{s_part}' not found in category '{c_match}'."
                            )
                    else:
                        print(f"[!] Warning: Skill category '{c_part}' not found.")
                else:
                    c_match = next(
                        (c for c in skills_by_cat if c.lower() == tok.lower()),
                        None,
                    )
                    if c_match:
                        selected_skills_dict[c_match] = {
                            s["id"] for s in skills_by_cat[c_match]
                        }
                    else:
                        found = False
                        for cat_name, cat_skills in skills_by_cat.items():
                            s_match = next(
                                (
                                    s
                                    for s in cat_skills
                                    if s["id"].lower() == tok.lower()
                                ),
                                None,
                            )
                            if s_match:
                                selected_skills_dict.setdefault(cat_name, set()).add(
                                    s_match["id"]
                                )
                                found = True
                                break
                        if not found:
                            print(
                                f"[!] Warning: Skill or category '{tok}' not found in available skills."
                            )
            selected_skills_dict = {
                k: sorted(v) for k, v in selected_skills_dict.items() if v
            }
    else:
        selected_skills_dict = state.get("selected_skills", {})

    apply_workspace_to_targets(
        target_path=target_path,
        repo_root=repo_root,
        scanned=scanned,
        active_target_ids=active_tools,
        selected_agent_ids=selected_agent_ids,
        selected_rule_ids=selected_rule_ids,
        selected_skills_dict=selected_skills_dict,
        lang=current_lang,
    )

    state["active_targets"] = active_tools
    state["selected_agents"] = selected_agent_ids
    state["selected_rules"] = selected_rule_ids
    state["selected_skills"] = selected_skills_dict
    save_workspace_state(target_path, state)
    print(f"\n[OK] {t('sync_success', current_lang)}")
