#!/usr/bin/env python3
"""
Rules management and configuration menu for omni-agents TUI.
Rendered using modern rounded panels, comparison tables, and status badges.
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
from omni_agents.tui.theme import (
    COLOR_MUTED,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    Panel,
    Table,
    Text,
    box,
    console,
    escape,
    get_styled_choice,
    press_enter_to_continue,
    render_banner,
    render_selection_card,
)


def select_global_rule_profile(
    rules: list[dict[str, Any]], lang: str = "en"
) -> dict[str, Any] | None:
    """Prompts the user to select which AGENTS.md rule profile will be applied globally."""
    if not rules:
        return None
    if len(rules) == 1:
        return rules[0]

    clear_screen()
    rule_items = [
        {"id": r["id"], "name": r["id"], "description": r.get("description", "")}
        for r in rules
    ]

    render_selection_card(
        title=t("global_rule_select_title", lang),
        items=rule_items,
        instructions=t("global_rule_select_help", lang),
        selected_ids=set(),
        id_key="id",
        name_key="name",
        desc_key="description",
        footer_hint=t("hint_rule_select", lang),
        subtitle=t("global_rule_select_prompt", lang),
    )

    while True:
        choice = get_styled_choice(t("your_choice", lang))

        if choice in ("v", "voltar", "volver", "q", "exit", "sair", "salir", ""):
            return None

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(rules):
                return rules[idx - 1]

        for r in rules:
            if choice == r["id"].lower():
                return r

        render_banner(t("invalid_option", lang), level="warning")


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
        render_banner(t("no_rules_found", lang), level="warning")
        press_enter_to_continue(t("press_enter_menu", lang))
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
        ws_display = str(target_path) if target_path else t("not_defined", lang)

        # Header Info Table
        info_grid = Table.grid(padding=(0, 2))
        info_grid.add_column(style="dim", width=18)
        info_grid.add_column()
        info_grid.add_row(t("target_workspace", lang), f"[bold white]{escape(ws_display)}[/bold white]")
        info_grid.add_row(t("global_dir_label", lang), "[dim]~/.gemini/config/rules[/dim]")

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

        info_grid.add_row(
            f"[bold {COLOR_SUCCESS}]●[/bold {COLOR_SUCCESS}] {t('rules_status_workspace', lang)}",
            f"[bold {COLOR_SUCCESS}][{escape(ws_names)}][/bold {COLOR_SUCCESS}]",
        )

        if has_legacy_global_junction and curr_selected_global == available_rule_ids:
            info_grid.add_row(
                f"[bold {COLOR_WARNING}]![/bold {COLOR_WARNING}] {t('rules_status_global', lang)}",
                f"[bold {COLOR_WARNING}][{escape(glob_names)}] (!)[/bold {COLOR_WARNING}]",
            )
        else:
            info_grid.add_row(
                f"[bold {COLOR_PRIMARY}]●[/bold {COLOR_PRIMARY}] {t('rules_status_global', lang)}",
                f"[{COLOR_PRIMARY}][{escape(glob_names)}][/{COLOR_PRIMARY}]",
            )

        header_panel = Panel(
            info_grid,
            title=f"[bold {COLOR_PRIMARY}]{escape(t('rules_mgmt_title', lang))}[/bold {COLOR_PRIMARY}]",
            title_align="left",
            box=box.ROUNDED,
            border_style="dim cyan",
            padding=(1, 2),
        )
        console.print(header_panel)

        if is_default_or_system_path(target_path):
            render_banner(
                t("default_path_warning_banner", lang, path=target_path).splitlines()[0],
                level="warning",
            )

        # Rules Comparison Table
        table = Table(box=None, show_header=True, padding=(0, 1), expand=True)
        table.add_column(t("table_col_index", lang), style="dim", width=4, justify="right")
        table.add_column(t("table_col_rule", lang), style="bold white", width=18)
        table.add_column(t("table_col_workspace", lang), width=18, justify="center")
        table.add_column(t("table_col_global", lang), width=18, justify="center")
        table.add_column(t("table_col_description", lang), style=COLOR_MUTED)

        for idx, rule in enumerate(rules, 1):
            rid = rule["id"]
            if rid in curr_selected_workspace:
                is_ws = f"[bold {COLOR_SUCCESS}]\\[x] {t('rules_status_active', lang)}[/bold {COLOR_SUCCESS}]"
            else:
                is_ws = f"[{COLOR_MUTED}]\\[ ] {t('rules_status_unchecked', lang)}[/{COLOR_MUTED}]"

            if rid in curr_selected_global:
                is_glob = f"[bold {COLOR_PRIMARY}]\\[x] {t('rules_status_active', lang)}[/bold {COLOR_PRIMARY}]"
            else:
                is_glob = f"[{COLOR_MUTED}]\\[ ] {t('rules_status_unchecked', lang)}[/{COLOR_MUTED}]"

            desc = rule.get("description", "")
            desc_prev = desc[:45] + "..." if len(desc) > 45 else desc

            table.add_row(
                escape(f"[{idx:2d}]"),
                escape(rid),
                is_ws,
                is_glob,
                escape(desc_prev),
            )

        rules_panel = Panel(
            table,
            title=f"[bold white]{escape(t('rules_options_header', lang))}[/bold white]",
            title_align="left",
            subtitle=f"[{COLOR_MUTED}]{escape(t('rules_table_hint', lang))}[/{COLOR_MUTED}]",
            subtitle_align="right",
            box=box.ROUNDED,
            border_style="dim white",
            padding=(1, 1),
        )
        console.print(rules_panel)

        commands_panel = Panel(
            Text(t("rules_commands_help", lang), style="dim"),
            box=box.ROUNDED,
            border_style="dim",
            padding=(0, 1),
        )
        console.print(commands_panel)

        choice = get_styled_choice(t("your_choice", lang))

        if choice in ("v", "voltar", "volver", "q"):
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
                active_tools = current_state.get("active_targets", [])
                if active_tools:
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
                else:
                    render_banner(t("no_tools_selected_warning", lang), level="warning")
                    press_enter_to_continue(t("press_enter", lang))

            # 2. Apply global rules
            app_config["global_rules"] = sorted(curr_selected_global)
            save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)
            apply_global_rules_to_targets(
                repo_root=repo_root,
                scanned=all_scanned or scanned,
                selected_global_rule_ids=sorted(curr_selected_global),
                lang=lang,
            )

            render_banner(t("rules_saved_ok", lang), level="success")
            render_banner(
                t("rules_saved_ws_summary", lang, count=len(curr_selected_workspace)),
                level="info",
            )
            render_banner(
                t("rules_saved_glob_summary", lang, count=len(curr_selected_global)),
                level="info",
            )
            press_enter_to_continue(t("press_enter_menu", lang))
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
