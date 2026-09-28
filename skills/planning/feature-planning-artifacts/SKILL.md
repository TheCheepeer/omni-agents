---
name: feature-planning-artifacts
description: >-
    Use when creating or iterating staged planning artifacts for complex features: design discussions, structure outlines, final execution plans, or exploratory technical research.
    Slices work into executable vertical layers, establishes review gates with the user between stages, and derisks high-value items before code is written.
---

# Feature Planning Artifacts

Create or update structured, staged planning artifacts for requirements demanding prior research, architectural judgment, vertical slicing, and a verified plan before implementation.

This skill is **not** a throwaway, single-pass plan generator. It takes a scope, performs reconnaissance, drafts or updates the current-stage artifact, and **stops at the review gate**. Do not advance to the next stage until the current artifact is approved by the user or they explicitly request proceeding.

Treat planning as meta-engineering: each document makes future implementation safer by specifying success criteria, clarifying architectural decisions, and designing regression gates.

## Sources and References

Before producing or updating artifacts, consult:

- The selected roadmap item, opportunity card, or preliminary brief.
- Prior artifacts for this effort (design discussion, outline, or plan drafts).
- The `coding-standards` skill as the canonical source for vocabulary and code idioms.
- Project documents: `GEMINI.md`, `AGENTS.md`, `README.md`, ADRs, and current Git status.
- Canonical templates in [references/artifact-templates.md](references/artifact-templates.md).

## The Stage Contract

Always advance via the smallest stage that yields solid progress:

| Stage                    | When to Use                                               | Input                                     | Resulting Output                                           | Stop Gate                                          |
| ------------------------ | --------------------------------------------------------- | ----------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------- |
| **Research Questions**   | Broad uncertainty about how the system currently works    | User request or roadmap item              | Precise questions on current code behavior                 | Stop after questions; await approval to research   |
| **Technical Research**   | Raised questions must be answered by the code             | Research questions                        | Purely descriptive report of current code                  | Stop after research; recommend design discussion   |
| **Design Discussion**    | The feature requires architectural choices and trade-offs | Research or sufficient repository context | Options, recommendation, settled decisions, open questions | Stop for human review; DO NOT draft outline yet    |
| **Structure Outline**    | Design is approved or has a clear direction               | Accepted design discussion                | Vertical implementation slices                             | Stop for human review; DO NOT draft final plan yet |
| **Final Execution Plan** | Structure outline is approved                             | Accepted outline                          | Self-contained, safe execution plan for any executor       | Stop for execution handoff                         |

If the user simply says "plan this", begin with a **design discussion**, unless uncertainties are so extensive that research questions must come first. Never generate everything at once without pauses.

## File Structure and Destination

Colocate the artifact bundle in `.agents/plans/features/<feature-slug>/`:

```txt
.agents/plans/features/<feature-slug>/README.md
.agents/plans/features/<feature-slug>/001-design-discussion.md
.agents/plans/features/<feature-slug>/002-structure-outline.md
.agents/plans/features/<feature-slug>/003-plan.md
```

If descriptive research was required:

```txt
.agents/plans/features/<feature-slug>/001-research-questions.md
.agents/plans/features/<feature-slug>/002-research.md
.agents/plans/features/<feature-slug>/003-design-discussion.md
```

Create or update exactly **one primary artifact** per interaction, along with the bundle index `README.md`.

## Detailed Workflow by Stage

1. **Define the Current Stage:** Assess existing files. If a design discussion is under review, iterate on it rather than creating an outline. Define success criteria before writing.
2. **Technical Research:** Keep research strictly descriptive (current code behavior, data flows, tests, and constraints). No solution recommendations or opinions in this phase.
3. **Design Discussion:** Present current state, desired end state, explicit non-goals, evaluated alternatives, technical recommendation, and open questions. Set `status: in-review` and request user validation.
4. **Structure Outline:** Once design is accepted, slice implementation into vertical phases. List touched files, core signatures, and per-phase tests.
5. **Final Plan:** Derived from the accepted outline, draft an executor-ready plan with exact test commands, stop conditions, and autonomy boundaries.

## User Review Gates

Use clear, direct handoff prompts when concluding a stage:

- **After research questions:** _"These are the questions regarding current system behavior I will investigate next."_
- **After research:** _"Here is the descriptive mapping of existing code; solution recommendations will be detailed in the design discussion."_
- **After design discussion:** _"Please review the recommended approach, discarded options, and open questions before we outline implementation phases."_
- **After structure outline:** _"Please review the vertical delivery slices and phase-level tests before we generate the detailed execution plan."_
- **After final plan:** _"The plan is complete and ready for safe execution."_

## Completion Criteria

The planning bundle is complete when each document has fulfilled its role and cleared its validation gate, allowing the feature to be implemented without hidden questions or architectural friction.
