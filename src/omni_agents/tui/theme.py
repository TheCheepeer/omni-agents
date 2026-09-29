#!/usr/bin/env python3
"""
Modern terminal design system and theme components for omni-agents.
Provides rounded panels, semantic status chips, consistent color palettes,
and cross-platform UTF-8 terminal output safety.
"""

from __future__ import annotations

import contextlib
import io
import sys
from collections.abc import Sequence
from typing import Any

from rich import box
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Safe UTF-8 reconfiguration for Windows console environments
if sys.platform.startswith("win"):
    with contextlib.suppress(AttributeError, OSError, ValueError, io.UnsupportedOperation):
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8")

# Global Rich console instance
console = Console(highlight=False)

# Semantic Color Constants
COLOR_PRIMARY = "cyan"
COLOR_ACCENT = "magenta"
COLOR_SUCCESS = "green"
COLOR_WARNING = "yellow"
COLOR_DANGER = "red"
COLOR_MUTED = "dim"
COLOR_TEXT = "white"
COLOR_BORDER = "dim cyan"

__all__ = [
    "COLOR_ACCENT",
    "COLOR_BORDER",
    "COLOR_DANGER",
    "COLOR_MUTED",
    "COLOR_PRIMARY",
    "COLOR_SUCCESS",
    "COLOR_TEXT",
    "COLOR_WARNING",
    "Console",
    "Panel",
    "Table",
    "Text",
    "box",
    "console",
    "escape",
    "get_styled_choice",
    "parse_menu_item",
    "press_enter_to_continue",
    "render_banner",
    "render_header",
    "render_menu_card",
    "render_selection_card",
]


def render_header(
    title: str,
    version: str,
    workspace: str,
    mode: str,
    active_targets: Sequence[str] | None = None,
    warning_banner: str | None = None,
    lang: str = "en",
    workspace_label: str | None = None,
    mode_label: str | None = None,
    active_targets_label: str | None = None,
    none_label: str | None = None,
) -> None:
    """
    Renders a modern rounded header panel displaying app metadata,
    workspace target, execution mode, and active target pills with full i18n support.
    """
    from omni_agents.i18n import t

    ws_lbl = workspace_label or t("target_workspace", lang)
    m_lbl = mode_label or t("mode_label", lang)
    targets_lbl = active_targets_label or t("active_tools", lang)
    none_str = none_label or t("none_default", lang)

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="dim", width=20)
    grid.add_column()

    grid.add_row(ws_lbl, f"[bold white]{escape(str(workspace))}[/bold white]")
    grid.add_row(m_lbl, f"[bold {COLOR_SUCCESS}]{escape(mode)}[/bold {COLOR_SUCCESS}]")

    if active_targets:
        target_pills = "  ".join(
            f"[bold {COLOR_PRIMARY}]●[/bold {COLOR_PRIMARY}] {escape(t_id)}"
            for t_id in active_targets
        )
        grid.add_row(targets_lbl, target_pills)
    else:
        grid.add_row(targets_lbl, f"[{COLOR_MUTED}]{escape(none_str)}[/{COLOR_MUTED}]")

    panel = Panel(
        grid,
        title=f"[bold {COLOR_PRIMARY}]{escape(title)}[/bold {COLOR_PRIMARY}] [{COLOR_MUTED}]v{escape(version)}[/{COLOR_MUTED}]",
        title_align="left",
        box=box.ROUNDED,
        border_style=COLOR_BORDER,
        padding=(1, 2),
    )
    console.print(panel)

    if warning_banner:
        render_banner(warning_banner, level="warning")


def parse_menu_item(text: str) -> tuple[str, str, str]:
    """
    Parses a menu string formatted like '[t] Title (Description)' into (key, title, desc).
    Handles i18n menu strings seamlessly.
    """
    import re

    m = re.match(r"^\[([^\]]+)\]\s*(.*)$", text.strip())
    if not m:
        return ("", text, "")
    key = m.group(1).strip()
    rest = m.group(2).strip()

    # Match trailing parenthesis: 'Title (Description)'
    m_paren = re.search(r"^(.*?)\s*\(([^)]+)\)\s*$", rest)
    if m_paren:
        return (key, m_paren.group(1).strip(), m_paren.group(2).strip())

    # Match trailing badge: 'Title: [current]'
    if ": [" in rest:
        parts = rest.split(": [", 1)
        return (key, parts[0].strip(), "[" + parts[1].strip())

    return (key, rest, "")


def render_menu_card(
    title: str,
    items: Sequence[str | tuple[str, str, str]],
    footer_hint: str = "Type shortcut key or 'q' to quit",
    border_style: str = "dim white",
) -> None:
    """
    Renders an action card with three aligned columns:
    1. Key shortcut (e.g. '[t]')
    2. Action title (e.g. 'Target Tools')
    3. Description / context (e.g. 'Toggle active assistants')
    """
    table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    table.add_column("Key", style=f"bold {COLOR_PRIMARY}", width=8, justify="right")
    table.add_column("Title", style="bold white", width=28)
    table.add_column("Desc", style=COLOR_MUTED)

    for item in items:
        if isinstance(item, str):
            key, item_title, desc = parse_menu_item(item)
        else:
            key, item_title, desc = item
        escaped_key = escape(f"[{key}]") if key else ""
        table.add_row(
            f"[bold {COLOR_PRIMARY}]{escaped_key}[/bold {COLOR_PRIMARY}]" if escaped_key else "",
            escape(item_title),
            escape(desc),
        )

    panel = Panel(
        table,
        title=f"[bold white]{escape(title)}[/bold white]",
        title_align="left",
        subtitle=f"[{COLOR_MUTED}]{escape(footer_hint)}[/{COLOR_MUTED}]",
        subtitle_align="right",
        box=box.ROUNDED,
        border_style=border_style,
        padding=(1, 1),
    )
    console.print(panel)


def render_selection_card(
    title: str,
    items: Sequence[dict[str, Any]],
    instructions: str,
    selected_ids: set[str],
    id_key: str = "id",
    name_key: str = "name",
    desc_key: str = "description",
    footer_hint: str = "Type number/token to toggle • 's' to save • 'v' to return",
    border_style: str = "dim cyan",
    subtitle: str | None = None,
) -> None:
    """
    Renders an interactive multi-selection card (checkboxes / toggles).
    Items in selected_ids are styled with green active checkmarks [x] and bold text.
    """
    table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    table.add_column("Index", style="dim", width=6, justify="right")
    table.add_column("Status", width=5, justify="center")
    table.add_column("Name", style="bold white", width=26)
    table.add_column("Desc", style=COLOR_MUTED)

    for idx, item in enumerate(items, 1):
        item_id = item.get(id_key, "")
        item_name = item.get(name_key) or item.get("display_name") or item.get("id") or item_id
        desc = item.get(desc_key, "")
        if len(desc) > 55:
            desc = desc[:52] + "..."

        is_selected = item_id in selected_ids
        if is_selected:
            status_markup = f"[bold {COLOR_SUCCESS}]\\[x][/bold {COLOR_SUCCESS}]"
            name_markup = f"[bold white]{escape(item_name)}[/bold white]"
        else:
            status_markup = f"[{COLOR_MUTED}]\\[ ][/{COLOR_MUTED}]"
            name_markup = f"[{COLOR_MUTED}]{escape(item_name)}[/{COLOR_MUTED}]"

        idx_label = f"[{idx:2d}]"
        table.add_row(escape(idx_label), status_markup, name_markup, escape(desc))

    panel_title = f"[bold white]{escape(title)}[/bold white]"
    if subtitle:
        panel_title += f" [{COLOR_MUTED}]({escape(subtitle)})[/{COLOR_MUTED}]"

    panel = Panel(
        table,
        title=panel_title,
        title_align="left",
        subtitle=f"[{COLOR_MUTED}]{escape(footer_hint)}[/{COLOR_MUTED}]",
        subtitle_align="right",
        box=box.ROUNDED,
        border_style=border_style,
        padding=(1, 1),
    )
    console.print(panel)

    if instructions:
        instructions_panel = Panel(
            Text(instructions, style="dim"),
            box=box.ROUNDED,
            border_style="dim",
            padding=(0, 1),
        )
        console.print(instructions_panel)


def render_banner(message: str, level: str = "info") -> None:
    """Renders a styled notification banner with color-coded borders."""
    color_map = {
        "info": COLOR_PRIMARY,
        "success": COLOR_SUCCESS,
        "warning": COLOR_WARNING,
        "error": COLOR_DANGER,
    }
    border_color = color_map.get(level, COLOR_PRIMARY)
    panel = Panel(
        f"[bold {border_color}]{escape(message)}[/bold {border_color}]",
        box=box.ROUNDED,
        border_style=border_color,
        padding=(0, 1),
    )
    console.print(panel)


def get_styled_choice(prompt_text: str = "Your choice: ", default: str = "") -> str:
    """Prompts the user with a styled terminal input arrow."""
    try:
        arrow = f"[bold {COLOR_PRIMARY}]›[/bold {COLOR_PRIMARY}] "
        console.print(f"\n{arrow}[white]{escape(prompt_text)}[/white]", end="")
        raw_choice = input().strip()
        return raw_choice.lower() if raw_choice else default.lower()
    except (EOFError, KeyboardInterrupt):
        return "q"


def press_enter_to_continue(message: str = "Press Enter to continue...") -> None:
    """Waits for user Enter input with a styled muted prompt."""
    try:
        console.print(f"\n[{COLOR_MUTED}]{escape(message)}[/{COLOR_MUTED}]", end="")
        input()
    except (EOFError, KeyboardInterrupt):
        pass
