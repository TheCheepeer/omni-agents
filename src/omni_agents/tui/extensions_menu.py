#!/usr/bin/env python3
"""
Remote extensions management menu for omni-agents TUI.
Rendered using modern action cards, tables, and status banners.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from omni_agents.i18n import t
from omni_agents.remote_sync import (
    check_ext_updates,
    fetch_remote_tree,
    install_remote_component,
    load_manifest,
    save_manifest,
)
from omni_agents.tui.common import clear_screen
from omni_agents.tui.theme import (
    COLOR_DANGER,
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
    render_menu_card,
)


def handle_remote_extensions(
    documents_dir: Path,
    config: dict[str, Any],
    lang: str = "en",
) -> None:
    """Submenu for managing remote repository extensions in ext/."""
    ext_dir = documents_dir / "ext"

    while True:
        clear_screen()
        manifest = load_manifest(ext_dir)
        installed = manifest.get("installed", {})
        repo_url = config.get("repository", {}).get(
            "url", "https://github.com/TheCheepeer/omni-agents"
        )

        # Header Info Grid
        info_grid = Table.grid(padding=(0, 2))
        info_grid.add_column(style="dim", width=18)
        info_grid.add_column()
        info_grid.add_row(
            t("ext_installed_label", lang),
            f"[bold {COLOR_SUCCESS}]● {len(installed)} {t('ext_items_installed', lang)}[/bold {COLOR_SUCCESS}]",
        )
        info_grid.add_row(t("ext_repo_url_label", lang), f"[dim]{escape(repo_url)}[/dim]")

        header_panel = Panel(
            info_grid,
            title=f"[bold {COLOR_PRIMARY}]{escape(t('ext_title', lang))}[/bold {COLOR_PRIMARY}]",
            title_align="left",
            box=box.ROUNDED,
            border_style="dim cyan",
            padding=(1, 2),
        )
        console.print(header_panel)

        menu_items = [
            t("ext_menu_download", lang),
            t("ext_menu_update", lang),
            t("ext_menu_remove", lang),
            t("ext_menu_back", lang),
        ]

        render_menu_card(
            title=t("ext_actions_title", lang),
            items=menu_items,
            footer_hint=t("hint_ext_actions", lang),
        )

        choice = get_styled_choice(t("choose_option", lang))

        if choice in ("v", "voltar", "volver", "q", ""):
            return

        elif choice == "1":
            render_banner(t("ext_connecting", lang), level="info")
            tree = fetch_remote_tree(config, timeout=2.5)
            if not tree:
                render_banner(t("offline_notice", lang), level="warning")
                render_banner(t("offline_action_error", lang), level="error")
                press_enter_to_continue(t("press_enter", lang))
                continue

            clear_screen()
            total_skills_count = sum(
                len(v) for v in tree["skills_by_category"].values()
            )

            download_items = [
                ("1", t("menu_agents_short", lang), t("remote_available", lang, count=len(tree["agents"]))),
                ("2", t("menu_rules_short", lang), t("remote_available", lang, count=len(tree["rules"]))),
                ("3", t("menu_skills_short", lang), t("remote_available", lang, count=total_skills_count)),
                ("v", t("ext_menu_back", lang), t("cancel", lang)),
            ]

            render_menu_card(
                title=t("ext_download_title", lang),
                items=download_items,
                footer_hint=t("hint_browse_category", lang),
            )

            sub_choice = get_styled_choice(t("choose_option", lang))

            if sub_choice == "1":
                items_table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
                items_table.add_column("Index", style="dim", width=6, justify="right")
                items_table.add_column("Status", width=6)
                items_table.add_column("Name", style="bold white")

                for idx, a in enumerate(tree["agents"], 1):
                    is_in = f"agents/{a['id']}" in installed
                    status = (
                        f"[bold {COLOR_SUCCESS}]\\[x][/bold {COLOR_SUCCESS}]"
                        if is_in
                        else f"[{COLOR_MUTED}]\\[ ][/{COLOR_MUTED}]"
                    )
                    items_table.add_row(escape(f"[{idx}]"), status, escape(a["id"]))

                panel = Panel(
                    items_table,
                    title=f"[bold white]{escape(t('remote_subagents_title', lang))}[/bold white]",
                    box=box.ROUNDED,
                    border_style="dim cyan",
                    padding=(1, 1),
                )
                console.print(panel)

                sel = get_styled_choice(t("ext_prompt_download", lang))
                if sel.isdigit() and 1 <= int(sel) <= len(tree["agents"]):
                    target_agent = tree["agents"][int(sel) - 1]["id"]
                    render_banner(
                        t("ext_downloading", lang, item=target_agent), level="info"
                    )
                    ok = install_remote_component(
                        "agents", target_agent, config, ext_dir, tree_data=tree
                    )
                    msg = (
                        t("ext_download_ok", lang, item=target_agent)
                        if ok
                        else t("ext_download_fail", lang, item=target_agent)
                    )
                    render_banner(msg, level="success" if ok else "error")
                    press_enter_to_continue(t("press_enter", lang))

            elif sub_choice == "2":
                items_table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
                items_table.add_column("Index", style="dim", width=6, justify="right")
                items_table.add_column("Status", width=6)
                items_table.add_column("Name", style="bold white")

                for idx, r in enumerate(tree["rules"], 1):
                    is_in = f"rules/{r['id']}" in installed
                    status = (
                        f"[bold {COLOR_SUCCESS}]\\[x][/bold {COLOR_SUCCESS}]"
                        if is_in
                        else f"[{COLOR_MUTED}]\\[ ][/{COLOR_MUTED}]"
                    )
                    items_table.add_row(escape(f"[{idx}]"), status, escape(r["id"]))

                panel = Panel(
                    items_table,
                    title=f"[bold white]{escape(t('remote_rules_title', lang))}[/bold white]",
                    box=box.ROUNDED,
                    border_style="dim cyan",
                    padding=(1, 1),
                )
                console.print(panel)

                sel = get_styled_choice(t("ext_prompt_download", lang))
                if sel.isdigit() and 1 <= int(sel) <= len(tree["rules"]):
                    target_rule = tree["rules"][int(sel) - 1]["id"]
                    render_banner(
                        t("ext_downloading", lang, item=target_rule), level="info"
                    )
                    ok = install_remote_component(
                        "rules", target_rule, config, ext_dir, tree_data=tree
                    )
                    msg = (
                        t("ext_download_ok", lang, item=target_rule)
                        if ok
                        else t("ext_download_fail", lang, item=target_rule)
                    )
                    render_banner(msg, level="success" if ok else "error")
                    press_enter_to_continue(t("press_enter", lang))

            elif sub_choice == "3":
                all_skills = []
                for cat, items in sorted(tree["skills_by_category"].items()):
                    for item in items:
                        all_skills.append((cat, item["id"]))

                items_table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
                items_table.add_column("Index", style="dim", width=6, justify="right")
                items_table.add_column("Status", width=6)
                items_table.add_column("Category", style=COLOR_MUTED, width=14)
                items_table.add_column("Skill ID", style="bold white")

                for idx, (cat, s_id) in enumerate(all_skills, 1):
                    is_in = f"skills/{cat}/{s_id}" in installed
                    status = (
                        f"[bold {COLOR_SUCCESS}]\\[x][/bold {COLOR_SUCCESS}]"
                        if is_in
                        else f"[{COLOR_MUTED}]\\[ ][/{COLOR_MUTED}]"
                    )
                    items_table.add_row(
                        escape(f"[{idx}]"), status, escape(cat), escape(s_id)
                    )

                panel = Panel(
                    items_table,
                    title=f"[bold white]{escape(t('remote_skills_title', lang))}[/bold white]",
                    box=box.ROUNDED,
                    border_style="dim cyan",
                    padding=(1, 1),
                )
                console.print(panel)

                sel = get_styled_choice(t("ext_prompt_download", lang))
                if sel.isdigit() and 1 <= int(sel) <= len(all_skills):
                    cat, s_id = all_skills[int(sel) - 1]
                    render_banner(
                        t("ext_downloading", lang, item=f"{cat}/{s_id}"), level="info"
                    )
                    ok = install_remote_component(
                        "skills",
                        s_id,
                        config,
                        ext_dir,
                        category=cat,
                        tree_data=tree,
                    )
                    msg = (
                        t("ext_download_ok", lang, item=s_id)
                        if ok
                        else t("ext_download_fail", lang, item=s_id)
                    )
                    render_banner(msg, level="success" if ok else "error")
                    press_enter_to_continue(t("press_enter", lang))

        elif choice == "2":
            render_banner(t("ext_checking_updates", lang), level="info")
            updates = check_ext_updates(ext_dir, config, timeout=2.0)
            if not updates:
                render_banner(t("ext_up_to_date", lang), level="success")
            else:
                render_banner(
                    t("ext_updates_found", lang, count=len(updates)), level="warning"
                )
                for u in updates:
                    console.print(
                        f"    [dim]●[/dim] [white]{escape(u['key'])}[/white] [dim]({u['current_sha'][:7]} -> {u['new_sha'][:7]})[/dim]"
                    )
                up_choice = get_styled_choice(t("ext_prompt_update_all", lang), default="y")
                if up_choice in ("", "s", "sim", "y", "yes", "si", "sí"):
                    tree = fetch_remote_tree(config, timeout=3.0)
                    for u in updates:
                        install_remote_component(
                            u["type"],
                            u["id"],
                            config,
                            ext_dir,
                            category=u.get("category"),
                            tree_data=tree,
                        )
                    render_banner(t("sync_success", lang), level="success")
            press_enter_to_continue(t("press_enter", lang))

        elif choice == "3":
            if not installed:
                render_banner(t("ext_none_installed", lang), level="warning")
                press_enter_to_continue(t("press_enter", lang))
                continue

            items_list = list(installed.keys())
            table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
            table.add_column("Index", style="dim", width=6, justify="right")
            table.add_column("Extension Key", style="bold white")

            for idx, k in enumerate(items_list, 1):
                table.add_row(escape(f"[{idx}]"), escape(k))

            panel = Panel(
                table,
                title=f"[bold {COLOR_DANGER}]{escape(t('ext_installed_list_title', lang))}[/bold {COLOR_DANGER}]",
                box=box.ROUNDED,
                border_style="dim red",
                padding=(1, 1),
            )
            console.print(panel)

            sel = get_styled_choice(t("ext_prompt_remove", lang))
            if sel.isdigit() and 1 <= int(sel) <= len(items_list):
                key_to_del = items_list[int(sel) - 1]
                del installed[key_to_del]
                save_manifest(ext_dir, manifest)
                target_file = ext_dir / key_to_del
                if target_file.is_dir():
                    shutil.rmtree(target_file, ignore_errors=True)
                elif target_file.is_file():
                    target_file.unlink(missing_ok=True)
                render_banner(
                    t("ext_removed_success", lang, key=key_to_del), level="success"
                )
                press_enter_to_continue(t("press_enter", lang))
