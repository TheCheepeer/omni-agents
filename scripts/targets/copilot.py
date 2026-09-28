#!/usr/bin/env python3
"""
Adaptador para GitHub Copilot.
Gera o arquivo consolidado .github/copilot-instructions.md com regras,
diretrizes e catalogo de skills ativas.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import (
    BaseTarget,
    parse_frontmatter,
    safe_remove_dir_if_empty,
    safe_remove_file,
    safe_write_text,
)


class CopilotTarget(BaseTarget):
    target_id = "copilot"
    display_name = "GitHub Copilot"
    description = "Gera instrucoes consolidadas em .github/copilot-instructions.md"
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
        github_dir = target_path / ".github"
        github_dir.mkdir(parents=True, exist_ok=True)
        copilot_file = github_dir / "copilot-instructions.md"

        sections = [
            "# GitHub Copilot Custom Instructions",
            "",
            "> Diretrizes e padroes de desenvolvimento sincronizados a partir do repositorio central.",
            "",
        ]

        # 1. Regras
        if rules:
            sections.append("## Diretrizes de Desenvolvimento e Padroes")
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
            sections.append("## Papeis e Personas Sugeridas")
            sections.append("")
            for a in agents:
                agent_path = Path(a["path"])
                name, desc = parse_frontmatter(agent_path)
                sections.append(f"### Persona: {name}")
                if desc:
                    sections.append(f"*{desc}*")
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
            sections.append("## Procedimentos e Habilidades (Skills)")
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
                sections.append("")

        output_text = "\n".join(sections).strip() + "\n"
        safe_write_text(copilot_file, output_text)
        print(
            f"  [+] Copilot: instrucoes geradas em {copilot_file.relative_to(target_path)}"
        )
        return True

    def clean_workspace(self, target_path: Path) -> bool:
        github_dir = target_path / ".github"
        copilot_file = github_dir / "copilot-instructions.md"
        safe_remove_file(copilot_file)
        safe_remove_dir_if_empty(github_dir)
        print("  [-] Copilot: copilot-instructions.md removido.")
        return True
