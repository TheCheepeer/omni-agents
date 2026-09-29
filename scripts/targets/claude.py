#!/usr/bin/env python3
"""
Adapter for Claude Code / Anthropic.
Generates consolidated CLAUDE.md in project root with rules,
subagents, and modular skills catalog, plus ~/.claude/ global support.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import (
    BaseTarget,
    find_skill_file,
    parse_frontmatter,
    safe_remove_file,
    safe_remove_tree,
    safe_write_text,
    t_target,
)


class ClaudeTarget(BaseTarget):
    target_id = "claude"
    display_name = "Claude Code (Anthropic)"
    description = (
        "Generates CLAUDE.md in workspace root and global instructions in ~/.claude/"
    )
    supports_global = True

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
        claude_md = target_path / "CLAUDE.md"

        sections = [
            "# Project Instructions (Claude Code)",
            "",
            "> Engineering guidelines, subagents, and operating procedures synchronized automatically from omni-agent.",
            "",
        ]

        # 1. Rules
        if rules:
            sections.append("## Global Engineering Guidelines & Rules")
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
            sections.append("## Specialized Subagents & Personas")
            sections.append("")
            sections.append(
                "When performing complex tasks, adopt the persona or delegate to the following specialized profiles:"
            )
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
            sections.append("## Operating Procedures & Skills")
            sections.append("")
            sections.append("Modular procedures to be followed when applicable:")
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
                        sections.append(
                            f"  *Location:* `{skill_file.resolve().as_posix()}`"
                        )
                sections.append("")

        output_text = "\n".join(sections).strip() + "\n"
        safe_write_text(claude_md, output_text)
        print(f"  [+] {t_target('claude_generated', lang, name=claude_md.name)}")
        return True

    def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
        claude_md = target_path / "CLAUDE.md"
        claude_dir = target_path / ".claude"
        safe_remove_file(claude_md)
        safe_remove_tree(claude_dir)
        print(f"  [-] {t_target('claude_clean_done', lang)}")
        return True

    def configure_global(self, repo_root: Path, lang: str = "en") -> bool:
        claude_global = Path.home() / ".claude"
        claude_global.mkdir(parents=True, exist_ok=True)
        global_rule = claude_global / "CLAUDE.md"

        if global_rule.exists():
            try:
                ans = (
                    input(f"\n  [?] {t_target('claude_rules_overwrite_prompt', lang)}")
                    .strip()
                    .lower()
                )
                should_overwrite = ans in ("s", "sim", "y", "yes")
            except (EOFError, KeyboardInterrupt):
                should_overwrite = False
            if not should_overwrite:
                print(f"  [i] {t_target('claude_global_rules_kept', lang)}")
                return True

        rules_dir = repo_root / "rules"
        content_parts = ["# Global User Instructions (Claude Code)\n"]
        if rules_dir.exists():
            for f in sorted(rules_dir.glob("*.md")):
                try:
                    content_parts.append(f.read_text(encoding="utf-8"))
                    content_parts.append("\n---\n")
                except OSError:
                    pass

        safe_write_text(global_rule, "\n".join(content_parts))
        print(f"  [+] {t_target('claude_global_done', lang, path=global_rule)}")
        return True

    def clean_global(self, lang: str = "en") -> bool:
        global_rule = Path.home() / ".claude" / "CLAUDE.md"
        safe_remove_file(global_rule)
        print(f"  [-] {t_target('claude_global_removed', lang)}")
        return True
