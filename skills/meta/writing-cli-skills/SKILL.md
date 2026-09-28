---
name: writing-cli-skills
description: >-
    Use when authoring an agent skill that wraps a command-line interface (CLI) tool or terminal binary.
    Guides hands-on tool exploration, installation and usage structures, trigger-rich descriptions for semantic activation, task-oriented command grouping, progressive disclosure, and pre-publish checklists.
---

# Authoring Skills for CLI Tools (Writing CLI Skills)

How to build high-quality skills that package and teach command-line interface (CLI) tools to AI agents.

## Quickstart

1. **Install and run the tool hands-on** — do not just read docs. Testing real commands uncovers real behaviors, undocumented gotchas, and defaults that reference manuals omit.
2. Run `--help` across each primary subcommand.
3. Test the most frequent day-to-day operations.
4. Note counterintuitive behaviors or surprises.
5. Copy the template in `references/template.md` into the new skill directory.
6. Populate sections based on real terminal findings.
7. Strip irrelevant sections.

```bash
# 1. Test tool in the terminal
my-cli --help
my-cli subcommand --help

# 2. Skill placement in Gemini/Antigravity:
# Project-level: .agents/skills/my-cli/SKILL.md
# Global-level: ~/.gemini/config/skills/my-cli/SKILL.md
```

## What NOT to Do

- Do not dump unfiltered `--help` output — extract only actionable flags.
- Do not document dozens of obscure flags — cover the 80% daily use cases.
- Do not include commands you have not verified yourself.
- Keep the root `SKILL.md` under 500 lines to preserve context window tokens.

## Skill Sections

### Mandatory

| Section              | Purpose                                                               |
| -------------------- | --------------------------------------------------------------------- |
| **YAML Frontmatter** | `name` and trigger-rich `description` enabling semantic matching      |
| **Installation**     | How to install or build the binary across supported operating systems |
| **Primary Usage**    | The 80% highest-frequency commands and workflows                      |

### Recommended

| Section                | When to Include                                                   |
| ---------------------- | ----------------------------------------------------------------- |
| Prerequisites          | Tool requires API tokens, cloud accounts, or runtime dependencies |
| Output Formats         | Tool supports flags like `--json` that simplify agent parsing     |
| Tips and Gotchas       | Interactive prompts that block the terminal and must be bypassed  |
| Troubleshooting        | How to enable verbose debugging (`--verbose`, `--debug`)          |
| Uninstall / Data paths | Where the tool persists state, cache, or configuration files      |

## Frontmatter Descriptions

Include explicit intent phrases so the agent knows precisely when to load the skill:

```yaml
# Good: descriptive with concrete scenarios
description: Monitors RSS feeds for updates. Use when following technical blogs, checking new releases, or building feed-reading pipelines.

# Bad: overly generic
description: RSS tool.
```

## Organizing Commands

Group commands by **user task** rather than CLI command hierarchy:

- View / List
- Create / Add
- Update / Edit
- Delete / Remove
- Search / Filter

## Progressive Disclosure

Keep `SKILL.md` lean. Move comprehensive reference material to `references/`:

```text
my-cli/
├── SKILL.md                 # Fast, essential everyday workflows
├── references/
│   ├── advanced-config.md   # Complex configuration options
│   └── api-reference.md     # Full catalog of flags and subcommands
└── scripts/
    └── helper.sh            # Deterministic automation scripts
```

## Publication Checklist

- [ ] Frontmatter includes kebab-case `name` and trigger-rich `description`.
- [ ] Installation instructions verified.
- [ ] Includes verification check (`tool --version`).
- [ ] Config file paths and environment variables documented.
- [ ] Realistic examples with sample command and output formats.
- [ ] JSON output flags highlighted (preferred for agents).
- [ ] Warnings against interactive commands that hang terminals.
- [ ] Lean main file with deep reference manuals moved to `references/`.
