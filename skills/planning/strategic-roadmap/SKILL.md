---
name: strategic-roadmap
description: >-
    Use when the user asks "what should I work on in this repository?", "what is worth doing next?", requests a repository audit, technical debt priorities, architecture assessment, or strategic discovery of code-grounded opportunities.
    Generates a roadmap artifact sequenced into Now/Next/Later, discarded items with rationale, and recommended next artifacts. Not for standard commercial product roadmaps.
---

# Strategic Repository Roadmap (Strategic Roadmap)

Plan the work that is genuinely worth doing in a repository. This is a senior, audit-based judgment phase: mine project documentation, past plans, active branches, and code architecture; analyze opportunities across improvement categories; expand upon user-provided ideas; surface non-obvious improvements; discard low-value work; and sequence the highest-leverage initiatives.

Treat this as meta-engineering: prefer structural improvements that enhance future development cycles, automated verification, autonomy boundaries, and codebase health over disconnected spot fixes.

## Sources and References

Before producing the roadmap, leverage corresponding skills and references:

- `improve` for evidence-based auditing and "not worth doing now" verdicts.
- `coding-standards` as the canonical source for vocabulary and architectural idioms (deep modules, state boundaries, boundary parsing).
- Project documentation: `GEMINI.md`, `AGENTS.md`, `README.md`, ADRs, and open issues.

## Workflow

### 1. Define Scope and Repository Goals

- Identify the specific repository and existing artifacts.
- Clarify what "better" means for this project: end-user value, delivery velocity, test verification robustness, complexity reduction, or operational reliability.
- Include user-suggested ideas as starting points, not the exhaustive list.
- If primary goals are ambiguous, ask a brief alignment question before ranking items.

### 2. Non-Mutating Reconnaissance

- Read context and existing plans before judging.
- Identify test and build commands, active branches, and hot areas of recent Git churn.
- **Do not modify source code.** Produce only the roadmap artifact.
- If credentials or secrets are spotted, cite only path and line; never transcribe secret values.

### 3. Opportunity Audit

- Audit core categories: correctness/bugs, security, performance, tests, technical debt, migrations, tooling, and documentation.
- Identify decisions repeatedly re-debated by the team; propose stable policies or ADRs to settle them.
- Apply objective architectural criteria: where comprehension requires jumping across dozens of files, where interfaces are nearly as complex as their implementations, and where boundaries leak internal details.
- Do not propose final interfaces at this stage: capture friction, recommended direction, and the next planning artifact.

### 4. Validation and Sequencing

- Open cited code to verify each opportunity; never trust unverified tool outputs blindly.
- Order by **leverage**: expected impact divided by probable effort, weighted by technical confidence.
- Establish autonomy tiers: routine delegation to executors, design review, or direct human sign-off.
- Formally record discarded or deferred ideas to prevent them from being redundantly rediscovered in future audits.

### 5. Draft the Roadmap

- Create `.agents/ROADMAP.md` (or project equivalent) using the template in [references/roadmap-template.md](references/roadmap-template.md).
- Prefer **Now / Next / Later** sequencing over arbitrary dates.
- Every item must indicate its next planning artifact: `roadmap-to-improve-plans`, `feature-planning-artifacts`, `research spike`, `user decision`, or `discard`.

## Completion Criteria

The strategic roadmap is complete when any developer or future agent can pick the next work item without re-scanning the entire repository: top opportunities are ranked with evidence, discarded ideas are documented with rationale, and the next planning step is explicit.
