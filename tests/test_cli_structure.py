"""
Unit tests for the omni_agents modular package architecture using src/ layout.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from omni_agents import __version__
from omni_agents.cli import build_parser
from omni_agents.core.scanner import scan_component_sources
from omni_agents.i18n import get_available_languages, resolve_language_code, t
from omni_agents.targets import get_all_targets, get_available_target_ids, get_target


class TestOmniAgentsPackage(unittest.TestCase):
    """Verifies that the omni_agents package structure and submodules work as expected."""

    def setUp(self):
        self.env = dict(os.environ)
        # Ensure src/ is in PYTHONPATH for subprocesses
        existing_pythonpath = self.env.get("PYTHONPATH", "")
        self.env["PYTHONPATH"] = (
            f"{SRC_DIR};{existing_pythonpath}"
            if sys.platform.startswith("win")
            else f"{SRC_DIR}:{existing_pythonpath}"
        )

    def test_version_present(self):
        self.assertTrue(isinstance(__version__, str))
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+")

    def test_i18n_catalogs_loaded(self):
        langs = get_available_languages()
        codes = [l["code"] for l in langs]
        self.assertIn("en", codes)
        self.assertIn("pt", codes)
        self.assertIn("es", codes)
        self.assertEqual(resolve_language_code("pt_BR"), "pt")
        self.assertEqual(resolve_language_code("en-US"), "en")
        self.assertNotEqual(t("app_title", "en"), "app_title")
        self.assertNotEqual(t("app_title", "pt"), "app_title")

    def test_targets_registry(self):
        targets = get_all_targets()
        self.assertGreaterEqual(len(targets), 5)
        target_ids = get_available_target_ids()
        self.assertIn("antigravity", target_ids)
        self.assertIn("cursor", target_ids)
        self.assertIn("claude", target_ids)
        self.assertIsNotNone(get_target("antigravity"))

    def test_scanner_discovers_components(self):
        sources = scan_component_sources(REPO_ROOT)
        self.assertIn("repo", sources)
        self.assertIn("merged", sources)
        merged = sources["merged"]
        self.assertIn("agents", merged)
        self.assertIn("rules", merged)
        self.assertIn("skills_by_category", merged)
        self.assertGreater(len(merged["agents"]), 0)
        self.assertGreater(len(merged["rules"]), 0)
        self.assertGreater(len(merged["skills_by_category"]), 0)

    def test_cli_parser_builds(self):
        parser = build_parser()
        self.assertIsNotNone(parser)
        args = parser.parse_args(["--info"])
        self.assertTrue(args.info)

    def test_cli_execution_info_flag(self):
        proc = subprocess.run(
            [sys.executable, "-m", "omni_agents", "--info"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=self.env,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("omni-agents Diagnostic Info:", proc.stdout)

    def test_cli_execution_list_tools_flag(self):
        proc = subprocess.run(
            [sys.executable, "-m", "omni_agents", "--list-tools"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=self.env,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Supported Tools:", proc.stdout)
        self.assertIn("antigravity", proc.stdout)

    def test_cli_execution_list_agents_flag(self):
        proc = subprocess.run(
            [sys.executable, "-m", "omni_agents", "--list-agents"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=self.env,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)

    def test_direct_script_execution(self):
        # Run python src/omni_agents/cli.py directly with clean environment (no PYTHONPATH)
        clean_env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        cli_file = SRC_DIR / "omni_agents" / "cli.py"
        proc = subprocess.run(
            [sys.executable, str(cli_file), "--info"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=clean_env,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Diagnostic Info", proc.stdout)

    def test_tui_theme_components(self):
        from omni_agents.tui import theme
        from omni_agents.tui.theme import Console

        # Test string parsing
        k, title, desc = theme.parse_menu_item("[t] Select Target Tools (Antigravity, Cursor, Claude...)")
        self.assertEqual(k, "t")
        self.assertEqual(title, "Select Target Tools")
        self.assertEqual(desc, "Antigravity, Cursor, Claude...")

        # Test rendering without exception
        record_console = Console(file=io.StringIO(), record=True, highlight=False)
        old_console = theme.console
        theme.console = record_console
        try:
            theme.render_header(
                title="TEST TITLE",
                version="1.0.0",
                workspace="/test/path",
                mode="Test Mode",
                active_targets=["antigravity", "cursor"],
            )
            theme.render_menu_card(
                title="Actions",
                items=[("t", "Target Tools", "Toggle assistants")],
            )
            theme.render_selection_card(
                title="Select Targets",
                items=[{"id": "test", "name": "Test Tool", "description": "A tool"}],
                instructions="Test instructions",
                selected_ids={"test"},
            )
            theme.render_banner("Test Banner", level="success")
            output = record_console.export_text()
            self.assertIn("TEST TITLE", output)
            self.assertIn("Target Tools", output)
            self.assertIn("Test Tool", output)
            self.assertIn("Test Banner", output)
        finally:
            theme.console = old_console

    def test_i18n_catalogs_consistency_and_zero_emojis(self):
        import json
        import re

        lang_dir = SRC_DIR / "omni_agents" / "languages"
        # Regex for common emojis
        emoji_pattern = re.compile(
            r"[\U0001F600-\U0001F64F"
            r"\U0001F300-\U0001F5FF"
            r"\U0001F680-\U0001F6FF"
            r"\U0001F700-\U0001F77F"
            r"\U0001F780-\U0001F7FF"
            r"\U0001F800-\U0001F8FF"
            r"\U0001F900-\U0001F9FF"
            r"\U0001FA00-\U0001FA6F"
            r"\U0001FA70-\U0001FAFF"
            r"\U00002702-\U000027B0"
            r"\U000024C2-\U0001F251]"
        )

        critical_keys = [
            "target_workspace",
            "active_tools",
            "mode_label",
            "table_col_index",
            "table_col_rule",
            "table_col_workspace",
            "table_col_global",
            "table_col_description",
            "table_col_status",
            "status_active",
            "status_inactive",
            "status_available",
            "hint_toggle_save_return",
        ]

        for lang_file in lang_dir.glob("*.json"):
            content = lang_file.read_text(encoding="utf-8")
            # Strict Zero-emoji check
            found_emojis = emoji_pattern.findall(content)
            self.assertEqual(
                found_emojis,
                [],
                f"Found emoji in {lang_file.name}: {found_emojis}",
            )

            data = json.loads(content)
            ui_dict = data.get("ui", {})
            for key in critical_keys:
                self.assertIn(key, ui_dict, f"Missing '{key}' in {lang_file.name}")

    def test_portuguese_purity_in_menu(self):
        # Ensure the Portuguese menu translations are not mixed with unadapted English words
        for key in ["menu_select_tools", "menu_rules", "menu_skills", "menu_sync", "menu_clean"]:
            text = t(key, "pt")
            self.assertNotIn("Workspace", text)
            self.assertNotIn("Skills", text)
            self.assertNotIn("Sync", text)

    def test_single_source_of_truth_version(self):
        """Ensures __version__ is defined in one place and consistently referenced everywhere."""
        from omni_agents import __version__ as root_version
        from omni_agents.env_paths import DEFAULT_CONFIG
        from omni_agents.remote_sync import USER_AGENT as sync_ua
        from omni_agents.updater import USER_AGENT as updater_ua
        from omni_agents.updater import __version__ as updater_version

        self.assertEqual(root_version, updater_version)
        self.assertEqual(DEFAULT_CONFIG["version"], root_version)
        self.assertIn(root_version, sync_ua)
        self.assertIn(root_version, updater_ua)


if __name__ == "__main__":
    unittest.main()

