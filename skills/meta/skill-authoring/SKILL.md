---
name: skill-authoring
description: >-
    Use when creating, authoring, refining, or debugging skills for AI agents.
    Guides SKILL.md file structure, frontmatter schemas, trigger-rich descriptions for semantic activation, progressive disclosure organization, structural validation, and troubleshooting skills that fail to activate or get ignored by models.
---

# Skill Authoring and Maintenance (Skill Authoring)

Use this guide as an authoritative manual for creating, auditing, and maintaining high-impact skills for AI coding agents.

A skill is considered complete when it activates only on appropriate queries, delivers unambiguous instructions without wasting context window tokens, and grounds its advice in verifiable repository evidence.

AI agents read `name` and `description` before loading the file body. The main body is pulled into working context only when the description matches the user's intent. Supporting references, scripts, and templates are read strictly on demand. Always author content respecting this loading hierarchy.

## Choose the Appropriate Workflow

| Objective                                             | Entry Point                                        | Secondary Resources                                                                              |
| ----------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Create a simple skill from scratch                    | [workflows/create.md](workflows/create.md)         | [templates/simple.md](templates/simple.md), [references/patterns.md](references/patterns.md)     |
| Create or update from project docs and history        | [workflows/synthesize.md](workflows/synthesize.md) | [README.md](README.md), [references/examples.md](references/examples.md)                         |
| Review or audit an existing skill                     | [references/rules.md](references/rules.md)         | [references/examples.md](references/examples.md), [spec/specification.md](spec/specification.md) |
| Verify that a skill activates and responds correctly  | [workflows/test.md](workflows/test.md)             | [workflows/debug.md](workflows/debug.md) upon failure                                            |
| Diagnose a skill that fails to activate or is ignored | [workflows/debug.md](workflows/debug.md)           | [spec/specification.md](spec/specification.md)                                                   |
| Refine a skill after an observed runtime failure      | [workflows/refine.md](workflows/refine.md)         | [references/rules.md](references/rules.md)                                                       |

## Cardinal Quality Rules

1. **Descriptions must contain trigger keywords:** Without explicit intent verbs and domain nouns, agents cannot match queries semantically.
2. **Descriptions describe capabilities and conditions, not step-by-step procedures:** Agents can fixate on frontmatter summaries instead of reading detailed instructions in the body if steps are compressed into the description.
3. **Descriptions use 3rd-person phrasing:** Injected as system metadata ("Use when...", "Guides..."), never as conversational agent dialogue.
4. **Name must match the parent folder exactly:** In kebab-case format (`skill-name`).
5. **Critical instructions live near the top:** In long files, terminal instructions experience attention degradation.
6. **`SKILL.md` must remain lean:** Runtime context is expensive; relocate deep technical manuals to `references/`.
7. **References must be explicitly linked in Markdown:** Relative links allow agents to navigate referenced resources systematically.
8. **Precision over volume:** Bloated, rambling instructions degrade agent reasoning reliability.

## Skill Anatomy

```text
skill-name/
├── SKILL.md              # Mandatory entry point (core instructions and rules)
├── README.md             # Optional: human maintainer documentation
├── references/           # Optional: deep-dive manuals loaded on demand
├── scripts/              # Optional: deterministic executable scripts
└── assets/               # Optional: templates, schemas, and static assets
```

Recommended content distribution:

- **`SKILL.md`:** YAML frontmatter and foundational operational rules.
- **`references/*.md`:** Detailed explanations and manuals that agents read only when specialized depth is needed.
- **`scripts/*`:** Deterministic, repetitive operations that code executes more reliably than text generation.
- **`assets/*`:** Output templates, JSON schemas, and raw examples.

## Writing Effective Frontmatter Descriptions

The description determines whether the skill is loaded or bypassed. Follow this template:

```yaml
description: >-
    Use when [trigger conditions] — [specific capabilities].
    Handles [file formats, contexts, failure symptoms, related terms].
```

**Recommended Example:**

```yaml
description: >-
    Use when working with PDF files — text extraction, form filling, and document merging.
    Handles .pdf files, scanned forms, and interactive form fields.
```

**Anti-Pattern to Avoid:**

```yaml
description: Processes PDFs by extracting text and creating reports.
```

## Progressive Disclosure

| Layer       | Content                    | When Loaded                          | Purpose                                 |
| ----------- | -------------------------- | ------------------------------------ | --------------------------------------- |
| **Layer 1** | `name` + `description`     | Always (injected in initial context) | Fast, accurate activation matching      |
| **Layer 2** | `SKILL.md` body            | On skill activation                  | Core operational workflow and idioms    |
| **Layer 3** | `references/` & `scripts/` | On demand                            | Surgical deep-dives for specialized ops |

## Body Structure of `SKILL.md`

Write for an intelligent reasoning agent. Do not explain standard basics. Provide:

1. **Choice:** Identify the operational track or mode quickly.
2. **Action:** Clear imperative steps and decision gates.
3. **Examples:** Concrete, idiomatic snippets.
4. **Guards:** Common failure modes, false positives, and pitfalls.
5. **Verification:** Exact command or check confirming success.

Prefer tables, structured lists, and focused snippets over verbose narrative prose.
