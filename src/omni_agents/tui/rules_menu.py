#!/usr/bin/env python3
"""
Rules management and configuration menu for omni-agents TUI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.core.config import save_app_config
from omni_agents.core.linker import (
    apply_global_rules_to_targets,
    apply_workspace_to_targets,
)
from omni_agents.core.workspace import (
    confirm_or_choose_project_workspace,
    resolve_workspace,
)
from omni_agents.env_paths import is_default_or_system_path
from omni_agents.i18n import t
from omni_agents.targets.base import get_link_target, is_link
from omni_agents.tui.common import clear_screen, confirm_exit_unsaved


def select_global_rule_profile(
    rules: list[dict[str, Any]], lang: str = "en"
) -> dict[str, Any] | None:
    """Prompts the user to select which AGENTS.md rule profile will be applied globally."""
    if not rules:
        return None
    if len(rules) == 1:
        return rules[0]

    clear_screen()
    print("\n" + "=" * 65)
    print(f"  {t('global_rule_select_title', lang)}")
    print("=" * 65)
    print(f"{t('global_rule_select_prompt', lang)}\n")

    for idx, r in enumerate(rules, 1):
        desc = r.get("description", "")
        desc_preview = f" - {desc[:52]}..." if desc else ""
        print(f"  [{idx}] {r['id']:<18}{desc_preview}")

    print("\n" + "-" * 65)
    print(t("global_rule_select_help", lang))
    print("-" * 65)

    while True:
        try:
            choice = input(f"\n{t('your_choice', lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return None

        if choice in ("v", "voltar", "volver", "q", "exit", "sair", "salir", ""):
            return None

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(rules):
                return rules[idx - 1]

        for r in rules:
            if choice == r["id"].lower():
                return r

        print(f"[!] {t('invalid_option', lang)}")


def handle_rules(
    target_path: Path | None,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
    app_config: dict[str, Any],
    omni_docs_dir: Path | None = None,
    all_scanned: dict[str, Any] | None = None,
    lang: str = "en",
) -> Path | None:
    """
    Dedicated screen for configuring and managing rules: Workspace (local) vs Global (machine-wide).
    Allows user to explicitly mark/uncheck (desmarcar) rules for either scope, ensuring
    rules are never linked to global automatically.
    """
    rules = scanned.get("rules", [])
    if not rules:
        print(f"[!] {t('no_rules_found', lang)}")
        try:
            input(f"\n{t('press_enter_menu', lang)}")
        except (EOFError, KeyboardInterrupt):
            pass
        return target_path

    available_rule_ids = {r["id"] for r in rules}

    # 1. Workspace selection resolution
    curr_selected_workspace: set[str] = set()
    if target_path:
        if (
            "selected_rules" in current_state
            and current_state["selected_rules"] is not None
        ):
            saved_ws = set(current_state["selected_rules"])
            if "AGENTS.md" in saved_ws and "AGENTS.md" not in available_rule_ids:
                saved_ws.remove("AGENTS.md")
                if "pt-br-dev" in available_rule_ids:
                    saved_ws.add("pt-br-dev")
            curr_selected_workspace = saved_ws.intersection(available_rule_ids)
        else:
            ws_rules_dir = target_path / ".agents" / "rules"
            if ws_rules_dir.exists() and ws_rules_dir.is_dir():
                for item in ws_rules_dir.glob("*.md"):
                    if item.stem in available_rule_ids:
                        curr_selected_workspace.add(item.stem)

    # 2. Global selection resolution & legacy link detection
    curr_selected_global: set[str] = set()
    has_legacy_global_junction = False
    gemini_rules_path = Path.home() / ".gemini" / "config" / "rules"

    if "global_rules" in app_config and app_config["global_rules"] is not None:
        curr_selected_global = set(app_config["global_rules"]).intersection(
            available_rule_ids
        )
    else:
        if gemini_rules_path.exists():
            if is_link(gemini_rules_path):
                target_link = get_link_target(gemini_rules_path)
                try:
                    repo_rules_norm = (repo_root / "rules").resolve().as_posix().lower()
                    target_link_norm = (
                        target_link.resolve().as_posix().lower() if target_link else ""
                    )
                    if target_link and (
                        target_link_norm == repo_rules_norm
                        or target_link_norm.endswith("/rules")
                    ):
                        has_legacy_global_junction = True
                        curr_selected_global = set(available_rule_ids)
                    else:
                        for rid in available_rule_ids:
                            if target_link and rid in str(target_link):
                                curr_selected_global.add(rid)
                except OSError:
                    pass
            elif gemini_rules_path.is_dir():
                for f in gemini_rules_path.glob("*.md"):
                    if f.stem in available_rule_ids:
                        curr_selected_global.add(f.stem)

    initial_selected_workspace = set(curr_selected_workspace)
    initial_selected_global = set(curr_selected_global)

    while True:
        clear_screen()
        print("\n" + "=" * 65)
        print(f"  {t('rules_mgmt_title', lang)}")
        print("=" * 65)
        ws_display = str(target_path) if target_path else t("not_defined", lang)
        print(f"  {t('target_workspace', lang)}: {ws_display}")
        if is_default_or_system_path(target_path):
            print(
                f"  {t('default_path_warning_banner', lang, path=target_path).splitlines()[0]}"
            )
        print(f"  {t('global_dir_label', lang)}:     ~/.gemini/config/rules\n")

        ws_names = (
            ", ".join(sorted(curr_selected_workspace))
            if curr_selected_workspace
            else t("rules_none_active", lang)
        )
        glob_names = (
            ", ".join(sorted(curr_selected_global))
            if curr_selected_global
            else t("rules_none_active", lang)
        )
        print(f"  * {t('rules_status_workspace', lang)}: [{ws_names}]")
        if has_legacy_global_junction and curr_selected_global == available_rule_ids:
            print(f"  * {t('rules_status_global', lang)}:  [{glob_names}] (!)")
            print(f"    [!] {t('rules_legacy_link_warning', lang)}")
        else:
            print(f"  * {t('rules_status_global', lang)}:  [{glob_names}]")

        print("\n" + t("rules_options_header", lang))
        print(
            f"  {'#':<4} {'Rule':<16} {'Workspace (Local)':<20} {'Global (Machine)':<18} Description"
        )
        print("  " + "-" * 75)
        for idx, rule in enumerate(rules, 1):
            rid = rule["id"]
            is_ws = (
                f"[x] {t('rules_status_active', lang)}"
                if rid in curr_selected_workspace
                else f"[ ] {t('rules_status_unchecked', lang)}"
            )
            is_glob = (
                f"[x] {t('rules_status_active', lang)}"
                if rid in curr_selected_global
                else f"[ ] {t('rules_status_unchecked', lang)}"
            )
            desc = rule.get("description", "")
            desc_prev = (
                f" - {desc[:32]}..."
                if len(desc) > 32
                else (f" - {desc}" if desc else "")
            )
            print(f"  [{idx:2d}] {rid:<16} {is_ws:<20} {is_glob:<18}{desc_prev}")

        print("\n" + "-" * 65)
        print(t("rules_commands_help", lang))
        print("-" * 65)

        try:
            choice = input(f"\n{t('your_choice', lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return target_path

        if choice in ("v", "voltar", "volver"):
            changed = (curr_selected_workspace != initial_selected_workspace) or (
                curr_selected_global != initial_selected_global
            )
            if changed and not confirm_exit_unsaved(lang=lang):
                continue
            return target_path

        if choice == "":
            continue

        if choice in ("s", "salvar", "save", "guardar"):
            if curr_selected_workspace:
                if not target_path:
                    target_path = resolve_workspace(None, lang=lang)
                    if not target_path:
                        continue
                elif is_default_or_system_path(target_path):
                    target_path = confirm_or_choose_project_workspace(
                        target_path, lang=lang
                    )
                    if not target_path:
                        continue

            # 1. Apply workspace rules
            if target_path:
                current_state["selected_rules"] = sorted(curr_selected_workspace)
                active_tools = current_state.get("active_targets") or ["antigravity"]
                apply_workspace_to_targets(
                    target_path=target_path,
                    repo_root=repo_root,
                    scanned=all_scanned or scanned,
                    active_target_ids=active_tools,
                    selected_agent_ids=current_state.get("selected_agents", []),
                    selected_rule_ids=current_state["selected_rules"],
                    selected_skills_dict=current_state.get("selected_skills", {}),
                    lang=lang,
                )

            # 2. Apply global rules
            app_config["global_rules"] = sorted(curr_selected_global)
            save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)
            apply_global_rules_to_targets(
                repo_root=repo_root,
                scanned=all_scanned or scanned,
                selected_global_rule_ids=sorted(curr_selected_global),
                lang=lang,
            )

            print(f"\n[OK] {t('rules_saved_ok', lang)}")
            print(
                f"     {t('rules_saved_ws_summary', lang, count=len(curr_selected_workspace))}"
            )
            print(
                f"     {t('rules_saved_glob_summary', lang, count=len(curr_selected_global))}"
            )
            try:
                input(f"\n{t('press_enter_menu', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
            return target_path

        # Clear / uncheck commands
        if choice in ("clean-w", "clear-w", "limpar-w", "desmarcar-w"):
            curr_selected_workspace.clear()
            continue

        if choice in ("clean-g", "clear-g", "limpar-g", "desmarcar-g"):
            curr_selected_global.clear()
            has_legacy_global_junction = False
            continue

        if choice in (
            "clean-all",
            "clear-all",
            "limpar-tudo",
            "desmarcar-tudo",
            "clean",
            "clear",
            "limpar",
            "desmarcar",
        ):
            curr_selected_workspace.clear()
            curr_selected_global.clear()
            has_legacy_global_junction = False
            continue

        # Select all commands
        if choice in ("all-w", "todas-w"):
            if not target_path:
                target_path = resolve_workspace(None, lang=lang)
            curr_selected_workspace = {r["id"] for r in rules}
            continue

        if choice in ("all-g", "todas-g"):
            curr_selected_global = {r["id"] for r in rules}
            has_legacy_global_junction = False
            continue

        if choice in ("all", "todas"):
            if not target_path:
                target_path = resolve_workspace(None, lang=lang)
            curr_selected_workspace = {r["id"] for r in rules}
            continue

        # Granular tokens
        raw_tokens = [
            t_tok.strip()
            for t_tok in choice.replace(";", ",").replace(" ", ",").split(",")
            if t_tok.strip()
        ]

        for token in raw_tokens:
            if token.startswith(("w:", "w")) and len(token) > 1:
                sub = token.lstrip("w:")
                if sub.isdigit():
                    num = int(sub)
                    if 1 <= num <= len(rules):
                        rid = rules[num - 1]["id"]
                        if not target_path:
                            target_path = resolve_workspace(None, lang=lang)
                        if rid in curr_selected_workspace:
                            curr_selected_workspace.remove(rid)
                        else:
                            curr_selected_workspace.add(rid)
                else:
                    matched = next(
                        (r["id"] for r in rules if r["id"].lower() == sub), None
                    )
                    if matched:
                        if not target_path:
                            target_path = resolve_workspace(None, lang=lang)
                        if matched in curr_selected_workspace:
                            curr_selected_workspace.remove(matched)
                        else:
                            curr_selected_workspace.add(matched)

            elif token.startswith(("g:", "g")) and len(token) > 1:
                sub = token.lstrip("g:")
                has_legacy_global_junction = False
                if sub.isdigit():
                    num = int(sub)
                    if 1 <= num <= len(rules):
                        rid = rules[num - 1]["id"]
                        if rid in curr_selected_global:
                            curr_selected_global.remove(rid)
                        else:
                            curr_selected_global.add(rid)
                else:
                    matched = next(
                        (r["id"] for r in rules if r["id"].lower() == sub), None
                    )
                    if matched:
                        if matched in curr_selected_global:
                            curr_selected_global.remove(matched)
                        else:
                            curr_selected_global.add(matched)

            elif token.isdigit():
                num = int(token)
                if 1 <= num <= len(rules):
                    rid = rules[num - 1]["id"]
                    if not target_path:
                        target_path = resolve_workspace(None, lang=lang)
                    if rid in curr_selected_workspace:
                        curr_selected_workspace.remove(rid)
                    else:
                        curr_selected_workspace.add(rid)

            else:
                matched = next(
                    (r["id"] for r in rules if r["id"].lower() == token), None
                )
                if matched:
                    if not target_path:
                        target_path = resolve_workspace(None, lang=lang)
                    if matched in curr_selected_workspace:
                        curr_selected_workspace.remove(matched)
                    else:
                        curr_selected_workspace.add(matched)
