#!/usr/bin/env python3
"""
Remote extensions management menu for omni-agents TUI.
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

        print("\n" + "=" * 65)
        print(f"  {t('ext_title', lang)}")
        print("=" * 65)
        print(f"  {t('ext_installed_count', lang, count=len(installed))}")
        repo_url = config.get("repository", {}).get(
            "url", "https://github.com/TheCheepeer/omni-agents"
        )
        print(f"  {t('repo_label', lang)}:   {repo_url}")
        print("-" * 65)
        print(f"  {t('ext_menu_download', lang)}")
        print(f"  {t('ext_menu_update', lang)}")
        print(f"  {t('ext_menu_remove', lang)}")
        print(f"  {t('ext_menu_back', lang)}")
        print("=" * 65)

        try:
            choice = input(f"\n{t('choose_option', lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return

        if choice in ("v", "voltar", "volver", ""):
            return

        elif choice == "1":
            print(f"\n-> {t('ext_connecting', lang)}")
            tree = fetch_remote_tree(config, timeout=2.5)
            if not tree:
                print(f"\n[!] {t('offline_notice', lang)}")
                print(f"    {t('offline_action_error', lang)}")
                try:
                    input(f"\n{t('press_enter', lang)}")
                except (EOFError, KeyboardInterrupt):
                    pass
                continue

            clear_screen()
            total_skills_count = sum(
                len(v) for v in tree["skills_by_category"].values()
            )
            print("\n" + "=" * 65)
            print(f"  {t('ext_download_title', lang)}")
            print("=" * 65)
            print(f"  {t('ext_agents_available', lang, count=len(tree['agents']))}")
            print(f"  {t('ext_rules_available', lang, count=len(tree['rules']))}")
            print(f"  {t('ext_skills_available', lang, count=total_skills_count)}")
            print(f"  {t('ext_menu_back', lang)}")
            print("=" * 65)

            try:
                sub_choice = input(f"\n{t('choose_option', lang)}").strip().lower()
            except (EOFError, KeyboardInterrupt):
                continue

            if sub_choice == "1":
                for idx, a in enumerate(tree["agents"], 1):
                    is_in = "[x]" if f"agents/{a['id']}" in installed else "[ ]"
                    print(f"  [{idx}] {is_in} {a['id']}")
                sel = input(f"\n{t('ext_prompt_download', lang)}").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(tree["agents"]):
                    target_agent = tree["agents"][int(sel) - 1]["id"]
                    print(f"-> {t('ext_downloading', lang, item=target_agent)}")
                    ok = install_remote_component(
                        "agents", target_agent, config, ext_dir, tree_data=tree
                    )
                    msg = (
                        t("ext_download_ok", lang, item=target_agent)
                        if ok
                        else t("ext_download_fail", lang, item=target_agent)
                    )
                    print(f"\n{'[OK]' if ok else '[x]'} {msg}")
                    try:
                        input(f"\n{t('press_enter', lang)}")
                    except (EOFError, KeyboardInterrupt):
                        pass

            elif sub_choice == "2":
                for idx, r in enumerate(tree["rules"], 1):
                    is_in = "[x]" if f"rules/{r['id']}" in installed else "[ ]"
                    print(f"  [{idx}] {is_in} {r['id']}")
                sel = input(f"\n{t('ext_prompt_download', lang)}").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(tree["rules"]):
                    target_rule = tree["rules"][int(sel) - 1]["id"]
                    print(f"-> {t('ext_downloading', lang, item=target_rule)}")
                    ok = install_remote_component(
                        "rules", target_rule, config, ext_dir, tree_data=tree
                    )
                    msg = (
                        t("ext_download_ok", lang, item=target_rule)
                        if ok
                        else t("ext_download_fail", lang, item=target_rule)
                    )
                    print(f"\n{'[OK]' if ok else '[x]'} {msg}")
                    try:
                        input(f"\n{t('press_enter', lang)}")
                    except (EOFError, KeyboardInterrupt):
                        pass

            elif sub_choice == "3":
                all_skills = []
                for cat, items in sorted(tree["skills_by_category"].items()):
                    for item in items:
                        all_skills.append((cat, item["id"]))
                for idx, (cat, s_id) in enumerate(all_skills, 1):
                    is_in = "[x]" if f"skills/{cat}/{s_id}" in installed else "[ ]"
                    print(f"  [{idx}] {is_in} {cat}/{s_id}")
                sel = input(f"\n{t('ext_prompt_download', lang)}").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(all_skills):
                    cat, s_id = all_skills[int(sel) - 1]
                    print(f"-> {t('ext_downloading', lang, item=f'{cat}/{s_id}')}")
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
                    print(f"\n{'[OK]' if ok else '[x]'} {msg}")
                    try:
                        input(f"\n{t('press_enter', lang)}")
                    except (EOFError, KeyboardInterrupt):
                        pass

        elif choice == "2":
            print(f"\n-> {t('ext_checking_updates', lang)}")
            updates = check_ext_updates(ext_dir, config, timeout=2.0)
            if not updates:
                print(f"[OK] {t('ext_up_to_date', lang)}")
            else:
                print(f"\n[!] {t('ext_updates_found', lang, count=len(updates))}")
                for u in updates:
                    print(
                        f"    * {u['key']} ({u['current_sha'][:7]} -> {u['new_sha'][:7]})"
                    )
                try:
                    up_choice = (
                        input(f"\n{t('ext_prompt_update_all', lang)}").strip().lower()
                    )
                except (EOFError, KeyboardInterrupt):
                    up_choice = "n"
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
                    print(f"\n[OK] {t('sync_success', lang)}")
            try:
                input(f"\n{t('press_enter', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass

        elif choice == "3":
            if not installed:
                print(f"\n[!] {t('ext_none_installed', lang)}")
                try:
                    input(f"\n{t('press_enter', lang)}")
                except (EOFError, KeyboardInterrupt):
                    pass
                continue

            items_list = list(installed.keys())
            print(f"\n{t('ext_installed_list_title', lang)}")
            for idx, k in enumerate(items_list, 1):
                print(f"  [{idx}] {k}")
            sel = input(f"\n{t('ext_prompt_remove', lang)}").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(items_list):
                key_to_del = items_list[int(sel) - 1]
                del installed[key_to_del]
                save_manifest(ext_dir, manifest)
                target_file = ext_dir / key_to_del
                if target_file.is_dir():
                    shutil.rmtree(target_file, ignore_errors=True)
                elif target_file.is_file():
                    target_file.unlink(missing_ok=True)
                print(f"\n[OK] {t('ext_removed_success', lang, key=key_to_del)}")
                try:
                    input(f"\n{t('press_enter', lang)}")
                except (EOFError, KeyboardInterrupt):
                    pass
