#!/usr/bin/env python3
"""
Universal adapter and open standard derivatives (AGENTS.md).
Supports:
- Universal (pure AGENTS.md in project root)
- Kiro (AGENTS.md + .kiro/)
- OpenCode (AGENTS.md + .opencode/)
- Codex (AGENTS.md for OpenAI Codex ecosystem)
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
    t_target,
)


class UniversalTarget(BaseTarget):
    target_id = "universal"
    display_name = "Universal (AGENTS.md)"
    description = "Generates standardized AGENTS.md in project root"
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

        header_title = f"# Project Guidelines (AGENTS.md{title_suffix})"
        sections = [
            header_title,
            "",
            "> This file defines standards, rules, and tool catalogs followed by AI agents.",
            "",
        ]

        # 1. Rules
        if rules:
            sections.append("## Global Development Guidelines")
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
            sections.append("## Specialized Subagent Personas")
            sections.append("")
            for a in agents:
                agent_path = Path(a["path"])
                name, desc = parse_frontmatter(agent_path)
                sections.append(f"### {name}")
                if desc:
                    sections.append(f"**Description:** {desc}")
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
            sections.append("## Operating Procedures & Modular Skills")
            sections.append("")
            for cat_name in sorted(skills_by_cat.keys()):
                skill_ids = skills_by_cat[cat_name]
                if not skill_ids:
                    continue
                sections.append(f"### Category: {cat_name.upper()}")
                for s_id in sorted(skill_ids):
                    skill_file = repo_root / "skills" / cat_name / s_id / "SKILL.md"
                    if skill_file.exists():
                        _, s_desc = parse_frontmatter(skill_file)
                        desc_str = f" - {s_desc}" if s_desc else ""
                        sections.append(f"- **{s_id}**{desc_str}")
                        sections.append(
                            f"  *Path:* `{skill_file.resolve().as_posix()}`"
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
        lang: str = "en",
    ) -> bool:
        dest = self.generate_agents_md(
            target_path, repo_root, agents, rules, skills_by_cat
        )
        print(f"  [+] {t_target('universal_generated', lang, name=dest.name)}")
        return True

    def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
        agents_md = target_path / "AGENTS.md"
        safe_remove_file(agents_md)
        print(f"  [-] {t_target('universal_clean_done', lang)}")
        return True


class KiroTarget(UniversalTarget):
    target_id = "kiro"
    display_name = "Kiro"
    description = "Generates AGENTS.md and support structure in .kiro/"
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
        dest = self.generate_agents_md(
            target_path, repo_root, agents, rules, skills_by_cat, title_suffix=" - Kiro"
        )
        kiro_dir = target_path / ".kiro"
        kiro_dir.mkdir(parents=True, exist_ok=True)
        print(f"  [+] {t_target('kiro_generated', lang, name=dest.name)}")
        return True

    def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
        super().clean_workspace(target_path, lang=lang)
        kiro_dir = target_path / ".kiro"
        safe_remove_tree(kiro_dir)
        print(f"  [-] {t_target('kiro_clean_done', lang)}")
        return True


class OpenCodeTarget(UniversalTarget):
    target_id = "opencode"
    display_name = "OpenCode"
    description = "Generates AGENTS.md and support structure in .opencode/"
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
        print(f"  [+] {t_target('opencode_generated', lang, name=dest.name)}")
        return True

    def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
        super().clean_workspace(target_path, lang=lang)
        opencode_dir = target_path / ".opencode"
        safe_remove_tree(opencode_dir)
        print(f"  [-] {t_target('opencode_clean_done', lang)}")
        return True


class CodexTarget(UniversalTarget):
    target_id = "codex"
    display_name = "Codex (OpenAI)"
    description = "Generates AGENTS.md optimized for the OpenAI Codex ecosystem"
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
        dest = self.generate_agents_md(
            target_path,
            repo_root,
            agents,
            rules,
            skills_by_cat,
            title_suffix=" - Codex",
        )
        print(f"  [+] {t_target('codex_generated', lang, name=dest.name)}")
        return True

    def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
        return super().clean_workspace(target_path, lang=lang)
