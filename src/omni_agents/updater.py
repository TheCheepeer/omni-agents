#!/usr/bin/env python3
"""
Update checking module for omni-agents.
Checks for new versions on PyPI (for global installations) or Git (for local dev mode),
with a short timeout to ensure quick CLI launch, and offers optional interactive upgrade.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

try:
    from omni_agents import __version__
    from omni_agents.i18n import t
except ImportError:
    from . import __version__
    from .i18n import t

USER_AGENT = f"omni-agents/{__version__} (Python urllib)"


def _parse_version_tuple(ver_str: str) -> tuple[int, ...]:
    """Parses version string (e.g. '1.2.3') into integer tuple for reliable comparison."""
    parts = []
    for chunk in ver_str.split("."):
        clean = "".join(c for c in chunk if c.isdigit())
        if clean:
            parts.append(int(clean))
    return tuple(parts) if parts else (0,)


def check_for_updates(
    current_version: str = __version__,
    is_dev: bool = False,
    timeout: float = 1.5,
) -> dict[str, Any] | None:
    """
    Checks if updates are available for omni-agents.
    In dev mode, queries Git remote commit.
    In global mode, queries PyPI public API for omni-agents package.
    Returns dictionary with update details or None if up-to-date or offline.
    """
    if is_dev:
        try:
            # Check local commit
            local_proc = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            local_sha = local_proc.stdout.strip()
            if not local_sha:
                return None

            # Check remote commit in refs/heads/main
            remote_proc = subprocess.run(
                ["git", "ls-remote", "origin", "refs/heads/main"],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            remote_line = remote_proc.stdout.strip()
            if not remote_line:
                return None

            remote_sha = remote_line.split()[0]
            if remote_sha and remote_sha != local_sha:
                return {
                    "type": "git",
                    "current_version": local_sha[:7],
                    "new_version": remote_sha[:7],
                }
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None
        return None

    # Query PyPI API
    pypi_url = "https://pypi.org/pypi/omni-agents-cli/json"
    req = urllib.request.Request(
        pypi_url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            latest_version = data.get("info", {}).get("version")
            if latest_version and _parse_version_tuple(
                latest_version
            ) > _parse_version_tuple(current_version):
                return {
                    "type": "pypi",
                    "current_version": current_version,
                    "new_version": latest_version,
                }
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
        OSError,
    ):
        return None

    return None


def execute_upgrade(update_info: dict[str, Any], lang: str = "en") -> bool:
    """Executes upgrade command corresponding to installation type."""
    up_type = update_info.get("type")

    if up_type == "git":
        print(f"\n-> {t('update_executing', lang, cmd='git pull')}")
        try:
            res = subprocess.run(["git", "pull"], check=False)
            return res.returncode == 0
        except OSError:
            return False

    # PyPI installation
    if shutil.which("uv"):
        print(
            f"\n-> {t('update_executing', lang, cmd='uv tool upgrade omni-agents-cli')}"
        )
        res = subprocess.run(["uv", "tool", "upgrade", "omni-agents-cli"], check=False)
        return res.returncode == 0

    if shutil.which("pipx"):
        print(f"\n-> {t('update_executing', lang, cmd='pipx upgrade omni-agents-cli')}")
        res = subprocess.run(["pipx", "upgrade", "omni-agents-cli"], check=False)
        return res.returncode == 0

    print(
        f"\n-> {t('update_executing', lang, cmd='pip install --upgrade omni-agents-cli')}"
    )
    res = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "omni-agents-cli"],
        check=False,
    )
    return res.returncode == 0


def prompt_and_upgrade(update_info: dict[str, Any], lang: str = "en") -> bool:
    """
    Displays update notification in terminal and requests user confirmation.
    If accepted, runs upgrade command and returns True.
    """
    new_ver = update_info.get("new_version")
    curr_ver = update_info.get("current_version")

    prompt_text = t("update_available_prompt", lang, new=new_ver, current=curr_ver)
    success_msg = t("update_success", lang)
    failure_msg = t("update_failed", lang)

    try:
        choice = input(prompt_text).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False

    # Default to Yes on empty Enter
    if choice in ("", "s", "sim", "y", "yes"):
        success = execute_upgrade(update_info, lang=lang)
        if success:
            print(f"\n{success_msg}\n")
            return True
        else:
            print(f"\n{failure_msg}\n")
            return False

    return False
