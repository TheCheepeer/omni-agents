#!/usr/bin/env python3
"""
Remote communication and extension synchronization module for omni-agents.
Fetches remote catalogs from GitHub, downloads selected skills, rules, and agents
into Documents/omni-agents/ext/, and checks for component updates with built-in
fault tolerance and automatic graceful offline mode.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

USER_AGENT = "omni-agents/1.0.0 (Python urllib)"


def _make_request(url: str, timeout: float = 2.0) -> bytes | None:
    """Executes safe HTTP GET request with strict timeout and custom User-Agent."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def fetch_remote_tree(
    config: dict[str, Any], timeout: float = 2.0
) -> dict[str, Any] | None:
    """
    Fetches the repository file tree from GitHub API.
    Returns categorized dictionary with available agents, rules, and skills,
    or None if the connection fails (offline mode).
    """
    repo_cfg = config.get("repository", {})
    api_base = repo_cfg.get(
        "api_base_url", "https://api.github.com/repos/TheCheepeer/omni-agents"
    )
    branch = repo_cfg.get("branch", "main")

    tree_url = f"{api_base}/git/trees/{branch}?recursive=1"
    raw_data = _make_request(tree_url, timeout=timeout)
    if not raw_data:
        return None

    try:
        data = json.loads(raw_data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

    tree = data.get("tree", [])
    result: dict[str, Any] = {
        "agents": [],
        "rules": [],
        "skills_by_category": {},
        "raw_entries": {},
    }

    for item in tree:
        path_str = item.get("path", "")
        sha = item.get("sha", "")
        item_type = item.get("type", "")

        if item_type != "blob":
            continue

        result["raw_entries"][path_str] = sha

        # Subagents
        if path_str.startswith("agents/") and path_str.endswith(".md"):
            filename = Path(path_str).name
            result["agents"].append({"id": filename, "path": path_str, "sha": sha})

        # Rules (Supports rules/<profile>/AGENTS.md and legacy rules/*.md)
        elif path_str.startswith("rules/") and path_str.endswith(".md"):
            parts = path_str.split("/")
            if len(parts) >= 3 and parts[-1].upper() == "AGENTS.MD":
                profile_id = parts[1]
                result["rules"].append({"id": profile_id, "path": path_str, "sha": sha})
            else:
                filename = Path(path_str).name
                result["rules"].append({"id": filename, "path": path_str, "sha": sha})

        # Modular Skills (skills/<category>/<skill_id>/SKILL.md)
        elif path_str.startswith("skills/") and path_str.endswith("SKILL.md"):
            parts = path_str.split("/")
            if len(parts) >= 4:
                cat = parts[1]
                skill_id = parts[2]
                if cat not in result["skills_by_category"]:
                    result["skills_by_category"][cat] = []
                result["skills_by_category"][cat].append(
                    {
                        "id": skill_id,
                        "category": cat,
                        "path": path_str,
                        "sha": sha,
                    }
                )

    return result


def download_remote_file(raw_url: str, dest_path: Path, timeout: float = 3.0) -> bool:
    """Downloads a remote file from raw URL to destination path."""
    content = _make_request(raw_url, timeout=timeout)
    if content is None:
        return False

    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(content)
        return True
    except OSError:
        return False


def load_manifest(ext_dir: Path) -> dict[str, Any]:
    """Loads extension manifest for installed components."""
    manifest_file = ext_dir / "manifest.json"
    if manifest_file.exists():
        try:
            return json.loads(manifest_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"installed": {}, "last_check": None}


def save_manifest(ext_dir: Path, manifest: dict[str, Any]) -> bool:
    """Saves extension manifest for installed components."""
    manifest_file = ext_dir / "manifest.json"
    try:
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        manifest_file.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return True
    except OSError:
        return False


def install_remote_component(
    comp_type: str,  # 'agents', 'rules', or 'skills'
    item_id: str,
    config: dict[str, Any],
    ext_dir: Path,
    category: str | None = None,
    tree_data: dict[str, Any] | None = None,
    timeout: float = 3.0,
) -> bool:
    """
    Downloads a remote component to the ext/ directory.
    Records installation details and SHA hash in the local manifest.
    """
    repo_cfg = config.get("repository", {})
    raw_base = repo_cfg.get(
        "raw_base_url",
        "https://raw.githubusercontent.com/TheCheepeer/omni-agents/main",
    )

    manifest = load_manifest(ext_dir)
    installed = manifest.setdefault("installed", {})

    if comp_type == "agents":
        file_path = f"agents/{item_id}"
        url = f"{raw_base}/{file_path}"
        dest = ext_dir / "agents" / item_id
        if download_remote_file(url, dest, timeout=timeout):
            sha = (
                tree_data.get("raw_entries", {}).get(file_path, "") if tree_data else ""
            )
            installed[file_path] = {"type": "agents", "id": item_id, "sha": sha}
            save_manifest(ext_dir, manifest)
            return True
        return False

    elif comp_type == "rules":
        if item_id.endswith(".md"):
            file_path = f"rules/{item_id}"
            dest = ext_dir / "rules" / item_id
        else:
            file_path = f"rules/{item_id}/AGENTS.md"
            dest = ext_dir / "rules" / item_id / "AGENTS.md"

        url = f"{raw_base}/{file_path}"
        if download_remote_file(url, dest, timeout=timeout):
            sha = (
                tree_data.get("raw_entries", {}).get(file_path, "") if tree_data else ""
            )
            installed[file_path] = {"type": "rules", "id": item_id, "sha": sha}
            save_manifest(ext_dir, manifest)
            return True
        return False

    elif comp_type == "skills" and category:
        skill_prefix = f"skills/{category}/{item_id}/"
        skill_md_path = f"{skill_prefix}SKILL.md"
        url = f"{raw_base}/{skill_md_path}"
        dest = ext_dir / "skills" / category / item_id / "SKILL.md"
        if download_remote_file(url, dest, timeout=timeout):
            sha = (
                tree_data.get("raw_entries", {}).get(skill_md_path, "")
                if tree_data
                else ""
            )
            key = f"skills/{category}/{item_id}"
            installed[key] = {
                "type": "skills",
                "category": category,
                "id": item_id,
                "sha": sha,
            }
            save_manifest(ext_dir, manifest)
            return True
        return False

    return False


def check_ext_updates(
    ext_dir: Path, config: dict[str, Any], timeout: float = 1.5
) -> list[dict[str, Any]]:
    """
    Checks if updates are available for components in ext/.
    Compares local manifest SHA hashes against the remote GitHub tree.
    Returns list of items with updates available.
    """
    manifest = load_manifest(ext_dir)
    installed = manifest.get("installed", {})
    if not installed:
        return []

    tree = fetch_remote_tree(config, timeout=timeout)
    if not tree:
        return []

    raw_entries = tree.get("raw_entries", {})
    updates: list[dict[str, Any]] = []

    for key, info in installed.items():
        comp_type = info.get("type")
        current_sha = info.get("sha", "")

        remote_path = key
        if comp_type == "skills":
            remote_path = f"{key}/SKILL.md"

        remote_sha = raw_entries.get(remote_path)
        if remote_sha and current_sha and remote_sha != current_sha:
            updates.append(
                {
                    "key": key,
                    "type": comp_type,
                    "id": info.get("id"),
                    "category": info.get("category"),
                    "current_sha": current_sha,
                    "new_sha": remote_sha,
                }
            )

    return updates
