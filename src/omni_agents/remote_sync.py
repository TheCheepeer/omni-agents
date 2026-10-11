#!/usr/bin/env python3
"""
Remote communication and extension synchronization module for omni-agents.
Fetches remote catalogs from GitHub, downloads selected skills, rules, and agents
into Documents/omni-agents/ext/, supports direct installation of external Git repositories
(such as community skills from skills.sh/GitHub), and checks for component updates
with built-in fault tolerance and automatic graceful offline mode.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from omni_agents import __version__
except ImportError:
    from . import __version__

from omni_agents.targets.base import parse_frontmatter

USER_AGENT = f"omni-agents/{__version__} (Python urllib)"


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


def slugify_id(text: str) -> str:
    """Converts a skill/agent name into a clean lowercase identifier."""
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", text.strip().lower())
    cleaned = re.sub(r"-+", "-", cleaned)
    return cleaned.strip("-") or "custom-skill"


def normalize_git_url(source: str) -> tuple[str, str | None, str | None]:
    """
    Normalizes a Git repository source into (clone_url, branch, subpath).
    Supports:
      - https://github.com/owner/repo
      - https://github.com/owner/repo.git
      - owner/repo
      - github.com/owner/repo
      - https://github.com/owner/repo/tree/branch/subpath
    """
    source = source.strip()

    # Tree link: https://github.com/owner/repo/tree/branch/subpath
    m_tree = re.match(
        r"^(https?://github\.com/[^/]+/[^/]+)/tree/([^/]+)(?:/(.+))?$", source
    )
    if m_tree:
        base_url = m_tree.group(1)
        branch = m_tree.group(2)
        subpath = m_tree.group(3)
        clone_url = f"{base_url}.git" if not base_url.endswith(".git") else base_url
        return clone_url, branch, subpath

    # Shorthand: owner/repo
    if re.match(r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$", source):
        return f"https://github.com/{source}.git", None, None

    # github.com/owner/repo
    if source.startswith("github.com/"):
        return (
            f"https://{source}.git"
            if not source.endswith(".git")
            else f"https://{source}"
        ), None, None

    # Standard URL
    if not source.endswith(".git") and "github.com" in source:
        return f"{source.rstrip('/')}.git", None, None

    return source, None, None


def get_remote_git_commit(
    clone_url: str, branch: str | None = None, timeout: float = 4.0
) -> str | None:
    """
    Fetches the remote commit SHA of a Git repository without downloading the whole repository.
    Uses 'git ls-remote' with fallback to GitHub REST API if applicable.
    """
    ref = f"refs/heads/{branch}" if branch else "HEAD"
    try:
        res = subprocess.run(
            ["git", "ls-remote", clone_url, ref],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            first_line = res.stdout.strip().splitlines()[0]
            sha = first_line.split()[0].strip()
            if len(sha) >= 7:
                return sha
    except (subprocess.SubprocessError, OSError, IndexError):
        pass

    # Fallback: GitHub REST API if it's a GitHub URL
    m = re.search(
        r"github\.com[/:]([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+?)(?:\.git)?$", clone_url
    )
    if m:
        owner, repo = m.group(1), m.group(2)
        target_ref = branch or "HEAD"
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{target_ref}"
        raw = _make_request(api_url, timeout=timeout)
        if raw:
            try:
                data = json.loads(raw.decode("utf-8"))
                sha = data.get("sha")
                if sha and isinstance(sha, str):
                    return sha
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

    return None


def install_external_git_component(
    source: str,
    ext_dir: Path,
    skill_id: str | None = None,
    category: str = "community",
    timeout: float = 30.0,
) -> dict[str, Any] | None:
    """
    Downloads an external skill or agent repository via Git (shallow clone)
    and installs it into ext/skills/<category>/<skill_id>/ (or ext/agents/).
    Records complete origin metadata (URL, branch, commit SHA, timestamp, command)
    in ext/manifest.json for future update checks and reproducibility.
    """
    clone_url, url_branch, url_subpath = normalize_git_url(source)

    with tempfile.TemporaryDirectory(prefix="omni_ext_") as tmp_dir:
        tmp_path = Path(tmp_dir)

        clone_cmd = ["git", "clone", "--depth", "1"]
        if url_branch:
            clone_cmd.extend(["--branch", url_branch])
        clone_cmd.extend([clone_url, str(tmp_path)])

        try:
            res = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if res.returncode != 0:
                if url_branch:
                    res = subprocess.run(
                        ["git", "clone", "--depth", "1", clone_url, str(tmp_path)],
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )
                if res.returncode != 0:
                    return None
        except (subprocess.SubprocessError, OSError):
            return None

        commit_sha = ""
        try:
            sha_res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(tmp_path),
                capture_output=True,
                text=True,
                timeout=5.0,
                check=False,
            )
            if sha_res.returncode == 0:
                commit_sha = sha_res.stdout.strip()
        except (subprocess.SubprocessError, OSError):
            pass

        detected_branch = url_branch
        if not detected_branch:
            try:
                br_res = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=str(tmp_path),
                    capture_output=True,
                    text=True,
                    timeout=5.0,
                    check=False,
                )
                if br_res.returncode == 0 and br_res.stdout.strip():
                    detected_branch = br_res.stdout.strip()
            except (subprocess.SubprocessError, OSError):
                pass
        detected_branch = detected_branch or "main"

        search_root = tmp_path
        if url_subpath:
            cand_sub = tmp_path / url_subpath
            if cand_sub.exists() and cand_sub.is_dir():
                search_root = cand_sub

        root_skill_md = search_root / "SKILL.md"
        final_id = skill_id

        # Case 1: SKILL.md found directly at search root
        if root_skill_md.exists():
            name, desc = parse_frontmatter(root_skill_md)
            if not final_id:
                final_id = (
                    slugify_id(name) if name else slugify_id(Path(clone_url).stem)
                )
            dest_dir = ext_dir / "skills" / category / final_id
            if dest_dir.exists():
                shutil.rmtree(dest_dir, ignore_errors=True)
            dest_dir.mkdir(parents=True, exist_ok=True)

            for item in search_root.iterdir():
                if item.name == ".git":
                    continue
                dst_item = dest_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dst_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dst_item)

            manifest = load_manifest(ext_dir)
            installed = manifest.setdefault("installed", {})
            manifest_key = f"skills/{category}/{final_id}"
            installed[manifest_key] = {
                "type": "skills",
                "category": category,
                "id": final_id,
                "name": name or final_id,
                "description": desc,
                "sha": commit_sha,
                "source_type": "git",
                "source_url": clone_url,
                "branch": detected_branch,
                "installed_at": datetime.now(timezone.utc).isoformat(),
                "command": f"omni add {source}"
                + (f" --skill {final_id}" if skill_id else ""),
            }
            save_manifest(ext_dir, manifest)
            return {
                "key": manifest_key,
                "type": "skills",
                "category": category,
                "id": final_id,
                "name": name or final_id,
                "sha": commit_sha,
                "path": dest_dir,
            }

        # Case 2: Multi-skill repository (search subdirectories)
        skill_dirs = []
        for path in search_root.glob("**/SKILL.md"):
            if ".git" in path.parts:
                continue
            skill_dirs.append(path.parent)

        if skill_dirs:
            target_skill_dir = None
            if final_id:
                for sd in skill_dirs:
                    if sd.name.lower() == final_id.lower():
                        target_skill_dir = sd
                        break
            if not target_skill_dir and len(skill_dirs) == 1:
                target_skill_dir = skill_dirs[0]

            if target_skill_dir:
                name, desc = parse_frontmatter(target_skill_dir / "SKILL.md")
                final_id = final_id or slugify_id(target_skill_dir.name)
                dest_dir = ext_dir / "skills" / category / final_id
                if dest_dir.exists():
                    shutil.rmtree(dest_dir, ignore_errors=True)
                dest_dir.mkdir(parents=True, exist_ok=True)

                for item in target_skill_dir.iterdir():
                    if item.name == ".git":
                        continue
                    dst_item = dest_dir / item.name
                    if item.is_dir():
                        shutil.copytree(item, dst_item, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dst_item)

                manifest = load_manifest(ext_dir)
                installed = manifest.setdefault("installed", {})
                manifest_key = f"skills/{category}/{final_id}"
                installed[manifest_key] = {
                    "type": "skills",
                    "category": category,
                    "id": final_id,
                    "name": name or final_id,
                    "description": desc,
                    "sha": commit_sha,
                    "source_type": "git",
                    "source_url": clone_url,
                    "branch": detected_branch,
                    "installed_at": datetime.now(timezone.utc).isoformat(),
                    "command": f"omni add {source}"
                    + (f" --skill {final_id}" if skill_id else ""),
                }
                save_manifest(ext_dir, manifest)
                return {
                    "key": manifest_key,
                    "type": "skills",
                    "category": category,
                    "id": final_id,
                    "name": name or final_id,
                    "sha": commit_sha,
                    "path": dest_dir,
                }

        # Case 3: Check for agents/*.md
        agents_dir = search_root / "agents"
        if agents_dir.exists() and agents_dir.is_dir():
            agent_files = list(agents_dir.glob("*.md"))
            if agent_files:
                target_agent = None
                if final_id:
                    cand_name = (
                        final_id if final_id.endswith(".md") else f"{final_id}.md"
                    )
                    target_agent = next(
                        (
                            f
                            for f in agent_files
                            if f.name.lower() == cand_name.lower()
                        ),
                        None,
                    )
                if not target_agent and len(agent_files) == 1:
                    target_agent = agent_files[0]

                if target_agent:
                    dest_agents_dir = ext_dir / "agents"
                    dest_agents_dir.mkdir(parents=True, exist_ok=True)
                    dest_file = dest_agents_dir / target_agent.name
                    shutil.copy2(target_agent, dest_file)
                    name, desc = parse_frontmatter(target_agent)

                    manifest = load_manifest(ext_dir)
                    installed = manifest.setdefault("installed", {})
                    manifest_key = f"agents/{target_agent.name}"
                    installed[manifest_key] = {
                        "type": "agents",
                        "id": target_agent.name,
                        "name": name or target_agent.name,
                        "description": desc,
                        "sha": commit_sha,
                        "source_type": "git",
                        "source_url": clone_url,
                        "branch": detected_branch,
                        "installed_at": datetime.now(timezone.utc).isoformat(),
                        "command": f"omni add {source}",
                    }
                    save_manifest(ext_dir, manifest)
                    return {
                        "key": manifest_key,
                        "type": "agents",
                        "id": target_agent.name,
                        "name": name or target_agent.name,
                        "sha": commit_sha,
                        "path": dest_file,
                    }

        return None


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
                tree_data.get("raw_entries", {}).get(file_path, "")
                if tree_data
                else ""
            )
            installed[file_path] = {
                "type": "agents",
                "id": item_id,
                "sha": sha,
                "source_type": "catalog",
            }
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
                tree_data.get("raw_entries", {}).get(file_path, "")
                if tree_data
                else ""
            )
            installed[file_path] = {
                "type": "rules",
                "id": item_id,
                "sha": sha,
                "source_type": "catalog",
            }
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
                "source_type": "catalog",
            }
            save_manifest(ext_dir, manifest)
            return True
        return False

    return False


def check_all_extensions_updates(
    ext_dir: Path,
    config: dict[str, Any],
    timeout: float = 4.0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Checks for updates across all installed extensions in ext/ (both official catalog and external git).
    Returns a tuple of:
      (all_statuses, updates_available)
    where all_statuses contains information for all installed extensions,
    and updates_available contains only those with an update available.
    """
    manifest = load_manifest(ext_dir)
    installed = manifest.get("installed", {})
    if not installed:
        return [], []

    has_catalog_items = any(
        info.get("source_type") != "git" for info in installed.values()
    )
    tree = fetch_remote_tree(config, timeout=timeout) if has_catalog_items else None
    raw_entries = tree.get("raw_entries", {}) if tree else {}

    all_statuses: list[dict[str, Any]] = []
    updates_available: list[dict[str, Any]] = []

    for key, info in installed.items():
        comp_type = info.get("type", "skills")
        current_sha = info.get("sha", "")
        item_id = info.get("id", key.split("/")[-1])
        category = info.get("category")
        source_type = info.get("source_type", "catalog")
        source_url = info.get("source_url") or config.get("repository", {}).get(
            "url", "https://github.com/TheCheepeer/omni-agents"
        )
        item_name = info.get("name") or item_id
        new_sha = None

        if source_type == "git":
            branch = info.get("branch")
            new_sha = get_remote_git_commit(source_url, branch=branch, timeout=timeout)
        else:
            remote_path = key
            if comp_type == "skills" and not remote_path.endswith("SKILL.md"):
                remote_path = f"{key}/SKILL.md"
            new_sha = raw_entries.get(remote_path)

        has_update = bool(
            new_sha and current_sha and new_sha[:12] != current_sha[:12]
        )

        status_entry = {
            "key": key,
            "type": comp_type,
            "id": item_id,
            "category": category,
            "name": item_name,
            "source_type": source_type,
            "source_url": source_url,
            "current_sha": current_sha,
            "new_sha": new_sha or current_sha,
            "has_update": has_update,
        }
        all_statuses.append(status_entry)
        if has_update:
            updates_available.append(status_entry)

    return all_statuses, updates_available


def check_ext_updates(
    ext_dir: Path, config: dict[str, Any], timeout: float = 2.0
) -> list[dict[str, Any]]:
    """Legacy compatibility wrapper returning list of available updates."""
    _, updates = check_all_extensions_updates(ext_dir, config, timeout=timeout)
    return updates
