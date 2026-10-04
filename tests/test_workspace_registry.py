"""
Unit tests for the central workspace registry (tracking, pruning, and persistence).
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from omni_agents.core.workspace import (
    add_tracked_workspace,
    load_tracked_workspaces,
    remove_tracked_workspace,
)
from omni_agents.targets.base import load_workspace_state, save_workspace_state


class TestWorkspaceRegistry(unittest.TestCase):
    """Verifies that the central workspaces.json registry tracks and prunes workspaces cleanly."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="omni_test_reg_"))
        self.docs_dir = self.temp_dir / "Documents" / "omni-agents"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        self.project_a = self.temp_dir / "projects" / "project_a"
        self.project_a.mkdir(parents=True, exist_ok=True)

        self.project_b = self.temp_dir / "projects" / "project_b"
        self.project_b.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_and_load_tracked_workspaces(self):
        add_tracked_workspace(
            self.project_a,
            active_tools=["cursor", "claude"],
            omni_docs_dir=self.docs_dir,
        )
        workspaces = load_tracked_workspaces(omni_docs_dir=self.docs_dir)
        self.assertEqual(len(workspaces), 1)
        self.assertEqual(workspaces[0]["path"], str(self.project_a.resolve()))
        self.assertEqual(workspaces[0]["active_tools"], ["claude", "cursor"])

    def test_auto_prune_nonexistent_workspace(self):
        add_tracked_workspace(
            self.project_a,
            active_tools=["cursor"],
            omni_docs_dir=self.docs_dir,
        )
        add_tracked_workspace(
            self.project_b,
            active_tools=["antigravity"],
            omni_docs_dir=self.docs_dir,
        )
        self.assertEqual(len(load_tracked_workspaces(self.docs_dir)), 2)

        # Delete project_b from disk
        shutil.rmtree(self.project_b, ignore_errors=True)

        # Loading again should prune project_b
        workspaces = load_tracked_workspaces(omni_docs_dir=self.docs_dir)
        self.assertEqual(len(workspaces), 1)
        self.assertEqual(workspaces[0]["path"], str(self.project_a.resolve()))

    def test_remove_tracked_workspace(self):
        add_tracked_workspace(
            self.project_a,
            active_tools=["antigravity"],
            omni_docs_dir=self.docs_dir,
        )
        self.assertEqual(len(load_tracked_workspaces(self.docs_dir)), 1)

        remove_tracked_workspace(self.project_a, omni_docs_dir=self.docs_dir)
        self.assertEqual(len(load_tracked_workspaces(self.docs_dir)), 0)

    def test_save_workspace_state_updates_registry(self):
        state = {
            "active_targets": ["cursor"],
            "selected_agents": [],
            "selected_rules": [],
            "selected_skills": {},
        }
        save_workspace_state(self.project_a, state, omni_docs_dir=self.docs_dir)
        workspaces = load_tracked_workspaces(self.docs_dir)
        self.assertEqual(len(workspaces), 1)
        self.assertEqual(workspaces[0]["active_tools"], ["cursor"])

        # When active_targets becomes empty, it should be removed from registry
        state["active_targets"] = []
        save_workspace_state(self.project_a, state, omni_docs_dir=self.docs_dir)
        self.assertEqual(len(load_tracked_workspaces(self.docs_dir)), 0)
