#!/usr/bin/env python3
"""
omni-agent: Multi-Tool Agent, Rules & Skills Configurator.
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
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

# Ensures scripts/ is in sys.path for safe relative target imports
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Garante codificacao UTF-8 no terminal para suporte estavel a caracteres acentuados
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from i18n import (
    get_available_languages,
    get_language_badge,
    get_language_name,
    resolve_language_code,
    t,
)
from targets import (
    get_all_targets,
    get_available_target_ids,
    get_target,
    load_workspace_state,
    save_workspace_state,
)
from targets.base import parse_frontmatter


def load_app_config(repo_root: Path) -> dict[str, Any]:
    """Loads persistent local application preferences (config.json)."""
    cfg_file = repo_root / "config.json"
    if not cfg_file.exists():
        return {}
    try:
        return json.loads(cfg_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_app_config(repo_root: Path, config: dict[str, Any]):
    """Persists local application preferences to config.json."""
    cfg_file = repo_root / "config.json"
    try:
        cfg_file.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def has_graphical_display() -> bool:
    """Verifica se ha um display grafico disponivel no ambiente."""
    if sys.platform.startswith("win") or sys.platform.startswith("darwin"):
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def is_gui_available() -> bool:
    """Verifica se o display grafico e o modulo Tkinter estao disponiveis."""
    if not has_graphical_display():
        return False
    return importlib.util.find_spec("tkinter") is not None


def clear_screen():
    """Limpa a tela do terminal de forma multiplataforma."""
    os.system("cls" if sys.platform.startswith("win") else "clear")


def pick_directory_gui(
    title: str = "Select Project Repository Directory",
) -> str | None:
    """Abre interface grafica nativa (Tkinter) para selecao de pasta."""
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


def scan_repository(repo_root: Path) -> dict[str, Any]:
    """
    Escaneia dinamicamente as pastas do repositorio:
    - skills/<categoria>/<skill_name>/SKILL.md
    - agents/*.md
    - rules/*.md
    """
    data: dict[str, Any] = {"skills_by_category": {}, "agents": [], "rules": []}

    # 1. Escaneia Skills
    skills_dir = repo_root / "skills"
    if skills_dir.exists() and skills_dir.is_dir():
        for category_dir in sorted(skills_dir.iterdir()):
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                cat_name = category_dir.name
                skills_list = []
                for item in sorted(category_dir.iterdir()):
                    skill_md = item / "SKILL.md"
                    if item.is_dir() and skill_md.exists():
                        name, desc = parse_frontmatter(skill_md)
                        skills_list.append(
                            {
                                "id": item.name,
                                "name": name,
                                "description": desc,
                                "path": item.resolve(),
                            }
                        )
                if skills_list:
                    data["skills_by_category"][cat_name] = skills_list

    # 2. Escaneia Subagentes
    agents_dir = repo_root / "agents"
    if agents_dir.exists() and agents_dir.is_dir():
        for item in sorted(agents_dir.glob("*.md")):
            name, desc = parse_frontmatter(item)
            data["agents"].append(
                {
                    "id": item.name,
                    "name": name,
                    "description": desc,
                    "path": item.resolve(),
                }
            )

    # 3. Escaneia Regras
    rules_dir = repo_root / "rules"
    if rules_dir.exists() and rules_dir.is_dir():
        for item in sorted(rules_dir.glob("*.md")):
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
            data["rules"].append(
                {
                    "id": item.name,
                    "name": name,
                    "description": desc,
                    "path": item.resolve(),
                }
            )

    return data


def resolve_workspace(current_target: Path | None, lang: str = "en") -> Path | None:
    """Solicita a definicao do workspace alvo, abrindo janela grafica nativa se disponivel."""
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

        if val.lower() in ("v", "voltar", ""):
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
    """Executa a aplicacao das regras, agentes e skills em todos os targets ativos."""
    if not active_target_ids:
        print(f"  [!] {t('no_active_tools', lang)}")
        return False

    agents_map = {a["id"]: a for a in scanned["agents"]}
    rules_map = {r["id"]: r for r in scanned["rules"]}

    active_agents = [agents_map[aid] for aid in selected_agent_ids if aid in agents_map]
    active_rules = [rules_map[rid] for rid in selected_rule_ids if rid in rules_map]

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


def confirm_exit_unsaved(lang: str = "en") -> bool:
    """Pergunta ao usuário se deseja sair sem salvar caso haja alterações pendentes."""
    try:
        resp = input(f"\n{t('unsaved_changes_warning', lang)}").strip().lower()
        return resp in ("s", "sim", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        return True


def handle_target_selection(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
    lang: str = "en",
) -> list[str]:
    """Menu interativo para selecionar e alternar quais ferramentas serao configuradas."""
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

        if choice in ("v", "voltar"):
            if active_set != initial_set and not confirm_exit_unsaved(lang=lang):
                continue
            break

        if choice in ("s", "salvar", "save"):
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
        elif choice in ("limpar", "clear"):
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


def handle_global_configuration(repo_root: Path, lang: str = "en"):
    """Menu para gerenciar instalacao de configuracoes globais (Antigravity, Claude, etc.)."""
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

    if choice in ("v", "voltar", ""):
        return

    if choice == "all":
        for target in targets_with_global:
            print(f"\n-> {t('linking', lang, tool=target.display_name)}")
            target.configure_global(repo_root, lang=lang)
        try:
            input(f"\n{t('press_enter', lang)}")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    if choice in ("limpar", "clear"):
        print(f"\n-> {t('cleaning_global', lang)}")
        for target in targets_with_global:
            target.clean_global(lang=lang)
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
            target.configure_global(repo_root, lang=lang)
            try:
                input(f"\n{t('press_enter', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass


def handle_agents(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
    lang: str = "en",
):
    """Opcao: Selecao e ativacao de subagentes para o workspace."""
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

        if user_input in ("v", "voltar"):
            if curr_selected != initial_selected and not confirm_exit_unsaved(
                lang=lang
            ):
                continue
            return

        if user_input in ("s", "salvar", "save"):
            current_state["selected_agents"] = sorted(curr_selected)
            apply_workspace_to_targets(
                target_path=target_path,
                repo_root=repo_root,
                scanned=scanned,
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
        elif user_input in ("limpar", "clear"):
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
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
    lang: str = "en",
):
    """Opcao: Selecao e ativacao de regras para o workspace."""
    rules = scanned["rules"]
    if not rules:
        print(f"[!] {t('no_rules_found', lang)}")
        try:
            input(f"\n{t('press_enter_menu', lang)}")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    curr_selected = set(current_state.get("selected_rules", []))
    if not curr_selected and rules:
        curr_selected = {rule["id"] for rule in rules}
    initial_selected = set(curr_selected)

    while True:
        clear_screen()
        print("\n" + "=" * 65)
        print(f"  {t('rules_title', lang)}")
        print("=" * 65)
        print(f"{t('target_workspace', lang)}: {target_path}\n")

        for idx, rule in enumerate(rules, 1):
            is_sel = "[x]" if rule["id"] in curr_selected else "[ ]"
            desc = rule.get("description", "")
            desc_preview = f" - {desc[:58]}..." if desc else ""
            print(f"  [{idx:2d}] {is_sel} {rule['id']:<24}{desc_preview}")

        print("\n" + "-" * 65)
        print(t("how_to_select_rules", lang))
        print("-" * 65)

        try:
            user_input = input(f"\n{t('your_choice', lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return

        if user_input in ("v", "voltar"):
            if curr_selected != initial_selected and not confirm_exit_unsaved(
                lang=lang
            ):
                continue
            return

        if user_input in ("s", "salvar", "save"):
            current_state["selected_rules"] = sorted(curr_selected)
            apply_workspace_to_targets(
                target_path=target_path,
                repo_root=repo_root,
                scanned=scanned,
                active_target_ids=current_state.get("active_targets", ["antigravity"]),
                selected_agent_ids=current_state.get("selected_agents", []),
                selected_rule_ids=current_state["selected_rules"],
                selected_skills_dict=current_state.get("selected_skills", {}),
                lang=lang,
            )
            print(f"\n[OK] {t('rules_activated', lang, count=len(curr_selected))}")
            try:
                input(f"\n{t('press_enter_menu', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
            return

        if user_input == "":
            continue

        if user_input == "all":
            curr_selected = {rule["id"] for rule in rules}
        elif user_input in ("limpar", "clear"):
            curr_selected.clear()
        else:
            tokens = [
                token.strip()
                for token in user_input.replace(";", ",").split(",")
                if token.strip()
            ]
            for token in tokens:
                if token.isdigit():
                    num = int(token)
                    if 1 <= num <= len(rules):
                        rid = rules[num - 1]["id"]
                        if rid in curr_selected:
                            curr_selected.remove(rid)
                        else:
                            curr_selected.add(rid)


def handle_category_submenu(
    cat_name: str, skills: list[dict], selected_set: set[str], lang: str = "en"
) -> set[str]:
    """Submenu dinamico para gerenciar as skills de uma categoria especifica."""
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

        if choice in ("v", "voltar", ""):
            break

        if choice == "all":
            for skill in skills:
                current_selected.add(skill["id"])
        elif choice in ("limpar", "clear"):
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
    lang: str = "en",
):
    """Opcao: Menu dinamico de categorias de skills com submenus individuais."""
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

        if choice in ("v", "voltar"):
            has_changed = any(
                selected_by_cat.get(cat, set()) != initial_by_cat.get(cat, set())
                for cat in set(selected_by_cat.keys()) | set(initial_by_cat.keys())
            )
            if has_changed and not confirm_exit_unsaved(lang=lang):
                continue
            break

        if choice == "":
            continue

        if choice in ("s", "salvar", "save"):
            current_state["selected_skills"] = {
                k: sorted(v) for k, v in selected_by_cat.items() if v
            }
            apply_workspace_to_targets(
                target_path=target_path,
                repo_root=repo_root,
                scanned=scanned,
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

        elif choice in ("limpar", "clear"):
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
    """Opcao: Desinstalacao e limpeza isolada por ferramenta."""
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

    if choice in ("v", "voltar", ""):
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

    if choice in ("v", "voltar"):
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
    save_app_config(repo_root, app_config)

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


def main():
    parser = argparse.ArgumentParser(
        description="omni-agent: Multi-Tool Agent, Rules & Skills Configurator.",
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
        help="Path to the target repository directory (optional)",
    )
    parser.add_argument(
        "-t",
        "--tool",
        "--target-tool",
        dest="target_tool",
        help="Target tool (antigravity, claude, cursor, copilot, universal, kiro, opencode, codex, or all)",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Executes fast synchronization in target workspace without interactive menu",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Removes configurations from target workspace for specified tool (or all)",
    )
    parser.add_argument(
        "--global",
        dest="is_global",
        action="store_true",
        help="Applies global configuration for specified tool (or all)",
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

    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    # Resolucao de Workspace
    target_raw = args.target
    target_path = Path(target_raw).resolve() if target_raw else None
    if target_path and (not target_path.exists() or not target_path.is_dir()):
        print(
            f"\n[x] Error: Path does not exist or is not a directory: {target_path}\n"
        )
        sys.exit(1)

    app_config = load_app_config(repo_root)
    workspace_state = load_workspace_state(target_path) if target_path else {}
    # Default is ALWAYS English ('en'), unless specified via args, config.json, or workspace_state
    current_lang = resolve_language_code(
        args.lang
        or app_config.get("language")
        or workspace_state.get("language")
        or "en"
    )

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

    # Modo Global via CLI
    if args.is_global:
        tools = (
            [get_target(args.target_tool)]
            if args.target_tool and args.target_tool != "all"
            else [target for target in get_all_targets() if target.supports_global]
        )
        for target in tools:
            if target:
                print(f"\n-> {t('linking', current_lang, tool=target.display_name)}")
                target.configure_global(repo_root, lang=current_lang)
        sys.exit(0)

    scanned = scan_repository(repo_root)

    # Modo Limpeza via CLI
    if args.clean and target_path:
        state = load_workspace_state(target_path)
        tool_ids = (
            [args.target_tool.lower()]
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

    # Modo Sincronizacao via CLI
    if args.sync and target_path:
        state = load_workspace_state(target_path)
        active_tools = state.get("active_targets", [])
        if args.target_tool:
            if args.target_tool == "all":
                active_tools = get_available_target_ids()
            else:
                active_tools = [args.target_tool.lower()]
        if not active_tools:
            active_tools = ["antigravity"]

        apply_workspace_to_targets(
            target_path=target_path,
            repo_root=repo_root,
            scanned=scanned,
            active_target_ids=active_tools,
            selected_agent_ids=state.get("selected_agents", []),
            selected_rule_ids=state.get("selected_rules")
            or [r["id"] for r in scanned["rules"]],
            selected_skills_dict=state.get("selected_skills", {}),
            lang=current_lang,
        )
        print(f"\n[OK] {t('sync_success', current_lang)}")
        sys.exit(0)

    # Menu Interativo
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

        print("\n" + "=" * 65)
        print(f"  {t('app_title', current_lang)}")
        print("=" * 65)
        print(f"  {t('target_workspace', current_lang)}:     {target_display}")
        print(f"  {t('active_tools', current_lang)}: {active_tools_display}")
        print("-" * 65)
        print(f"  {t('menu_select_tools', current_lang)}")
        print(f"  {t('menu_global', current_lang)}")
        print(f"  {t('menu_agents', current_lang)}")
        print(f"  {t('menu_rules', current_lang)}")
        print(f"  {t('menu_skills', current_lang)}")
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
            print(f"\n{t('exit_msg', current_lang)}\n")
            sys.exit(0)

        if choice in ("t", "tool", "tools", "ferramentas"):
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
                handle_target_selection(
                    target_path, repo_root, scanned, workspace_state, lang=current_lang
                )

        elif choice in ("1", "global"):
            handle_global_configuration(repo_root, lang=current_lang)

        elif choice in ("2", "agents", "agent"):
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
                handle_agents(
                    target_path, repo_root, scanned, workspace_state, lang=current_lang
                )

        elif choice in ("3", "rules", "rule"):
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
                handle_rules(
                    target_path, repo_root, scanned, workspace_state, lang=current_lang
                )

        elif choice in ("4", "skills", "skill"):
            target_path = resolve_workspace(target_path, lang=current_lang)
            if target_path:
                handle_skills(
                    target_path, repo_root, scanned, workspace_state, lang=current_lang
                )

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
                    or [r["id"] for r in scanned["rules"]],
                    selected_skills_dict=workspace_state.get("selected_skills", {}),
                    lang=current_lang,
                )
                print(f"\n[OK] {t('sync_success', current_lang)}")
                try:
                    input(f"\n{t('press_enter', current_lang)}")
                except (EOFError, KeyboardInterrupt):
                    pass

        elif choice in ("c", "clean", "limpar"):
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
            )

        elif choice in ("5", "sair", "exit", "q", "quit"):
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
