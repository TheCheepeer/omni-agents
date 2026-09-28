---
name: writing-plans
description: >-
    Write self-contained implementation plan files that an independent executor (even another model or fresh session) can execute without prior author context.
    Divides work into PR-sized plans with verification gates (tests/lint), STOP conditions, and a memo protocol for design forks.
    Use when asked to write or create plans, turn specs/tickets into execution plans, or when another skill hands off planning. Not for arbitrarily deciding what to build or executing code directly.
---

# Writing Implementation Plans

You are writing plans for an executor who has not seen this conversation, did not follow the prior codebase exploration, and does not know sibling plans — potentially even a smaller model or a fresh session. Always write with this executor in mind: session context is lost on restart, and a detailed plan costs only a brief read, whereas an ambiguous plan halts or derails execution.

Plans are **intent-based: outcomes over rigid prescriptions**. Specify what must be true when finished, pinpoint exact files and symbols, reference exemplary existing files in the project to emulate, and provide an explicit verification command for each step. Give the executor goal clarity and the technical latitude to implement the cleanest solution.

This skill begins when the _scope_ ("the what") has already been decided at least in broad strokes — a user request, an issue, an RFC, or an agreed design. It does not handle initial brainstorming or unilateral feature invention. If a decision is missing from the plan, research the codebase first; only questions that cannot be resolved from code should be asked of the user — one at a time, with your clear recommendation.

During planning, write only to the designated plans directory. Do not modify application source code while planning.

## Where Plans Should Be Saved

Resolve the destination in this order of precedence (use the first match):

1. Explicit project convention — an existing plans directory or path specified in `GEMINI.md` or `AGENTS.md`.
2. `$AGENTS_PLANS_DIR` environment variable, if set.
3. `./docs/plans/`, if `./docs/` exists.
4. `./plans/` (create the directory if missing).
5. If not clearly inside a project, ask the user.

## Prior Reconnaissance (Recon)

Before drafting any plan, uncover what every plan needs to contain:

- **Exact build, test, lint, and typecheck commands** — verified in actual repository configuration (`package.json`, `justfile`, `Makefile`, `noxfile`, CI), not guessed. These form the verification gates for each step.
- **Conventions and exemplar files** — error handling, naming, test structure, with at least one concrete example file for each pattern the executor must follow.
- **VCS in use and current revision.** Record the base revision/commit and a drift check command (diff of affected paths) in the plan.

If the repository lacks working verification commands, call that out — establishing a verification baseline may need to be plan #1.

## Work Decomposition

**One plan = one independent, reviewable change** — roughly the size of a cohesive Pull Request, leaving the codebase green and tests passing upon completion. If the task is larger, break it into multiple numbered plans with explicit dependencies (scaffolding/preparatory plans that lay ground before the main change).

You decide how to slice the work into deliverable units; you do not unilaterally invent new scope.

## File Structure

Scale the structure to the scope of effort:

- **Single plan**: a single file at `<destination>/<plan-slug>.md`. No index or numbering.
- **Multiple plans**: dedicated subdirectory — `<destination>/<effort-slug>/NNN-<step-slug>.md` with a `README.md` serving as the index. Numbering is sequential, monotonic, and never renumbered; execution order belongs in the index.
- Memos sit alongside plans as `memo-<slug>.md`.

## Drafting

Consult [references/plan-template.md](references/plan-template.md) before writing the first plan. For multi-plan efforts, write the index last using [references/index-template.md](references/index-template.md).

Code in plans: **sketches and signatures over full implementations**. Pseudocode, function signatures, types, and interfaces communicate intent without pretending to be runtime-tested. Overly verbose prose code rots quickly and encourages copy-paste bugs. Provide full code only when there is a strict, unavoidable constraint, citing the `file:line` pointer.

## Memo Protocol: Decisions During Execution

Plans encountering unexpected design forks during execution trigger the memo protocol:

- **Executor's part**: embedded in each plan (the STOP conditions). Upon hitting an unforeseen architectural decision, the executor pauses and records current state, objective, and open questions.
- **Your part**: upon receiving the question, investigate the codebase, draft a `memo-<slug>.md` alongside the plans using [references/memo-template.md](references/memo-template.md) — verdict first, `file:line` evidence, discarded alternatives — and update or create affected plans, updating the index.

## Reconciling Existing Plans

Before writing, inspect the destination directory. If plans already exist for this effort, reconcile rather than duplicate: amend existing plans if additive, mark superseded plans in the index, and sequence new work monotonically.
