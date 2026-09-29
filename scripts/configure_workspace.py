#!/usr/bin/env python3
"""
omni-agents: Multi-Tool Agent, Rules & Skills Configurator.
Cross-platform (Windows, Linux, macOS) using only Python standard library.

Supported Tools:
- Google Antigravity
- Claude Code (Anthropic)
- Cursor IDE
- GitHub Copilot
- Universal (AGENTS.md)
- Kiro
- OpenCode
- Codex (OpenAI)
- Multi-Tool (All simultaneously)
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

# Ensures scripts/ is in sys.path for safe relative target imports
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Ensures UTF-8 terminal encoding for stable accented character support
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from env_paths import (
    ensure_omni_documents_structure,
    is_dev_mode,
    open_folder_in_explorer,
    save_omni_config,
)
from i18n import (
    get_available_languages,
    get_language_badge,
    get_language_name,
    resolve_language_code,
    t,
)
from remote_sync import (
    check_ext_updates,
    fetch_remote_tree,
    install_remote_component,
    load_manifest,
    save_manifest,
)
from targets import (
    get_all_targets,
    get_available_target_ids,
    get_target,
    load_workspace_state,
    save_workspace_state,
)
from targets.base import get_link_target, is_link, parse_frontmatter
from updater import __version__, check_for_updates, prompt_and_upgrade


def load_app_config(
    repo_root: Path, omni_docs_dir: Path | None = None
) -> dict[str, Any]:
    """Loads persistent application preferences from Documents or repo root."""
    if omni_docs_dir:
        cfg_file = omni_docs_dir / "config.json"
        if cfg_file.exists():
            try:
                return json.loads(cfg_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
    cfg_file = repo_root / "config.json"
    if cfg_file.exists():
        try:
            return json.loads(cfg_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_app_config(
    repo_root: Path,
    config: dict[str, Any],
    omni_docs_dir: Path | None = None,
):
    """Persists application preferences to Documents/omni-agents/config.json and repo root."""
    if omni_docs_dir:
        save_omni_config(config)
    if is_dev_mode(repo_root):
        cfg_file = repo_root / "config.json"
        try:
            cfg_file.write_text(
                json.dumps(config, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except OSError:
            pass


def has_graphical_display() -> bool:
    """Checks if a graphical display environment is available."""
    if sys.platform.startswith("win") or sys.platform.startswith("darwin"):
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def is_gui_available() -> bool:
    """Checks if both graphical display and Tkinter module are available."""
    if not has_graphical_display():
        return False
    return importlib.util.find_spec("tkinter") is not None


def clear_screen():
    """Cross-platform terminal screen cleaner."""
    os.system("cls" if sys.platform.startswith("win") else "clear")


def pick_directory_gui(
    title: str = "Select Project Repository Directory",
) -> str | None:
    """Opens native GUI file dialog (Tkinter) for directory selection."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return None

    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", True)
        root.update()
        root.focus_force()
        selected_path = filedialog.askdirectory(parent=root, title=title)
        root.destroy()
        return selected_path if selected_path else None
    except (tk.TclError, RuntimeError, OSError):
        return None


def _scan_source_directory(source_dir: Path) -> dict[str, Any]:
    """Scans a directory containing skills/, agents/, and/or rules/ folders."""
    skills_map: dict[str, dict[str, dict[str, Any]]] = {}
    agents_map: dict[str, dict[str, Any]] = {}
    rules_map: dict[str, dict[str, Any]] = {}

    # 1. Skills
    skills_dir = source_dir / "skills"
    if skills_dir.exists() and skills_dir.is_dir():
        for category_dir in sorted(skills_dir.iterdir()):
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                cat_name = category_dir.name
                for item in sorted(category_dir.iterdir()):
                    skill_md = item / "SKILL.md"
                    if item.is_dir() and skill_md.exists():
                        name, desc = parse_frontmatter(skill_md)
                        skills_map.setdefault(cat_name, {})[item.name] = {
                            "id": item.name,
                            "name": name,
                            "description": desc,
                            "path": item.resolve(),
                        }

    # 2. Subagents
    agents_dir = source_dir / "agents"
    if agents_dir.exists() and agents_dir.is_dir():
        for item in sorted(agents_dir.glob("*.md")):
            name, desc = parse_frontmatter(item)
            agents_map[item.name] = {
                "id": item.name,
                "name": name,
                "description": desc,
                "path": item.resolve(),
            }

    # 3. Rules (Supports rules/<profile>/AGENTS.md and legacy rules/*.md)
    rules_dir = source_dir / "rules"
    if rules_dir.exists() and rules_dir.is_dir():
        for item in sorted(rules_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                rule_file = None
                for candidate in (
                    "AGENTS.md",
                    "agents.md",
                    "Agents.md",
                    "RULE.md",
                    "rule.md",
                    f"{item.name}.md",
                ):
                    candidate_path = item / candidate
                    if candidate_path.exists() and candidate_path.is_file():
                        rule_file = candidate_path
                        break
                if rule_file:
                    name, desc = parse_frontmatter(rule_file)
                    if not desc:
                        try:
                            for line in rule_file.read_text(
                                encoding="utf-8"
                            ).splitlines():
                                sline = line.strip()
                                if sline and not sline.startswith(("#", "---")):
                                    desc = sline
                                    break
                        except (OSError, UnicodeDecodeError):
                            desc = ""
                    rules_map[item.name] = {
                        "id": item.name,
                        "name": name or item.name,
                        "description": desc,
                        "path": rule_file.resolve(),
                        "dir_path": item.resolve(),
                    }
            elif (
                item.is_file()
                and item.suffix == ".md"
                and not item.name.startswith(".")
            ):
                name, desc = parse_frontmatter(item)
                if not desc:
                    try:
                        for line in item.read_text(encoding="utf-8").splitlines():
                            sline = line.strip()
                            if sline and not sline.startswith(("#", "---")):
                                desc = sline
                                break
                    except (OSError, UnicodeDecodeError):
                        desc = ""
                rules_map[item.stem] = {
                    "id": item.stem,
                    "name": name or item.stem,
                    "description": desc,
                    "path": item.resolve(),
                    "dir_path": item.parent.resolve(),
                }

    return {"skills": skills_map, "agents": agents_map, "rules": rules_map}


def _format_layer_data(layer_raw: dict[str, Any]) -> dict[str, Any]:
    skills_by_cat: dict[str, list[dict[str, Any]]] = {}
    for cat_name, cat_skills in sorted(layer_raw["skills"].items()):
        if cat_skills:
            skills_by_cat[cat_name] = sorted(
                cat_skills.values(), key=lambda x: str(x["id"])
            )
    return {
        "skills_by_category": skills_by_cat,
        "agents": sorted(layer_raw["agents"].values(), key=lambda x: str(x["id"])),
        "rules": sorted(layer_raw["rules"].values(), key=lambda x: str(x["id"])),
    }


def scan_component_sources(
    repo_root: Path, documents_dir: Path | None = None
) -> dict[str, Any]:
    """
    Dynamically scans and isolates components across layers:
    - 'repo': Base repository (ONLY when running in dev mode from a cloned Git repo)
    - 'ext': Remote extensions (Documents/omni-agents/ext)
    - 'custom': User personal overrides (Documents/omni-agents/custom)
    - 'merged': Consolidated components across active layers
    """
    empty_raw: dict[str, Any] = {"skills": {}, "agents": {}, "rules": {}}

    is_dev = is_dev_mode(repo_root)
    repo_raw = (
        _scan_source_directory(repo_root)
        if is_dev and repo_root.exists() and repo_root.is_dir()
        else empty_raw
    )

    ext_dir = (documents_dir / "ext") if documents_dir else None
    ext_raw = (
        _scan_source_directory(ext_dir)
        if ext_dir and ext_dir.exists() and ext_dir.is_dir()
        else empty_raw
    )

    custom_dir = (documents_dir / "custom") if documents_dir else None
    custom_raw = (
        _scan_source_directory(custom_dir)
        if custom_dir and custom_dir.exists() and custom_dir.is_dir()
        else empty_raw
    )

    merged_skills: dict[str, dict[str, dict[str, Any]]] = {}
    merged_agents: dict[str, dict[str, Any]] = {}
    merged_rules: dict[str, dict[str, Any]] = {}

    def _merge_layer(layer_data: dict[str, Any]):
        for cat, skills in layer_data["skills"].items():
            merged_skills.setdefault(cat, {}).update(skills)
        merged_agents.update(layer_data["agents"])
        merged_rules.update(layer_data["rules"])

    if is_dev:
        _merge_layer(repo_raw)
    _merge_layer(ext_raw)
    _merge_layer(custom_raw)

    merged_raw = {
        "skills": merged_skills,
        "agents": merged_agents,
        "rules": merged_rules,
    }

    return {
        "repo": _format_layer_data(repo_raw),
        "ext": _format_layer_data(ext_raw),
        "custom": _format_layer_data(custom_raw),
        "merged": _format_layer_data(merged_raw),
    }


def scan_repository(
    repo_root: Path, documents_dir: Path | None = None
) -> dict[str, Any]:
    """Compatibility wrapper returning merged components across active layers."""
    sources = scan_component_sources(repo_root, documents_dir=documents_dir)
    return sources["merged"]


def select_component_source(
    component_type: str,
    sources: dict[str, Any],
    is_dev: bool,
    omni_docs_dir: Path | None,
    target_path: Path | None = None,
    lang: str = "en",
) -> dict[str, Any] | None:
    """
    Submenu for selecting component origin (ext, custom, or all; plus repo in dev mode).
    If the chosen folder is empty, warns the user clearly with instructions on where to
    download (via option [e]) or place custom files (via option [o]).
    """
    type_label_map = {
        "agents": t("menu_agents", lang).lstrip("[0123456789] ").strip(),
        "rules": t("menu_rules", lang).lstrip("[0123456789] ").strip(),
        "skills": t("menu_skills", lang).lstrip("[0123456789] ").strip(),
    }
    type_display = type_label_map.get(component_type, component_type)

    def _get_count(layer_key: str) -> int:
        data = sources.get(layer_key, {})
        if component_type == "agents":
            return len(data.get("agents", []))
        if component_type == "rules":
            return len(data.get("rules", []))
        if component_type == "skills":
            skills_cat = data.get("skills_by_category", {})
            return sum(len(v) for v in skills_cat.values())
        return 0

    repo_count = _get_count("repo")
    ext_count = _get_count("ext")
    custom_count = _get_count("custom")
    all_count = _get_count("merged")

    custom_subpath = (
        (omni_docs_dir / "custom" / component_type)
        if omni_docs_dir
        else Path.home() / "Documents" / "omni-agents" / "custom" / component_type
    )

    while True:
        clear_screen()
        print("\n" + "=" * 65)
        print(f"  {t('source_menu_title', lang, type=type_display)}")
        print("=" * 65)
        if target_path:
            print(f"  {t('target_workspace', lang)}: {target_path}")
        print("-" * 65)

        if is_dev:
            print(
                f"  {t('source_layer_repo', lang, type=component_type, count=repo_count)}"
            )
            print(
                f"  {t('source_layer_ext_dev', lang, type=component_type, count=ext_count)}"
            )
            print(
                f"  {t('source_layer_custom_dev', lang, type=component_type, count=custom_count)}"
            )
            print(f"  {t('source_layer_all_dev', lang, count=all_count)}")
        else:
            print(
                f"  {t('source_layer_ext', lang, type=component_type, count=ext_count)}"
            )
            print(
                f"  {t('source_layer_custom', lang, type=component_type, count=custom_count)}"
            )
            print(f"  {t('source_layer_all', lang, count=all_count)}")

        print(f"  {t('ext_menu_back', lang)}")
        print("-" * 65)

        try:
            choice = input(f"\n{t('choose_option', lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return None

        if choice in ("v", "voltar", "volver", "back", "q", "exit"):
            return None

        selected_layer = None
        if is_dev:
            if choice == "1":
                selected_layer = "repo"
            elif choice == "2":
                selected_layer = "ext"
            elif choice == "3":
                selected_layer = "custom"
            elif choice in ("4", "all", "todos", "todas"):
                selected_layer = "merged"
        else:
            if choice == "1":
                selected_layer = "ext"
            elif choice == "2":
                selected_layer = "custom"
            elif choice in ("3", "all", "todos", "todas"):
                selected_layer = "merged"

        if not selected_layer:
            print(f"[!] {t('invalid_option', lang)}")
            try:
                input(f"\n{t('press_enter', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
            continue

        layer_count = _get_count(selected_layer)
        if layer_count == 0:
            clear_screen()
            print("\n" + "=" * 65)
            print(f"  {type_display.upper()}")
            print("=" * 65)
            if selected_layer == "ext":
                print(f"\n[!] {t('source_empty_ext', lang, type=component_type)}")
            elif selected_layer == "custom":
                print(
                    f"\n[!] {t('source_empty_custom', lang, type=component_type, path=custom_subpath)}"
                )
            elif selected_layer == "merged":
                print(f"\n[!] {t('source_empty_all', lang, type=component_type)}")
            else:
                fallback_key = (
                    "no_agents_found"
                    if component_type == "agents"
                    else "no_rules_found"
                    if component_type == "rules"
                    else "no_skills_found"
                )
                print(f"\n[!] {t(fallback_key, lang)}")
            try:
                input(f"\n{t('press_enter_menu', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
            continue

        return sources[selected_layer]


def resolve_workspace(current_target: Path | None, lang: str = "en") -> Path | None:
    """Prompts for target workspace path, opening native GUI dialog if available."""
    if current_target and current_target.exists() and current_target.is_dir():
        return current_target

    clear_screen()
    print("\n" + "=" * 65)
    print(f"  {t('target_workspace', lang).upper()}")
    print("=" * 65)

    if is_gui_available():
        gui_path = pick_directory_gui(title=t("workspace_selector_title", lang))
        if gui_path:
            p = Path(gui_path).resolve()
            if p.exists() and p.is_dir():
                print(f"[OK] {t('path_selected', lang, path=p)}")
                return p

    while True:
        try:
            val = input(f"\n{t('prompt_path', lang)}").strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if val.lower() in ("v", "voltar", "volver", ""):
            return None

        clean_val = val.strip("\"'")
        p = Path(clean_val).resolve()
        if p.exists() and p.is_dir():
            return p
        print(f"[x] {t('path_invalid', lang, path=p)}")


def apply_workspace_to_targets(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    active_target_ids: list[str],
    selected_agent_ids: list[str],
    selected_rule_ids: list[str],
    selected_skills_dict: dict[str, list[str] | set[str]],
    lang: str = "en",
) -> bool:
    """Applies rules, agents, and skills across all active target tools."""
    if not active_target_ids:
        print(f"  [!] {t('no_active_tools', lang)}")
        return False

    agents_map = {a["id"]: a for a in scanned["agents"]}
    rules_map = {r["id"]: r for r in scanned["rules"]}

    normalized_rule_ids = []
    for rid in selected_rule_ids:
        if rid in rules_map:
            normalized_rule_ids.append(rid)
        elif rid == "AGENTS.md" and rules_map:
            fallback = (
                "pt-br-dev"
                if "pt-br-dev" in rules_map
                else next(iter(rules_map.keys()))
            )
            normalized_rule_ids.append(fallback)

    active_agents = [agents_map[aid] for aid in selected_agent_ids if aid in agents_map]
    active_rules = [rules_map[rid] for rid in normalized_rule_ids if rid in rules_map]

    skills_by_cat: dict[str, set[str]] = {
        k: set(v) for k, v in selected_skills_dict.items() if v
    }

    print(f"\n-> {t('applying_configs', lang, count=len(active_target_ids))}")
    for t_id in active_target_ids:
        adapter = get_target(t_id)
        if adapter:
            print(
                f"\n  [{t('processing', lang)}] {adapter.display_name} ({adapter.target_id})..."
            )
            try:
                adapter.configure_workspace(
                    target_path=target_path,
                    repo_root=repo_root,
                    scanned=scanned,
                    agents=active_agents,
                    rules=active_rules,
                    skills_by_cat=skills_by_cat,
                    lang=lang,
                )
            except (OSError, RuntimeError, ValueError, KeyError) as e:
                print(
                    f"  [x] {t('error_applying', lang, target=adapter.display_name, error=e)}"
                )

    state_to_save = {
        "language": lang,
        "active_targets": active_target_ids,
        "selected_agents": selected_agent_ids,
        "selected_rules": selected_rule_ids,
        "selected_skills": {k: sorted(v) for k, v in skills_by_cat.items()},
    }
    save_workspace_state(target_path, state_to_save)
    return True


def apply_global_rules_to_targets(
    repo_root: Path,
    scanned: dict[str, Any],
    selected_global_rule_ids: list[str],
    lang: str = "en",
):
    """Applies global rules to all tools that support global configurations (Antigravity, Claude)."""
    rules_map = {r["id"]: r for r in scanned.get("rules", [])}
    active_global_rules = [
        rules_map[rid] for rid in selected_global_rule_ids if rid in rules_map
    ]

    # 1. Google Antigravity
    ag_target = get_target("antigravity")
    if ag_target and hasattr(ag_target, "apply_global_rules"):
        rules_dst = Path.home() / ".gemini" / "config" / "rules"
        ag_target.apply_global_rules(rules_dst, active_global_rules, lang=lang)

    # 2. Claude Code
    claude_target = get_target("claude")
    if claude_target:
        claude_target.configure_global(
            repo_root=repo_root,
            lang=lang,
            selected_rules=active_global_rules,
        )


def confirm_exit_unsaved(lang: str = "en") -> bool:
    """Prompts the user whether to discard unsaved changes."""
    try:
        resp = input(f"\n{t('unsaved_changes_warning', lang)}").strip().lower()
        return resp in ("s", "sim", "y", "yes", "si", "sí")
    except (EOFError, KeyboardInterrupt):
        return True


def handle_target_selection(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
    lang: str = "en",
) -> list[str]:
    """Interactive menu to select and toggle target tools to configure."""
    all_targets = get_all_targets()
    active_set = set(current_state.get("active_targets", []))
    if not active_set:
        active_set.add("antigravity")
    initial_set = set(active_set)

    while True:
        clear_screen()
        print("\n" + "=" * 65)
        print(f"  {t('target_selection_title', lang)}")
        print("=" * 65)
        print(f"{t('target_workspace', lang)}: {target_path}\n")
        print(f"{t('target_available', lang)}")

        for idx, target in enumerate(all_targets, 1):
            is_active = "[x]" if target.target_id in active_set else "[ ]"
            print(
                f"  [{idx}] {is_active} {target.display_name:<26} - {target.get_description(lang)}"
            )

        print("\n" + "-" * 65)
        print(t("target_commands", lang))
        print("-" * 65)

        try:
            choice = input(f"\n{t('your_choice', lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice in ("v", "voltar", "volver"):
            if active_set != initial_set and not confirm_exit_unsaved(lang=lang):
                continue
            break

        if choice in ("s", "salvar", "save", "guardar"):
            new_active_list = [
                target.target_id
                for target in all_targets
                if target.target_id in active_set
            ]
            if not new_active_list:
                print(f"  [!] {t('must_select_one_tool', lang)}")
                try:
                    input(t("press_enter", lang))
                except (EOFError, KeyboardInterrupt):
                    pass
                continue

            current_state["active_targets"] = new_active_list
            apply_workspace_to_targets(
                target_path=target_path,
                repo_root=repo_root,
                scanned=scanned,
                active_target_ids=new_active_list,
                selected_agent_ids=current_state.get("selected_agents", []),
                selected_rule_ids=current_state.get("selected_rules", []),
                selected_skills_dict=current_state.get("selected_skills", {}),
                lang=lang,
            )
            print(f"\n[OK] {t('targets_updated', lang)}")
            try:
                input(f"\n{t('press_enter', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
            return new_active_list

        if choice == "":
            continue

        if choice == "all":
            active_set = {target.target_id for target in all_targets}
        elif choice in ("limpar", "clear", "limpiar"):
            active_set.clear()
        else:
            tokens = [
                token.strip()
                for token in choice.replace(";", ",").split(",")
                if token.strip()
            ]
            for token in tokens:
                if token.isdigit():
                    num = int(token)
                    if 1 <= num <= len(all_targets):
                        tid = all_targets[num - 1].target_id
                        if tid in active_set:
                            active_set.remove(tid)
                        else:
                            active_set.add(tid)
                else:
                    matched = next(
                        (target for target in all_targets if target.target_id == token),
                        None,
                    )
                    if matched:
                        tid = matched.target_id
                        if tid in active_set:
                            active_set.remove(tid)
                        else:
                            active_set.add(tid)

    return list(active_set)


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


def handle_global_configuration(
    repo_root: Path,
    scanned: dict[str, Any],
    app_config: dict[str, Any],
    omni_docs_dir: Path | None = None,
    lang: str = "en",
):
    """Menu for managing global machine-wide configuration links (Antigravity, Claude, etc.)."""
    clear_screen()
    print("\n" + "=" * 65)
    print(f"  {t('global_title', lang)}")
    print("=" * 65)
    print(t("global_subtitle", lang))

    targets_with_global = [
        target for target in get_all_targets() if target.supports_global
    ]
    for idx, target in enumerate(targets_with_global, 1):
        print(f"  [{idx}] {target.display_name:<26} - {target.get_description(lang)}")

    print("\n" + "-" * 65)
    print(t("global_options", lang))
    print("-" * 65)

    try:
        choice = input(f"\n{t('your_choice', lang)}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return

    if choice in ("v", "voltar", "volver", ""):
        return

    rules = scanned.get("rules", [])
    rules_map = {r["id"]: r for r in rules}
    global_rule_ids = app_config.get("global_rules", [])
    configured_rules = [rules_map[rid] for rid in global_rule_ids if rid in rules_map]

    if choice == "all":
        for target in targets_with_global:
            print(f"\n-> {t('linking', lang, tool=target.display_name)}")
            target.configure_global(
                repo_root,
                lang=lang,
                selected_rules=configured_rules,
            )
        print(f"\n[i] {t('global_rules_info_note', lang)}")
        try:
            input(f"\n{t('press_enter', lang)}")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    if choice in ("limpar", "clear", "limpiar"):
        print(f"\n-> {t('cleaning_global', lang)}")
        for target in targets_with_global:
            target.clean_global(lang=lang)
        app_config["global_rules"] = []
        save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)
        try:
            input(f"\n{t('press_enter', lang)}")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(targets_with_global):
            target = targets_with_global[num - 1]
            print(f"\n-> {t('linking', lang, tool=target.display_name)}")
            target.configure_global(
                repo_root,
                lang=lang,
                selected_rules=configured_rules,
            )
            print(f"\n[i] {t('global_rules_info_note', lang)}")
            try:
                input(f"\n{t('press_enter', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass


def handle_agents(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
    all_scanned: dict[str, Any] | None = None,
    lang: str = "en",
):
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
            if curr_selected_workspace and not target_path:
                target_path = resolve_workspace(None, lang=lang)
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
):
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


def handle_clean_workspace(
    target_path: Path,
    current_state: dict[str, Any],
    lang: str = "en",
):
    """Option: Cleanup and uninstallation isolated by target tool."""
    clear_screen()
    print("\n" + "=" * 65)
    print(f"  {t('clean_title', lang)}")
    print("=" * 65)
    print(f"{t('target_workspace', lang)}: {target_path}\n")

    all_targets = get_all_targets()
    active_targets = current_state.get("active_targets", [])

    print(t("configured_tools", lang))
    for idx, target in enumerate(all_targets, 1):
        status = "(Active)" if target.target_id in active_targets else "(Inactive)"
        print(f"  [{idx}] {target.display_name:<26} {status}")

    print("\n" + "-" * 65)
    print(t("clean_options", lang))
    print("-" * 65)

    try:
        choice = input(f"\n{t('your_choice', lang)}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return

    if choice in ("v", "voltar", "volver", ""):
        return

    if choice == "all":
        for target in all_targets:
            target.clean_workspace(target_path, lang=lang)
        current_state["active_targets"] = []
        save_workspace_state(target_path, current_state)
        print(f"\n[OK] {t('clean_all_done', lang)}")
        try:
            input(f"\n{t('press_enter', lang)}")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(all_targets):
            target = all_targets[num - 1]
            target.clean_workspace(target_path, lang=lang)
            if target.target_id in active_targets:
                active_targets.remove(target.target_id)
                current_state["active_targets"] = active_targets
                save_workspace_state(target_path, current_state)
            print(f"\n[OK] {t('clean_target_done', lang, target=target.display_name)}")
            try:
                input(f"\n{t('press_enter', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass


def handle_language_selection(
    repo_root: Path,
    target_path: Path | None,
    current_lang: str,
    app_config: dict[str, Any],
    workspace_state: dict[str, Any],
    omni_docs_dir: Path | None = None,
) -> str:
    """Interactively allows user to toggle or choose UI language and persists it in config.json."""
    available_langs = get_available_languages()
    current_code = resolve_language_code(current_lang)

    clear_screen()
    print("\n" + "=" * 65)
    print(f"  {t('lang_selection_title', current_code)}")
    print("=" * 65)

    for idx, l_desc in enumerate(available_langs, 1):
        code = l_desc["code"]
        name = l_desc["name"]
        default_tag = " (default)" if code == "en" else ""
        active_tag = " *" if code == current_code else ""
        print(f"  [{idx}] {name}{default_tag}{active_tag}")

    print("\n" + "-" * 65)
    curr_badge = get_language_badge(current_code)
    print(f"  {t('lang_toggle_hint', current_code, current=curr_badge)}")
    print(f"  {t('lang_cancel_hint', current_code)}")
    print("-" * 65)

    try:
        choice = input(f"\n{t('choose_option', current_code)}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return current_code

    if choice in ("v", "voltar", "volver"):
        return current_code

    if choice == "":
        codes = [l["code"] for l in available_langs]
        if current_code in codes:
            idx = (codes.index(current_code) + 1) % len(codes)
            new_lang = codes[idx]
        else:
            new_lang = codes[0] if codes else "en"
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(available_langs):
            new_lang = available_langs[idx]["code"]
        else:
            return current_code
    else:
        new_lang = resolve_language_code(choice)
        if new_lang == "en" and choice not in (
            "en",
            "english",
            "ingles",
            "inglês",
            "1",
        ):
            return current_code

    app_config["language"] = new_lang
    save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)

    if target_path:
        workspace_state["language"] = new_lang
        save_workspace_state(target_path, workspace_state)

    lang_name = get_language_name(new_lang)
    print(f"\n[OK] {t('lang_saved', new_lang, name=lang_name, lang=lang_name)}")
    try:
        input(f"\n{t('press_enter', new_lang)}")
    except (EOFError, KeyboardInterrupt):
        pass

    return new_lang


def handle_remote_extensions(
    documents_dir: Path,
    config: dict[str, Any],
    lang: str = "en",
):
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


def main():
    parser = argparse.ArgumentParser(
        description="omni-agents: Multi-Tool Agent, Rules & Skills Configurator.",
        epilog=(
            "Usage examples:\n"
            "  python scripts/configure_workspace.py\n"
            "  python scripts/configure_workspace.py .\n"
            "  python scripts/configure_workspace.py /path/to/project --tool cursor\n"
            "  python scripts/configure_workspace.py /path/to/project --sync --lang en\n"
            "  python scripts/configure_workspace.py --global\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Path to the target repository directory (optional, defaults to current directory for inline actions)",
    )
    parser.add_argument(
        "-t",
        "--tool",
        "--tools",
        "--target-tool",
        dest="target_tool",
        help="Target tool(s) (comma-separated: antigravity, claude, cursor, copilot, universal, kiro, opencode, codex, or all)",
    )
    parser.add_argument(
        "-a",
        "--agent",
        "--agents",
        dest="agents",
        default=None,
        help="Subagent ID(s) to activate in workspace (comma-separated: e.g. 'code-reviewer,security-auditor' or 'all', 'none')",
    )
    parser.add_argument(
        "-r",
        "--rule",
        "--rules",
        "--rule-profile",
        dest="rule_profile",
        default=None,
        help="Rule profile ID(s) to apply (comma-separated: e.g. 'general,pt-br-dev' or 'all', 'none')",
    )
    parser.add_argument(
        "-s",
        "--skill",
        "--skills",
        dest="skills",
        default=None,
        help="Skill ID(s) or categories to activate in workspace (comma-separated: e.g. 'testing,git/commit-helper' or 'all', 'none')",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Executes fast synchronization in target workspace without interactive menu",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Removes configurations from target workspace for specified tool(s) (or all)",
    )
    parser.add_argument(
        "--global",
        dest="is_global",
        action="store_true",
        help="Applies global configuration for specified tool(s) (or all)",
    )
    parser.add_argument(
        "-y",
        "--yes",
        dest="assume_yes",
        action="store_true",
        help="Automatically answer yes to confirmation prompts (e.g. link overwrite)",
    )
    parser.add_argument(
        "--lang",
        default=None,
        help="UI Language (e.g. en, pt, pt-BR, etc.)",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="Lists all supported tools and exits",
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="Lists available subagents and exits",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="Lists available rules and exits",
    )
    parser.add_argument(
        "--list-skills",
        action="store_true",
        help="Lists available modular skills by category and exits",
    )
    parser.add_argument(
        "--ext-list",
        action="store_true",
        help="Lists installed remote extensions and exits",
    )
    parser.add_argument(
        "--ext-install",
        "--ext-download",
        dest="ext_install",
        default=None,
        metavar="ITEM",
        help="Installs a remote extension from catalog (e.g. 'agents/code-reviewer.md' or 'skills/testing/pytest')",
    )
    parser.add_argument(
        "--ext-update",
        action="store_true",
        help="Checks and updates all installed remote extensions",
    )
    parser.add_argument(
        "--ext-remove",
        dest="ext_remove",
        default=None,
        metavar="KEY",
        help="Removes an installed remote extension by key",
    )
    parser.add_argument(
        "--open-folder",
        action="store_true",
        help="Opens personal omni-agents folder in File Explorer (or displays path)",
    )
    parser.add_argument(
        "--no-update-check",
        action="store_true",
        help="Disables automatic version and update checks on startup",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Checks for tool updates and executes upgrade if available",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Displays system paths, active configuration, and execution mode",
    )

    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    is_dev = is_dev_mode(repo_root)
    omni_docs_dir, _ = ensure_omni_documents_structure()

    # Workspace resolution
    target_raw = args.target
    target_path = Path(target_raw).resolve() if target_raw else None
    if target_path and (not target_path.exists() or not target_path.is_dir()):
        print(
            f"\n[x] Error: Path does not exist or is not a directory: {target_path}\n"
        )
        sys.exit(1)

    app_config = load_app_config(repo_root, omni_docs_dir=omni_docs_dir)
    workspace_state = load_workspace_state(target_path) if target_path else {}
    # Default is ALWAYS English ('en'), unless specified via args, config.json, or workspace_state
    current_lang = resolve_language_code(
        args.lang
        or app_config.get("language")
        or workspace_state.get("language")
        or "en"
    )

    if args.info:
        print("\nomni-agents Diagnostic Info:")
        print(f"  CLI Version:      v{__version__}")
        print(
            f"  Execution Mode:   {'Local Dev Mode (Repository)' if is_dev else 'Global Mode (Documents)'}"
        )
        print(f"  Repo Root:        {repo_root}")
        print(f"  Documents Dir:    {omni_docs_dir}")
        print(
            f"  Configured Repo:  {app_config.get('repository', {}).get('url', 'N/A')}"
        )
        print(f"  Default Language: {app_config.get('language', 'en')}")
        sys.exit(0)

    if args.update:
        print(f"\n{t('update_checking', current_lang, version=__version__)}")
        up_info = check_for_updates(
            current_version=__version__, is_dev=is_dev, timeout=3.0
        )
        if up_info:
            prompt_and_upgrade(up_info, lang=current_lang)
        else:
            print(f"\n{t('update_up_to_date', current_lang)}")
        sys.exit(0)

    if args.list_tools:
        print("\nSupported Tools:")
        for target in get_all_targets():
            supports_glob = (
                "[Global + Workspace]" if target.supports_global else "[Workspace]"
            )
            print(
                f"  * {target.target_id:<14} - {target.display_name:<24} {supports_glob}"
            )
        sys.exit(0)

    # Automatic update check on startup
    if (
        not args.no_update_check
        and not args.sync
        and not args.clean
        and not args.is_global
    ):
        with contextlib.suppress(OSError, TimeoutError):
            up_info = check_for_updates(
                current_version=__version__, is_dev=is_dev, timeout=1.5
            )
            if up_info and prompt_and_upgrade(up_info, lang=current_lang):
                sys.exit(0)

    scanned = scan_repository(repo_root, documents_dir=omni_docs_dir)

    # Personal folder inline action
    if args.open_folder:
        if has_graphical_display():
            open_folder_in_explorer(omni_docs_dir)
        print(f"Personal omni-agents folder: {omni_docs_dir}")
        sys.exit(0)

    # Component discovery / inspection inline actions
    if args.list_agents:
        agents = scanned.get("agents", [])
        print("\nAvailable Subagents:")
        if not agents:
            print("  (None found)")
        for a in agents:
            desc = a.get("description", "")
            desc_str = f" - {desc[:70]}..." if desc else ""
            print(f"  * {a['id']:<28}{desc_str}")
        sys.exit(0)

    if args.list_rules:
        rules = scanned.get("rules", [])
        print("\nAvailable Rules:")
        if not rules:
            print("  (None found)")
        for r in rules:
            desc = r.get("description", "")
            desc_str = f" - {desc[:70]}..." if desc else ""
            print(f"  * {r['id']:<24}{desc_str}")
        sys.exit(0)

    if args.list_skills:
        skills_cat = scanned.get("skills_by_category", {})
        print("\nAvailable Modular Skills by Category:")
        if not skills_cat:
            print("  (None found)")
        for cat, items in sorted(skills_cat.items()):
            print(f"\n  [{cat}] ({len(items)} skills):")
            for item in items:
                desc = item.get("description", "")
                desc_str = f" - {desc[:60]}..." if desc else ""
                print(f"    * {item['id']:<24}{desc_str}")
        sys.exit(0)

    # Remote Extensions inline actions
    ext_dir = (omni_docs_dir / "ext") if omni_docs_dir else None
    if args.ext_list:
        manifest = load_manifest(ext_dir) if ext_dir else {}
        installed = manifest.get("installed", {})
        print("\nInstalled Remote Extensions:")
        if not installed:
            print("  (No extensions currently installed in ext/)")
        for k, v in installed.items():
            print(f"  * {k:<32} (sha: {v.get('sha', '')[:7]})")
        sys.exit(0)

    if args.ext_install:
        if not ext_dir:
            print("[x] Error: Personal documents directory is not available.")
            sys.exit(1)
        raw_target = args.ext_install.replace("\\", "/").strip("/")
        parts = raw_target.split("/")
        comp_type = parts[0] if parts[0] in ("agents", "rules", "skills") else None
        comp_id = parts[-1]
        cat = parts[1] if comp_type == "skills" and len(parts) > 2 else None

        if not comp_type:
            tree = fetch_remote_tree(app_config, timeout=5.0)
            if tree:
                if any(
                    a["id"].lower() == comp_id.lower() for a in tree.get("agents", [])
                ):
                    comp_type = "agents"
                elif any(
                    r["id"].lower() == comp_id.lower() for r in tree.get("rules", [])
                ):
                    comp_type = "rules"
                else:
                    for c_name, c_skills in tree.get("skills_by_category", {}).items():
                        if any(s["id"].lower() == comp_id.lower() for s in c_skills):
                            comp_type = "skills"
                            cat = c_name
                            break
        if not comp_type:
            print(
                f"[x] Error: Could not identify component type for '{args.ext_install}'."
            )
            print(
                "    Use format: 'agents/<id>.md', 'rules/<id>', or 'skills/<cat>/<id>'"
            )
            sys.exit(1)

        print(f"-> Installing remote {comp_type}: {comp_id}...")
        ok = install_remote_component(
            comp_type, comp_id, app_config, ext_dir, category=cat
        )
        if ok:
            print(f"[OK] Successfully installed {comp_type}/{comp_id} in ext/")
            sys.exit(0)
        else:
            print(f"[x] Failed to install {comp_type}/{comp_id}.")
            sys.exit(1)

    if args.ext_update:
        if not ext_dir:
            print("[x] Error: Personal documents directory is not available.")
            sys.exit(1)
        print("-> Checking for remote extension updates...")
        updates = check_ext_updates(ext_dir, app_config, timeout=5.0)
        if not updates:
            print("[OK] All extensions in ext/ are up to date.")
            sys.exit(0)
        print(f"-> Found {len(updates)} update(s). Applying...")
        tree = fetch_remote_tree(app_config, timeout=5.0)
        for u in updates:
            install_remote_component(
                u["type"],
                u["id"],
                app_config,
                ext_dir,
                category=u.get("category"),
                tree_data=tree,
            )
        print("[OK] Extensions updated successfully.")
        sys.exit(0)

    if args.ext_remove:
        if not ext_dir:
            print("[x] Error: Personal documents directory is not available.")
            sys.exit(1)
        manifest = load_manifest(ext_dir)
        installed = manifest.get("installed", {})
        key_to_del = next(
            (k for k in installed if k.lower() == args.ext_remove.lower()), None
        )
        if not key_to_del:
            print(
                f"[x] Error: Extension '{args.ext_remove}' not found in installed extensions."
            )
            sys.exit(1)
        del installed[key_to_del]
        save_manifest(ext_dir, manifest)
        target_file = ext_dir / key_to_del
        if target_file.is_dir():
            shutil.rmtree(target_file, ignore_errors=True)
        elif target_file.is_file():
            target_file.unlink(missing_ok=True)
        print(f"[OK] Removed extension: {key_to_del}")
        sys.exit(0)

    # Resolve target_path default for inline actions if omitted
    has_inline_action = (
        args.sync
        or args.clean
        or args.agents is not None
        or args.skills is not None
        or (args.rule_profile is not None and not args.is_global)
    )
    if target_path is None and has_inline_action and not args.is_global:
        target_path = Path.cwd().resolve()

    # Global Clean via CLI
    if args.is_global and args.clean:
        tools = (
            [
                get_target(t)
                for t in [
                    x.strip().lower()
                    for x in args.target_tool.replace(";", ",").split(",")
                    if x.strip()
                ]
            ]
            if args.target_tool and args.target_tool != "all"
            else [target for target in get_all_targets() if target.supports_global]
        )
        for target in tools:
            if target:
                target.clean_global(lang=current_lang)
        app_config["global_rules"] = []
        save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)
        print("\n[OK] Global clean completed.")
        sys.exit(0)

    # Global Mode via CLI
    if args.is_global:
        tools = (
            [
                get_target(t)
                for t in [
                    x.strip().lower()
                    for x in args.target_tool.replace(";", ",").split(",")
                    if x.strip()
                ]
            ]
            if args.target_tool and args.target_tool != "all"
            else [target for target in get_all_targets() if target.supports_global]
        )
        rules = scanned.get("rules", [])
        rules_map = {r["id"]: r for r in rules}
        selected_rules = []
        if args.rule_profile:
            if args.rule_profile.lower() in ("none", "clear", "limpar"):
                selected_rules = []
            elif args.rule_profile.lower() in ("all", "todas"):
                selected_rules = list(rules)
            else:
                rule_tokens = [
                    tok.strip()
                    for tok in args.rule_profile.replace(";", ",").split(",")
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
            selected_rules = [
                rules_map[rid] for rid in configured_ids if rid in rules_map
            ]

        for target in tools:
            if target:
                print(f"\n-> {t('linking', current_lang, tool=target.display_name)}")
                target.configure_global(
                    repo_root,
                    lang=current_lang,
                    selected_rules=selected_rules,
                    assume_yes=args.assume_yes,
                )
        app_config["global_rules"] = [r["id"] for r in selected_rules]
        save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)
        sys.exit(0)

    # Clean Mode via CLI
    if args.clean and target_path:
        state = load_workspace_state(target_path)
        tool_ids = (
            [
                x.strip().lower()
                for x in args.target_tool.replace(";", ",").split(",")
                if x.strip()
            ]
            if args.target_tool and args.target_tool != "all"
            else get_available_target_ids()
        )
        for tid in tool_ids:
            adapter = get_target(tid)
            if adapter:
                adapter.clean_workspace(target_path, lang=current_lang)
                if tid in state.get("active_targets", []):
                    state["active_targets"].remove(tid)
        save_workspace_state(target_path, state)
        print("\n[OK] Clean completed.")
        sys.exit(0)

    # Workspace Configuration & Sync Mode via CLI
    if has_inline_action and target_path:
        state = load_workspace_state(target_path)
        active_tools = state.get("active_targets", [])
        if args.target_tool:
            if args.target_tool.lower() == "all":
                active_tools = get_available_target_ids()
            else:
                tool_tokens = [
                    t.strip().lower()
                    for t in args.target_tool.replace(";", ",").split(",")
                    if t.strip()
                ]
                matched_tools = [t for t in tool_tokens if get_target(t) is not None]
                if matched_tools:
                    active_tools = matched_tools
                else:
                    print(
                        f"[!] Warning: No recognized tools in '{args.target_tool}'. Supported: {', '.join(get_available_target_ids())}"
                    )
        if not active_tools:
            active_tools = ["antigravity"]

        # Agents
        if args.agents is not None:
            if args.agents.lower() in ("none", "clear", "limpar"):
                selected_agent_ids = []
            elif args.agents.lower() in ("all", "todos"):
                selected_agent_ids = [a["id"] for a in scanned.get("agents", [])]
            else:
                agent_tokens = [
                    tok.strip()
                    for tok in args.agents.replace(";", ",").split(",")
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
        if args.rule_profile is not None:
            if args.rule_profile.lower() in ("none", "clear", "limpar"):
                selected_rule_ids = []
            elif args.rule_profile.lower() in ("all", "todas"):
                selected_rule_ids = [r["id"] for r in scanned.get("rules", [])]
            else:
                rule_tokens = [
                    tok.strip()
                    for tok in args.rule_profile.replace(";", ",").split(",")
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
                        print(
                            f"[!] Warning: Rule '{tok}' not found in available rules."
                        )
        else:
            selected_rule_ids = (
                state.get("selected_rules")
                if state.get("selected_rules") is not None
                else [r["id"] for r in scanned.get("rules", [])]
            )

        # Skills
        skills_by_cat = scanned.get("skills_by_category", {})
        if args.skills is not None:
            if args.skills.lower() in ("none", "clear", "limpar"):
                selected_skills_dict = {}
            elif args.skills.lower() in ("all", "todas"):
                selected_skills_dict = {
                    cat: [s["id"] for s in s_list]
                    for cat, s_list in skills_by_cat.items()
                }
            else:
                selected_skills_dict = {}
                skill_tokens = [
                    tok.strip()
                    for tok in args.skills.replace(";", ",").split(",")
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
                                    selected_skills_dict.setdefault(
                                        cat_name, set()
                                    ).add(s_match["id"])
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
        sys.exit(0)

    # Interactive Menu
    while True:
        clear_screen()
        workspace_state = load_workspace_state(target_path) if target_path else {}
        if (
            not args.lang
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
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
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
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
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
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
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
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
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
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
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


if __name__ == "__main__":
    main()
