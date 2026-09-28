#!/usr/bin/env python3
"""
Adaptador para Claude Code / Anthropic.
Gera o arquivo CLAUDE.md consolidado na raiz do projeto com regras,
subagentes e catalogo de skills disponiveis, alem de suporte a ~/.claude/.
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


class ClaudeTarget(BaseTarget):
    target_id = "claude"
    display_name = "Claude Code (Anthropic)"
    description = "Gera CLAUDE.md na raiz do workspace e instrucoes em ~/.claude/"
    supports_global = True

    def configure_workspace(
        self,
        target_path: Path,
        repo_root: Path,
        scanned: dict[str, Any],
        agents: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        skills_by_cat: dict[str, set[str]],
    ) -> bool:
        claude_md = target_path / "CLAUDE.md"

        sections = [
            "# Instrucoes do Projeto (Claude Code)",
            "",
            "> Diretrizes, subagentes e procedimentos configurados automaticamente a partir do repositorio central de agentes.",
            "",
        ]

        # 1. Regras
        if rules:
            sections.append("## Diretrizes e Regras Globais")
            sections.append("")
            for r in rules:
                rule_path = Path(r["path"])
                try:
                    content = rule_path.read_text(encoding="utf-8")
                    # Remove frontmatter se houver para apresentacao limpa
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
            sections.append("## Subagentes e Personas Especializadas")
            sections.append("")
            sections.append(
                "Ao executar tarefas complexas, utilize a postura ou delegue para os seguintes perfis especializados:"
            )
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
            sections.append("## Habilidades e Procedimentos (Skills)")
            sections.append("")
            sections.append(
                "Procedimentos modulares que devem ser seguidos quando aplicavel:"
            )
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
                            f"  *Localizacao:* `{skill_file.resolve().as_posix()}`"
                        )
                sections.append("")

        output_text = "\n".join(sections).strip() + "\n"
        safe_write_text(claude_md, output_text)
        print(f"  [+] Claude Code: arquivo gerado em {claude_md.name}")
        return True

    def clean_workspace(self, target_path: Path) -> bool:
        claude_md = target_path / "CLAUDE.md"
        claude_dir = target_path / ".claude"
        safe_remove_file(claude_md)
        safe_remove_tree(claude_dir)
        print("  [-] Claude Code: CLAUDE.md e .claude/ removidos do workspace.")
        return True

    def configure_global(self, repo_root: Path) -> bool:
        claude_global = Path.home() / ".claude"
        claude_global.mkdir(parents=True, exist_ok=True)
        global_rule = claude_global / "CLAUDE.md"

        # Le regras globais
        rules_dir = repo_root / "rules"
        content_parts = ["# Instrucoes Globais do Usuario (Claude Code)\n"]
        if rules_dir.exists():
            for f in sorted(rules_dir.glob("*.md")):
                try:
                    content_parts.append(f.read_text(encoding="utf-8"))
                    content_parts.append("\n---\n")
                except OSError:
                    pass

        safe_write_text(global_rule, "\n".join(content_parts))
        print(f"  [+] Claude Global: configurado em {global_rule}")
        return True

    def clean_global(self) -> bool:
        global_rule = Path.home() / ".claude" / "CLAUDE.md"
        safe_remove_file(global_rule)
        print("  [-] Claude Global: arquivo ~/.claude/CLAUDE.md removido.")
        return True
