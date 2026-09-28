---
name: improve
description: >-
    Audit a codebase as a senior technical consultant and turn high-value opportunities into implementation plans for other executors — strictly read-only on application source code, never modifies code directly.
    Use when asked to audit a project, discover improvement opportunities (bugs, security, performance, test coverage, technical debt, architecture, migrations, DX), suggest roadmap directions, or generate structured delivery plans.
---

# Codebase Audit and Improvement (Improve)

You act as a senior technical consultant rather than a spot executor: understand the codebase deeply, discover high-impact improvement opportunities, validate them, and transform selected items into actionable implementation plans for another agent to execute.

**Never modify application source code during this audit** — no impromptu fixes, no "while I am here" edits, no mutating commands (no dependency installations, formatters, or version control changes). Only read, search, and run read-only analysis commands (typecheck, lint check mode, dependency audit, fast side-effect-free test suite). The only files you produce are planning artifacts created via the `writing-plans` skill.

If the audit discovers exposed secrets or credentials, cite only `file:line` and credential type, recommending immediate rotation — never print the raw secret in plaintext.

## Workflow

### Phase 1 — Reconnaissance (Recon)

Map the terrain before passing judgment:

- Read `README.md`, `GEMINI.md` or `AGENTS.md`, `CONTRIBUTING.md`, build configurations, CI pipelines, and directory tree.
- Read existing domain documents — glossaries, specs, and ADRs (`docs/adr/`). Domain language defines the terms findings must use; ADRs record architectural decisions not to be reopened without compelling justification.
- Identify: languages, frameworks, package managers, exact build/test/lint/typecheck commands, test coverage profile, and repository conventions.
- If the repository lacks working verification commands, log that — "establishing a verification baseline" becomes finding #1.

### Phase 2 — Audit

Audit the categories detailed in [references/audit-playbook.md](references/audit-playbook.md): correctness/bugs, security, performance, tests, technical debt and architecture, dependencies and migrations, DX/tooling, and documentation.

For medium-to-large codebases, distribute analysis across concurrent read-only subagents:

- Each subagent focuses on one category.
- Subagent prompts must include reference paths, recon facts, and explicit instructions to return only evidenced findings without modifying files.

Effort levels (default `standard`; requested by users with keywords like `quick` or `deep`):

| Level      | Coverage                                | Subagents        | Findings                                      |
| ---------- | --------------------------------------- | ---------------- | --------------------------------------------- |
| `quick`    | Only critical spots identified in recon | 0 to 1           | Top 5 to 6, HIGH confidence only              |
| `standard` | Core modules and highest-risk surfaces  | Up to 4 parallel | Full findings table                           |
| `deep`     | Full repository scan                    | Up to 8 parallel | Full findings table including research spikes |

Always explicitly declare in the final report what was _not_ audited.

### Phase 3 — Validation, Prioritization, and Confirmation

**Validate before presenting — subagents produce false positives.**
For each finding entering the report, open the cited file and line yourself to confirm. Discard behaviors that are intentional by design or inaccurate line references.

Present validated findings sorted by leverage (impact / effort, weighted by confidence):

| #   | Finding | Category | Impact | Effort | Risk | Evidence (`file:line`) |
| --- | ------- | -------- | ------ | ------ | ---- | ---------------------- |

Present **product and direction suggestions separately**, below the primary table — these are strategic ideas for the maintainer to judge, not defects. Limit to 2 to 4 grounded suggestions with trade-offs.

Next, ask the user which findings they wish to convert into actionable plans (recommend the 3 to 5 highest-leverage items). Await their selection.

### Phase 4 — Handoff to Writing-Plans

Approved findings become the formal scope. Invoke the **writing-plans** skill to generate execution plan artifacts:

- Slice work into PR-sized plans.
- Establish verification gates with real commands.
- Define STOP conditions for unforeseen design forks.

Record evaluated and discarded findings in the "Discarded and Rationale" section of the effort index so they are not re-audited unnecessarily later.

## Invocation Variations

- Default (no extra flags) -> standard full workflow.
- `quick` / `deep` -> adjusts audit depth.
- Targeted focus (`security`, `perf`, `tests`, etc.) -> quick recon followed by exclusive audit of that domain.
- `branch` -> audits only the current branch changes relative to main.

## Agent Stance

You are advising technically, not pitching. State facts with sobriety, note uncertainties honestly, and prefer saying "not worth doing right now" over inflating the list with trivialities. A short list of high-leverage plans is worth far more than a bloated inventory of speculative suggestions.
