---
name: roadmap-to-improve-plans
description: >-
    Use when turning a roadmap, repository priorities, architecture, or selected opportunities into grouped batches of numbered improvement plans for future executors.
    Generates README.md indexes, NNN-*.md plan files, memos (memo-*.md), test verification gates, drift checks, STOP conditions, and handoff notes for executors.
---

# From Roadmap to Improvement Plans

Convert selected opportunities from a strategic roadmap into structured batches of numbered improvement plans. This is the detailed planning phase: preserve audit judgments and architectural diagnoses for each opportunity, detailing them to the precision necessary for future executors to act with complete safety.

Treat plan writing as meta-engineering: outputs must improve future execution cycles by conveying expected impact, risks, design hypotheses, regression checks, autonomy boundaries, and stop conditions.

## Sources and References

Before drafting plans, consult relevant materials:

- `.agents/ROADMAP.md` (or project equivalent).
- The `improve` skill to recover the original audit findings: category, evidence, impact, effort, risk, confidence, and solution sketch.
- The `coding-standards` skill to cite violated idioms and architectural guarantees.
- Project docs and commands: `GEMINI.md`, `AGENTS.md`, `README.md`, ADRs, build/test scripts, and CI pipelines.

## Workflow

### 1. Select Planning Scope

- Start from approved roadmap opportunities.
- Treat each effort directory as a cohesive improvement batch: one core theme, one clear outcome, one index `README.md`.
- Separate unrelated features or goals into distinct batches.
- Respect roadmap dependency order; do not turn everything into uncoordinated parallel tasks.

### 2. Reconcile with Current State

- Verify current repository status in version control (Git) so planning is not based on stale code.
- Reopen and validate code evidence cited in the roadmap.
- Identify exact build, linter, and test commands.
- Never copy keys or credentials into plans; reference only file and line.

### 3. Decompose into Numbered Plans (`NNN-*.md`)

- Each `NNN-*.md` plan must represent a PR-sized change, applicable independently or with explicit dependency on a prior plan.
- Prefer vertical functional slices over horizontal layer-by-layer rewrites.
- For architectural plans, state the diagnosis: current friction, deletion test, locality gain, and recommendation level.
- Do not pretend an open technical choice is ready for immediate coding. Route architectural uncertainties to research spikes or design memos.

### 4. Write Index and Plans

- Save in `.agents/plans/improvements/<effort-slug>/` (or project convention).
- Use [references/index-template.md](references/index-template.md) for `README.md`.
- Use [references/plan-template.md](references/plan-template.md) for each numbered plan.
- Use [references/memo-template.md](references/memo-template.md) to record decisions and design forks.

### 5. Define Autonomy Boundaries

- In the batch index, flag plans requiring special care or domain decisions before coding.
- For each plan, specify: what can be routinely executed by an agent, what requires design review, and what mandates direct human approval.

## Plan Requirements

Every numbered plan must be self-contained for an executor with no prior session history:

- Rationale, impact, and expected return.
- Current state evidence (`file:line`).
- Desired end state.
- In-scope and explicit out-of-scope boundaries.
- PR-sized implementation step sequence.
- Exact automated verification commands.
- Autonomy tier (routine execution, design review, or human approval).
- STOP conditions for incorrect assumptions or failing tests.
- Discarded approaches and why they were rejected.
- Delivery guidance for fresh execution sessions.

## Completion Criteria

The planning batch is complete when the index clarifies execution order and plan maturity, each numbered plan can be handed to a clean executor, and tasks with architectural uncertainty are flagged for prior review.
