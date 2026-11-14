#!/usr/bin/env python3
"""
Adapter for Google Antigravity.
Configures subagents, rules, and workspace-local skills in .agents/ directory
and supports global configuration in ~/.gemini/config/.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from .base import (
    BaseTarget,
    create_dir_link,
    is_link,
    remove_dir_link,
    safe_remove_dir_if_empty,
    safe_remove_file,
    safe_remove_tree,
    sync_skills_directory,
    t_target,
    update_gitignore,
)


class AntigravityTarget(BaseTarget):
    target_id = "antigravity"
    display_name = "Google Antigravity"
    description = (
        "Configuration via .agents/ (skills/, rules/, agents/) in workspace"
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
        agents_dir = target_path / ".agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        # 1. Subagents
        subagents_dest = agents_dir / "agents"
        if agents:
            if is_link(subagents_dest):
                remove_dir_link(subagents_dest)
            subagents_dest.mkdir(parents=True, exist_ok=True)
            active_agent_names = set()
            for a in agents:
                agent_name = a["id"] if a["id"].endswith(".md") else f"{a['id']}.md"
                active_agent_names.add(agent_name)
                dest_file = subagents_dest / agent_name
                if is_link(dest_file):
                    safe_remove_tree(dest_file)
                dest_file.write_text(
                    Path(a["path"]).read_text(encoding="utf-8"), encoding="utf-8"
                )
            for item in list(subagents_dest.iterdir()):
                if item.name not in active_agent_names or not item.is_file() or is_link(item):
                    safe_remove_tree(item)
            print(f"  [+] {t_target('antigravity_agents', lang, count=len(agents))}")
        else:
            safe_remove_tree(subagents_dest)

        # 2. Rules
        rules_dest = agents_dir / "rules"
        if rules:
            if is_link(rules_dest):
                remove_dir_link(rules_dest)
            rules_dest.mkdir(parents=True, exist_ok=True)
            active_names = set()
            for r in rules:
                rule_name = r["id"] if r["id"].endswith(".md") else f"{r['id']}.md"
                active_names.add(rule_name)
                dest_file = rules_dest / rule_name
                if is_link(dest_file):
                    safe_remove_tree(dest_file)
                dest_file.write_text(
                    Path(r["path"]).read_text(encoding="utf-8"), encoding="utf-8"
                )
            for f in list(rules_dest.iterdir()):
                if f.name not in active_names or not f.is_file() or is_link(f):
                    safe_remove_tree(f)
            print(f"  [+] {t_target('antigravity_rules', lang, count=len(rules))}")
        else:
            safe_remove_tree(rules_dest)

        # 3. Workspace-local Skills (real copies inside .agents/skills/, no external paths)
        safe_remove_file(agents_dir / "skills.json")
        skills_dest = agents_dir / "skills"
        synced_skills = sync_skills_directory(
            skills_dest, repo_root, scanned, skills_by_cat
        )
        print(f"  [+] {t_target('antigravity_skills', lang, count=len(synced_skills))}")

        update_gitignore(target_path, [".agents/"], lang=lang)
        return True

    def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
        agents_dir = target_path / ".agents"
        if not agents_dir.exists():
            print(f"  [i] {t_target('antigravity_clean_nothing', lang)}")
            return True

        safe_remove_tree(agents_dir / "agents")
        safe_remove_tree(agents_dir / "rules")
        safe_remove_tree(agents_dir / "skills")
        safe_remove_file(agents_dir / "skills.json")

        safe_remove_dir_if_empty(agents_dir)
        print(f"  [-] {t_target('antigravity_clean_done', lang)}")
        return True

    def apply_global_rules(
        self,
        rules_dst: Path,
        rules: list[dict[str, Any]],
        lang: str = "en",
    ) -> bool:
        """Applies explicit rules to ~/.gemini/config/rules/ as individual files, or cleans if empty."""
        if is_link(rules_dst):
            remove_dir_link(rules_dst)

        if not rules:
            if rules_dst.exists() and rules_dst.is_dir():
                for f in list(rules_dst.iterdir()):
                    if f.is_file() and f.suffix == ".md":
                        f.unlink()
                safe_remove_dir_if_empty(rules_dst)
            print(f"  [-] {t_target('antigravity_global_rules_cleaned', lang)}")
            return True

        rules_dst.mkdir(parents=True, exist_ok=True)
        active_names = set()
        for r in rules:
            rule_name = r["id"] if r["id"].endswith(".md") else f"{r['id']}.md"
            active_names.add(rule_name)
            dest_file = rules_dst / rule_name
            dest_file.write_text(
                Path(r["path"]).read_text(encoding="utf-8"), encoding="utf-8"
            )

        if rules_dst.exists() and rules_dst.is_dir():
            for f in list(rules_dst.iterdir()):
                if f.is_file() and f.name not in active_names:
                    f.unlink()

        print(
            f"  [+] {t_target('antigravity_global_rules_updated', lang, count=len(rules))}"
        )
        return True

    def configure_global(
        self,
        repo_root: Path,
        lang: str = "en",
        selected_rules: list[dict[str, Any]] | None = None,
        selected_rule: dict[str, Any] | None = None,
        assume_yes: bool = False,
    ) -> bool:
        home = Path.home()
        global_dir = home / ".gemini" / "config"
        global_dir.mkdir(parents=True, exist_ok=True)

        agents_src = repo_root / "agents"
        agents_dst = global_dir / "agents"

        skills_src = repo_root / "skills" / "global"
        skills_dst = global_dir / "skills"

        rules_dst = global_dir / "rules"

        success = True
        try:
            if agents_src.exists() and create_dir_link(
                agents_src, agents_dst, lang=lang, assume_yes=assume_yes
            ):
                print(f"  [+] {t_target('antigravity_global_agents', lang)}")

            if skills_src.exists() and create_dir_link(
                skills_src, skills_dst, lang=lang, assume_yes=assume_yes
            ):
                print(f"  [+] {t_target('antigravity_global_skills', lang)}")

            # Global rules: NEVER link automatically!
            # Only apply if selected_rules is explicitly provided.
            if selected_rules is not None or selected_rule is not None:
                active_rules = (
                    selected_rules
                    if selected_rules is not None
                    else ([selected_rule] if selected_rule else [])
                )
                self.apply_global_rules(rules_dst, active_rules, lang=lang)
            elif is_link(rules_dst):
                # If there's a legacy automatic whole-directory link, remove it to stop unwanted global enforcement
                remove_dir_link(rules_dst)
                print(f"  [i] {t_target('antigravity_legacy_link_removed', lang)}")
        except (OSError, RuntimeError, subprocess.SubprocessError) as e:
            print(f"  [x] {t_target('antigravity_global_error', lang, error=e)}")
            success = False

        return success

    def clean_global(self, lang: str = "en") -> bool:
        home = Path.home()
        global_dir = home / ".gemini" / "config"
        for t in [global_dir / "agents", global_dir / "skills"]:
            if is_link(t):
                remove_dir_link(t)
                print(
                    f"  [-] {t_target('antigravity_global_removed', lang, name=t.name)}"
                )
        rules_target = global_dir / "rules"
        if is_link(rules_target):
            remove_dir_link(rules_target)
            print(
                f"  [-] {t_target('antigravity_global_removed', lang, name=rules_target.name)}"
            )
        elif rules_target.exists() and rules_target.is_dir():
            for f in list(rules_target.iterdir()):
                if f.is_file():
                    f.unlink()
            safe_remove_dir_if_empty(rules_target)
            print(f"  [-] {t_target('antigravity_global_rules_cleaned', lang)}")
        return True
