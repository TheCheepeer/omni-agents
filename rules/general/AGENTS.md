---
name: general-development-guidelines
description: Core engineering standards, security rules, English communication guidelines, no emojis, and clean software architecture.
---

# Global Development Guidelines (General)

This file defines standards, architectural guidelines, and rules that must be strictly followed by all AI agents.

## General Principles

- Adhere to Clean Code and solid software architecture principles.
- Maintain an uncompromising focus on security, performance, and maintainability.
- Preserve the integrity of preexisting documentation, comments, and project conventions.

## Security

- Never hardcode or commit credentials, API keys, passwords, secrets, or sensitive tokens.
- Validate and sanitize all user inputs across boundaries.
- Follow OWASP Top 10 recommendations and secure coding standards.

## Communication and Style

- Provide direct, clear, concise, and objective responses.
- Maintain stylistic consistency with the preexisting codebase.
- **Language Adaptation:** Always reply in the language used by the user in their prompt (default to English when unspecified).
- **Strict Grammar and Orthography:** Strictly respect standard orthography, grammar, and punctuation across all languages in responses, documentation, UI strings, code comments, and commit messages.
- **Absolute Prohibition of Emojis:** Never use emojis under any circumstances (in responses, code comments, documentation, commits, or system messages). Keep all communication strictly textual, clean, and professional.

## Frontend and Styling (Tailwind CSS)

- **Mandatory Standard:** All web and frontend development must use **Tailwind CSS** for styling.
- **Latest Stable Version:**
    - Always adopt the most recent stable release available.
    - Check the official registry or documentation before bootstrapping new projects.
    - For Tailwind CSS v4+, use the modern native CSS setup (`@import "tailwindcss";` and `@theme` directives), avoiding legacy configuration files (`tailwind.config.js`) unless the preexisting project already runs on v3.
- **Prohibition of Standalone CSS & CSS-in-JS:** Do not create separate stylesheet files (`.css`, `.scss`) or install CSS-in-JS libraries (such as `styled-components` or `emotion`), unless explicitly requested or preexisting.
- **Dynamic Utility Composition:** When combining conditional utility classes, always use `clsx` and `tailwind-merge` (standard `cn(...)` helper function).
- **Accessibility & Interactive States:** Ensure visible focus rings (`focus-visible:ring-*`), screen-reader support (`sr-only`), and explicit interactive states (`hover:`, `active:`, `disabled:`).
