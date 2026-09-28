#!/usr/bin/env python3
"""
Configurador Declarativo de Workspace e Global para Antigravity / Agents.

Funciona de forma multiplataforma (Windows, Linux e macOS).
Oferece um menu interativo para:
1. Configuração Global (vincular core de agentes, regras e skills no ~/.gemini/config)
2. Seleção de Subagentes para o Workspace alvo
3. Seleção de Regras para o Workspace alvo
4. Seleção de Skills Modulares para o Workspace alvo
5. Sair
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


def has_graphical_display() -> bool:
    """Verifica se há um display gráfico disponível no ambiente."""
    if sys.platform.startswith("win") or sys.platform.startswith("darwin"):
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def is_gui_available() -> bool:
    """Verifica se o display gráfico e o módulo Tkinter estão disponíveis."""
    if not has_graphical_display():
        return False
    return importlib.util.find_spec("tkinter") is not None


def clear_screen():
    """Limpa a tela do terminal de forma multiplataforma."""
    os.system("cls" if sys.platform.startswith("win") else "clear")


def pick_directory_gui(title="Selecione o Repositório do Projeto"):
    """Tentativa de carregar interface gráfica nativa (Tkinter) para seleção de pasta."""
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


def is_link(path: Path) -> bool:
    """Verifica se o caminho é um link simbólico ou junction no Windows/Unix."""
    if not path.exists():
        return path.is_symlink()
    if path.is_symlink():
        return True
    if sys.platform.startswith("win"):
        try:
            st = os.lstat(path)
            # FILE_ATTRIBUTE_REPARSE_POINT = 0x400
            return bool(st.st_file_attributes & 0x400)
        except OSError:
            return False
    return False


def remove_dir_link(path: Path):
    """Remove um link com segurança, sem deletar arquivos reais do alvo."""
    if not path.exists() and not path.is_symlink():
        return
    if sys.platform.startswith("win"):
        try:
            os.rmdir(path)
        except OSError:
            import subprocess

            subprocess.run(["cmd", "/c", "rmdir", str(path)], check=True)
    else:
        if path.is_symlink():
            path.unlink()
        else:
            path.rmdir()


def create_dir_link(src: Path, dst: Path):
    """Cria um link de diretório multiplataforma (Junction no Windows, Symlink no Unix)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        if is_link(dst):
            remove_dir_link(dst)
        else:
            backup_dst = dst.with_name(f"{dst.name}.backup")
            print(f"  [!] Diretório já existente não é um link: {dst}")
            print(f"      Movendo para backup: {backup_dst.name}")
            dst.rename(backup_dst)

    if sys.platform.startswith("win"):
        try:
            import _winapi

            _winapi.CreateJunction(str(src), str(dst))
        except (AttributeError, OSError):
            import subprocess

            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
                check=True,
                shell=True,
            )
    else:
        dst.symlink_to(src, target_is_directory=True)


def parse_frontmatter(file_path: Path):
    """Extrai campos básicos de frontmatter YAML simples sem dependências externas."""
    default_name = file_path.stem
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return default_name, ""

    name, description = default_name, ""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_lines = parts[1].splitlines()
            in_multiline_desc = False
            desc_buffer = []

            for line in yaml_lines:
                stripped = line.strip()
                if stripped.startswith("name:"):
                    in_multiline_desc = False
                    name = stripped.split("name:", 1)[1].strip().strip('"').strip("'")
                elif stripped.startswith("description:"):
                    val = (
                        stripped.split("description:", 1)[1]
                        .strip()
                        .strip('"')
                        .strip("'")
                    )
                    if val in (">-", ">", "|", "|-", ""):
                        in_multiline_desc = True
                    else:
                        description = val
                elif in_multiline_desc:
                    if line.startswith(("  ", "\t")):
                        desc_buffer.append(stripped)
                    else:
                        in_multiline_desc = False

            if desc_buffer and not description:
                description = " ".join(desc_buffer)

    return name, description


def scan_repository(repo_root: Path):
    """
    Escaneia dinamicamente as pastas do repositório:
    - skills/<categoria>/<skill_name>/SKILL.md
    - agents/*.md
    - rules/*.md
    """
    data = {"skills_by_category": {}, "agents": [], "rules": []}

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


def update_gitignore(target_path: Path):
    """Adiciona '.agents/' ao .gitignore do projeto alvo caso ainda não esteja."""
    gitignore_path = target_path / ".gitignore"
    entry = ".agents/"

    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines()]
        if entry not in lines and ".agents" not in lines:
            with gitignore_path.open("a", encoding="utf-8") as f:
                if content and not content.endswith("\n"):
                    f.write("\n")
                f.write(f"{entry}\n")
            print(f"  [+] Adicionado '{entry}' ao .gitignore existente.")
        else:
            print(f"  [i] '{entry}' já está presente no .gitignore.")
    else:
        gitignore_path.write_text(f"{entry}\n", encoding="utf-8")
        print(f"  [+] Arquivo .gitignore criado com '{entry}'.")


def init_workspace(target_path: Path, interactive: bool = True) -> Path:
    """Garante que a pasta .agents/, o manifesto skills.json e o .gitignore existam no workspace."""
    agents_dir = target_path / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    skills_json_path = agents_dir / "skills.json"
    if not skills_json_path.exists():
        initial_manifest = {"entries": []}
        skills_json_path.write_text(
            json.dumps(initial_manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  [+] Arquivo criado: {skills_json_path}")
    else:
        print(f"  [i] Manifesto existente: {skills_json_path}")

    update_gitignore(target_path)
    print(f"\n[OK] Workspace configurado com sucesso:\n     {target_path}")
    if interactive:
        try:
            input("\nPressione Enter para continuar...")
        except (EOFError, KeyboardInterrupt):
            pass
    return target_path


def resolve_workspace(current_target: Path | None) -> Path | None:
    """Solicita a definição do workspace alvo, abrindo janela gráfica nativa se disponível."""
    if current_target and current_target.exists() and current_target.is_dir():
        return current_target

    clear_screen()
    print("\n" + "=" * 65)
    print("  DEFINIR WORKSPACE ALVO")
    print("=" * 65)

    # 1. Se houver interface gráfica disponível, abre direto o seletor nativo
    if is_gui_available():
        print("-> Abrindo janela gráfica nativa para seleção da pasta...")
        selected = pick_directory_gui("Selecione a Pasta do Projeto Alvo")
        if selected:
            path = Path(selected).resolve()
            if path.exists() and path.is_dir():
                return init_workspace(path)

        print("\n[!] Nenhuma pasta selecionada pela janela gráfica.")
        print("    Você pode digitar o caminho manualmente abaixo ou voltar.")

    # 2. Fallback CLI para ambiente sem UI ou se a janela foi cancelada
    print("\n" + "-" * 65)
    print("Informe o caminho do projeto alvo:")
    print("  * Digite o caminho da pasta (ou '.' para a pasta atual)")
    print("  * Digite 'v' para voltar ao menu principal")
    print("-" * 65)

    try:
        raw = input("\nCaminho do repositório: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None

    if raw.lower() in ("v", "voltar", ""):
        return None

    path = Path(raw).resolve()
    if not path.exists() or not path.is_dir():
        print(
            f"\n[x] Erro: O caminho especificado não existe ou não é um diretório: {path}"
        )
        try:
            input("\nPressione Enter para continuar...")
        except (EOFError, KeyboardInterrupt):
            pass
        return None

    return init_workspace(path)


def handle_global_configuration(repo_root: Path):
    """Opção 1: Exibe os comandos/links e executa após confirmação, protegendo regras globais."""
    clear_screen()
    global_dir = Path.home() / ".gemini" / "config"
    agents_src = repo_root / "agents"
    agents_dst = global_dir / "agents"
    rules_src = repo_root / "rules"
    rules_dst = global_dir / "rules"
    skills_src = repo_root / "skills" / "global"
    skills_dst = global_dir / "skills"

    print("\n" + "=" * 65)
    print("  [1] CONFIGURAÇÃO GLOBAL DO ANTIGRAVITY")
    print("=" * 65)
    print("Esta opção vincula as pastas do repositório diretamente na pasta")
    print(f"de configuração do Antigravity:\n  -> {global_dir}\n")
    link_type = (
        "Junction (Windows)"
        if sys.platform.startswith("win")
        else "Symbolic Link (Unix)"
    )
    print(f"Tipo de vínculo utilizado: {link_type}")
    print("\nLinks que serão processados:")

    agents_status = (
        "(Já existe)" if agents_dst.exists() or agents_dst.is_symlink() else "(Novo)"
    )
    skills_status = (
        "(Já existe)" if skills_dst.exists() or skills_dst.is_symlink() else "(Novo)"
    )
    rules_status = (
        "(Já existe - exigirá confirmação para substituir)"
        if rules_dst.exists() or rules_dst.is_symlink()
        else "(Novo - exigirá confirmação)"
    )

    print("  * Subagentes (agents):")
    print(f"    Origem:  {agents_src}")
    print(f"    Destino: {agents_dst} {agents_status}")
    print("  * Core Global de Skills:")
    print(f"    Origem:  {skills_src}")
    print(f"    Destino: {skills_dst} {skills_status}")
    print("  * Regras Globais (rules):")
    print(f"    Origem:  {rules_src}")
    print(f"    Destino: {rules_dst} {rules_status}")

    print("\n" + "-" * 65)
    print("O que deseja fazer?")
    print("  [s] Iniciar vinculação global")
    print("  [v] Voltar ao Menu Principal")
    print("-" * 65)

    try:
        choice = input("\nSua escolha: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return

    if choice in ("s", "sim", "y", "yes"):
        print("\n-> Aplicando links globais...")

        # 1. Subagentes
        if agents_src.exists():
            try:
                create_dir_link(agents_src, agents_dst)
                print("  [+] Subagentes (agents) vinculado com sucesso!")
            except (OSError, RuntimeError, subprocess.SubprocessError) as e:
                print(f"  [x] Falha ao vincular Subagentes: {e}")
        else:
            print(f"  [x] Pasta de origem não encontrada: {agents_src}")

        # 2. Core Global de Skills
        if skills_src.exists():
            try:
                create_dir_link(skills_src, skills_dst)
                print("  [+] Core Global de Skills vinculado com sucesso!")
            except (OSError, RuntimeError, subprocess.SubprocessError) as e:
                print(f"  [x] Falha ao vincular Core Global de Skills: {e}")
        else:
            print(f"  [x] Pasta de origem não encontrada: {skills_src}")

        # 3. Regras Globais (confirmação explícita para não sobrescrever sem querer)
        rules_exists = rules_dst.exists() or rules_dst.is_symlink()
        print("\n" + "-" * 65)
        print("  AVALIAÇÃO DE REGRAS GLOBAIS")
        print("-" * 65)
        if rules_exists:
            print(f"  A pasta de regras globais já existe em:\n    -> {rules_dst}")
            if rules_dst.is_dir():
                try:
                    existing_rules = [f.name for f in rules_dst.glob("*.md")]
                    if existing_rules:
                        print(
                            f"  Regras atuais encontradas: {', '.join(existing_rules)}"
                        )
                except OSError:
                    existing_rules = []
            print("\n  [?] Deseja SUBSTITUIR as regras globais existentes")
            print("      pelas regras deste repositório? [s/N]")
        else:
            print(f"  Destino de regras globais: {rules_dst}")
            print("  [?] Deseja vincular as Regras Globais deste repositório? [s/N]")

        try:
            rules_choice = input("  Sua escolha para regras [s/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            rules_choice = "n"

        if rules_choice in ("s", "sim", "y", "yes"):
            if rules_src.exists():
                try:
                    create_dir_link(rules_src, rules_dst)
                    print("  [+] Regras Globais (rules) vinculado com sucesso!")
                except (OSError, RuntimeError, subprocess.SubprocessError) as e:
                    print(f"  [x] Falha ao vincular Regras Globais: {e}")
            else:
                print(f"  [x] Pasta de origem não encontrada: {rules_src}")
        else:
            print("  [i] Regras Globais mantidas sem alteração (não substituídas).")

        print("\n[OK] Configuração global concluída!")
        try:
            input("\nPressione Enter para voltar ao menu principal...")
        except (EOFError, KeyboardInterrupt):
            pass
    else:
        print("[i] Nenhuma alteração global realizada. Retornando ao menu.")


def handle_agents(target_path: Path, scanned: dict):
    """Opção 2: Seleção e ativação de subagentes para o workspace alvo."""
    clear_screen()
    print("\n" + "=" * 65)
    print("  [2] SUBAGENTES DISPONÍVEIS PARA O WORKSPACE")
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

    for idx, a in enumerate(agents, 1):
        desc = a.get("description", "")
        desc_preview = f" - {desc[:60]}..." if desc else ""
        print(f"  [{idx:2d}] {a['id']:<26}{desc_preview}")

    print("\n" + "-" * 65)
    print("Como selecionar:")
    print("  * Digite os números separados por vírgula (ex: 1, 3)")
    print("  * 'all' para selecionar todos")
    print("  * 'v' para voltar ao menu principal")
    print("-" * 65)

    try:
        user_input = input("\nSua escolha: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return

    if user_input in ("v", "voltar", ""):
        return

    tokens = [t.strip() for t in user_input.replace(";", ",").split(",") if t.strip()]
    selected = []
    if "all" in tokens:
        selected = agents[:]
    else:
        for t in tokens:
            if t.isdigit():
                num = int(t)
                if 1 <= num <= len(agents):
                    selected.append(agents[num - 1])
            else:
                for a in agents:
                    if a["id"].lower() == t or a["id"].lower().replace(".md", "") == t:
                        selected.append(a)

    if not selected:
        print("[!] Nenhum subagente selecionado.")
        try:
            input("\nPressione Enter para voltar ao menu...")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    dest_dir = target_path / ".agents" / "agents"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for a in selected:
        dest_file = dest_dir / a["id"]
        dest_file.write_text(
            Path(a["path"]).read_text(encoding="utf-8"), encoding="utf-8"
        )
        print(f"  [+] Ativado: {dest_file.name}")

    update_gitignore(target_path)
    print(f"\n[OK] {len(selected)} subagente(s) ativado(s) em {dest_dir}!")
    try:
        input("\nPressione Enter para voltar ao menu...")
    except (EOFError, KeyboardInterrupt):
        pass


def handle_rules(target_path: Path, scanned: dict):
    """Opção 3: Seleção e ativação de regras para o workspace alvo."""
    clear_screen()
    print("\n" + "=" * 65)
    print("  [3] REGRAS DISPONÍVEIS PARA O WORKSPACE")
    print("=" * 65)
    print(f"Workspace Alvo: {target_path}\n")

    rules = scanned["rules"]
    if not rules:
        print("[!] Nenhuma regra encontrada na pasta rules/.")
        try:
            input("\nPressione Enter para voltar ao menu...")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    for idx, r in enumerate(rules, 1):
        desc = r.get("description", "")
        desc_preview = f" - {desc[:60]}..." if desc else ""
        print(f"  [{idx:2d}] {r['id']:<26}{desc_preview}")

    print("\n" + "-" * 65)
    print("Como selecionar:")
    print("  * Digite os números separados por vírgula (ex: 1)")
    print("  * 'all' para selecionar todas")
    print("  * 'v' para voltar ao menu principal")
    print("-" * 65)

    try:
        user_input = input("\nSua escolha: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return

    if user_input in ("v", "voltar", ""):
        return

    tokens = [t.strip() for t in user_input.replace(";", ",").split(",") if t.strip()]
    selected = []
    if "all" in tokens:
        selected = rules[:]
    else:
        for t in tokens:
            if t.isdigit():
                num = int(t)
                if 1 <= num <= len(rules):
                    selected.append(rules[num - 1])
            else:
                for r in rules:
                    if r["id"].lower() == t or r["id"].lower().replace(".md", "") == t:
                        selected.append(r)

    if not selected:
        print("[!] Nenhuma regra selecionada.")
        return

    dest_dir = target_path / ".agents" / "rules"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for r in selected:
        dest_file = dest_dir / r["id"]
        dest_file.write_text(
            Path(r["path"]).read_text(encoding="utf-8"), encoding="utf-8"
        )
        print(f"  [+] Ativada: {dest_file.name}")

    update_gitignore(target_path)
    print(f"\n[OK] {len(selected)} regra(s) ativada(s) em {dest_dir}!")
    try:
        input("\nPressione Enter para voltar ao menu...")
    except (EOFError, KeyboardInterrupt):
        pass


def load_existing_skills(target_path: Path) -> dict[str, set[str]]:
    """Carrega as skills já configuradas no .agents/skills.json do workspace."""
    skills_json_path = target_path / ".agents" / "skills.json"
    selected: dict[str, set[str]] = {}
    if not skills_json_path.exists():
        return selected

    try:
        data = json.loads(skills_json_path.read_text(encoding="utf-8"))
        for entry in data.get("entries", []):
            path_str = entry.get("path", "")
            cat_name = Path(path_str).name
            include_only = entry.get("include_only", [])
            if cat_name and include_only:
                selected[cat_name] = set(include_only)
    except (json.JSONDecodeError, OSError):
        selected = {}

    return selected


def save_skills_manifest(
    target_path: Path, selected_by_cat: dict[str, set[str]], repo_root: Path
):
    """Gera o arquivo .agents/skills.json com as categorias e skills selecionadas."""
    agents_workspace_dir = target_path / ".agents"
    agents_workspace_dir.mkdir(parents=True, exist_ok=True)
    skills_json_path = agents_workspace_dir / "skills.json"

    entries = []
    total_skills = 0
    for cat_name in sorted(selected_by_cat.keys()):
        skill_ids = selected_by_cat[cat_name]
        if skill_ids:
            cat_path = (repo_root / "skills" / cat_name).resolve().as_posix()
            entries.append({"path": cat_path, "include_only": sorted(skill_ids)})
            total_skills += len(skill_ids)

    skills_manifest = {"entries": entries}
    skills_json_path.write_text(
        json.dumps(skills_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    update_gitignore(target_path)

    print(f"\n[OK] Manifesto gerado com sucesso: {skills_json_path}")
    print(f"     ({total_skills} skills configuradas em {len(entries)} categoria(s))")


def handle_category_submenu(
    cat_name: str, skills: list[dict], selected_set: set[str]
) -> set[str]:
    """Submenu dinâmico para gerenciar as skills de uma categoria específica."""
    current_selected = set(selected_set)

    while True:
        clear_screen()
        print("\n" + "-" * 65)
        print(f"  CATEGORIA: {cat_name.upper()} ({len(skills)} skills disponíveis)")
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
        print("  * Digite números para alternar seleção (ex: 1, 3)")
        print("  * 'all' para marcar todas desta categoria")
        print("  * 'limpar' para desmarcar todas desta categoria")
        print("  * 'v' para voltar à lista de categorias")
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


def handle_skills(target_path: Path, scanned: dict, repo_root: Path):
    """Opção 4: Menu dinâmico de categorias de skills com submenus individuais."""
    skills_by_cat = scanned["skills_by_category"]
    if not skills_by_cat:
        print("[!] Nenhuma categoria de skills encontrada na pasta skills/.")
        try:
            input("\nPressione Enter para voltar ao menu...")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    # Carrega seleções preexistentes no workspace
    selected_by_cat: dict[str, set[str]] = load_existing_skills(target_path)
    categories = sorted(skills_by_cat.keys())

    while True:
        clear_screen()
        total_selected = sum(len(v) for v in selected_by_cat.values())
        cats_with_selection = len([c for c, v in selected_by_cat.items() if v])

        print("\n" + "=" * 65)
        print("  [4] SKILLS MODULARES POR CATEGORIA")
        print("=" * 65)
        print(f"Workspace Alvo: {target_path}\n")
        print("Categorias Disponíveis:")

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
        print("  * Digite o número da categoria para abrir seu submenu (ex: 1)")
        print("  * 's' ou 'salvar' para aplicar/gerar o .agents/skills.json")
        print("  * 'all' para marcar todas as skills de todas as categorias")
        print("  * 'limpar' para desmarcar todas")
        print("  * 'v' para voltar ao Menu Principal")
        print("-" * 65)

        try:
            choice = input("\nEscolha uma opção: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice in ("v", "voltar"):
            break

        if choice in ("s", "salvar", "save"):
            save_skills_manifest(target_path, selected_by_cat, repo_root)
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
            print("  [i] Todas as seleções foram desmarcadas.")

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
                print(f"[!] Opção inválida. Digite um número de 1 a {len(categories)}.")
        elif choice in skills_by_cat:
            cat_name = choice
            skills = skills_by_cat[cat_name]
            curr_sel = selected_by_cat.get(cat_name, set())
            updated = handle_category_submenu(cat_name, skills, curr_sel)
            if updated:
                selected_by_cat[cat_name] = updated
            else:
                selected_by_cat.pop(cat_name, None)
        else:
            print("[!] Opção não reconhecida.")


def main():
    parser = argparse.ArgumentParser(
        description="Configurador interativo e modular de Workspace e Global para Antigravity.",
        epilog=(
            "Exemplos de uso:\n"
            "  python scripts/configure_workspace.py\n"
            "  python scripts/configure_workspace.py .\n"
            "  python scripts/configure_workspace.py /root/projeto/\n"
            '  python scripts/configure_workspace.py "C:\\Users\\User\\MeuProjeto"\n'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Caminho do repositório alvo (opcional)",
    )
    parser.add_argument(
        "-t",
        "--target",
        dest="target_flag",
        help="Caminho do repositório alvo (compatibilidade)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent

    target_raw = args.target or args.target_flag
    target_path = Path(target_raw).resolve() if target_raw else None
    if target_path:
        if not target_path.exists() or not target_path.is_dir():
            print(
                f"\n[x] Erro: O caminho especificado não existe ou não é um diretório: {target_path}\n"
            )
            sys.exit(1)
        init_workspace(target_path, interactive=False)

    scanned = scan_repository(repo_root)

    while True:
        clear_screen()
        target_display = (
            str(target_path)
            if target_path
            else "[Não definido - digite 'w' ou selecione uma opção]"
        )

        print("\n" + "=" * 65)
        print("  CONFIGURADOR DE AGENTES, REGRAS E SKILLS - ANTIGRAVITY")
        print("=" * 65)
        print(f"  Workspace Alvo: {target_display}")
        print("-" * 65)
        print("  [1] Configuração Global (Vincular core global ao Antigravity)")
        print("  [2] Agents (Subagentes para o Workspace)")
        print("  [3] Rules (Regras para o Workspace)")
        print("  [4] Skills (Skills modulares para o Workspace)")
        print("  [5] Sair")
        print("-" * 65)
        print("  [w] Definir / Alterar Workspace Alvo")
        print("=" * 65)

        try:
            choice = input("\nEscolha uma opção (1-5 ou 'w'): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando configurador. Até logo!\n")
            sys.exit(0)

        if choice in ("1", "global"):
            handle_global_configuration(repo_root)

        elif choice in ("2", "agents", "agent"):
            target_path = resolve_workspace(target_path)
            if target_path:
                handle_agents(target_path, scanned)

        elif choice in ("3", "rules", "rule"):
            target_path = resolve_workspace(target_path)
            if target_path:
                handle_rules(target_path, scanned)

        elif choice in ("4", "skills", "skill"):
            target_path = resolve_workspace(target_path)
            if target_path:
                handle_skills(target_path, scanned, repo_root)

        elif choice in ("5", "sair", "exit", "q", "quit"):
            print("\nEncerrando configurador. Até logo!\n")
            sys.exit(0)

        elif choice in ("w", "workspace"):
            new_target = resolve_workspace(None)
            if new_target:
                target_path = new_target

        else:
            print("[!] Opção inválida. Digite um número de 1 a 5 ou 'w'.")


if __name__ == "__main__":
    main()
