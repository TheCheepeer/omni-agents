#!/usr/bin/env python3
"""
Adaptador para Google Antigravity.
Configura subagentes, regras e manifesto skills.json na pasta .agents/ do workspace
e vincula o core global em ~/.gemini/config/.
"""

from __future__ import annotations

import json
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
    update_gitignore,
)


class AntigravityTarget(BaseTarget):
    target_id = "antigravity"
    display_name = "Google Antigravity"
    description = "Configuracao via .agents/ (workspace) e ~/.gemini/config/ (global)"
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
        agents_dir = target_path / ".agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        # 1. Subagentes
        if agents:
            subagents_dest = agents_dir / "agents"
            subagents_dest.mkdir(parents=True, exist_ok=True)
            for a in agents:
                dest_file = subagents_dest / a["id"]
                dest_file.write_text(
                    Path(a["path"]).read_text(encoding="utf-8"), encoding="utf-8"
                )
            print(
                f"  [+] Antigravity: {len(agents)} subagente(s) copiado(s) em .agents/agents/"
            )

        # 2. Regras
        if rules:
            rules_dest = agents_dir / "rules"
            rules_dest.mkdir(parents=True, exist_ok=True)
            for r in rules:
                dest_file = rules_dest / r["id"]
                dest_file.write_text(
                    Path(r["path"]).read_text(encoding="utf-8"), encoding="utf-8"
                )
            print(
                f"  [+] Antigravity: {len(rules)} regra(s) copiada(s) em .agents/rules/"
            )

        # 3. Manifesto de Skills
        entries = []
        total_skills = 0
        for cat_name in sorted(skills_by_cat.keys()):
            skill_ids = skills_by_cat[cat_name]
            if skill_ids:
                cat_path = (repo_root / "skills" / cat_name).resolve().as_posix()
                entries.append({"path": cat_path, "include_only": sorted(skill_ids)})
                total_skills += len(skill_ids)

        skills_json_path = agents_dir / "skills.json"
        manifest = {"entries": entries}
        skills_json_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            f"  [+] Antigravity: manifesto skills.json gerado ({total_skills} skills)"
        )

        update_gitignore(target_path, [".agents/"])
        return True

    def clean_workspace(self, target_path: Path) -> bool:
        agents_dir = target_path / ".agents"
        if not agents_dir.exists():
            print("  [i] Antigravity: nada para limpar no workspace.")
            return True

        safe_remove_tree(agents_dir / "agents")
        safe_remove_tree(agents_dir / "rules")
        safe_remove_file(agents_dir / "skills.json")

        safe_remove_dir_if_empty(agents_dir)
        print("  [-] Antigravity: configuracoes removidas de .agents/")
        return True

    def configure_global(self, repo_root: Path) -> bool:
        home = Path.home()
        global_dir = home / ".gemini" / "config"
        global_dir.mkdir(parents=True, exist_ok=True)

        agents_src = repo_root / "agents"
        agents_dst = global_dir / "agents"

        skills_src = repo_root / "skills" / "global"
        skills_dst = global_dir / "skills"

        rules_src = repo_root / "rules"
        rules_dst = global_dir / "rules"

        success = True
        try:
            if agents_src.exists():
                create_dir_link(agents_src, agents_dst)
                print(
                    "  [+] Antigravity Global: subagentes vinculados em ~/.gemini/config/agents"
                )
            if skills_src.exists():
                create_dir_link(skills_src, skills_dst)
                print(
                    "  [+] Antigravity Global: skills globais vinculadas em ~/.gemini/config/skills"
                )
            if rules_src.exists():
                create_dir_link(rules_src, rules_dst)
                print(
                    "  [+] Antigravity Global: regras vinculadas em ~/.gemini/config/rules"
                )
        except (OSError, RuntimeError, subprocess.SubprocessError) as e:
            print(f"  [x] Antigravity Global: falha ao vincular: {e}")
            success = False

        return success

    def clean_global(self) -> bool:
        home = Path.home()
        global_dir = home / ".gemini" / "config"
        targets = [global_dir / "agents", global_dir / "skills", global_dir / "rules"]
        for t in targets:
            if is_link(t):
                remove_dir_link(t)
                print(f"  [-] Antigravity Global: link desfeito em {t.name}")
        return True
