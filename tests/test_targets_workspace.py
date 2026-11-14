"""
Unit tests for workspace-local target adapters (Antigravity and other tools):
- Workspace confinement (real directory copies, no external paths, no symlinks)
- Legacy .agents/skills.json removal and load_workspace_state fallback
- Pruning deselected skills and empty skill sets (--skills none)
- Collision handling and ignored temporary directories
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from omni_agents.targets import get_target
from omni_agents.targets.base import is_link, load_workspace_state, save_workspace_state


class TestWorkspaceTargetsConfinement(unittest.TestCase):
    """Verifies workspace-local skill copying and removal of external path leaks."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="omni_test_targets_"))
        self.repo_root = self.temp_dir / "repo"
        self.workspace = self.temp_dir / "workspace"
        self.repo_root.mkdir(parents=True, exist_ok=True)
        self.workspace.mkdir(parents=True, exist_ok=True)

        # Create external skill sources in repo_root
        self.skill_alpha = self.repo_root / "skills" / "stacks" / "alpha-skill"
        (self.skill_alpha / "references").mkdir(parents=True, exist_ok=True)
        (self.skill_alpha / "scripts").mkdir(parents=True, exist_ok=True)
        (self.skill_alpha / "__pycache__").mkdir(parents=True, exist_ok=True)
        (self.skill_alpha / ".git").mkdir(parents=True, exist_ok=True)

        (self.skill_alpha / "SKILL.md").write_text(
            "---\nname: alpha-skill\ndescription: Alpha skill\n---\n# Alpha\n",
            encoding="utf-8",
        )
        (self.skill_alpha / "references" / "guide.md").write_text(
            "# Reference Guide\n", encoding="utf-8"
        )
        (self.skill_alpha / "scripts" / "run.py").write_text(
            "print('ok')\n", encoding="utf-8"
        )
        (self.skill_alpha / "__pycache__" / "run.cpython-312.pyc").write_bytes(b"\x00")
        (self.skill_alpha / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

        self.skill_beta = self.repo_root / "skills" / "docs" / "beta-skill"
        self.skill_beta.mkdir(parents=True, exist_ok=True)
        (self.skill_beta / "SKILL.md").write_text(
            "---\nname: beta-skill\ndescription: Beta skill\n---\n# Beta\n",
            encoding="utf-8",
        )

        # Rule and agent fixtures
        rule_dir = self.repo_root / "rules" / "general"
        rule_dir.mkdir(parents=True, exist_ok=True)
        self.rule_file = rule_dir / "AGENTS.md"
        self.rule_file.write_text("# General Rules\nFollow standards.\n", encoding="utf-8")

        agents_dir = self.repo_root / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        self.agent_file = agents_dir / "code-reviewer.md"
        self.agent_file.write_text(
            "---\nname: Code Reviewer\ndescription: Reviews code\n---\nReview carefully.\n",
            encoding="utf-8",
        )

        self.scanned = {
            "agents": [{"id": "code-reviewer.md", "path": str(self.agent_file)}],
            "rules": [{"id": "general", "path": str(self.rule_file)}],
            "skills_by_category": {
                "stacks": [{"id": "alpha-skill", "path": str(self.skill_alpha)}],
                "docs": [{"id": "beta-skill", "path": str(self.skill_beta)}],
            },
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _assert_no_links_inside(self, root_dir: Path) -> None:
        self.assertFalse(is_link(root_dir), f"{root_dir} must not be a symlink/junction")
        for item in root_dir.rglob("*"):
            self.assertFalse(is_link(item), f"{item} must not be a symlink/junction")

    def test_antigravity_copies_full_skill_dirs_and_removes_legacy_skills_json(self):
        target = get_target("antigravity")
        self.assertIsNotNone(target)

        # Plant legacy .agents/skills.json that should be deleted
        agents_dir = self.workspace / ".agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        legacy_manifest = agents_dir / "skills.json"
        legacy_manifest.write_text(
            json.dumps({"entries": [{"path": "/external/path", "include_only": ["alpha-skill"]}]}),
            encoding="utf-8",
        )

        ok = target.configure_workspace(
            target_path=self.workspace,
            repo_root=self.repo_root,
            scanned=self.scanned,
            agents=self.scanned["agents"],
            rules=self.scanned["rules"],
            skills_by_cat={"stacks": {"alpha-skill"}, "docs": {"beta-skill"}},
            lang="en",
        )
        self.assertTrue(ok)

        # Legacy skills.json must be removed
        self.assertFalse(legacy_manifest.exists())

        # Full directory structure must be copied locally
        copied_alpha = agents_dir / "skills" / "alpha-skill"
        self.assertTrue((copied_alpha / "SKILL.md").is_file())
        self.assertTrue((copied_alpha / "references" / "guide.md").is_file())
        self.assertTrue((copied_alpha / "scripts" / "run.py").is_file())
        self.assertTrue((agents_dir / "skills" / "beta-skill" / "SKILL.md").is_file())

        # Temporary/VCS garbage must be ignored
        self.assertFalse((copied_alpha / "__pycache__").exists())
        self.assertFalse((copied_alpha / ".git").exists())

        # .gitignore must contain .agents/
        gitignore = (self.workspace / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".agents/", gitignore)

        # Must be real files, never symlinks/junctions
        self._assert_no_links_inside(agents_dir)

    def test_antigravity_prunes_unselected_skills_and_cleans_on_none(self):
        target = get_target("antigravity")
        agents_dir = self.workspace / ".agents"

        target.configure_workspace(
            target_path=self.workspace,
            repo_root=self.repo_root,
            scanned=self.scanned,
            agents=self.scanned["agents"],
            rules=self.scanned["rules"],
            skills_by_cat={"stacks": {"alpha-skill"}, "docs": {"beta-skill"}},
            lang="en",
        )
        self.assertTrue((agents_dir / "skills" / "alpha-skill").exists())
        self.assertTrue((agents_dir / "skills" / "beta-skill").exists())

        # Re-sync keeping only alpha-skill and removing agents
        target.configure_workspace(
            target_path=self.workspace,
            repo_root=self.repo_root,
            scanned=self.scanned,
            agents=[],
            rules=self.scanned["rules"],
            skills_by_cat={"stacks": {"alpha-skill"}},
            lang="en",
        )
        self.assertTrue((agents_dir / "skills" / "alpha-skill" / "SKILL.md").exists())
        self.assertFalse((agents_dir / "skills" / "beta-skill").exists())
        self.assertFalse((agents_dir / "agents").exists())

        # Sync with no skills (--skills none) removes .agents/skills/ completely
        target.configure_workspace(
            target_path=self.workspace,
            repo_root=self.repo_root,
            scanned=self.scanned,
            agents=[],
            rules=[],
            skills_by_cat={},
            lang="en",
        )
        self.assertFalse((agents_dir / "skills").exists())
        self.assertFalse((agents_dir / "rules").exists())
        self.assertFalse((agents_dir / "skills.json").exists())

    def test_antigravity_replaces_symlinked_skill_with_real_copy(self):
        target = get_target("antigravity")
        skills_dir = self.workspace / ".agents" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        outside_target = self.temp_dir / "outside_dir"
        outside_target.mkdir()

        # Simulate a legacy symlink or junction inside .agents/skills/
        link_path = skills_dir / "alpha-skill"
        try:
            if sys.platform.startswith("win"):
                import _winapi
                _winapi.CreateJunction(str(outside_target), str(link_path))
            else:
                link_path.symlink_to(outside_target, target_is_directory=True)
        except OSError:
            # Skip symlink creation part if OS restricts it, still run configure_workspace
            pass

        target.configure_workspace(
            target_path=self.workspace,
            repo_root=self.repo_root,
            scanned=self.scanned,
            agents=[],
            rules=[],
            skills_by_cat={"stacks": {"alpha-skill"}},
            lang="en",
        )
        self._assert_no_links_inside(self.workspace / ".agents")
        self.assertTrue((link_path / "SKILL.md").is_file())
        self.assertFalse((outside_target / "SKILL.md").exists())

    def test_skill_id_collision_across_categories_is_deterministic(self):
        # Two different categories both define 'shared-name'
        cat1_skill = self.repo_root / "skills" / "frontend" / "shared-name"
        cat2_skill = self.repo_root / "skills" / "backend" / "shared-name"
        cat1_skill.mkdir(parents=True, exist_ok=True)
        cat2_skill.mkdir(parents=True, exist_ok=True)
        (cat1_skill / "SKILL.md").write_text("# Frontend Shared\n", encoding="utf-8")
        (cat2_skill / "SKILL.md").write_text("# Backend Shared\n", encoding="utf-8")

        scanned = {
            "agents": [],
            "rules": [],
            "skills_by_category": {
                "backend": [{"id": "shared-name", "path": str(cat2_skill)}],
                "frontend": [{"id": "shared-name", "path": str(cat1_skill)}],
            },
        }
        target = get_target("antigravity")
        target.configure_workspace(
            target_path=self.workspace,
            repo_root=self.repo_root,
            scanned=scanned,
            agents=[],
            rules=[],
            skills_by_cat={"backend": {"shared-name"}, "frontend": {"shared-name"}},
            lang="en",
        )
        skills_dir = self.workspace / ".agents" / "skills"
        self.assertIn("Backend Shared", (skills_dir / "shared-name" / "SKILL.md").read_text(encoding="utf-8"))
        self.assertIn(
            "Frontend Shared",
            (skills_dir / "frontend-shared-name" / "SKILL.md").read_text(encoding="utf-8"),
        )

    def test_load_workspace_state_reads_state_and_legacy_skills_json(self):
        # Legacy skills.json fallback when workspace_state.json does not exist
        agents_dir = self.workspace / ".agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "skills.json").write_text(
            json.dumps(
                {
                    "entries": [
                        {"path": "C:/external/skills/stacks", "include_only": ["alpha-skill"]}
                    ]
                }
            ),
            encoding="utf-8",
        )
        legacy_state = load_workspace_state(self.workspace)
        self.assertEqual(legacy_state["selected_skills"], {"stacks": ["alpha-skill"]})
        self.assertFalse(legacy_state["tools_configured"])

        # workspace_state.json takes precedence
        save_workspace_state(
            self.workspace,
            {
                "language": "pt",
                "active_targets": ["antigravity"],
                "selected_agents": [],
                "selected_rules": ["general"],
                "selected_skills": {"docs": ["beta-skill"]},
                "tools_configured": True,
            },
        )
        state = load_workspace_state(self.workspace)
        self.assertEqual(state["language"], "pt")
        self.assertEqual(state["active_targets"], ["antigravity"])
        self.assertEqual(state["selected_skills"], {"docs": ["beta-skill"]})
        self.assertTrue(state["tools_configured"])

    def test_other_targets_use_workspace_local_skills_without_external_paths(self):
        repo_path_str = self.repo_root.resolve().as_posix()

        cases = [
            ("claude", "CLAUDE.md", ".claude/skills"),
            ("cursor", ".cursor/rules/skills.mdc", ".cursor/skills"),
            ("copilot", ".github/copilot-instructions.md", ".github/skills"),
            ("universal", "AGENTS.md", ".agents/skills"),
            ("kiro", "AGENTS.md", ".kiro/skills"),
            ("opencode", "AGENTS.md", ".opencode/skills"),
            ("codex", "AGENTS.md", ".agents/skills"),
        ]

        for target_id, doc_rel, skills_rel in cases:
            ws = self.temp_dir / f"ws_{target_id}"
            ws.mkdir(parents=True, exist_ok=True)
            adapter = get_target(target_id)
            self.assertIsNotNone(adapter)

            ok = adapter.configure_workspace(
                target_path=ws,
                repo_root=self.repo_root,
                scanned=self.scanned,
                agents=self.scanned["agents"],
                rules=self.scanned["rules"],
                skills_by_cat={"stacks": {"alpha-skill"}},
                lang="en",
            )
            self.assertTrue(ok, f"{target_id} configure_workspace failed")

            doc_file = ws / doc_rel
            self.assertTrue(doc_file.is_file(), f"Missing {doc_rel} for {target_id}")
            doc_text = doc_file.read_text(encoding="utf-8")
            self.assertNotIn(
                repo_path_str,
                doc_text,
                f"{target_id} leaked external path in {doc_rel}",
            )
            expected_rel_ref = f"{skills_rel}/alpha-skill/SKILL.md"
            self.assertIn(
                expected_rel_ref,
                doc_text,
                f"{target_id} missing workspace-relative path {expected_rel_ref}",
            )

            copied_skill = ws / skills_rel / "alpha-skill"
            self.assertTrue((copied_skill / "SKILL.md").is_file())
            self.assertTrue((copied_skill / "references" / "guide.md").is_file())
            self._assert_no_links_inside(copied_skill)

            # Cleaning removes generated config and skills directory
            adapter.clean_workspace(ws, lang="en")
            self.assertFalse(doc_file.exists(), f"{target_id} failed to clean {doc_rel}")
            self.assertFalse(
                (ws / skills_rel).exists(),
                f"{target_id} failed to clean {skills_rel}",
            )

    def test_codex_clean_preserves_shared_agents_skills_when_antigravity_active(self):
        save_workspace_state(
            self.workspace,
            {
                "active_targets": ["antigravity", "codex"],
                "selected_agents": [],
                "selected_rules": [],
                "selected_skills": {"stacks": ["alpha-skill"]},
            },
        )
        ag = get_target("antigravity")
        codex = get_target("codex")
        ag.configure_workspace(
            self.workspace,
            self.repo_root,
            self.scanned,
            [],
            [],
            {"stacks": {"alpha-skill"}},
        )
        codex.configure_workspace(
            self.workspace,
            self.repo_root,
            self.scanned,
            [],
            [],
            {"stacks": {"alpha-skill"}},
        )

        codex.clean_workspace(self.workspace, lang="en")
        self.assertFalse((self.workspace / "AGENTS.md").exists())
        self.assertTrue((self.workspace / ".agents" / "skills" / "alpha-skill" / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
