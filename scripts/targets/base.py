#!/usr/bin/env python3
"""
Modulo base com utilitarios e classe abstrata para alvos de configuracao (Targets).
Multiplataforma (Windows, Linux e macOS) sem dependencias externas.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def is_link(path: Path) -> bool:
    """Verifica se o caminho e um link simbolico ou junction no Windows/Unix."""
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
    """Remove um link com seguranca, sem deletar arquivos reais do alvo."""
    if not path.exists() and not path.is_symlink():
        return
    if sys.platform.startswith("win"):
        try:
            os.rmdir(path)
        except OSError:
            subprocess.run(["cmd", "/c", "rmdir", str(path)], check=True)
    else:
        if path.is_symlink():
            path.unlink()
        else:
            path.rmdir()


def create_dir_link(src: Path, dst: Path):
    """Cria um link de diretorio multiplataforma (Junction no Windows, Symlink no Unix)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        if is_link(dst):
            remove_dir_link(dst)
        else:
            backup_dst = dst.with_name(f"{dst.name}.backup")
            print(f"  [!] Diretorio ja existente nao e um link: {dst}")
            print(f"      Movendo para backup: {backup_dst.name}")
            dst.rename(backup_dst)

    if sys.platform.startswith("win"):
        try:
            import _winapi

            _winapi.CreateJunction(str(src), str(dst))
        except (AttributeError, OSError):
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
                check=True,
                shell=True,
            )
    else:
        dst.symlink_to(src, target_is_directory=True)


def safe_write_text(path: Path, content: str):
    """Grava conteudo em arquivo garantindo que o diretorio pai exista."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def safe_remove_file(path: Path):
    """Remove arquivo se existir."""
    if path.exists():
        path.unlink()


def safe_remove_dir_if_empty(path: Path):
    """Remove diretorio somente se estiver vazio."""
    if path.exists() and path.is_dir():
        try:
            if not any(path.iterdir()):
                path.rmdir()
        except OSError:
            pass


def safe_remove_tree(path: Path):
    """Remove diretorio e todo seu conteudo recursivamente."""
    if not path.exists():
        if is_link(path):
            remove_dir_link(path)
        return
    if is_link(path):
        remove_dir_link(path)
    elif path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    elif path.is_file():
        path.unlink()


def update_gitignore(target_path: Path, entries: list[str]):
    """Adiciona entradas ao .gitignore do projeto alvo caso ainda nao estejam presentes."""
    if not entries:
        return
    gitignore_path = target_path / ".gitignore"
    existing_lines: set[str] = set()
    raw_content = ""

    if gitignore_path.exists():
        try:
            raw_content = gitignore_path.read_text(encoding="utf-8")
            existing_lines = {line.strip() for line in raw_content.splitlines()}
        except OSError:
            existing_lines = set()

    to_add = [e for e in entries if e.strip() not in existing_lines]
    if not to_add:
        return

    with gitignore_path.open("a", encoding="utf-8") as f:
        if raw_content and not raw_content.endswith("\n"):
            f.write("\n")
        for item in to_add:
            f.write(f"{item}\n")
    print(f"  [+] Atualizado .gitignore com: {', '.join(to_add)}")


def remove_from_gitignore(target_path: Path, entries: list[str]):
    """Remove entradas do .gitignore do projeto alvo."""
    gitignore_path = target_path / ".gitignore"
    if not gitignore_path.exists():
        return

    try:
        content = gitignore_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        entries_set = set(entries)
        new_lines = [line for line in lines if line.strip() not in entries_set]
        if len(new_lines) != len(lines):
            new_content = "\n".join(new_lines)
            if new_content:
                new_content += "\n"
            gitignore_path.write_text(new_content, encoding="utf-8")
            print(f"  [-] Removido do .gitignore: {', '.join(entries)}")
    except OSError:
        pass


def parse_frontmatter(file_path: Path) -> tuple[str, str]:
    """Extrai campos basicos de frontmatter YAML simples sem dependencias externas."""
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


def load_workspace_state(target_path: Path) -> dict[str, Any]:
    """Carrega o estado e preferencias salvas no workspace alvo."""
    state_file = target_path / ".agents" / "workspace_state.json"
    if not state_file.exists():
        # Tenta carregar legado skills.json caso exista
        skills_file = target_path / ".agents" / "skills.json"
        selected_skills: dict[str, set[str]] = {}
        if skills_file.exists():
            try:
                data = json.loads(skills_file.read_text(encoding="utf-8"))
                for entry in data.get("entries", []):
                    cat_name = Path(entry.get("path", "")).name
                    include_only = entry.get("include_only", [])
                    if cat_name and include_only:
                        selected_skills[cat_name] = set(include_only)
            except (json.JSONDecodeError, OSError):
                pass

        return {
            "active_targets": ["antigravity"] if skills_file.exists() else [],
            "selected_agents": [],
            "selected_rules": ["AGENTS.md"],
            "selected_skills": {k: sorted(v) for k, v in selected_skills.items()},
        }

    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        return {
            "active_targets": data.get("active_targets", []),
            "selected_agents": data.get("selected_agents", []),
            "selected_rules": data.get("selected_rules", []),
            "selected_skills": data.get("selected_skills", {}),
        }
    except (json.JSONDecodeError, OSError):
        return {
            "active_targets": [],
            "selected_agents": [],
            "selected_rules": [],
            "selected_skills": {},
        }


def save_workspace_state(target_path: Path, state: dict[str, Any]):
    """Persiste o estado do workspace para permitir sincronizacao e limpeza posterior."""
    state_file = target_path / ".agents" / "workspace_state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    update_gitignore(target_path, [".agents/"])


class BaseTarget:
    """Classe base que define o contrato de um adaptador de ferramenta."""

    target_id: str = ""
    display_name: str = ""
    description: str = ""
    supports_global: bool = False

    def configure_workspace(
        self,
        target_path: Path,
        repo_root: Path,
        scanned: dict[str, Any],
        agents: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        skills_by_cat: dict[str, set[str]],
    ) -> bool:
        """Aplica a configuracao especifica da ferramenta no workspace alvo."""
        raise NotImplementedError

    def clean_workspace(self, target_path: Path) -> bool:
        """Remove arquivos de configuracao criados para esta ferramenta no workspace alvo."""
        raise NotImplementedError

    def configure_global(self, repo_root: Path) -> bool:
        """Aplica configuracao global da ferramenta no ambiente do usuario."""
        return False

    def clean_global(self) -> bool:
        """Remove configuracao global da ferramenta."""
        return False
