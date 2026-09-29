"""
Unit tests for tool configuration lifecycle:
- No default tool pre-selection (no default Antigravity)
- Header displays 'Nenhuma selecionada' / 'None selected'
- First-run tool prompt and persistence of user choice
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from omni_agents.core.config import load_app_config, save_app_config
from omni_agents.env_paths import DEFAULT_CONFIG, is_default_or_system_path
from omni_agents.i18n import t
from omni_agents.targets.base import load_workspace_state, save_workspace_state
from omni_agents.tui import theme
from omni_agents.tui.targets_menu import handle_target_selection


class TestToolConfigurationLifecycle(unittest.TestCase):
    """Verifies that no default tool is forced and user choices are asked and persisted."""

    def test_default_config_has_no_default_tool(self):
        """DEFAULT_CONFIG must not have antigravity or any tool hardcoded as active."""
        self.assertEqual(DEFAULT_CONFIG.get("active_targets"), [])
        self.assertFalse(DEFAULT_CONFIG.get("tools_configured", True))

    def test_i18n_none_default_does_not_mention_antigravity(self):
        """UI strings for none_default must not mention Antigravity as default."""
        for lang, expected in [
            ("en", "None selected"),
            ("pt", "Nenhuma selecionada"),
            ("es", "Ninguna seleccionada"),
        ]:
            val = t("none_default", lang)
            self.assertEqual(val, expected)
            self.assertNotIn("antigravity", val.lower())
            self.assertNotIn("default", val.lower())
            self.assertNotIn("padrão", val.lower())

    def test_render_header_empty_targets(self):
        """render_header should display 'Nenhuma selecionada' when active_targets is empty."""
        record_console = theme.Console(file=io.StringIO(), record=True, highlight=False)
        old_console = theme.console
        theme.console = record_console
        try:
            theme.render_header(
                title="TEST",
                version="1.0.0",
                workspace="/dummy",
                mode="Dev",
                active_targets=[],
                lang="pt",
            )
            output = record_console.export_text()
            self.assertIn("Nenhuma selecionada", output)
            self.assertNotIn("padrão: Antigravity", output)
        finally:
            theme.console = old_console

    def test_load_workspace_state_defaults_to_empty_active_targets(self):
        """Loading workspace state from a directory without state must return active_targets == []."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = load_workspace_state(Path(tmpdir))
            self.assertEqual(state.get("active_targets"), [])

    def test_legacy_default_antigravity_cleaned_in_load_app_config(self):
        """Legacy config.json with active_targets: ['antigravity'] but no tools_configured is cleared."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            cfg_file = docs_dir / "config.json"
            cfg_file.write_text(
                json.dumps({
                    "version": "1.0.0",
                    "language": "pt",
                    "active_targets": ["antigravity"],
                }),
                encoding="utf-8",
            )

            loaded = load_app_config(repo_root=Path(tmpdir), omni_docs_dir=docs_dir)
            self.assertEqual(loaded.get("active_targets"), [])

    def test_user_explicit_antigravity_preserved_when_tools_configured(self):
        """If user explicitly configured tools and selected antigravity, it must be preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            cfg_file = docs_dir / "config.json"
            cfg_file.write_text(
                json.dumps({
                    "version": "1.0.0",
                    "tools_configured": True,
                    "active_targets": ["antigravity"],
                }),
                encoding="utf-8",
            )

            loaded = load_app_config(repo_root=Path(tmpdir), omni_docs_dir=docs_dir)
            self.assertEqual(loaded.get("active_targets"), ["antigravity"])

    def test_handle_target_selection_first_run_saves_choices(self):
        """handle_target_selection saves user's choice to app_config and workspace_state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "project"
            work_dir.mkdir()
            docs_dir = Path(tmpdir) / "omni_docs"
            docs_dir.mkdir()

            app_cfg = {"tools_configured": False, "active_targets": []}
            ws_state = {"active_targets": []}
            scanned = {"agents": [], "rules": [], "skills_by_category": {}}

            # Simulate user typing "2" (Claude), then "s" (save)
            inputs = ["2", "s"]
            with patch("omni_agents.tui.targets_menu.get_styled_choice", side_effect=inputs), patch(
                "omni_agents.tui.targets_menu.press_enter_to_continue"
            ):
                chosen = handle_target_selection(
                    target_path=work_dir,
                    repo_root=Path(tmpdir),
                    scanned=scanned,
                    current_state=ws_state,
                    lang="pt",
                    app_config=app_cfg,
                    omni_docs_dir=docs_dir,
                    is_first_run=True,
                )

            self.assertIn("claude", chosen)
            self.assertNotIn("antigravity", chosen)
            self.assertTrue(app_cfg.get("tools_configured"))
            self.assertEqual(app_cfg.get("active_targets"), ["claude"])

            # Verify saved on disk in workspace_state.json
            saved_ws = load_workspace_state(work_dir)
            self.assertEqual(saved_ws.get("active_targets"), ["claude"])

    def test_is_default_or_system_path_permits_temp_workspaces(self):
        """Temporary directories and projects within them must not be rejected as system directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "subproject"
            self.assertFalse(is_default_or_system_path(work_dir))
            self.assertFalse(is_default_or_system_path(Path(tmpdir)))

        # Home directory itself must be detected as default/system
        self.assertTrue(is_default_or_system_path(Path.home()))


if __name__ == "__main__":
    unittest.main()
