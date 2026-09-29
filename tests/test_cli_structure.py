"""
Unit tests for the omni_agents modular package architecture using src/ layout.
"""

from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
