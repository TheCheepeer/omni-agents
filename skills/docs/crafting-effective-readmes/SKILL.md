---
name: crafting-effective-readmes
description: >-
    Use when drafting, structuring, or improving README.md files.
    Not every README serves the same purpose — provides templates and guidelines tailored to audience and project type (open source, internal, personal, or configuration).
---

# Crafting Effective READMEs

## Overview

READMEs answer the questions your audience will have. Different audiences require different information — an open-source contributor needs fundamentally different context than you will six months from now opening a configuration folder.

**Always ask:** Who will read this file, and what do they need to know to succeed?

## Process

### Step 1: Identify the Task

Determine the active documentation task:

| Task         | When to Use                                                          |
| ------------ | -------------------------------------------------------------------- |
| **Creation** | Brand new project with no existing README                            |
| **Addition** | Need to document a new feature, command, or guide                    |
| **Update**   | Features have changed or dependencies/instructions have become stale |
| **Review**   | Audit to verify the README matches actual code reality               |

### Step 2: Task-Specific Questions

**When creating the initial README:**

1. What is the project type? (see Project Types below)
2. What problem does the project solve in a single sentence?
3. What is the fastest path to "it works" (quickstart)?
4. Are there critical prerequisites or key highlights?

**When adding a new section:**

1. What exact capability needs to be documented?
2. Where does this fit logically in the existing structure?
3. Who is the primary stakeholder for this section?

**When updating existing content:**

1. What changed in the codebase or architecture?
2. Read the current README and identify obsolete sections.
3. Propose targeted changes without removing still-valid material.

**When reviewing and auditing:**

1. Read the existing README.
2. Compare against real configuration files (`package.json`, `Cargo.toml`, build scripts).
3. Flag discrepancies or broken commands.

### Step 3: User Validation

Upon finishing a draft, always validate: **"Are there any additional details, environment constraints, or specific context you would like to include?"**

## Project Types

| Type                         | Target Audience                         | Primary Sections                                                        | Reference Template        |
| ---------------------------- | --------------------------------------- | ----------------------------------------------------------------------- | ------------------------- |
| **Open Source**              | External contributors and users         | Installation, Usage, Contributing, License                              | `templates/oss.md`        |
| **Personal**                 | Future you and portfolio visitors       | What it does, Tech stack, Design decisions                              | `templates/personal.md`   |
| **Internal / Corporate**     | Teammates and onboarding developers     | Local setup, Architecture, Runbooks, Environment variables              | `templates/internal.md`   |
| **Configuration / Dotfiles** | Future you (reconstructing local setup) | What lives here, Why it was configured this way, How to extend, Gotchas | `templates/xdg-config.md` |

If the project type is unclear, clarify before assuming a generic open-source template.

## Essential Sections (Present in Every README)

Every README requires at minimum:

1. **Project Name** — Clear, self-explanatory title
2. **Description** — What it is and why it exists, in 1 to 2 direct sentences
3. **Usage / Quickstart** — How to run or use it immediately with concrete examples

## Supporting Documents

- `section-checklist.md` — Recommended section checklist by project type
- `style-guide.md` — Common README mistakes and writing guidelines
- `using-references.md` — Deep dive guide and detailed templates
