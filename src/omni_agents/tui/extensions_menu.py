#!/usr/bin/env python3
"""
Remote extensions management menu for omni-agents TUI.
Rendered using modern action cards, tables, and status banners.
Supports browsing official catalog, adding external Git skills,
and interactive update checks with confirmation.
"""

from __future__ import annotations

import shutil
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
            t("ext_menu_add_external", lang),
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

        elif choice in ("2", "a", "add"):
            console.print(
                f"\n[bold white]{escape(t('ext_prompt_enter_url', lang))}[/bold white]"
            )
            raw_url = get_styled_choice(t("prompt_path", lang)).strip()
            if not raw_url or raw_url.lower() in ("v", "voltar", "volver", "q"):
                continue

            console.print(
                f"\n[dim]{escape(t('ext_prompt_enter_skill_name', lang))}[/dim]"
            )
            raw_skill = get_styled_choice(t("your_choice", lang)).strip()
            skill_id = raw_skill if raw_skill and raw_skill.lower() not in ("v", "voltar", "volver") else None

            render_banner(t("ext_downloading", lang, item=raw_url), level="info")
            result = install_external_git_component(
                source=raw_url,
                ext_dir=ext_dir,
                skill_id=skill_id,
                category="community",
                timeout=30.0,
            )
            if result:
                item_name = result.get("name") or result["id"]
                render_banner(
                    t("ext_download_ok", lang, item=item_name),
                    level="success",
                )
            else:
                render_banner(
                    t("ext_download_fail", lang, item=raw_url),
                    level="error",
                )
            press_enter_to_continue(t("press_enter", lang))

        elif choice in ("3", "u", "update"):
            render_banner(t("ext_checking_updates", lang), level="info")
            _all_statuses, updates = check_all_extensions_updates(ext_dir, config, timeout=3.5)
            if not updates:
                render_banner(t("ext_up_to_date", lang), level="success")
            else:
                render_banner(
                    t("ext_updates_found", lang, count=len(updates)), level="warning"
                )

                update_table = Table(box=box.ROUNDED, expand=True)
                update_table.add_column("Extension", style="bold white")
                update_table.add_column("Type", style="dim", width=10)
                update_table.add_column("Current SHA", style="dim yellow", width=12)
                update_table.add_column("New SHA", style="bold green", width=12)

                for u in updates:
                    update_table.add_row(
                        escape(u["key"]),
                        escape(u["type"]),
                        escape(u["current_sha"][:7]),
                        escape(u["new_sha"][:7]),
                    )

                console.print(update_table)

                up_choice = get_styled_choice(t("ext_prompt_update_all", lang), default="y")
                if up_choice in ("", "s", "sim", "y", "yes", "si", "sí"):
                    tree = fetch_remote_tree(config, timeout=3.0)
                    for u in updates:
                        if u.get("source_type") == "git":
                            install_external_git_component(
                                source=u["source_url"],
                                ext_dir=ext_dir,
                                skill_id=u["id"],
                                category=u.get("category", "community"),
                            )
                        else:
                            install_remote_component(
                                u["type"],
                                u["id"],
                                config,
                                ext_dir,
                                category=u.get("category"),
                                tree_data=tree,
                            )
                    render_banner(t("sync_success", lang), level="success")
                else:
                    render_banner(t("ext_update_aborted", lang), level="info")
            press_enter_to_continue(t("press_enter", lang))

        elif choice in ("4", "r", "remove"):
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
