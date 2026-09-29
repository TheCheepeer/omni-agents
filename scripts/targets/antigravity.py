#!/usr/bin/env python3
"""
Adapter for Google Antigravity.
Configures subagents, rules, and skills.json in .agents/ workspace directory
and links global core to ~/.gemini/config/.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .base import (
    BaseTarget,
    create_dir_link,
    find_skill_file,
    is_link,
    remove_dir_link,
    safe_remove_dir_if_empty,
    safe_remove_file,
    safe_remove_tree,
    t_target,
    update_gitignore,
)


class AntigravityTarget(BaseTarget):
    target_id = "antigravity"
    display_name = "Google Antigravity"
    description = (
        "Configuration via .agents/ (workspace) and ~/.gemini/config/ (global)"
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
        agents_dir = target_path / ".agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        # 1. Subagents
        if agents:
            subagents_dest = agents_dir / "agents"
            subagents_dest.mkdir(parents=True, exist_ok=True)
            for a in agents:
                dest_file = subagents_dest / a["id"]
                dest_file.write_text(
                    Path(a["path"]).read_text(encoding="utf-8"), encoding="utf-8"
                )
            print(f"  [+] {t_target('antigravity_agents', lang, count=len(agents))}")

        # 2. Rules
        if rules:
            rules_dest = agents_dir / "rules"
            rules_dest.mkdir(parents=True, exist_ok=True)
            for r in rules:
                rule_name = r["id"] if r["id"].endswith(".md") else f"{r['id']}.md"
                dest_file = rules_dest / rule_name
                dest_file.write_text(
                    Path(r["path"]).read_text(encoding="utf-8"), encoding="utf-8"
                )
            print(f"  [+] {t_target('antigravity_rules', lang, count=len(rules))}")

        # 3. Skills Manifest
        entries = []
        total_skills = 0
        for cat_name in sorted(skills_by_cat.keys()):
            skill_ids = skills_by_cat[cat_name]
            if skill_ids:
                cat_dirs: dict[str, list[str]] = {}
                for s_id in skill_ids:
                    s_file = find_skill_file(repo_root, scanned, cat_name, s_id)
                    parent_dir = s_file.parent.parent.resolve().as_posix()
                    cat_dirs.setdefault(parent_dir, []).append(s_id)
                for cat_path, ids in sorted(cat_dirs.items()):
                    entries.append({"path": cat_path, "include_only": sorted(ids)})
                total_skills += len(skill_ids)

        skills_json_path = agents_dir / "skills.json"
        manifest = {"entries": entries}
        skills_json_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  [+] {t_target('antigravity_skills', lang, count=total_skills)}")

        update_gitignore(target_path, [".agents/"], lang=lang)
        return True

    def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
        agents_dir = target_path / ".agents"
        if not agents_dir.exists():
            print(f"  [i] {t_target('antigravity_clean_nothing', lang)}")
            return True

        safe_remove_tree(agents_dir / "agents")
        safe_remove_tree(agents_dir / "rules")
        safe_remove_file(agents_dir / "skills.json")

        safe_remove_dir_if_empty(agents_dir)
        print(f"  [-] {t_target('antigravity_clean_done', lang)}")
        return True

    def configure_global(
        self,
        repo_root: Path,
        lang: str = "en",
        selected_rule: dict[str, Any] | None = None,
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
            if agents_src.exists():
                create_dir_link(agents_src, agents_dst, lang=lang)
                print(f"  [+] {t_target('antigravity_global_agents', lang)}")
            if skills_src.exists():
                create_dir_link(skills_src, skills_dst, lang=lang)
                print(f"  [+] {t_target('antigravity_global_skills', lang)}")

            rule_src = None
            if selected_rule:
                if (
                    selected_rule.get("dir_path")
                    and Path(selected_rule["dir_path"]).exists()
                ):
                    rule_src = Path(selected_rule["dir_path"])
                elif selected_rule.get("path") and Path(selected_rule["path"]).exists():
                    rule_src = Path(selected_rule["path"]).parent
            if not rule_src:
                rule_src = repo_root / "rules"

            if rule_src.exists():
                should_link_rules = True
                if rules_dst.exists():
                    try:
                        is_same_target = (
                            is_link(rules_dst)
                            and rules_dst.resolve() == rule_src.resolve()
                        )
                    except OSError:
                        is_same_target = False

                    if not is_same_target:
                        try:
                            ans = (
                                input(
                                    f"\n  [?] {t_target('antigravity_rules_overwrite_prompt', lang)}"
                                )
                                .strip()
                                .lower()
                            )
                            should_link_rules = ans in (
                                "s",
                                "sim",
                                "y",
                                "yes",
                                "si",
                                "sí",
                            )
                        except (EOFError, KeyboardInterrupt):
                            should_link_rules = False

                if should_link_rules:
                    create_dir_link(rule_src, rules_dst, lang=lang)
                    if selected_rule:
                        print(
                            f"  [+] {t_target('antigravity_global_rules_linked', lang, profile=selected_rule['id'])}"
                        )
                    else:
                        print(f"  [+] {t_target('antigravity_global_rules', lang)}")
                else:
                    print(f"  [i] {t_target('antigravity_global_rules_kept', lang)}")
        except (OSError, RuntimeError, subprocess.SubprocessError) as e:
            print(f"  [x] {t_target('antigravity_global_error', lang, error=e)}")
            success = False

        return success

    def clean_global(self, lang: str = "en") -> bool:
        home = Path.home()
        global_dir = home / ".gemini" / "config"
        targets = [global_dir / "agents", global_dir / "skills", global_dir / "rules"]
        for t in targets:
            if is_link(t):
                remove_dir_link(t)
                print(
                    f"  [-] {t_target('antigravity_global_removed', lang, name=t.name)}"
                )
        return True
