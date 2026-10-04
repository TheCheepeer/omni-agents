#!/usr/bin/env python3
"""
Scanner module for omni-agents.
Discovers skills, agents, and rules across repository, personal (custom), and extension (ext) layers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.env_paths import is_dev_mode
from omni_agents.targets.base import parse_frontmatter


def _scan_source_directory(source_dir: Path) -> dict[str, Any]:
    """Scans a directory containing skills/, agents/, and/or rules/ folders."""
    skills_map: dict[str, dict[str, dict[str, Any]]] = {}
    agents_map: dict[str, dict[str, Any]] = {}
    rules_map: dict[str, dict[str, Any]] = {}

    # 1. Skills
    skills_dir = source_dir / "skills"
    if skills_dir.exists() and skills_dir.is_dir():
        for category_dir in sorted(skills_dir.iterdir()):
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                cat_name = category_dir.name
                for item in sorted(category_dir.iterdir()):
                    skill_md = item / "SKILL.md"
                    if item.is_dir() and skill_md.exists():
                        name, desc = parse_frontmatter(skill_md)
                        skills_map.setdefault(cat_name, {})[item.name] = {
                            "id": item.name,
                            "name": name,
                            "description": desc,
                            "path": item.resolve(),
                        }

    # 2. Subagents
    agents_dir = source_dir / "agents"
    if agents_dir.exists() and agents_dir.is_dir():
        for item in sorted(agents_dir.glob("*.md")):
            name, desc = parse_frontmatter(item)
            agents_map[item.name] = {
                "id": item.name,
                "name": name,
                "description": desc,
                "path": item.resolve(),
            }

    # 3. Rules (Supports rules/<profile>/AGENTS.md and legacy rules/*.md)
    rules_dir = source_dir / "rules"
    if rules_dir.exists() and rules_dir.is_dir():
        for item in sorted(rules_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                rule_file = None
                for candidate in (
                    "AGENTS.md",
                    "agents.md",
                    "Agents.md",
                    "RULE.md",
                    "rule.md",
                    f"{item.name}.md",
                ):
                    candidate_path = item / candidate
                    if candidate_path.exists() and candidate_path.is_file():
                        rule_file = candidate_path
                        break
                if rule_file:
                    name, desc = parse_frontmatter(rule_file)
                    if not desc:
                        try:
                            for line in rule_file.read_text(
                                encoding="utf-8"
                            ).splitlines():
                                sline = line.strip()
                                if sline and not sline.startswith(("#", "---")):
                                    desc = sline
                                    break
                        except (OSError, UnicodeDecodeError):
                            desc = ""
                    rules_map[item.name] = {
                        "id": item.name,
                        "name": name or item.name,
                        "description": desc,
                        "path": rule_file.resolve(),
                        "dir_path": item.resolve(),
                    }
            elif (
                item.is_file()
                and item.suffix == ".md"
                and not item.name.startswith(".")
            ):
                name, desc = parse_frontmatter(item)
                if not desc:
                    try:
                        for line in item.read_text(encoding="utf-8").splitlines():
                            sline = line.strip()
                            if sline and not sline.startswith(("#", "---")):
                                desc = sline
                                break
                    except (OSError, UnicodeDecodeError):
                        desc = ""
                rules_map[item.stem] = {
                    "id": item.stem,
                    "name": name or item.stem,
                    "description": desc,
                    "path": item.resolve(),
                    "dir_path": item.parent.resolve(),
                }

    return {"skills": skills_map, "agents": agents_map, "rules": rules_map}


def _format_layer_data(layer_raw: dict[str, Any]) -> dict[str, Any]:
    skills_by_cat: dict[str, list[dict[str, Any]]] = {}
    for cat_name, cat_skills in sorted(layer_raw["skills"].items()):
        if cat_skills:
            skills_by_cat[cat_name] = sorted(
                cat_skills.values(), key=lambda x: str(x["id"])
            )
    return {
        "skills_by_category": skills_by_cat,
        "agents": sorted(layer_raw["agents"].values(), key=lambda x: str(x["id"])),
        "rules": sorted(layer_raw["rules"].values(), key=lambda x: str(x["id"])),
    }


def scan_component_sources(
    repo_root: Path, documents_dir: Path | None = None
) -> dict[str, Any]:
    """
    Dynamically scans and isolates components across layers:
    - 'repo': Base repository (ONLY when running in dev mode from a cloned Git repo)
    - 'ext': Remote extensions (Documents/omni-agents/ext)
    - 'custom': User personal overrides (Documents/omni-agents/custom)
    - 'merged': Consolidated components across active layers
    """
    empty_raw: dict[str, Any] = {"skills": {}, "agents": {}, "rules": {}}

    is_dev = is_dev_mode(repo_root)
    repo_raw = (
        _scan_source_directory(repo_root)
        if is_dev and repo_root.exists() and repo_root.is_dir()
        else empty_raw
    )

    ext_dir = (documents_dir / "ext") if documents_dir else None
    ext_raw = (
        _scan_source_directory(ext_dir)
        if ext_dir and ext_dir.exists() and ext_dir.is_dir()
        else empty_raw
    )

    custom_dir = (documents_dir / "custom") if documents_dir else None
    custom_raw = (
        _scan_source_directory(custom_dir)
        if custom_dir and custom_dir.exists() and custom_dir.is_dir()
        else empty_raw
    )

    builtin_dir = Path(__file__).resolve().parent.parent / "builtin"
    builtin_raw = (
        _scan_source_directory(builtin_dir)
        if builtin_dir.exists() and builtin_dir.is_dir()
        else empty_raw
    )

    merged_skills: dict[str, dict[str, dict[str, Any]]] = {}
    merged_agents: dict[str, dict[str, Any]] = {}
    merged_rules: dict[str, dict[str, Any]] = {}

    def _merge_layer(layer_data: dict[str, Any]):
        for cat, skills in layer_data["skills"].items():
            merged_skills.setdefault(cat, {}).update(skills)
        merged_agents.update(layer_data["agents"])
        merged_rules.update(layer_data["rules"])

    _merge_layer(builtin_raw)
    if is_dev:
        _merge_layer(repo_raw)
    _merge_layer(ext_raw)
    _merge_layer(custom_raw)

    merged_raw = {
        "skills": merged_skills,
        "agents": merged_agents,
        "rules": merged_rules,
    }

    return {
        "repo": _format_layer_data(repo_raw),
        "ext": _format_layer_data(ext_raw),
        "custom": _format_layer_data(custom_raw),
        "merged": _format_layer_data(merged_raw),
    }


def scan_repository(
    repo_root: Path, documents_dir: Path | None = None
) -> dict[str, Any]:
    """Compatibility wrapper returning merged components across active layers."""
    sources = scan_component_sources(repo_root, documents_dir=documents_dir)
    return sources["merged"]
