#!/usr/bin/env python3
"""
Skills management and category selection menu for omni-agents TUI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.core.linker import apply_workspace_to_targets
from omni_agents.i18n import t
from omni_agents.tui.common import clear_screen, confirm_exit_unsaved


def handle_category_submenu(
    cat_name: str, skills: list[dict], selected_set: set[str], lang: str = "en"
) -> set[str]:
    """Dynamic submenu to manage skills within a specific category."""
    current_selected = set(selected_set)

    while True:
        clear_screen()
        print("\n" + "-" * 65)
        print(f"  {t('cat_title', lang, cat=cat_name.upper(), count=len(skills))}")
        print("-" * 65)

        for idx, skill in enumerate(skills, 1):
            is_sel = "[x]" if skill["id"] in current_selected else "[ ]"
            desc_preview = (
                skill["description"][:58] + "..."
                if len(skill["description"]) > 58
                else skill["description"]
            )
            print(f"  [{idx:2d}] {is_sel} {skill['id']:<24} - {desc_preview}")

        print("\n" + "-" * 65)
        print(t("cat_nav", lang))
        print("-" * 65)

        try:
            choice = input(f"\n{t('your_choice', lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice in ("v", "voltar", "volver", ""):
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
        print(f"[!] {t('no_skills_found', lang)}")
        try:
            input(f"\n{t('press_enter_menu', lang)}")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    raw_saved = current_state.get("selected_skills", {})
    selected_by_cat: dict[str, set[str]] = {k: set(v) for k, v in raw_saved.items()}
    initial_by_cat = {k: set(v) for k, v in selected_by_cat.items()}
    categories = sorted(skills_by_cat.keys())

    while True:
        clear_screen()
        total_selected = sum(len(v) for v in selected_by_cat.values())
        cats_with_selection = len([c for c, v in selected_by_cat.items() if v])

        print("\n" + "=" * 65)
        print(f"  {t('skills_title', lang)}")
        print("=" * 65)
        print(f"{t('target_workspace', lang)}: {target_path}\n")
        print(t("categories_available", lang))

        for idx, cat_name in enumerate(categories, 1):
            skills = skills_by_cat[cat_name]
            sel_count = len(selected_by_cat.get(cat_name, set()))
            status = (
                f"({sel_count}/{len(skills)})" if sel_count > 0 else f"({len(skills)})"
            )
            print(f"  [{idx:2d}] {cat_name.upper():<16} {status}")

        print(
            f"\n{t('total_skills_sel', lang, skills=total_selected, cats=cats_with_selection)}"
        )
        print("\n" + "-" * 65)
        print(t("skills_nav", lang))
        print("-" * 65)

        try:
            choice = input(f"\n{t('choose_option', lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice in ("v", "voltar", "volver"):
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
            print(f"\n[OK] {t('skills_synced', lang)}")
            try:
                input(f"\n{t('press_enter_menu', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
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
                print(f"[!] {t('invalid_option', lang)}")
        elif choice in skills_by_cat:
            cat_name = choice
            skills = skills_by_cat[cat_name]
            curr_sel = selected_by_cat.get(cat_name, set())
            updated = handle_category_submenu(cat_name, skills, curr_sel, lang=lang)
            if updated:
                selected_by_cat[cat_name] = updated
            else:
                selected_by_cat.pop(cat_name, None)
