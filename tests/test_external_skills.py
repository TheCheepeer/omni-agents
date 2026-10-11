"""
Unit tests for external skills package management, Git resolution,
and update verification lifecycle with user confirmation.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from omni_agents.cli import build_parser, main
from omni_agents.commands.ext_cmd import check_extensions, update_extensions
from omni_agents.remote_sync import (
    check_all_extensions_updates,
    get_remote_git_commit,
    install_external_git_component,
    load_manifest,
    normalize_git_url,
    save_manifest,
    slugify_id,
)


class TestExternalSkillsManagement(unittest.TestCase):
    """Verifies external Git repository parsing, installation, and update checks."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ext_dir = Path(self.temp_dir.name) / "ext"
        self.ext_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_normalize_git_url(self):
        # Shorthand owner/repo
        url, branch, sub = normalize_git_url("blader/humanizer")
        self.assertEqual(url, "https://github.com/blader/humanizer.git")
        self.assertIsNone(branch)
        self.assertIsNone(sub)

        # Full URL without .git
        url, branch, sub = normalize_git_url("https://github.com/blader/humanizer")
        self.assertEqual(url, "https://github.com/blader/humanizer.git")

        # Full URL with .git
        url, branch, sub = normalize_git_url("https://github.com/blader/humanizer.git")
        self.assertEqual(url, "https://github.com/blader/humanizer.git")

        # Deep branch and subpath URL
        url, branch, sub = normalize_git_url(
            "https://github.com/owner/repo/tree/dev/skills/my-skill"
        )
        self.assertEqual(url, "https://github.com/owner/repo.git")
        self.assertEqual(branch, "dev")
        self.assertEqual(sub, "skills/my-skill")

    def test_slugify_id(self):
        self.assertEqual(slugify_id("Humanizer"), "humanizer")
        self.assertEqual(slugify_id("React 19 State"), "react-19-state")
        self.assertEqual(slugify_id("  clean_code--helper  "), "clean_code-helper")

    @patch("subprocess.run")
    def test_get_remote_git_commit(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8\tHEAD\n"
        mock_run.return_value = mock_proc

        sha = get_remote_git_commit("https://github.com/blader/humanizer.git")
        self.assertEqual(sha, "225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8")

    def test_install_external_git_component_local_repo(self):
        # Create a mock source git repository
        src_repo_dir = Path(self.temp_dir.name) / "mock_remote_repo"
        src_repo_dir.mkdir(parents=True, exist_ok=True)

        # Initialize mock git repository
        subprocess.run(["git", "init"], cwd=str(src_repo_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(src_repo_dir), check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(src_repo_dir), check=True)

        skill_md = src_repo_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: Humanizer\ndescription: Removes AI writing patterns\n---\n# Humanizer\nInstructions...",
            encoding="utf-8",
        )
        (src_repo_dir / "scripts").mkdir()
        (src_repo_dir / "scripts" / "helper.py").write_text("print('hello')", encoding="utf-8")

        subprocess.run(["git", "add", "."], cwd=str(src_repo_dir), check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(src_repo_dir), check=True)

        # Install mock repo into ext_dir
        res = install_external_git_component(
            source=str(src_repo_dir),
            ext_dir=self.ext_dir,
            skill_id="humanizer",
            category="community",
        )

        self.assertIsNotNone(res)
        self.assertEqual(res["id"], "humanizer")
        self.assertEqual(res["category"], "community")

        # Verify filesystem
        installed_skill_md = self.ext_dir / "skills" / "community" / "humanizer" / "SKILL.md"
        self.assertTrue(installed_skill_md.exists())
        installed_script = self.ext_dir / "skills" / "community" / "humanizer" / "scripts" / "helper.py"
        self.assertTrue(installed_script.exists())

        # Verify manifest.json
        manifest = load_manifest(self.ext_dir)
        self.assertIn("skills/community/humanizer", manifest["installed"])
        info = manifest["installed"]["skills/community/humanizer"]
        self.assertEqual(info["source_type"], "git")
        self.assertEqual(info["id"], "humanizer")
        self.assertEqual(info["category"], "community")
        self.assertTrue(len(info["sha"]) >= 7)

    @patch("omni_agents.remote_sync.get_remote_git_commit")
    def test_check_all_extensions_updates(self, mock_get_commit):
        manifest = {
            "installed": {
                "skills/community/humanizer": {
                    "type": "skills",
                    "category": "community",
                    "id": "humanizer",
                    "name": "Humanizer",
                    "source_type": "git",
                    "source_url": "https://github.com/blader/humanizer.git",
                    "branch": "main",
                    "sha": "1111111111111111111111111111111111111111",
                }
            }
        }
        save_manifest(self.ext_dir, manifest)

        # Case 1: remote has a new commit
        mock_get_commit.return_value = "2222222222222222222222222222222222222222"
        all_statuses, updates = check_all_extensions_updates(self.ext_dir, {})
        self.assertEqual(len(updates), 1)
        self.assertTrue(updates[0]["has_update"])
        self.assertEqual(updates[0]["new_sha"], "2222222222222222222222222222222222222222")

        # Case 2: remote is identical
        mock_get_commit.return_value = "1111111111111111111111111111111111111111"
        all_statuses, updates = check_all_extensions_updates(self.ext_dir, {})
        self.assertEqual(len(updates), 0)

    @patch("omni_agents.commands.ext_cmd.check_all_extensions_updates")
    @patch("builtins.input", return_value="n")
    @patch("sys.stdin.isatty", return_value=True)
    def test_update_extensions_confirmation_rejection(self, mock_isatty, mock_input, mock_check):
        mock_check.return_value = (
            [{"key": "skills/community/humanizer", "has_update": True}],
            [{
                "key": "skills/community/humanizer",
                "name": "Humanizer",
                "type": "skills",
                "current_sha": "1111111",
                "new_sha": "2222222",
                "source_type": "git",
                "source_url": "https://github.com/blader/humanizer.git",
                "id": "humanizer",
                "category": "community",
            }],
        )

        # User types 'n', update is cancelled
        res = update_extensions({}, self.ext_dir, assume_yes=False)
        self.assertTrue(res)
        mock_input.assert_called_once()

    def test_cli_parser_ext_flags(self):
        parser = build_parser()
        args = parser.parse_args(["--ext-add", "blader/humanizer", "--skills", "humanizer"])
        self.assertEqual(args.ext_add, "blader/humanizer")
        self.assertEqual(args.skills, "humanizer")

        args_check = parser.parse_args(["--ext-check"])
        self.assertTrue(args_check.ext_check)


if __name__ == "__main__":
    unittest.main()

