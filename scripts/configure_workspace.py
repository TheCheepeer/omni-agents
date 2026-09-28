#!/usr/bin/env python3
"""
Configurador Declarativo e Modular de Workspace e Global para Agentes de IA.
Multiplataforma (Windows, Linux e macOS) sem dependencias externas.

Suporta:
- Google Antigravity
- Claude Code (Anthropic)
- Cursor IDE
- GitHub Copilot
- Universal (AGENTS.md)
- Kiro
- OpenCode
- Codex (OpenAI)
- Multi-Tool (Todos simultaneamente)
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

# Garante que a pasta scripts/ esteja no sys.path para importacao relativa segura
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from targets import (
    get_all_targets,
    get_available_target_ids,
    get_target,
    load_workspace_state,
    save_workspace_state,
)
from targets.base import parse_frontmatter


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


def pick_directory_gui(title: str = "Selecione o Repositorio do Projeto") -> str | None:
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


def resolve_workspace(current_target: Path | None) -> Path | None:
    """Solicita a definicao do workspace alvo, abrindo janela grafica nativa se disponivel."""
    if current_target and current_target.exists() and current_target.is_dir():
        return current_target

    clear_screen()
    print("\n" + "=" * 65)
    print("  DEFINIR WORKSPACE ALVO")
    print("=" * 65)

    if is_gui_available():
        print("-> Abrindo janela grafica nativa para selecao da pasta...")
        gui_path = pick_directory_gui()
        if gui_path:
            p = Path(gui_path).resolve()
            if p.exists() and p.is_dir():
                print(f"[OK] Pasta selecionada: {p}")
                return p

    while True:
        try:
            val = input(
                "\nDigite o caminho absoluto ou relativo do projeto alvo (ou 'v' para voltar): "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if val.lower() in ("v", "voltar", ""):
            return None

        clean_val = val.strip("\"'")
        p = Path(clean_val).resolve()
        if p.exists() and p.is_dir():
            return p
        print(f"[x] O caminho informado nao existe ou nao e uma pasta valida: {p}")


def apply_workspace_to_targets(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    active_target_ids: list[str],
    selected_agent_ids: list[str],
    selected_rule_ids: list[str],
    selected_skills_dict: dict[str, list[str] | set[str]],
) -> bool:
    """Executa a aplicacao das regras, agentes e skills em todos os targets ativos."""
    if not active_target_ids:
        print("  [!] Nenhuma ferramenta ativa selecionada no workspace.")
        return False

    # Filtra objetos completos
    agents_map = {a["id"]: a for a in scanned["agents"]}
    rules_map = {r["id"]: r for r in scanned["rules"]}

    active_agents = [agents_map[aid] for aid in selected_agent_ids if aid in agents_map]
    active_rules = [rules_map[rid] for rid in selected_rule_ids if rid in rules_map]

    skills_by_cat: dict[str, set[str]] = {
        k: set(v) for k, v in selected_skills_dict.items() if v
    }

    print(
        f"\n-> Aplicando configuracoes para {len(active_target_ids)} ferramenta(s)..."
    )
    for t_id in active_target_ids:
        adapter = get_target(t_id)
        if adapter:
            print(f"\n  [Processando] {adapter.display_name} ({adapter.target_id})...")
            try:
                adapter.configure_workspace(
                    target_path=target_path,
                    repo_root=repo_root,
                    scanned=scanned,
                    agents=active_agents,
                    rules=active_rules,
                    skills_by_cat=skills_by_cat,
                )
            except (OSError, RuntimeError, ValueError, KeyError) as e:
                print(f"  [x] Erro ao aplicar {adapter.display_name}: {e}")

    # Salva o estado atualizado no workspace
    state_to_save = {
        "active_targets": active_target_ids,
        "selected_agents": selected_agent_ids,
        "selected_rules": selected_rule_ids,
        "selected_skills": {k: sorted(v) for k, v in skills_by_cat.items()},
    }
    save_workspace_state(target_path, state_to_save)
    return True


def handle_target_selection(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
) -> list[str]:
    """Menu interativo para selecionar e alternar quais ferramentas serao configuradas."""
    all_targets = get_all_targets()
    active_set = set(current_state.get("active_targets", []))
    if not active_set:
        active_set.add("antigravity")

    while True:
        clear_screen()
        print("\n" + "=" * 65)
        print("  SELECAO DE FERRAMENTAS ALVO (MULTI-TOOL)")
        print("=" * 65)
        print(f"Workspace Alvo: {target_path}\n")
        print("Ferramentas disponiveis:")

        for idx, t in enumerate(all_targets, 1):
            is_active = "[x]" if t.target_id in active_set else "[ ]"
            print(f"  [{idx}] {is_active} {t.display_name:<26} - {t.description}")

        print("\n" + "-" * 65)
        print("Comandos:")
        print(
            "  * Digite numeros separados por virgula para alternar selecao (ex: 1, 3)"
        )
        print("  * 'all' para marcar TODAS as ferramentas (Multi-Tool)")
        print("  * 'limpar' para desmarcar todas")
        print("  * 's' ou 'salvar' para confirmar e sincronizar")
        print("  * 'v' para voltar sem salvar")
        print("-" * 65)

        try:
            choice = input("\nSua escolha: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice in ("v", "voltar"):
            break

        if choice in ("s", "salvar", "save", ""):
            new_active_list = [
                t.target_id for t in all_targets if t.target_id in active_set
            ]
            if not new_active_list:
                print("  [!] Pelo menos uma ferramenta deve estar selecionada.")
                try:
                    input("Pressione Enter...")
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
            )
            print("\n[OK] Ferramentas alvo atualizadas com sucesso!")
            try:
                input("\nPressione Enter para continuar...")
            except (EOFError, KeyboardInterrupt):
                pass
            return new_active_list

        if choice == "all":
            active_set = {t.target_id for t in all_targets}
        elif choice in ("limpar", "clear"):
            active_set.clear()
        else:
            tokens = [
                t.strip() for t in choice.replace(";", ",").split(",") if t.strip()
            ]
            for t in tokens:
                if t.isdigit():
                    num = int(t)
                    if 1 <= num <= len(all_targets):
                        tid = all_targets[num - 1].target_id
                        if tid in active_set:
                            active_set.remove(tid)
                        else:
                            active_set.add(tid)
                else:
                    matched = next(
                        (target for target in all_targets if target.target_id == t),
                        None,
                    )
                    if matched:
                        tid = matched.target_id
                        if tid in active_set:
                            active_set.remove(tid)
                        else:
                            active_set.add(tid)

    return list(active_set)


def handle_global_configuration(repo_root: Path):
    """Menu para gerenciar instalacao de configuracoes globais (Antigravity, Claude, etc.)."""
    clear_screen()
    print("\n" + "=" * 65)
    print("  CONFIGURACAO GLOBAL DE FERRAMENTAS")
    print("=" * 65)
    print("Esta opcao vincula os agentes, regras e skills essenciais")
    print("diretamente nas pastas de configuracao global do usuario na maquina.\n")

    targets_with_global = [t for t in get_all_targets() if t.supports_global]
    for idx, t in enumerate(targets_with_global, 1):
        print(f"  [{idx}] {t.display_name:<26} - {t.description}")

    print("\n" + "-" * 65)
    print("Opcoes:")
    print("  * Digite o numero da ferramenta para vincular")
    print("  * 'all' para vincular todas as ferramentas globais")
    print("  * 'limpar' para desinstalar links globais")
    print("  * 'v' para voltar ao menu principal")
    print("-" * 65)

    try:
        choice = input("\nSua escolha: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return

    if choice in ("v", "voltar", ""):
        return

    if choice == "all":
        for t in targets_with_global:
            print(f"\n-> Vinculando {t.display_name}...")
            t.configure_global(repo_root)
        try:
            input("\nPressione Enter para continuar...")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    if choice in ("limpar", "clear"):
        print("\n-> Removendo links globais...")
        for t in targets_with_global:
            t.clean_global()
        try:
            input("\nPressione Enter para continuar...")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(targets_with_global):
            target = targets_with_global[num - 1]
            print(f"\n-> Vinculando {target.display_name}...")
            target.configure_global(repo_root)
            try:
                input("\nPressione Enter para continuar...")
            except (EOFError, KeyboardInterrupt):
                pass


def handle_agents(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
):
    """Opcao: Selecao e ativacao de subagentes para o workspace."""
    clear_screen()
    print("\n" + "=" * 65)
    print("  SUBAGENTES DISPONIVEIS PARA O WORKSPACE")
    print("=" * 65)
    print(f"Workspace Alvo: {target_path}\n")

    agents = scanned["agents"]
    if not agents:
        print("[!] Nenhum subagente encontrado na pasta agents/.")
        try:
            input("\nPressione Enter para voltar ao menu...")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    curr_selected = set(current_state.get("selected_agents", []))
    for idx, a in enumerate(agents, 1):
        is_sel = "[x]" if a["id"] in curr_selected else "[ ]"
        desc = a.get("description", "")
        desc_preview = f" - {desc[:60]}..." if desc else ""
        print(f"  [{idx:2d}] {is_sel} {a['id']:<28}{desc_preview}")

    print("\n" + "-" * 65)
    print("Como selecionar:")
    print("  * Digite os numeros para alternar selecao (ex: 1, 2)")
    print("  * 'all' para marcar todos")
    print("  * 'limpar' para desmarcar todos")
    print("  * 's' ou 'salvar' para aplicar as ferramentas ativas")
    print("  * 'v' para voltar ao menu principal")
    print("-" * 65)

    while True:
        try:
            user_input = input("\nSua escolha: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return

        if user_input in ("v", "voltar"):
            return

        if user_input in ("s", "salvar", "save", ""):
            current_state["selected_agents"] = sorted(curr_selected)
            apply_workspace_to_targets(
                target_path=target_path,
                repo_root=repo_root,
                scanned=scanned,
                active_target_ids=current_state.get("active_targets", ["antigravity"]),
                selected_agent_ids=current_state["selected_agents"],
                selected_rule_ids=current_state.get("selected_rules", []),
                selected_skills_dict=current_state.get("selected_skills", {}),
            )
            print(f"\n[OK] {len(curr_selected)} subagente(s) ativado(s) com sucesso!")
            try:
                input("\nPressione Enter para voltar ao menu...")
            except (EOFError, KeyboardInterrupt):
                pass
            return

        if user_input == "all":
            curr_selected = {a["id"] for a in agents}
            print("  [+] Todos os subagentes foram marcados.")
        elif user_input in ("limpar", "clear"):
            curr_selected.clear()
            print("  [i] Todos os subagentes foram desmarcados.")
        else:
            tokens = [
                t.strip() for t in user_input.replace(";", ",").split(",") if t.strip()
            ]
            for t in tokens:
                if t.isdigit():
                    num = int(t)
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
                            if a["id"].lower() == t
                            or a["id"].lower().replace(".md", "") == t
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
):
    """Opcao: Selecao e ativacao de regras para o workspace."""
    rules = scanned["rules"]
    if not rules:
        print("[!] Nenhuma regra encontrada na pasta rules/.")
        try:
            input("\nPressione Enter para voltar ao menu...")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    curr_selected = set(current_state.get("selected_rules", []))
    if not curr_selected and rules:
        curr_selected = {r["id"] for r in rules}

    while True:
        clear_screen()
        print("\n" + "=" * 65)
        print("  REGRAS DISPONIVEIS PARA O WORKSPACE")
        print("=" * 65)
        print(f"Workspace Alvo: {target_path}\n")

        for idx, r in enumerate(rules, 1):
            is_sel = "[x]" if r["id"] in curr_selected else "[ ]"
            desc = r.get("description", "")
            desc_preview = f" - {desc[:58]}..." if desc else ""
            print(f"  [{idx:2d}] {is_sel} {r['id']:<24}{desc_preview}")

        print("\n" + "-" * 65)
        print("Como selecionar:")
        print("  * Digite os numeros para alternar selecao (ex: 1)")
        print("  * 'all' para marcar todas")
        print("  * 'limpar' para desmarcar todas")
        print("  * 's' ou 'salvar' para aplicar nas ferramentas ativas")
        print("  * 'v' para voltar ao menu principal")
        print("-" * 65)

        try:
            user_input = input("\nSua escolha: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return

        if user_input in ("v", "voltar"):
            return

        if user_input in ("s", "salvar", "save", ""):
            current_state["selected_rules"] = sorted(curr_selected)
            apply_workspace_to_targets(
                target_path=target_path,
                repo_root=repo_root,
                scanned=scanned,
                active_target_ids=current_state.get("active_targets", ["antigravity"]),
                selected_agent_ids=current_state.get("selected_agents", []),
                selected_rule_ids=current_state["selected_rules"],
                selected_skills_dict=current_state.get("selected_skills", {}),
            )
            print(f"\n[OK] {len(curr_selected)} regra(s) ativada(s) com sucesso!")
            try:
                input("\nPressione Enter para voltar ao menu...")
            except (EOFError, KeyboardInterrupt):
                pass
            return

        if user_input == "all":
            curr_selected = {r["id"] for r in rules}
        elif user_input in ("limpar", "clear"):
            curr_selected.clear()
        else:
            tokens = [
                t.strip() for t in user_input.replace(";", ",").split(",") if t.strip()
            ]
            for t in tokens:
                if t.isdigit():
                    num = int(t)
                    if 1 <= num <= len(rules):
                        rid = rules[num - 1]["id"]
                        if rid in curr_selected:
                            curr_selected.remove(rid)
                        else:
                            curr_selected.add(rid)


def handle_category_submenu(
    cat_name: str, skills: list[dict], selected_set: set[str]
) -> set[str]:
    """Submenu dinamico para gerenciar as skills de uma categoria especifica."""
    current_selected = set(selected_set)

    while True:
        clear_screen()
        print("\n" + "-" * 65)
        print(f"  CATEGORIA: {cat_name.upper()} ({len(skills)} skills disponiveis)")
        print("-" * 65)

        for idx, s in enumerate(skills, 1):
            is_sel = "[x]" if s["id"] in current_selected else "[ ]"
            desc_preview = (
                s["description"][:58] + "..."
                if len(s["description"]) > 58
                else s["description"]
            )
            print(f"  [{idx:2d}] {is_sel} {s['id']:<24} - {desc_preview}")

        print("\n" + "-" * 65)
        print("Como selecionar:")
        print("  * Digite numeros para alternar selecao (ex: 1, 3)")
        print("  * 'all' para marcar todas desta categoria")
        print("  * 'limpar' para desmarcar todas desta categoria")
        print("  * 'v' para voltar a lista de categorias")
        print("-" * 65)

        try:
            choice = input("\nSua escolha: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice in ("v", "voltar", ""):
            break

        if choice == "all":
            for s in skills:
                current_selected.add(s["id"])
        elif choice in ("limpar", "clear"):
            current_selected.clear()
        else:
            tokens = [
                t.strip() for t in choice.replace(";", ",").split(",") if t.strip()
            ]
            for t in tokens:
                if t.isdigit():
                    num = int(t)
                    if 1 <= num <= len(skills):
                        skill_id = skills[num - 1]["id"]
                        if skill_id in current_selected:
                            current_selected.remove(skill_id)
                        else:
                            current_selected.add(skill_id)
                else:
                    matched = next((s for s in skills if s["id"].lower() == t), None)
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
):
    """Opcao: Menu dinamico de categorias de skills com submenus individuais."""
    skills_by_cat = scanned["skills_by_category"]
    if not skills_by_cat:
        print("[!] Nenhuma categoria de skills encontrada na pasta skills/.")
        try:
            input("\nPressione Enter para voltar ao menu...")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    raw_saved = current_state.get("selected_skills", {})
    selected_by_cat: dict[str, set[str]] = {k: set(v) for k, v in raw_saved.items()}
    categories = sorted(skills_by_cat.keys())

    while True:
        clear_screen()
        total_selected = sum(len(v) for v in selected_by_cat.values())
        cats_with_selection = len([c for c, v in selected_by_cat.items() if v])

        print("\n" + "=" * 65)
        print("  SKILLS MODULARES POR CATEGORIA")
        print("=" * 65)
        print(f"Workspace Alvo: {target_path}\n")
        print("Categorias Disponiveis:")

        for idx, cat_name in enumerate(categories, 1):
            skills = skills_by_cat[cat_name]
            sel_count = len(selected_by_cat.get(cat_name, set()))
            status = (
                f"({sel_count}/{len(skills)} selecionadas)"
                if sel_count > 0
                else f"({len(skills)} skills)"
            )
            print(f"  [{idx:2d}] {cat_name.upper():<16} {status}")

        print(
            f"\nTotal selecionado no Workspace: {total_selected} skill(s) em {cats_with_selection} categoria(s)"
        )

        print("\n" + "-" * 65)
        print("Como navegar:")
        print("  * Digite o numero da categoria para abrir seu submenu (ex: 1)")
        print("  * 's' ou 'salvar' para aplicar nas ferramentas ativas")
        print("  * 'all' para marcar todas as skills de todas as categorias")
        print("  * 'limpar' para desmarcar todas")
        print("  * 'v' para voltar ao Menu Principal")
        print("-" * 65)

        try:
            choice = input("\nEscolha uma opcao: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice in ("v", "voltar"):
            break

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
            )
            print("\n[OK] Skills sincronizadas nas ferramentas ativas!")
            try:
                input("\nPressione Enter para voltar ao menu principal...")
            except (EOFError, KeyboardInterrupt):
                pass
            break

        if choice == "all":
            for cat_name, skills in skills_by_cat.items():
                selected_by_cat[cat_name] = {s["id"] for s in skills}
            print("  [+] Todas as skills de todas as categorias foram marcadas.")

        elif choice in ("limpar", "clear"):
            selected_by_cat.clear()
            print("  [i] Todas as selecoes foram desmarcadas.")

        elif choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(categories):
                cat_name = categories[num - 1]
                skills = skills_by_cat[cat_name]
                curr_sel = selected_by_cat.get(cat_name, set())
                updated = handle_category_submenu(cat_name, skills, curr_sel)
                if updated:
                    selected_by_cat[cat_name] = updated
                else:
                    selected_by_cat.pop(cat_name, None)
            else:
                print(f"[!] Opcao invalida. Digite um numero de 1 a {len(categories)}.")
        elif choice in skills_by_cat:
            cat_name = choice
            skills = skills_by_cat[cat_name]
            curr_sel = selected_by_cat.get(cat_name, set())
            updated = handle_category_submenu(cat_name, skills, curr_sel)
            if updated:
                selected_by_cat[cat_name] = updated
            else:
                selected_by_cat.pop(cat_name, None)


def handle_clean_workspace(
    target_path: Path,
    current_state: dict[str, Any],
):
    """Opcao: Desinstalacao e limpeza isolada por ferramenta."""
    clear_screen()
    print("\n" + "=" * 65)
    print("  LIMPEZA / DESINSTALACAO POR FERRAMENTA")
    print("=" * 65)
    print(f"Workspace Alvo: {target_path}\n")

    all_targets = get_all_targets()
    active_targets = current_state.get("active_targets", [])

    print("Ferramentas configuradas:")
    for idx, t in enumerate(all_targets, 1):
        status = "(Ativa)" if t.target_id in active_targets else "(Inativa)"
        print(f"  [{idx}] {t.display_name:<26} {status}")

    print("\n" + "-" * 65)
    print("Opcoes:")
    print("  * Digite o numero da ferramenta para remover suas configuracoes")
    print("  * 'all' para remover configuracoes de TODAS as ferramentas")
    print("  * 'v' para voltar ao menu principal")
    print("-" * 65)

    try:
        choice = input("\nSua escolha: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return

    if choice in ("v", "voltar", ""):
        return

    if choice == "all":
        for t in all_targets:
            t.clean_workspace(target_path)
        current_state["active_targets"] = []
        save_workspace_state(target_path, current_state)
        print("\n[OK] Todas as configuracoes foram removidas do workspace.")
        try:
            input("\nPressione Enter para continuar...")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(all_targets):
            target = all_targets[num - 1]
            target.clean_workspace(target_path)
            if target.target_id in active_targets:
                active_targets.remove(target.target_id)
                current_state["active_targets"] = active_targets
                save_workspace_state(target_path, current_state)
            print(f"\n[OK] Configuracoes de {target.display_name} removidas.")
            try:
                input("\nPressione Enter para continuar...")
            except (EOFError, KeyboardInterrupt):
                pass


def main():
    parser = argparse.ArgumentParser(
        description="Configurador interativo e modular de Workspace e Global para Agentes de IA.",
        epilog=(
            "Exemplos de uso:\n"
            "  python scripts/configure_workspace.py\n"
            "  python scripts/configure_workspace.py .\n"
            "  python scripts/configure_workspace.py /meu/projeto --tool cursor\n"
            "  python scripts/configure_workspace.py /meu/projeto --sync\n"
            "  python scripts/configure_workspace.py --global\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Caminho do repositorio alvo (opcional)",
    )
    parser.add_argument(
        "-t",
        "--tool",
        "--target-tool",
        dest="target_tool",
        help="Ferramenta alvo (antigravity, claude, cursor, copilot, universal, kiro, opencode, codex ou all)",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Executa sincronizacao rapida no workspace alvo sem menu interativo",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove configuracoes do workspace alvo para a ferramenta especificada (ou todas)",
    )
    parser.add_argument(
        "--global",
        dest="is_global",
        action="store_true",
        help="Aplica configuracao global para a ferramenta especificada (ou todas)",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="Lista todas as ferramentas suportadas e encerra",
    )

    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    if args.list_tools:
        print("\nFerramentas Suportadas:")
        for t in get_all_targets():
            supports_glob = (
                "[Global + Workspace]" if t.supports_global else "[Workspace]"
            )
            print(f"  * {t.target_id:<14} - {t.display_name:<24} {supports_glob}")
        sys.exit(0)

    # Modo Global via CLI
    if args.is_global:
        tools = (
            [get_target(args.target_tool)]
            if args.target_tool and args.target_tool != "all"
            else [t for t in get_all_targets() if t.supports_global]
        )
        for t in tools:
            if t:
                print(f"\n-> Aplicando configuracao global para {t.display_name}...")
                t.configure_global(repo_root)
        sys.exit(0)

    # Resolve Workspace
    target_raw = args.target
    target_path = Path(target_raw).resolve() if target_raw else None
    if target_path and (not target_path.exists() or not target_path.is_dir()):
        print(f"\n[x] Erro: Caminho nao existe ou nao e um diretorio: {target_path}\n")
        sys.exit(1)

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
                adapter.clean_workspace(target_path)
                if tid in state.get("active_targets", []):
                    state["active_targets"].remove(tid)
        save_workspace_state(target_path, state)
        print("\n[OK] Limpeza concluida.")
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
        )
        print("\n[OK] Sincronizacao concluida.")
        sys.exit(0)

    # Menu Interativo
    while True:
        clear_screen()
        workspace_state = load_workspace_state(target_path) if target_path else {}
        active_tools_display = (
            ", ".join(workspace_state.get("active_targets", []))
            if workspace_state.get("active_targets")
            else "Nenhuma (padrao: Antigravity)"
        )
        target_display = (
            str(target_path)
            if target_path
            else "[Nao definido - digite 'w' ou selecione uma opcao]"
        )

        print("\n" + "=" * 65)
        print("  CONFIGURADOR MULTI-TOOL DE AGENTES, REGRAS E SKILLS")
        print("=" * 65)
        print(f"  Workspace Alvo:     {target_display}")
        print(f"  Ferramentas Ativas: {active_tools_display}")
        print("-" * 65)
        print("  [t] Selecionar Ferramentas Alvo (Antigravity, Cursor, Claude...)")
        print("  [1] Configuracao Global da Maquina (Antigravity e Claude)")
        print("  [2] Subagentes para o Workspace")
        print("  [3] Regras para o Workspace")
        print("  [4] Skills Modulares para o Workspace")
        print("  [s] Sincronizar Tudo (Sync em todas as ferramentas ativas)")
        print("  [c] Limpeza / Desinstalacao por Ferramenta")
        print("  [5] Sair")
        print("-" * 65)
        print("  [w] Definir / Alterar Workspace Alvo")
        print("=" * 65)

        try:
            choice = input("\nEscolha uma opcao: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando configurador. Ate logo!\n")
            sys.exit(0)

        if choice in ("t", "tool", "tools", "ferramentas"):
            target_path = resolve_workspace(target_path)
            if target_path:
                handle_target_selection(
                    target_path, repo_root, scanned, workspace_state
                )

        elif choice in ("1", "global"):
            handle_global_configuration(repo_root)

        elif choice in ("2", "agents", "agent"):
            target_path = resolve_workspace(target_path)
            if target_path:
                handle_agents(target_path, repo_root, scanned, workspace_state)

        elif choice in ("3", "rules", "rule"):
            target_path = resolve_workspace(target_path)
            if target_path:
                handle_rules(target_path, repo_root, scanned, workspace_state)

        elif choice in ("4", "skills", "skill"):
            target_path = resolve_workspace(target_path)
            if target_path:
                handle_skills(target_path, repo_root, scanned, workspace_state)

        elif choice in ("s", "sync", "sincronizar"):
            target_path = resolve_workspace(target_path)
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
                )
                print("\n[OK] Sincronizacao concluida com sucesso!")
                try:
                    input("\nPressione Enter para continuar...")
                except (EOFError, KeyboardInterrupt):
                    pass

        elif choice in ("c", "clean", "limpar"):
            target_path = resolve_workspace(target_path)
            if target_path:
                handle_clean_workspace(target_path, workspace_state)

        elif choice in ("5", "sair", "exit", "q", "quit"):
            print("\nEncerrando configurador. Ate logo!\n")
            sys.exit(0)

        elif choice in ("w", "workspace"):
            new_target = resolve_workspace(None)
            if new_target:
                target_path = new_target

        else:
            print("[!] Opcao invalida. Digite uma opcao do menu.")


if __name__ == "__main__":
    main()
