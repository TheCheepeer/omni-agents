#!/usr/bin/env python3
"""
Skills management and category selection menu for omni-agents TUI.
Rendered using styled category cards, badge counts, and selection panels.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.core.linker import apply_workspace_to_targets
from omni_agents.i18n import t
from omni_agents.tui.common import clear_screen, confirm_exit_unsaved
from omni_agents.tui.theme import (
    COLOR_MUTED,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    Panel,
    Table,
    box,
    console,
    escape,
    get_styled_choice,
    press_enter_to_continue,
    render_banner,
    render_selection_card,
)


def handle_category_submenu(
    cat_name: str, skills: list[dict[str, Any]], selected_set: set[str], lang: str = "en"
) -> set[str]:
    """Dynamic submenu to manage skills within a specific category."""
    current_selected = set(selected_set)

    while True:
        clear_screen()
        render_selection_card(
            title=f"{t('table_col_category', lang).upper()}: {cat_name.upper()}",
            items=skills,
            instructions=t("cat_nav", lang),
            selected_ids=current_selected,
            id_key="id",
            name_key="id",
            desc_key="description",
            footer_hint=t("hint_cat_toggle", lang),
            subtitle=t("cat_skills_available", lang, count=len(skills)),
        )

        choice = get_styled_choice(t("your_choice", lang))

        if choice in ("v", "voltar", "volver", "q", ""):
            break

        if choice == "all":
            for skill in skills:
                current_selected.add(skill["id"])
        elif choice in ("limpar", "clear", "limpiar"):
            current_selected.clear()
        else:
            tokens = [
                token.strip()
                for token in choice.replace(";", ",").split(",")
                if token.strip()
            ]
            for token in tokens:
                if token.isdigit():
                    num = int(token)
                    if 1 <= num <= len(skills):
                        skill_id = skills[num - 1]["id"]
                        if skill_id in current_selected:
                            current_selected.remove(skill_id)
                        else:
                            current_selected.add(skill_id)
                else:
                    matched = next(
                        (s for s in skills if s["id"].lower() == token), None
                    )
                    if matched:
                        skill_id = matched["id"]
                        if skill_id in current_selected:
                            current_selected.remove(skill_id)
                        else:
                            current_selected.add(skill_id)

    return current_selected


def handle_skills(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
    all_scanned: dict[str, Any] | None = None,
    lang: str = "en",
) -> None:
    """Option: Modular skills category menu with dedicated submenus."""
    skills_by_cat = scanned["skills_by_category"]
    if not skills_by_cat:
        render_banner(t("no_skills_found", lang), level="warning")
        press_enter_to_continue(t("press_enter_menu", lang))
        return

    raw_saved = current_state.get("selected_skills", {})
    selected_by_cat: dict[str, set[str]] = {k: set(v) for k, v in raw_saved.items()}
    initial_by_cat = {k: set(v) for k, v in selected_by_cat.items()}
    categories = sorted(skills_by_cat.keys())

    while True:
        clear_screen()
        total_selected = sum(len(v) for v in selected_by_cat.values())
        cats_with_selection = len([c for c, v in selected_by_cat.items() if v])

        # Category Table
        cat_table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
        cat_table.add_column(t("table_col_index", lang), style="dim", width=6, justify="right")
        cat_table.add_column(t("table_col_category", lang), style="bold white", width=22)
        cat_table.add_column(t("table_col_status", lang), width=18)
        cat_table.add_column(t("table_col_description", lang), style=COLOR_MUTED)

        for idx, cat_name in enumerate(categories, 1):
            skills = skills_by_cat[cat_name]
            sel_count = len(selected_by_cat.get(cat_name, set()))
            if sel_count > 0:
                status_markup = (
                    f"[bold {COLOR_SUCCESS}]● {sel_count}/{len(skills)} {t('status_active', lang).lower()}[/bold {COLOR_SUCCESS}]"
                )
            else:
                status_markup = f"[{COLOR_MUTED}]○ {len(skills)} {t('status_available', lang).lower()}[/{COLOR_MUTED}]"

            preview_skills = ", ".join(s["id"] for s in skills[:3])
            if len(skills) > 3:
                preview_skills += f" {t('more_items', lang, count=len(skills) - 3)}"

            cat_table.add_row(
                escape(f"[{idx:2d}]"),
                escape(cat_name.upper()),
                status_markup,
                escape(preview_skills),
            )

        summary_text = t(
            "total_skills_sel",
            lang,
            skills=total_selected,
            cats=cats_with_selection,
        )

        categories_panel = Panel(
            cat_table,
            title=f"[bold white]{escape(t('skills_title', lang))}[/bold white]",
            title_align="left",
            subtitle=f"[bold {COLOR_PRIMARY}]{escape(summary_text)}[/bold {COLOR_PRIMARY}]",
            subtitle_align="right",
            box=box.ROUNDED,
            border_style="dim cyan",
            padding=(1, 1),
        )
        console.print(categories_panel)

        instructions_panel = Panel(
            f"[{COLOR_MUTED}]{escape(t('skills_nav', lang))}[/{COLOR_MUTED}]",
            box=box.ROUNDED,
            border_style="dim",
            padding=(0, 1),
        )
        console.print(instructions_panel)

        choice = get_styled_choice(t("choose_option", lang))

        if choice in ("v", "voltar", "volver", "q"):
            has_changed = any(
                selected_by_cat.get(cat, set()) != initial_by_cat.get(cat, set())
                for cat in set(selected_by_cat.keys()) | set(initial_by_cat.keys())
            )
            if has_changed and not confirm_exit_unsaved(lang=lang):
                continue
            break

        if choice == "":
            continue

        if choice in ("s", "salvar", "save", "guardar"):
            current_state["selected_skills"] = {
                k: sorted(v) for k, v in selected_by_cat.items() if v
            }
            apply_workspace_to_targets(
                target_path=target_path,
                repo_root=repo_root,
                scanned=all_scanned or scanned,
                active_target_ids=current_state.get("active_targets", ["antigravity"]),
                selected_agent_ids=current_state.get("selected_agents", []),
                selected_rule_ids=current_state.get("selected_rules", []),
                selected_skills_dict=current_state["selected_skills"],
                lang=lang,
            )
            render_banner(t("skills_synced", lang), level="success")
            press_enter_to_continue(t("press_enter_menu", lang))
            break

        if choice == "all":
            for cat_name, skills in skills_by_cat.items():
                selected_by_cat[cat_name] = {s["id"] for s in skills}

        elif choice in ("limpar", "clear", "limpiar"):
            selected_by_cat.clear()

        elif choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(categories):
                cat_name = categories[num - 1]
                skills = skills_by_cat[cat_name]
                curr_sel = selected_by_cat.get(cat_name, set())
                updated = handle_category_submenu(cat_name, skills, curr_sel, lang=lang)
                if updated:
                    selected_by_cat[cat_name] = updated
                else:
                    selected_by_cat.pop(cat_name, None)
            else:
                render_banner(t("invalid_option", lang), level="warning")
        elif choice in skills_by_cat:
            cat_name = choice
            skills = skills_by_cat[cat_name]
            curr_sel = selected_by_cat.get(cat_name, set())
            updated = handle_category_submenu(cat_name, skills, curr_sel, lang=lang)
            if updated:
                selected_by_cat[cat_name] = updated
            else:
                selected_by_cat.pop(cat_name, None)
