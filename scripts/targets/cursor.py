#!/usr/bin/env python3
"""
Adapter for Cursor IDE.
Generates modern rule files in .cursor/rules/<name>.mdc format
with globs and alwaysApply metadata, plus legacy .cursorrules fallback.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import (
    BaseTarget,
    parse_frontmatter,
    safe_remove_dir_if_empty,
    safe_remove_file,
    safe_remove_tree,
    safe_write_text,
    t_target,
)


class CursorTarget(BaseTarget):
    target_id = "cursor"
    display_name = "Cursor IDE"
    description = (
        "Generates modern .cursor/rules/*.mdc rules and legacy .cursorrules fallback"
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
        cursor_rules_dir = target_path / ".cursor" / "rules"
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        # 1. Rules in .mdc format
        if rules:
            for r in rules:
                rule_path = Path(r["path"])
                name, desc = parse_frontmatter(rule_path)
                rule_id = rule_path.stem

                try:
                    content = rule_path.read_text(encoding="utf-8")
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            content = parts[2].strip()
                except OSError:
                    continue

                mdc_content = [
                    "---",
                    f'description: "{desc or name}"',
                    "globs: *",
                    "alwaysApply: true",
                    "---",
                    "",
                    content,
                ]

                dest_file = cursor_rules_dir / f"{rule_id}.mdc"
                safe_write_text(dest_file, "\n".join(mdc_content) + "\n")
                count += 1

        # 2. Subagents as persona rule
        if agents:
            subagent_sections = [
                "---",
                'description: "Specialized subagent personas for software development"',
                "globs: *",
                "alwaysApply: false",
                "---",
                "",
                "# Specialized Subagent Personas",
                "",
            ]
            for a in agents:
                agent_path = Path(a["path"])
                name, desc = parse_frontmatter(agent_path)
                subagent_sections.append(f"## {name}")
                if desc:
                    subagent_sections.append(f"**Description:** {desc}")
                try:
                    body = agent_path.read_text(encoding="utf-8")
                    if body.startswith("---"):
                        parts = body.split("---", 2)
                        if len(parts) >= 3:
                            body = parts[2].strip()
                    subagent_sections.append("")
                    subagent_sections.append(body)
                    subagent_sections.append("")
                except OSError:
                    pass

            dest_agent = cursor_rules_dir / "subagents.mdc"
            safe_write_text(dest_agent, "\n".join(subagent_sections).strip() + "\n")
            count += 1

        # 3. Skills catalog rule
        total_skills = sum(len(v) for v in skills_by_cat.values())
        if total_skills > 0:
            skill_sections = [
                "---",
                'description: "Catalog of modular skills and operating procedures"',
                "globs: *",
                "alwaysApply: true",
                "---",
                "",
                "# Operating Procedures & Modular Skills",
                "",
            ]
            for cat_name in sorted(skills_by_cat.keys()):
                skill_ids = skills_by_cat[cat_name]
                if not skill_ids:
                    continue
                skill_sections.append(f"### Category: {cat_name.upper()}")
                for s_id in sorted(skill_ids):
                    skill_file = repo_root / "skills" / cat_name / s_id / "SKILL.md"
                    if skill_file.exists():
                        _, s_desc = parse_frontmatter(skill_file)
                        desc_str = f" - {s_desc}" if s_desc else ""
                        skill_sections.append(f"- **{s_id}**{desc_str}")
                        skill_sections.append(
                            f"  *Path:* `{skill_file.resolve().as_posix()}`"
                        )
                skill_sections.append("")

            dest_skill = cursor_rules_dir / "skills.mdc"
            safe_write_text(dest_skill, "\n".join(skill_sections).strip() + "\n")
            count += 1

        print(f"  [+] {t_target('cursor_generated', lang, count=count)}")
        return True

    def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
        cursor_dir = target_path / ".cursor"
        cursorrules_file = target_path / ".cursorrules"
        safe_remove_file(cursorrules_file)
        if cursor_dir.exists():
            safe_remove_tree(cursor_dir / "rules")
            safe_remove_dir_if_empty(cursor_dir)
        print(f"  [-] {t_target('cursor_clean_done', lang)}")
        return True
