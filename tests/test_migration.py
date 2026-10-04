#!/usr/bin/env python3
"""
Unit tests for migration and legacy global junctions cleanup.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omni_agents import __version__
from omni_agents.core.migration import cleanup_legacy_global_environment


class TestLegacyMigration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.fake_home = self.root / "home"
        self.fake_home.mkdir(parents=True, exist_ok=True)
        self.docs_dir = self.root / "Documents" / "omni-agents"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_gemini_config_junctions(self):
        gemini_config = self.fake_home / ".gemini" / "config"
        gemini_config.mkdir(parents=True, exist_ok=True)

        target_dir = self.root / "some_target"
        target_dir.mkdir(parents=True, exist_ok=True)

        # Create dummy directory or junction
        skills_junc = gemini_config / "skills"
        if sys.platform.startswith("win"):
            import subprocess

            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(skills_junc), str(target_dir)],
                check=False,
                shell=True,
            )
        else:
            skills_junc.symlink_to(target_dir)

        # Create dummy claude file
        claude_dir = self.fake_home / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        claude_file = claude_dir / "CLAUDE.md"
        claude_file.write_text(
            "# Managed by omni-agents\nRule content", encoding="utf-8"
        )

        # Create dummy config with legacy key
        cfg_file = self.docs_dir / "config.json"
        cfg_file.write_text(
            json.dumps({"version": "1.0.2", "global_rules": ["general"]}),
            encoding="utf-8",
        )

        with patch("pathlib.Path.home", return_value=self.fake_home):
            cleanup_legacy_global_environment(
                omni_docs_dir=self.docs_dir,
                repo_root=self.root,
                lang="en",
                verbose=False,
            )

        # Verify claude file was removed
        self.assertFalse(claude_file.exists())

        # Verify config was updated
        updated_cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
        self.assertNotIn("global_rules", updated_cfg)
        self.assertEqual(updated_cfg.get("version"), __version__)
        self.assertTrue(updated_cfg.get("legacy_global_cleaned"))

    def test_idempotent_migration_on_clean_environment(self):
        with patch("pathlib.Path.home", return_value=self.fake_home):
            removed = cleanup_legacy_global_environment(
                omni_docs_dir=self.docs_dir,
                repo_root=self.root,
                lang="en",
                verbose=False,
            )
        self.assertEqual(removed, [])


if __name__ == "__main__":
    unittest.main()
