#!/usr/bin/env python3
"""
Lightweight, decoupled Internationalization (i18n) module for omni-agents.
Dynamically loads language catalogs from scripts/languages/*.json.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

LANGUAGES_DIR = Path(__file__).resolve().parent / "languages"

_CATALOGS: dict[str, dict[str, Any]] = {}
_ALIAS_MAP: dict[str, str] = {}
_DEFAULT_CODE = "en"


def load_languages(languages_dir: Path | None = None) -> None:
    """Scans and loads all .json language files from the languages directory."""
    global _DEFAULT_CODE
    _CATALOGS.clear()
    _ALIAS_MAP.clear()

    target_dir = languages_dir or LANGUAGES_DIR
    if not target_dir.exists() or not target_dir.is_dir():
        return

    for file_path in sorted(target_dir.glob("*.json")):
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        meta = data.get("_meta", {})
        code = str(meta.get("code") or file_path.stem).lower().strip()
        name = meta.get("name") or code.capitalize()
        badge = meta.get("badge") or code.upper()
        is_default = bool(meta.get("default", False)) or code == "en"

        if is_default:
            _DEFAULT_CODE = code

        # Unified dictionary of strings for fast lookup
        strings: dict[str, str] = {}
        if isinstance(data.get("ui"), dict):
            strings.update(data["ui"])
        if isinstance(data.get("targets"), dict):
            strings.update(data["targets"])
        # Support flat keys for backwards compatibility or custom catalogs
        for k, v in data.items():
            if k not in (
                "_meta",
                "ui",
                "targets",
                "target_descriptions",
            ) and isinstance(v, str):
                strings[k] = v

        target_desc = data.get("target_descriptions", {})
        if not isinstance(target_desc, dict):
            target_desc = {}

        _CATALOGS[code] = {
            "meta": {
                "code": code,
                "name": name,
                "badge": badge,
                "default": is_default,
            },
            "strings": strings,
            "target_descriptions": target_desc,
        }

        # Map canonical code and aliases
        _ALIAS_MAP[code] = code
        aliases = meta.get("aliases", [])
        if isinstance(aliases, list):
            for alias in aliases:
                _ALIAS_MAP[str(alias).lower().strip()] = code


# Initial auto-load on module import
load_languages()


def get_available_languages() -> list[dict[str, str]]:
    """Returns sorted list of available language descriptors, with default language first."""
    if not _CATALOGS:
        return [{"code": "en", "name": "English", "badge": "EN"}]

    langs: list[dict[str, str]] = []
    default_lang: dict[str, str] | None = None

    for code, data in _CATALOGS.items():
        entry = {
            "code": code,
            "name": str(data["meta"]["name"]),
            "badge": str(data["meta"]["badge"]),
        }
        if data["meta"].get("default") or code == _DEFAULT_CODE:
            default_lang = entry
        else:
            langs.append(entry)

    langs.sort(key=lambda x: x["name"])
    if default_lang:
        return [default_lang] + langs
    return langs


def resolve_language_code(identifier: str | None) -> str:
    """
    Resolves language code, name, or alias to a valid registered language code.
    Defaults to English ('en') if unknown.
    """
    if not identifier:
        return _DEFAULT_CODE

    cleaned = str(identifier).lower().strip()
    if cleaned in _ALIAS_MAP:
        return _ALIAS_MAP[cleaned]

    # Check prefix (e.g. 'pt_BR' -> 'pt')
    if "_" in cleaned:
        prefix = cleaned.split("_")[0]
        if prefix in _ALIAS_MAP:
            return _ALIAS_MAP[prefix]
    if "-" in cleaned:
        prefix = cleaned.split("-")[0]
        if prefix in _ALIAS_MAP:
            return _ALIAS_MAP[prefix]

    return _DEFAULT_CODE


def get_language_name(locale: str) -> str:
    """Returns the display name of a language."""
    code = resolve_language_code(locale)
    if code in _CATALOGS:
        return str(_CATALOGS[code]["meta"]["name"])
    return code.capitalize()


def get_language_badge(locale: str) -> str:
    """Returns the badge representation of a language (e.g. 'EN', 'PT-BR')."""
    code = resolve_language_code(locale)
    if code in _CATALOGS:
        return str(_CATALOGS[code]["meta"]["badge"])
    return code.upper()


def t(key: str, locale: str = "en", **kwargs: Any) -> str:
    """
    Translates a key into the specified locale.
    Falls back to English ('en'), then returns the raw key if not found.
    Accepts arbitrary formatting kwargs safely.
    """
    code = resolve_language_code(locale)
    strings = _CATALOGS.get(code, {}).get("strings", {})
    template = strings.get(key)

    if template is None:
        # Fallback to default catalog
        default_strings = _CATALOGS.get(_DEFAULT_CODE, {}).get("strings", {})
        template = default_strings.get(key, key)

    if kwargs:
        # Also provide 'name' if 'lang' was passed, and 'lang' if 'name' was passed
        if "lang" in kwargs and "name" not in kwargs:
            kwargs["name"] = kwargs["lang"]
        elif "name" in kwargs and "lang" not in kwargs:
            kwargs["lang"] = kwargs["name"]

        try:
            return template.format(**kwargs)
        except (KeyError, ValueError, IndexError):
            return template

    return template


def t_target(key: str, locale: str = "en", **kwargs: Any) -> str:
    """Helper alias for target adapter localized messages."""
    return t(key, locale=locale, **kwargs)


def get_target_description(
    target_id: str, locale: str = "en", fallback: str = ""
) -> str:
    """Returns localized description for a target adapter."""
    code = resolve_language_code(locale)
    target_dict = _CATALOGS.get(code, {}).get("target_descriptions", {})
    if target_id in target_dict and "description" in target_dict[target_id]:
        return str(target_dict[target_id]["description"])

    # Fallback to default language
    default_dict = _CATALOGS.get(_DEFAULT_CODE, {}).get("target_descriptions", {})
    if target_id in default_dict and "description" in default_dict[target_id]:
        return str(default_dict[target_id]["description"])

    return fallback


def get_target_display_name(
    target_id: str, locale: str = "en", fallback: str = ""
) -> str:
    """Returns localized display name for a target adapter."""
    code = resolve_language_code(locale)
    target_dict = _CATALOGS.get(code, {}).get("target_descriptions", {})
    if target_id in target_dict and "display_name" in target_dict[target_id]:
        return str(target_dict[target_id]["display_name"])

    # Fallback to default language
    default_dict = _CATALOGS.get(_DEFAULT_CODE, {}).get("target_descriptions", {})
    if target_id in default_dict and "display_name" in default_dict[target_id]:
        return str(default_dict[target_id]["display_name"])

    return fallback


def detect_system_language() -> str:
    """Detects default environment locale, falling back to English ('en')."""
    for var in ("LANG", "LC_ALL", "LC_MESSAGES"):
        val = os.environ.get(var, "").lower()
        if "pt" in val:
            return "pt"
        if "es" in val:
            return "es"
    return _DEFAULT_CODE
