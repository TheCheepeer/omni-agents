#!/usr/bin/env python3
"""
Agents selection and activation menu for omni-agents TUI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.core.linker import apply_workspace_to_targets
from omni_agents.i18n import t
from omni_agents.tui.common import clear_screen, confirm_exit_unsaved


def handle_agents(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
    all_scanned: dict[str, Any] | None = None,
    lang: str = "en",
) -> None:
    """Option: Subagents selection and activation for target workspace."""
    agents = scanned["agents"]
    if not agents:
        print(f"[!] {t('no_agents_found', lang)}")
        try:
            input(f"\n{t('press_enter_menu', lang)}")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    curr_selected = set(current_state.get("selected_agents", []))
    initial_selected = set(curr_selected)

    while True:
        clear_screen()
        print("\n" + "=" * 65)
        print(f"  {t('agents_title', lang)}")
        print("=" * 65)
        print(f"{t('target_workspace', lang)}: {target_path}\n")

        for idx, agent in enumerate(agents, 1):
            is_sel = "[x]" if agent["id"] in curr_selected else "[ ]"
            desc = agent.get("description", "")
            desc_preview = f" - {desc[:60]}..." if desc else ""
            print(f"  [{idx:2d}] {is_sel} {agent['id']:<28}{desc_preview}")

        print("\n" + "-" * 65)
        print(t("how_to_select_agents", lang))
        print("-" * 65)

        try:
            user_input = input(f"\n{t('your_choice', lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return

        if user_input in ("v", "voltar", "volver"):
            if curr_selected != initial_selected and not confirm_exit_unsaved(
                lang=lang
            ):
                continue
            return

        if user_input in ("s", "salvar", "save", "guardar"):
            current_state["selected_agents"] = sorted(curr_selected)
            apply_workspace_to_targets(
                target_path=target_path,
                repo_root=repo_root,
                scanned=all_scanned or scanned,
                active_target_ids=current_state.get("active_targets", ["antigravity"]),
                selected_agent_ids=current_state["selected_agents"],
                selected_rule_ids=current_state.get("selected_rules", []),
                selected_skills_dict=current_state.get("selected_skills", {}),
                lang=lang,
            )
            print(f"\n[OK] {t('agents_activated', lang, count=len(curr_selected))}")
            try:
                input(f"\n{t('press_enter_menu', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
            return

        if user_input == "":
            continue

        if user_input == "all":
            curr_selected = {agent["id"] for agent in agents}
            print(f"  [+] {t('all_agents_marked', lang)}")
        elif user_input in ("limpar", "clear", "limpiar"):
            curr_selected.clear()
            print(f"  [i] {t('all_agents_cleared', lang)}")
        else:
            tokens = [
                token.strip()
                for token in user_input.replace(";", ",").split(",")
                if token.strip()
            ]
            for token in tokens:
                if token.isdigit():
                    num = int(token)
                    if 1 <= num <= len(agents):
                        aid = agents[num - 1]["id"]
                        if aid in curr_selected:
                            curr_selected.remove(aid)
                        else:
                            curr_selected.add(aid)
                else:
                    matched = next(
                        (
                            a
                            for a in agents
                            if a["id"].lower() == token
                            or a["id"].lower().replace(".md", "") == token
                        ),
                        None,
                    )
                    if matched:
                        aid = matched["id"]
                        if aid in curr_selected:
                            curr_selected.remove(aid)
                        else:
                            curr_selected.add(aid)
