"""
Unit tests for tool configuration lifecycle:
- No default tool pre-selection (no default Antigravity)
- Header displays 'Nenhuma selecionada' / 'None selected'
- First-run tool prompt and persistence of user choice
"""

from __future__ import annotations

import io
import json
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

from omni_agents.core.config import load_app_config
from omni_agents.env_paths import DEFAULT_CONFIG, is_default_or_system_path
from omni_agents.i18n import t
from omni_agents.targets.base import load_workspace_state
from omni_agents.tui import theme
from omni_agents.tui.targets_menu import handle_target_selection


class TestToolConfigurationLifecycle(unittest.TestCase):
    """Verifies that no default tool is forced and user choices are asked and persisted."""

    def test_default_config_has_no_default_tool(self):
        """DEFAULT_CONFIG must not have antigravity or any tool hardcoded as active."""
        self.assertNotIn("active_targets", DEFAULT_CONFIG)
        self.assertNotIn("tools_configured", DEFAULT_CONFIG)

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
        """Loading workspace state from a directory without state must return active_targets == [] and tools_configured is False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = load_workspace_state(Path(tmpdir))
            self.assertEqual(state.get("active_targets"), [])
            self.assertFalse(state.get("tools_configured"))

    def test_legacy_default_antigravity_cleaned_in_load_app_config(self):
        """Legacy config.json with active_targets or tools_configured is cleared."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            cfg_file = docs_dir / "config.json"
            cfg_file.write_text(
                json.dumps(
                    {
                        "version": "1.0.0",
                        "language": "pt",
                        "active_targets": ["antigravity"],
                        "tools_configured": True,
                    }
                ),
                encoding="utf-8",
            )

            loaded = load_app_config(repo_root=Path(tmpdir), omni_docs_dir=docs_dir)
            self.assertNotIn("active_targets", loaded)
            self.assertNotIn("tools_configured", loaded)

    def test_workspace_state_preserves_explicit_tool_configuration(self):
        """Workspace state must preserve explicit tool selections and tools_configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "project"
            work_dir.mkdir()
            state_file = work_dir / ".agents" / "workspace_state.json"
            state_file.parent.mkdir(parents=True, exist_ok=True)
            state_file.write_text(
                json.dumps(
                    {
                        "tools_configured": True,
                        "active_targets": ["antigravity"],
                    }
                ),
                encoding="utf-8",
            )

            loaded = load_workspace_state(work_dir)
            self.assertEqual(loaded.get("active_targets"), ["antigravity"])
            self.assertTrue(loaded.get("tools_configured"))

    def test_handle_target_selection_first_run_saves_choices_to_workspace(self):
        """handle_target_selection saves user's choice to workspace_state and leaves app_config clean."""
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "project"
            work_dir.mkdir()
            docs_dir = Path(tmpdir) / "omni_docs"
            docs_dir.mkdir()

            app_cfg = {}
            ws_state = {"active_targets": []}
            scanned = {"agents": [], "rules": [], "skills_by_category": {}}

            # Simulate user typing "2" (Claude), then "s" (save)
            inputs = ["2", "s"]
            with (
                patch(
                    "omni_agents.tui.targets_menu.get_styled_choice", side_effect=inputs
                ),
                patch("omni_agents.tui.targets_menu.press_enter_to_continue"),
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
            self.assertNotIn("active_targets", app_cfg)
            self.assertNotIn("tools_configured", app_cfg)

            # Verify saved on disk in workspace_state.json
            saved_ws = load_workspace_state(work_dir)
            self.assertEqual(saved_ws.get("active_targets"), ["claude"])
            self.assertTrue(saved_ws.get("tools_configured"))

    def test_workspace_isolation_no_cross_pollution(self):
        """Configuring tools in Workspace A must NOT affect Workspace B."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ws_a = Path(tmpdir) / "ws_a"
            ws_b = Path(tmpdir) / "ws_b"
            ws_a.mkdir()
            ws_b.mkdir()
            docs_dir = Path(tmpdir) / "omni_docs"
            docs_dir.mkdir()

            scanned = {"agents": [], "rules": [], "skills_by_category": {}}
            app_cfg = {}

            # Configure Workspace A with Antigravity (option "1")
            with (
                patch("omni_agents.tui.targets_menu.get_styled_choice", side_effect=["1", "s"]),
                patch("omni_agents.tui.targets_menu.press_enter_to_continue"),
            ):
                handle_target_selection(
                    target_path=ws_a,
                    repo_root=Path(tmpdir),
                    scanned=scanned,
                    current_state=load_workspace_state(ws_a),
                    lang="pt",
                    app_config=app_cfg,
                    omni_docs_dir=docs_dir,
                    is_first_run=True,
                )

            # Workspace A must have Antigravity and tools_configured: True
            state_a = load_workspace_state(ws_a)
            self.assertEqual(state_a.get("active_targets"), ["antigravity"])
            self.assertTrue(state_a.get("tools_configured"))

            # Workspace B must NOT have inherited Antigravity!
            state_b = load_workspace_state(ws_b)
            self.assertEqual(state_b.get("active_targets"), [])
            self.assertFalse(state_b.get("tools_configured"))

            # Global app_config must NOT have active_targets
            self.assertNotIn("active_targets", app_cfg)

            # Now configure Workspace B with Claude (option "2")
            with (
                patch("omni_agents.tui.targets_menu.get_styled_choice", side_effect=["2", "s"]),
                patch("omni_agents.tui.targets_menu.press_enter_to_continue"),
            ):
                handle_target_selection(
                    target_path=ws_b,
                    repo_root=Path(tmpdir),
                    scanned=scanned,
                    current_state=load_workspace_state(ws_b),
                    lang="pt",
                    app_config=app_cfg,
                    omni_docs_dir=docs_dir,
                    is_first_run=True,
                )

            # Workspace B must have Claude, Workspace A must still have Antigravity
            state_b_updated = load_workspace_state(ws_b)
            self.assertEqual(state_b_updated.get("active_targets"), ["claude"])
            self.assertTrue(state_b_updated.get("tools_configured"))

            state_a_check = load_workspace_state(ws_a)
            self.assertEqual(state_a_check.get("active_targets"), ["antigravity"])

    def test_is_default_or_system_path_permits_temp_workspaces(self):
        """Temporary directories and projects within them must not be rejected as system directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "subproject"
            self.assertFalse(is_default_or_system_path(work_dir))
            self.assertFalse(is_default_or_system_path(Path(tmpdir)))

        # Home directory itself must be detected as default/system
        self.assertTrue(is_default_or_system_path(Path.home()))


    def test_interactive_loop_prompts_only_first_run_per_workspace(self):
        """Interactive loop prompts for tools only on first run of each workspace."""
        from omni_agents.tui.menu import run_interactive_loop

        with tempfile.TemporaryDirectory() as tmpdir:
            ws_a = Path(tmpdir) / "ws_a"
            ws_b = Path(tmpdir) / "ws_b"
            ws_a.mkdir()
            ws_b.mkdir()
            docs_dir = Path(tmpdir) / "docs"
            docs_dir.mkdir()
            repo_root = Path(tmpdir) / "repo"
            repo_root.mkdir()
            scanned = {"agents": [], "rules": [], "skills_by_category": {}}

            # Run 1 on ws_a: should prompt
            with (
                patch("omni_agents.tui.menu.get_styled_choice", return_value="5"),
                patch("omni_agents.tui.menu.handle_target_selection", return_value=["antigravity"]) as mock_prompt,
                patch("sys.exit") as mock_exit,
            ):
                mock_exit.side_effect = SystemExit(0)
                try:
                    run_interactive_loop(
                        target_path=ws_a,
                        repo_root=repo_root,
                        omni_docs_dir=docs_dir,
                        app_config={},
                        scanned=scanned,
                        is_dev=False,
                        current_lang="en",
                    )
                except SystemExit:
                    pass

                self.assertEqual(mock_prompt.call_count, 1)

            # Run 2 on ws_a: state already exists, should NOT prompt
            with (
                patch("omni_agents.tui.menu.get_styled_choice", return_value="5"),
                patch("omni_agents.tui.menu.handle_target_selection") as mock_prompt,
                patch("sys.exit") as mock_exit,
            ):
                mock_exit.side_effect = SystemExit(0)
                try:
                    run_interactive_loop(
                        target_path=ws_a,
                        repo_root=repo_root,
                        omni_docs_dir=docs_dir,
                        app_config={},
                        scanned=scanned,
                        is_dev=False,
                        current_lang="en",
                    )
                except SystemExit:
                    pass

                self.assertEqual(mock_prompt.call_count, 0)

            # Run 3 on ws_b: unconfigured, should prompt
            with (
                patch("omni_agents.tui.menu.get_styled_choice", return_value="5"),
                patch("omni_agents.tui.menu.handle_target_selection", return_value=["cursor"]) as mock_prompt,
                patch("sys.exit") as mock_exit,
            ):
                mock_exit.side_effect = SystemExit(0)
                try:
                    run_interactive_loop(
                        target_path=ws_b,
                        repo_root=repo_root,
                        omni_docs_dir=docs_dir,
                        app_config={},
                        scanned=scanned,
                        is_dev=False,
                        current_lang="en",
                    )
                except SystemExit:
                    pass

                self.assertEqual(mock_prompt.call_count, 1)

            # Both workspaces maintain separate state
            self.assertEqual(load_workspace_state(ws_a)["active_targets"], ["antigravity"])
            self.assertEqual(load_workspace_state(ws_b)["active_targets"], ["cursor"])


if __name__ == "__main__":
    unittest.main()
