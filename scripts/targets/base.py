#!/usr/bin/env python3
"""
Base module with filesystem utilities and abstract base class for targets.
Cross-platform (Windows, Linux, macOS) using only Python standard library.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from i18n import get_target_description, t_target


def is_link(path: Path) -> bool:
    """Checks if the path is a symbolic link or junction on Windows/Unix."""
    if not os.path.lexists(path):
        return False
    if path.is_symlink():
        return True
    if hasattr(path, "is_junction") and path.is_junction():
        return True
    if sys.platform.startswith("win"):
        try:
            st = os.lstat(path)
            # FILE_ATTRIBUTE_REPARSE_POINT = 0x400
            return bool(st.st_file_attributes & 0x400)
        except OSError:
            return False
    return False


def remove_dir_link(path: Path):
    """Safely removes a directory link without deleting real target files."""
    if not os.path.lexists(path):
        return
    if sys.platform.startswith("win"):
        try:
            os.rmdir(path)
        except OSError:
            subprocess.run(["cmd", "/c", "rmdir", str(path)], check=True, shell=True)
    else:
        if path.is_symlink():
            path.unlink()
        else:
            path.rmdir()


def create_dir_link(src: Path, dst: Path, lang: str = "en"):
    """Creates a cross-platform directory link (Junction on Windows, Symlink on Unix)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(dst):
        if is_link(dst):
            remove_dir_link(dst)
        else:
            backup_dst = dst.with_name(f"{dst.name}.backup")
            print(f"  [!] {t_target('dir_not_link', lang, dst=dst)}")
            print(f"      {t_target('moving_backup', lang, name=backup_dst.name)}")
            dst.rename(backup_dst)

    if sys.platform.startswith("win"):
        try:
            import _winapi

            _winapi.CreateJunction(str(src), str(dst))
        except (AttributeError, OSError):
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
                check=True,
                shell=True,
            )
    else:
        dst.symlink_to(src, target_is_directory=True)


def safe_write_text(path: Path, content: str):
    """Writes text content to a file, ensuring parent directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def safe_remove_file(path: Path):
    """Removes file if it exists."""
    if path.exists():
        path.unlink()


def safe_remove_dir_if_empty(path: Path):
    """Removes directory only if empty."""
    if path.exists() and path.is_dir():
        try:
            if not any(path.iterdir()):
                path.rmdir()
        except OSError:
            pass


def safe_remove_tree(path: Path):
    """Recursively removes directory and all its contents."""
    if not os.path.lexists(path):
        return
    if is_link(path):
        remove_dir_link(path)
    elif path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    elif path.is_file():
        path.unlink()


def update_gitignore(target_path: Path, entries: list[str], lang: str = "en"):
    """Appends entries to target project's .gitignore if not already present."""
    if not entries:
        return
    gitignore_path = target_path / ".gitignore"
    existing_lines: set[str] = set()
    raw_content = ""

    if gitignore_path.exists():
        try:
            raw_content = gitignore_path.read_text(encoding="utf-8")
            existing_lines = {line.strip() for line in raw_content.splitlines()}
        except OSError:
            existing_lines = set()

    to_add = [e for e in entries if e.strip() not in existing_lines]
    if not to_add:
        return

    with gitignore_path.open("a", encoding="utf-8") as f:
        if raw_content and not raw_content.endswith("\n"):
            f.write("\n")
        for item in to_add:
            f.write(f"{item}\n")
    print(f"  [+] {t_target('updated_gitignore', lang, entries=', '.join(to_add))}")


def remove_from_gitignore(target_path: Path, entries: list[str], lang: str = "en"):
    """Removes entries from target project's .gitignore."""
    gitignore_path = target_path / ".gitignore"
    if not gitignore_path.exists():
        return

    try:
        content = gitignore_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        entries_set = set(entries)
        new_lines = [line for line in lines if line.strip() not in entries_set]
        if len(new_lines) != len(lines):
            new_content = "\n".join(new_lines)
            if new_content:
                new_content += "\n"
            gitignore_path.write_text(new_content, encoding="utf-8")
            print(
                f"  [-] {t_target('removed_gitignore', lang, entries=', '.join(entries))}"
            )
    except OSError:
        pass


def parse_frontmatter(file_path: Path) -> tuple[str, str]:
    """Extracts basic fields from simple YAML frontmatter without external dependencies."""
    default_name = file_path.stem
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return default_name, ""

    name, description = default_name, ""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_lines = parts[1].splitlines()
            in_multiline_desc = False
            desc_buffer = []

            for line in yaml_lines:
                stripped = line.strip()
                if stripped.startswith("name:"):
                    in_multiline_desc = False
                    name = stripped.split("name:", 1)[1].strip().strip('"').strip("'")
                elif stripped.startswith("description:"):
                    val = (
                        stripped.split("description:", 1)[1]
                        .strip()
                        .strip('"')
                        .strip("'")
                    )
                    if val in (">-", ">", "|", "|-", ""):
                        in_multiline_desc = True
                    else:
                        description = val
                elif in_multiline_desc:
                    if line.startswith(("  ", "\t")):
                        desc_buffer.append(stripped)
                    else:
                        in_multiline_desc = False

            if desc_buffer and not description:
                description = " ".join(desc_buffer)

    return name, description


def load_workspace_state(target_path: Path) -> dict[str, Any]:
    """Loads saved state and preferences from target workspace."""
    state_file = target_path / ".agents" / "workspace_state.json"
    if not state_file.exists():
        # Fallback to legacy skills.json if present
        skills_file = target_path / ".agents" / "skills.json"
        selected_skills: dict[str, set[str]] = {}
        if skills_file.exists():
            try:
                data = json.loads(skills_file.read_text(encoding="utf-8"))
                for entry in data.get("entries", []):
                    cat_name = Path(entry.get("path", "")).name
                    include_only = entry.get("include_only", [])
                    if cat_name and include_only:
                        selected_skills[cat_name] = set(include_only)
            except (json.JSONDecodeError, OSError):
                pass

        return {
            "active_targets": ["antigravity"] if skills_file.exists() else [],
            "selected_agents": [],
            "selected_rules": [],
            "selected_skills": {k: sorted(v) for k, v in selected_skills.items()},
        }

    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        return {
            "language": data.get("language"),
            "active_targets": data.get("active_targets", []),
            "selected_agents": data.get("selected_agents", []),
            "selected_rules": data.get("selected_rules", []),
            "selected_skills": data.get("selected_skills", {}),
        }
    except (json.JSONDecodeError, OSError):
        return {
            "language": None,
            "active_targets": [],
            "selected_agents": [],
            "selected_rules": [],
            "selected_skills": {},
        }


def save_workspace_state(target_path: Path, state: dict[str, Any]):
    """Persists workspace state to support synchronization and targeted uninstallation."""
    state_file = target_path / ".agents" / "workspace_state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    update_gitignore(target_path, [".agents/"])


def find_skill_file(
    repo_root: Path, scanned: dict[str, Any], cat_name: str, skill_id: str
) -> Path:
    """Resolves the SKILL.md file of a skill considering scanned layers (repo, custom, ext)."""
    skills_in_cat = scanned.get("skills_by_category", {}).get(cat_name, [])
    for s in skills_in_cat:
        if s.get("id") == skill_id:
            p = Path(s.get("path"))
            skill_md = p / "SKILL.md" if p.is_dir() else p
            if skill_md.exists():
                return skill_md
    return repo_root / "skills" / cat_name / skill_id / "SKILL.md"


class BaseTarget:
    """Base class defining the contract for a tool adapter."""

    target_id: str = ""
    display_name: str = ""
    description: str = ""
    supports_global: bool = False

    def get_description(self, lang: str = "en") -> str:
        """Returns localized description according to active language."""
        return get_target_description(
            self.target_id, locale=lang, fallback=self.description
        )

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
        """Applies tool-specific configuration to the target workspace."""
        raise NotImplementedError

    def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
        """Removes configuration files created for this tool in the target workspace."""
        raise NotImplementedError

    def configure_global(
        self,
        repo_root: Path,
        lang: str = "en",
        selected_rule: dict[str, Any] | None = None,
    ) -> bool:
        """Applies global machine configuration for this tool."""
        return False

    def clean_global(self, lang: str = "en") -> bool:
        """Removes global machine configuration for this tool."""
        return False
