#!/usr/bin/env python3
"""
Main interactive terminal loop for omni-agents TUI.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from omni_agents.core.linker import apply_workspace_to_targets
from omni_agents.core.scanner import scan_component_sources, scan_repository
from omni_agents.core.workspace import (
    confirm_or_choose_project_workspace,
    has_graphical_display,
    resolve_workspace,
)
from omni_agents.env_paths import is_default_or_system_path, open_folder_in_explorer
from omni_agents.i18n import get_language_badge, resolve_language_code, t
from omni_agents.targets import load_workspace_state
from omni_agents.tui.agents_menu import handle_agents
from omni_agents.tui.clean_menu import handle_clean_workspace
from omni_agents.tui.common import clear_screen
from omni_agents.tui.extensions_menu import handle_remote_extensions
from omni_agents.tui.language_menu import handle_language_selection
from omni_agents.tui.rules_menu import handle_rules
from omni_agents.tui.skills_menu import handle_skills
from omni_agents.tui.source_menu import select_component_source
from omni_agents.tui.targets_menu import (
    handle_global_configuration,
    handle_target_selection,
)
from omni_agents.updater import __version__


def run_interactive_loop(
    target_path: Path | None,
    repo_root: Path,
    omni_docs_dir: Path,
    app_config: dict[str, Any],
    scanned: dict[str, Any],
    is_dev: bool,
    current_lang: str,
    explicit_lang: bool = False,
) -> None:
    """Main interactive terminal loop for navigating configuration menus."""
    while True:
        clear_screen()
        workspace_state = load_workspace_state(target_path) if target_path else {}
        if (
            not explicit_lang
            and not app_config.get("language")
            and workspace_state.get("language")
        ):
            current_lang = resolve_language_code(workspace_state["language"])

        active_tools_display = (
            ", ".join(workspace_state.get("active_targets", []))
            if workspace_state.get("active_targets")
            else t("none_default", current_lang)
        )
        target_display = (
            str(target_path) if target_path else t("not_defined", current_lang)
        )

        lang_badge = get_language_badge(current_lang)

        mode_label = (
            t("mode_dev", current_lang) if is_dev else t("mode_global", current_lang)
        )

        print("\n" + "=" * 65)
        print(f"  {t('app_title', current_lang)} (v{__version__})")
        print("=" * 65)
        print(f"  {t('mode_label', current_lang)}:          {mode_label}")
        print(f"  {t('target_workspace', current_lang)}:     {target_display}")
        if is_default_or_system_path(target_path):
            print()
            for wline in t(
                "default_path_warning_banner", current_lang, path=target_path
            ).splitlines():
                print(f"  {wline}")
        print(f"  {t('active_tools', current_lang)}: {active_tools_display}")
        print("-" * 65)
        print(f"  {t('menu_select_tools', current_lang)}")
        print(f"  {t('menu_global', current_lang)}")
        print(f"  {t('menu_agents', current_lang)}")
        print(f"  {t('menu_rules', current_lang)}")
        print(f"  {t('menu_skills', current_lang)}")
        print(f"  {t('menu_ext', current_lang)}")
        if has_graphical_display():
            print(f"  {t('menu_custom_folder', current_lang)}")
        else:
            print(f"  {t('menu_custom_folder_headless', current_lang)}")
        print(f"  {t('menu_sync', current_lang)}")
        print(f"  {t('menu_clean', current_lang)}")
        print(f"  {t('menu_lang', current_lang, current=lang_badge)}")
        print(f"  {t('menu_exit', current_lang)}")
        print("-" * 65)
        print(f"  {t('menu_change_workspace', current_lang)}")
        print("=" * 65)

        try:
            choice = input(f"\n{t('choose_option', current_lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            clear_screen()
            print(f"\n{t('exit_msg', current_lang)}\n")
            sys.exit(0)

        if choice in ("t", "tool", "tools", "ferramentas", "herramientas"):
            target_path = confirm_or_choose_project_workspace(
                target_path, lang=current_lang
            )
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
                workspace_state = load_workspace_state(target_path)
                handle_target_selection(
                    target_path, repo_root, scanned, workspace_state, lang=current_lang
                )

        elif choice in ("1", "global"):
            handle_global_configuration(
                repo_root,
                scanned,
                app_config=app_config,
                omni_docs_dir=omni_docs_dir,
                lang=current_lang,
            )

        elif choice in ("2", "agents", "agent", "agentes", "subagentes"):
            target_path = confirm_or_choose_project_workspace(
                target_path, lang=current_lang
            )
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
                workspace_state = load_workspace_state(target_path)
                sources = scan_component_sources(repo_root, documents_dir=omni_docs_dir)
                selected_scanned = select_component_source(
                    "agents",
                    sources,
                    is_dev=is_dev,
                    omni_docs_dir=omni_docs_dir,
                    target_path=target_path,
                    lang=current_lang,
                )
                if selected_scanned:
                    handle_agents(
                        target_path,
                        repo_root,
                        selected_scanned,
                        workspace_state,
                        all_scanned=sources["merged"],
                        lang=current_lang,
                    )

        elif choice in ("3", "rules", "rule", "regras", "reglas"):
            sources = scan_component_sources(repo_root, documents_dir=omni_docs_dir)
            selected_scanned = select_component_source(
                "rules",
                sources,
                is_dev=is_dev,
                omni_docs_dir=omni_docs_dir,
                target_path=target_path,
                lang=current_lang,
            )
            if selected_scanned:
                target_path = handle_rules(
                    target_path,
                    repo_root,
                    selected_scanned,
                    workspace_state,
                    app_config,
                    omni_docs_dir=omni_docs_dir,
                    all_scanned=sources["merged"],
                    lang=current_lang,
                )

        elif choice in ("4", "skills", "skill"):
            target_path = confirm_or_choose_project_workspace(
                target_path, lang=current_lang
            )
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
                workspace_state = load_workspace_state(target_path)
                sources = scan_component_sources(repo_root, documents_dir=omni_docs_dir)
                selected_scanned = select_component_source(
                    "skills",
                    sources,
                    is_dev=is_dev,
                    omni_docs_dir=omni_docs_dir,
                    target_path=target_path,
                    lang=current_lang,
                )
                if selected_scanned:
                    handle_skills(
                        target_path,
                        repo_root,
                        selected_scanned,
                        workspace_state,
                        all_scanned=sources["merged"],
                        lang=current_lang,
                    )

        elif choice in ("e", "ext", "extensoes", "extensiones", "extensions"):
            handle_remote_extensions(
                documents_dir=omni_docs_dir,
                config=app_config,
                lang=current_lang,
            )
            scanned = scan_repository(repo_root, documents_dir=omni_docs_dir)

        elif choice in ("o", "open", "custom", "pessoal", "personal"):
            if has_graphical_display():
                opened = open_folder_in_explorer(omni_docs_dir)
                if opened:
                    print(
                        f"\n[OK] {t('folder_opened', current_lang, path=omni_docs_dir)}"
                    )
                else:
                    print(
                        f"\n[i] {t('folder_path_info', current_lang, path=omni_docs_dir)}"
                    )
            else:
                print(
                    f"\n[i] {t('folder_path_info', current_lang, path=omni_docs_dir)}"
                )
            try:
                input(f"\n{t('press_enter', current_lang)}")
            except (EOFError, KeyboardInterrupt):
                pass

        elif choice in ("s", "sync", "sincronizar"):
            target_path = confirm_or_choose_project_workspace(
                target_path, lang=current_lang
            )
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
                workspace_state = load_workspace_state(target_path)
                active_tools = workspace_state.get("active_targets") or ["antigravity"]
                apply_workspace_to_targets(
                    target_path=target_path,
                    repo_root=repo_root,
                    scanned=scanned,
                    active_target_ids=active_tools,
                    selected_agent_ids=workspace_state.get("selected_agents", []),
                    selected_rule_ids=workspace_state.get("selected_rules")
                    if workspace_state.get("selected_rules") is not None
                    else [r["id"] for r in scanned["rules"]],
                    selected_skills_dict=workspace_state.get("selected_skills", {}),
                    lang=current_lang,
                )
                print(f"\n[OK] {t('sync_success', current_lang)}")
                try:
                    input(f"\n{t('press_enter', current_lang)}")
                except (EOFError, KeyboardInterrupt):
                    pass

        elif choice in ("c", "clean", "limpar", "limpiar"):
            target_path = confirm_or_choose_project_workspace(
                target_path, lang=current_lang
            )
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
                workspace_state = load_workspace_state(target_path)
                handle_clean_workspace(target_path, workspace_state, lang=current_lang)

        elif choice in ("l", "lang", "idioma", "language"):
            current_lang = handle_language_selection(
                repo_root=repo_root,
                target_path=target_path,
                current_lang=current_lang,
                app_config=app_config,
                workspace_state=workspace_state,
                omni_docs_dir=omni_docs_dir,
            )

        elif choice in ("5", "sair", "exit", "q", "quit", "salir"):
            clear_screen()
            print(f"\n{t('exit_msg', current_lang)}\n")
            sys.exit(0)

        elif choice in ("w", "workspace"):
            new_target = resolve_workspace(None, lang=current_lang)
            if new_target:
                target_path = new_target

        else:
            print(f"[!] {t('invalid_option', current_lang)}")
