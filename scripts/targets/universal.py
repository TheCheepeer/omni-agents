#!/usr/bin/env python3
"""
Adaptador Universal e derivados de padrao aberto (AGENTS.md).
Atende:
- Universal (AGENTS.md puro na raiz)
- Kiro (AGENTS.md + .kiro/)
- OpenCode (AGENTS.md + .opencode/)
- Codex (AGENTS.md para ecossistema OpenAI Codex)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import (
    BaseTarget,
    parse_frontmatter,
    safe_remove_file,
    safe_remove_tree,
    safe_write_text,
)


class UniversalTarget(BaseTarget):
    target_id = "universal"
    display_name = "Universal (AGENTS.md)"
    description = "Gera AGENTS.md agnostico e padronizado na raiz do projeto"
    supports_global = False

    def generate_agents_md(
        self,
        target_path: Path,
        repo_root: Path,
        agents: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        skills_by_cat: dict[str, set[str]],
        title_suffix: str = "",
    ) -> Path:
        agents_md = target_path / "AGENTS.md"

        header_title = f"# Diretrizes do Projeto (AGENTS.md{title_suffix})"
        sections = [
            header_title,
            "",
            "> Este arquivo define padroes, regras e catalogo de ferramentas seguidos por agentes de IA.",
            "",
        ]

        # 1. Regras
        if rules:
            sections.append("## Diretrizes Globais de Desenvolvimento")
            sections.append("")
            for r in rules:
                rule_path = Path(r["path"])
                try:
                    content = rule_path.read_text(encoding="utf-8")
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            content = parts[2].strip()
                    sections.append(content)
                    sections.append("")
                except OSError:
                    pass

        # 2. Subagentes
        if agents:
            sections.append("## Personas de Subagentes Especializados")
            sections.append("")
            for a in agents:
                agent_path = Path(a["path"])
                name, desc = parse_frontmatter(agent_path)
                sections.append(f"### {name}")
                if desc:
                    sections.append(f"**Descricao:** {desc}")
                try:
                    body = agent_path.read_text(encoding="utf-8")
                    if body.startswith("---"):
                        parts = body.split("---", 2)
                        if len(parts) >= 3:
                            body = parts[2].strip()
                    sections.append("")
                    sections.append(body)
                    sections.append("")
                except OSError:
                    pass

        # 3. Skills
        total_skills = sum(len(v) for v in skills_by_cat.values())
        if total_skills > 0:
            sections.append("## Catalogo de Habilidades e Procedimentos (Skills)")
            sections.append("")
            for cat_name in sorted(skills_by_cat.keys()):
                skill_ids = skills_by_cat[cat_name]
                if not skill_ids:
                    continue
                sections.append(f"### Categoria: {cat_name.upper()}")
                for s_id in sorted(skill_ids):
                    skill_file = repo_root / "skills" / cat_name / s_id / "SKILL.md"
                    if skill_file.exists():
                        _, s_desc = parse_frontmatter(skill_file)
                        desc_str = f" - {s_desc}" if s_desc else ""
                        sections.append(f"- **{s_id}**{desc_str}")
                        sections.append(
                            f"  *Caminho:* `{skill_file.resolve().as_posix()}`"
                        )
                sections.append("")

        output_text = "\n".join(sections).strip() + "\n"
        safe_write_text(agents_md, output_text)
        return agents_md

    def configure_workspace(
        self,
        target_path: Path,
        repo_root: Path,
        scanned: dict[str, Any],
        agents: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        skills_by_cat: dict[str, set[str]],
    ) -> bool:
        dest = self.generate_agents_md(
            target_path, repo_root, agents, rules, skills_by_cat
        )
        print(f"  [+] Universal: gerado arquivo {dest.name} na raiz do projeto.")
        return True

    def clean_workspace(self, target_path: Path) -> bool:
        agents_md = target_path / "AGENTS.md"
        safe_remove_file(agents_md)
        print("  [-] Universal: AGENTS.md removido do workspace.")
        return True


class KiroTarget(UniversalTarget):
    target_id = "kiro"
    display_name = "Kiro"
    description = "Gera AGENTS.md e estrutura de suporte em .kiro/"
    supports_global = False

    def configure_workspace(
        self,
        target_path: Path,
        repo_root: Path,
        scanned: dict[str, Any],
        agents: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        skills_by_cat: dict[str, set[str]],
    ) -> bool:
        # Gera AGENTS.md padrao
        dest = self.generate_agents_md(
            target_path, repo_root, agents, rules, skills_by_cat, title_suffix=" - Kiro"
        )
        kiro_dir = target_path / ".kiro"
        kiro_dir.mkdir(parents=True, exist_ok=True)
        print(f"  [+] Kiro: configurado {dest.name} e pasta .kiro/ criada.")
        return True

    def clean_workspace(self, target_path: Path) -> bool:
        super().clean_workspace(target_path)
        kiro_dir = target_path / ".kiro"
        safe_remove_tree(kiro_dir)
        print("  [-] Kiro: pasta .kiro/ removida.")
        return True


class OpenCodeTarget(UniversalTarget):
    target_id = "opencode"
    display_name = "OpenCode"
    description = "Gera AGENTS.md e estrutura de suporte em .opencode/"
    supports_global = False

    def configure_workspace(
        self,
        target_path: Path,
        repo_root: Path,
        scanned: dict[str, Any],
        agents: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        skills_by_cat: dict[str, set[str]],
    ) -> bool:
        dest = self.generate_agents_md(
            target_path,
            repo_root,
            agents,
            rules,
            skills_by_cat,
            title_suffix=" - OpenCode",
        )
        opencode_dir = target_path / ".opencode"
        opencode_dir.mkdir(parents=True, exist_ok=True)
        print(f"  [+] OpenCode: configurado {dest.name} e pasta .opencode/ criada.")
        return True

    def clean_workspace(self, target_path: Path) -> bool:
        super().clean_workspace(target_path)
        opencode_dir = target_path / ".opencode"
        safe_remove_tree(opencode_dir)
        print("  [-] OpenCode: pasta .opencode/ removida.")
        return True


class CodexTarget(UniversalTarget):
    target_id = "codex"
    display_name = "Codex (OpenAI)"
    description = "Gera AGENTS.md otimizado para o ecossistema Codex"
    supports_global = False

    def configure_workspace(
        self,
        target_path: Path,
        repo_root: Path,
        scanned: dict[str, Any],
        agents: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        skills_by_cat: dict[str, set[str]],
    ) -> bool:
        dest = self.generate_agents_md(
            target_path,
            repo_root,
            agents,
            rules,
            skills_by_cat,
            title_suffix=" - Codex",
        )
        print(f"  [+] Codex: configurado {dest.name} na raiz do projeto.")
        return True

    def clean_workspace(self, target_path: Path) -> bool:
        return super().clean_workspace(target_path)
