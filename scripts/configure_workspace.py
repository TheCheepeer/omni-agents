#!/usr/bin/env python3
"""
Configurador Declarativo de Workspace para Antigravity / Agents.

Funciona de forma multiplataforma (Windows e Linux).
Abre uma janela para seleção da pasta do repositório alvo (ou aceita via CLI),
escaneia dinamicamente as categorias de skills, subagentes e regras,
permite a seleção interativa e gera a configuração em .agents/skills.json,
além de garantir que .agents/ esteja no .gitignore do projeto alvo.
"""

import argparse
import json
import sys
from pathlib import Path


# Tentativa de carregar interface gráfica (Tkinter) para seleção de pasta
def pick_directory_gui(title="Selecione o Repositório de Destino"):
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return None

    try:
        root = tk.Tk()
        root.withdraw()
        # Garante que a janela apareça na frente
        root.attributes("-topmost", True)
        selected_path = filedialog.askdirectory(title=title)
        root.destroy()
        return selected_path if selected_path else None
    except (tk.TclError, RuntimeError, OSError):
        return None


def parse_frontmatter(file_path: Path):
    """Extrai campos básicos de frontmatter YAML simples sem dependências externas."""
    default_name = file_path.parent.name
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return default_name, ""

    name, description = default_name, ""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_text = parts[1]
            for line in yaml_text.splitlines():
                stripped = line.strip()
                if stripped.startswith("name:"):
                    name = stripped.split("name:", 1)[1].strip().strip('"').strip("'")
                elif stripped.startswith("description:"):
                    description = (
                        stripped.split("description:", 1)[1]
                        .strip()
                        .strip('"')
                        .strip("'")
                    )
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
            data["agents"].append({"id": item.name, "path": item.resolve()})

    # 3. Escaneia Regras
    rules_dir = repo_root / "rules"
    if rules_dir.exists() and rules_dir.is_dir():
        for item in sorted(rules_dir.glob("*.md")):
            data["rules"].append({"id": item.name, "path": item.resolve()})

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


def main():
    parser = argparse.ArgumentParser(
        description="Configurador declarativo de Workspace para Antigravity."
    )
    parser.add_argument("-t", "--target", help="Caminho do repositório alvo (opcional)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent

    print("\n" + "=" * 65)
    print("  CONFIGURADOR DECLARATIVO DE WORKSPACE - ANTIGRAVITY")
    print("=" * 65)

    # 1. Seleção do repositório alvo
    target_dir = args.target
    if not target_dir:
        print("\n-> Abrindo janela para selecionar o repositório de destino...")
        target_dir = pick_directory_gui("Selecione o repositório do projeto")

    if not target_dir:
        print("\n[!] Nenhuma pasta selecionada pela janela.")
        target_dir = input(
            "Digite o caminho do repositório alvo manualmente (ou Enter para sair): "
        ).strip()
        if not target_dir:
            print("Operação cancelada.")
            sys.exit(0)

    target_path = Path(target_dir).resolve()
    if not target_path.exists() or not target_path.is_dir():
        print(
            f"[x] Erro: O caminho especificado não existe ou não é um diretório: {target_path}"
        )
        sys.exit(1)

    print(f"\n[OK] Repositório alvo selecionado:\n     {target_path}")

    # 2. Escaneamento automático de categorias
    scanned = scan_repository(repo_root)

    selectable_items = []
    item_counter = 1

    print("\n" + "-" * 65)
    print("  CATÁLOGO DE SKILLS DISPONÍVEIS POR CATEGORIA")
    print("-" * 65)

    for cat_name, skills in scanned["skills_by_category"].items():
        print(f"\n[Categoria: {cat_name.upper()}] ({len(skills)} skills)")
        for s in skills:
            desc_preview = (
                s["description"][:75] + "..."
                if len(s["description"]) > 75
                else s["description"]
            )
            print(f"  [{item_counter:2d}] {s['id']:<26} - {desc_preview}")
            selectable_items.append(
                {
                    "num": item_counter,
                    "type": "skill",
                    "category": cat_name,
                    "id": s["id"],
                    "path": s["path"],
                }
            )
            item_counter += 1

    if scanned["agents"]:
        print(f"\n[SUBAGENTES] ({len(scanned['agents'])} agentes)")
        for a in scanned["agents"]:
            print(f"  [{item_counter:2d}] {a['id']:<26} (subagente especializado)")
            selectable_items.append(
                {"num": item_counter, "type": "agent", "id": a["id"], "path": a["path"]}
            )
            item_counter += 1

    if scanned["rules"]:
        print(f"\n[REGRAS] ({len(scanned['rules'])} regras)")
        for r in scanned["rules"]:
            print(f"  [{item_counter:2d}] {r['id']:<26} (regras de diretrizes/padroes)")
            selectable_items.append(
                {"num": item_counter, "type": "rule", "id": r["id"], "path": r["path"]}
            )
            item_counter += 1

    print("\n" + "=" * 65)
    print("  SELEÇÃO DE ITENS")
    print("  * Digite os números separados por vírgula (ex: 1, 3, 7)")
    print("  * Ou digite o nome de categorias inteiras (ex: stacks, planning, agents)")
    print("  * Ou 'all' para selecionar tudo, ou 'enter' para nenhum")
    print("=" * 65)

    user_input = input("\nSua escolha: ").strip().lower()
    if not user_input:
        print("[!] Nenhum item selecionado. Nenhuma alteração feita.")
        sys.exit(0)

    selected_tokens = [
        t.strip() for t in user_input.replace(";", ",").split(",") if t.strip()
    ]

    selected_skills_by_cat = {}
    selected_agents = []
    selected_rules = []

    # Processa 'all'
    if "all" in selected_tokens:
        for item in selectable_items:
            if item["type"] == "skill":
                selected_skills_by_cat.setdefault(item["category"], []).append(
                    item["id"]
                )
            elif item["type"] == "agent":
                selected_agents.append(item)
            elif item["type"] == "rule":
                selected_rules.append(item)
    else:
        for token in selected_tokens:
            # Verifica se é nome de categoria inteira
            if token in scanned["skills_by_category"]:
                for s in scanned["skills_by_category"][token]:
                    selected_skills_by_cat.setdefault(token, []).append(s["id"])
            elif token == "agents":
                selected_agents.extend(scanned["agents"])
            elif token == "rules":
                selected_rules.extend(scanned["rules"])
            # Verifica se é número
            elif token.isdigit():
                num = int(token)
                matched = next(
                    (item for item in selectable_items if item["num"] == num), None
                )
                if matched:
                    if matched["type"] == "skill":
                        selected_skills_by_cat.setdefault(
                            matched["category"], []
                        ).append(matched["id"])
                    elif matched["type"] == "agent":
                        selected_agents.append(matched)
                    elif matched["type"] == "rule":
                        selected_rules.append(matched)
            # Verifica se é o próprio nome da skill/agente/regra
            else:
                matched = next(
                    (item for item in selectable_items if item["id"].lower() == token),
                    None,
                )
                if matched:
                    if matched["type"] == "skill":
                        selected_skills_by_cat.setdefault(
                            matched["category"], []
                        ).append(matched["id"])
                    elif matched["type"] == "agent":
                        selected_agents.append(matched)
                    elif matched["type"] == "rule":
                        selected_rules.append(matched)

    # 3. Aplica no projeto alvo
    print("\n-> Aplicando configurações no workspace alvo...")

    agents_workspace_dir = target_path / ".agents"
    agents_workspace_dir.mkdir(exist_ok=True)

    # 3.1 Gera .agents/skills.json
    total_skills = sum(len(v) for v in selected_skills_by_cat.values())
    if total_skills > 0:
        entries = []
        for cat_name, skill_ids in selected_skills_by_cat.items():
            cat_path = (repo_root / "skills" / cat_name).resolve().as_posix()
            entries.append({"path": cat_path, "include_only": sorted(set(skill_ids))})

        skills_json_path = agents_workspace_dir / "skills.json"
        skills_manifest = {"entries": entries}
        skills_json_path.write_text(
            json.dumps(skills_manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  [+] Manifesto gerado: {skills_json_path}")
        print(
            f"      ({total_skills} skills configuradas em {len(entries)} categorias)"
        )

    # 3.2 Subagentes (copia para .agents/agents/)
    if selected_agents:
        target_agents_dir = agents_workspace_dir / "agents"
        target_agents_dir.mkdir(exist_ok=True)
        for a in selected_agents:
            dest = target_agents_dir / a["id"]
            dest.write_text(
                Path(a["path"]).read_text(encoding="utf-8"), encoding="utf-8"
            )
            print(f"  [+] Subagente ativado: {dest.name}")

    # 3.3 Regras (copia para .agents/rules/)
    if selected_rules:
        target_rules_dir = agents_workspace_dir / "rules"
        target_rules_dir.mkdir(exist_ok=True)
        for r in selected_rules:
            dest = target_rules_dir / r["id"]
            dest.write_text(
                Path(r["path"]).read_text(encoding="utf-8"), encoding="utf-8"
            )
            print(f"  [+] Regra ativada: {dest.name}")

    # 3.4 Adiciona .agents/ ao .gitignore
    update_gitignore(target_path)

    print("\n" + "=" * 65)
    print("  CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"  Workspace: {target_path}")
    print(f"  Configurações salvas em: {agents_workspace_dir}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
