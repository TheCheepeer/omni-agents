#!/usr/bin/env python3
"""
Adapter for GitHub Copilot.
Generates consolidated .github/copilot-instructions.md with rules,
guidelines, and modular skills catalog.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import (
    BaseTarget,
    find_skill_file,
    parse_frontmatter,
    safe_remove_dir_if_empty,
    safe_remove_file,
    safe_write_text,
    t_target,
)


class CopilotTarget(BaseTarget):
    target_id = "copilot"
    display_name = "GitHub Copilot"
    description = (
        "Generates consolidated instructions in .github/copilot-instructions.md"
    )
    supports_global = False

    def configure_workspace(
        self,
        target_path: Path,
        repo_root: Path,
        scanned: dict[str, Any],
        agents: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        skills_by_cat: dict[str, set[str]],
        lang: str = "en",
    ) -> bool:
        github_dir = target_path / ".github"
        github_dir.mkdir(parents=True, exist_ok=True)
        copilot_file = github_dir / "copilot-instructions.md"

        sections = [
            "# GitHub Copilot Custom Instructions",
            "",
            "> Engineering guidelines and development standards synchronized from omni-agents.",
            "",
        ]

        # 1. Rules
        if rules:
            sections.append("## Development Guidelines & Engineering Standards")
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

        # 2. Subagents
        if agents:
            sections.append("## Recommended Personas & Roles")
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
            sections.append("## Operating Procedures & Skills")
            sections.append("")
            for cat_name in sorted(skills_by_cat.keys()):
                skill_ids = skills_by_cat[cat_name]
                if not skill_ids:
                    continue
                sections.append(f"### Category: {cat_name.upper()}")
                for s_id in sorted(skill_ids):
                    skill_file = find_skill_file(repo_root, scanned, cat_name, s_id)
                    if skill_file.exists():
                        _, s_desc = parse_frontmatter(skill_file)
                        desc_str = f" - {s_desc}" if s_desc else ""
                        sections.append(f"- **{s_id}**{desc_str}")
                sections.append("")

        output_text = "\n".join(sections).strip() + "\n"
        safe_write_text(copilot_file, output_text)
        print(
            f"  [+] {t_target('copilot_generated', lang, path=copilot_file.relative_to(target_path))}"
        )
        return True

    def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
        github_dir = target_path / ".github"
        copilot_file = github_dir / "copilot-instructions.md"
        safe_remove_file(copilot_file)
        safe_remove_dir_if_empty(github_dir)
        print(f"  [-] {t_target('copilot_clean_done', lang)}")
        return True
