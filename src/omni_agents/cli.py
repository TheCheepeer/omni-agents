#!/usr/bin/env python3
"""
omni-agents CLI entry point and argument router.
Cross-platform (Windows, Linux, macOS) using standard library.
"""

from __future__ import annotations

import argparse
import contextlib
import sys
from collections.abc import Sequence
from pathlib import Path

# Ensure parent directory (src/) is in sys.path when executed directly as a script
_SRC_DIR = Path(__file__).resolve().parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from omni_agents.commands.clean_cmd import clean_global_cli, clean_workspace_cli
from omni_agents.commands.diagnostics import run_update, show_info
from omni_agents.commands.ext_cmd import (
    install_extension,
    list_extensions,
    remove_extension,
    update_extensions,
)
from omni_agents.commands.list_cmd import (
    list_agents,
    list_rules,
    list_skills,
    list_tools,
)
from omni_agents.commands.sync_cmd import configure_global_cli, sync_workspace_cli
from omni_agents.core.config import load_app_config
from omni_agents.core.scanner import scan_repository
from omni_agents.core.workspace import has_graphical_display
from omni_agents.env_paths import (
    ensure_omni_documents_structure,
    find_repo_root,
    is_dev_mode,
    open_folder_in_explorer,
)
from omni_agents.i18n import resolve_language_code
from omni_agents.targets import load_workspace_state
from omni_agents.tui.menu import run_interactive_loop
from omni_agents.updater import (
    __version__,
    check_for_updates,
    prompt_and_upgrade,
)


def _configure_terminal_encoding() -> None:
    """Ensures UTF-8 terminal encoding on Windows for accented characters and symbols."""
    if sys.platform.startswith("win"):
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def build_parser() -> argparse.ArgumentParser:
    """Builds and returns the top-level command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="omni-agents",
        description="omni-agents: Multi-Tool Agent, Rules & Skills Configurator.",
        epilog=(
            "Usage examples:\n"
            "  omni-agents\n"
            "  omni-agents .\n"
            "  omni-agents /path/to/project --tools cursor\n"
            "  omni-agents /path/to/project --sync --lang en\n"
            "  omni-agents --global\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Path to target repository directory (defaults to current directory for inline actions)",
    )
    parser.add_argument(
        "-t",
        "--tool",
        "--tools",
        "--target-tool",
        dest="target_tool",
        help="Target tool(s) (comma-separated: antigravity, claude, cursor, copilot, universal, kiro, opencode, codex, or all)",
    )
    parser.add_argument(
        "-a",
        "--agent",
        "--agents",
        dest="agents",
        default=None,
        help="Subagent ID(s) to activate in workspace (comma-separated: e.g. 'code-reviewer,security-auditor' or 'all', 'none')",
    )
    parser.add_argument(
        "-r",
        "--rule",
        "--rules",
        "--rule-profile",
        dest="rule_profile",
        default=None,
        help="Rule profile ID(s) to apply (comma-separated: e.g. 'general,pt-br-dev' or 'all', 'none')",
    )
    parser.add_argument(
        "-s",
        "--skill",
        "--skills",
        dest="skills",
        default=None,
        help="Skill ID(s) or categories to activate in workspace (comma-separated: e.g. 'testing,git/commit-helper' or 'all', 'none')",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Executes fast synchronization in target workspace without interactive menu",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Removes configurations from target workspace for specified tool(s) (or all)",
    )
    parser.add_argument(
        "--global",
        dest="is_global",
        action="store_true",
        help="Applies global configuration for specified tool(s) (or all)",
    )
    parser.add_argument(
        "-y",
        "--yes",
        dest="assume_yes",
        action="store_true",
        help="Automatically answer yes to confirmation prompts (e.g. link overwrite)",
    )
    parser.add_argument(
        "--lang",
        default=None,
        help="UI Language (e.g. en, pt, pt-BR, etc.)",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="Lists all supported tools and exits",
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="Lists available subagents and exits",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="Lists available rules and exits",
    )
    parser.add_argument(
        "--list-skills",
        action="store_true",
        help="Lists available modular skills by category and exits",
    )
    parser.add_argument(
        "--ext-list",
        action="store_true",
        help="Lists installed remote extensions and exits",
    )
    parser.add_argument(
        "--ext-install",
        "--ext-download",
        dest="ext_install",
        default=None,
        metavar="ITEM",
        help="Installs a remote extension from catalog (e.g. 'agents/code-reviewer.md' or 'skills/testing/pytest')",
    )
    parser.add_argument(
        "--ext-update",
        action="store_true",
        help="Checks and updates all installed remote extensions",
    )
    parser.add_argument(
        "--ext-remove",
        dest="ext_remove",
        default=None,
        metavar="KEY",
        help="Removes an installed remote extension by key",
    )
    parser.add_argument(
        "--open-folder",
        action="store_true",
        help="Opens personal omni-agents folder in File Explorer (or displays path)",
    )
    parser.add_argument(
        "--no-update-check",
        action="store_true",
        help="Disables automatic version and update checks on startup",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Checks for tool updates and executes upgrade if available",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Displays system paths, active configuration, and execution mode",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI execution flow."""
    _configure_terminal_encoding()

    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = find_repo_root()
    is_dev = is_dev_mode(repo_root)
    omni_docs_dir, _ = ensure_omni_documents_structure()

    # Workspace target path resolution
    target_raw = args.target
    if target_raw:
        target_path = Path(target_raw).resolve()
        if not target_path.exists() or not target_path.is_dir():
            print(
                f"\n[x] Error: Path does not exist or is not a directory: {target_path}\n"
            )
            return 1
    else:
        try:
            target_path = Path.cwd().resolve()
        except OSError:
            target_path = None

    app_config = load_app_config(repo_root, omni_docs_dir=omni_docs_dir)
    workspace_state = load_workspace_state(target_path) if target_path else {}
    current_lang = resolve_language_code(
        args.lang
        or app_config.get("language")
        or workspace_state.get("language")
        or "en"
    )

    # 1. Diagnostics & Information
    if args.info:
        show_info(
            repo_root=repo_root,
            omni_docs_dir=omni_docs_dir,
            app_config=app_config,
            is_dev=is_dev,
        )
        return 0

    if args.update:
        run_update(is_dev=is_dev, current_lang=current_lang)
        return 0

    if args.list_tools:
        list_tools()
        return 0

    # 2. Automatic background update check on interactive launch
    if (
        not args.no_update_check
        and not args.sync
        and not args.clean
        and not args.is_global
    ):
        with contextlib.suppress(OSError, TimeoutError):
            up_info = check_for_updates(
                current_version=__version__, is_dev=is_dev, timeout=1.5
            )
            if up_info and prompt_and_upgrade(up_info, lang=current_lang):
                return 0

    scanned = scan_repository(repo_root, documents_dir=omni_docs_dir)

    # 3. Personal folder inspection
    if args.open_folder:
        if has_graphical_display():
            open_folder_in_explorer(omni_docs_dir)
        print(f"Personal omni-agents folder: {omni_docs_dir}")
        return 0

    # 4. Component listing
    if args.list_agents:
        list_agents(scanned)
        return 0

    if args.list_rules:
        list_rules(scanned)
        return 0

    if args.list_skills:
        list_skills(scanned)
        return 0

    # 5. Remote extensions operations
    ext_dir = (omni_docs_dir / "ext") if omni_docs_dir else None
    if args.ext_list:
        list_extensions(ext_dir)
        return 0

    if args.ext_install:
        ok = install_extension(args.ext_install, app_config, ext_dir)
        return 0 if ok else 1

    if args.ext_update:
        ok = update_extensions(app_config, ext_dir)
        return 0 if ok else 1

    if args.ext_remove:
        ok = remove_extension(args.ext_remove, ext_dir)
        return 0 if ok else 1

    # Inline action path resolution
    has_inline_action = (
        args.sync
        or args.clean
        or args.agents is not None
        or args.skills is not None
        or (args.rule_profile is not None and not args.is_global)
    )
    if target_path is None and has_inline_action and not args.is_global:
        target_path = Path.cwd().resolve()

    # 6. Global Clean via CLI
    if args.is_global and args.clean:
        clean_global_cli(
            target_tool=args.target_tool,
            app_config=app_config,
            repo_root=repo_root,
            omni_docs_dir=omni_docs_dir,
            current_lang=current_lang,
        )
        return 0

    # 7. Global Configuration Mode via CLI
    if args.is_global:
        configure_global_cli(
            target_tool=args.target_tool,
            rule_profile=args.rule_profile,
            assume_yes=args.assume_yes,
            app_config=app_config,
            scanned=scanned,
            repo_root=repo_root,
            omni_docs_dir=omni_docs_dir,
            current_lang=current_lang,
        )
        return 0

    # 8. Workspace Clean Mode via CLI
    if args.clean and target_path:
        clean_workspace_cli(
            target_path=target_path,
            target_tool=args.target_tool,
            assume_yes=args.assume_yes,
            current_lang=current_lang,
        )
        return 0

    # 9. Workspace Sync Mode via CLI
    if has_inline_action and target_path:
        sync_workspace_cli(
            target_path=target_path,
            target_tool=args.target_tool,
            agents_arg=args.agents,
            rule_profile_arg=args.rule_profile,
            skills_arg=args.skills,
            assume_yes=args.assume_yes,
            scanned=scanned,
            repo_root=repo_root,
            current_lang=current_lang,
            app_config=app_config,
        )
        return 0

    # 10. Interactive Terminal UI Loop
    run_interactive_loop(
        target_path=target_path,
        repo_root=repo_root,
        omni_docs_dir=omni_docs_dir,
        app_config=app_config,
        scanned=scanned,
        is_dev=is_dev,
        current_lang=current_lang,
        explicit_lang=bool(args.lang),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
