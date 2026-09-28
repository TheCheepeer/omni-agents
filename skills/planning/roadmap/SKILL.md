---
name: roadmap
description: >-
    Build evidence-based product or software roadmaps from repository state, tickets, ideas, audits, or user goals.
    Prioritizes and sequences work into Now/Next/Later, milestones, dependencies, risks, and execution handoffs.
    Use when asked to create technical roadmaps, release plans, backlog prioritization, or turn ideation/audit outputs into a delivery sequence. Not for directly implementing code or writing PR-level plans.
---

# Product and Software Roadmap (Roadmap)

Transform goals, candidate ideas, tickets, audit findings, and design documents into a clear, strategic view of upcoming work.

A roadmap consists of: **Direction + Prioritization + Dependencies**. It indicates which capabilities, outcomes, or architectural tracks are likely next, why they matter, and what must happen before they become reality. It is not an unconstrained wish list, an arbitrary commitment of calendar dates, or an uncurated backlog dump.

Operate one level above the `writing-plans` skill: establish sequencing, delivery slices, validation gates, and responsibility handoffs; do not prescribe code implementation details here. If an item needs product definition, route to ideation/brainstorming. If technical questions remain open, conduct a technical discussion. If implementation is decided, hand off to `writing-plans`.

Never modify application source code. Write only roadmap artifacts.

## Workflow

### Phase 1 — Define Horizon and Audience

Identify the roadmap context:

- **Audience:** maintainer, product owner, implementation agents, engineering team, or leadership.
- **Time horizon:** Now / Next / Later by default; use versioned releases or dated milestones only when an actual delivery schedule exists.
- **Scope:** full repository, product domain, feature family, technical debt, release, or migration.
- **Format:** direct chat response or persisted file artifact.

### Phase 2 — Reconnaissance (Recon)

Gather source material before prioritizing:

- Read project documents: `README.md`, `GEMINI.md`, `AGENTS.md`, ADRs, open issues, and prior roadmaps.
- If the roadmap derives from the `improve` skill, read approved findings and dependency notes.
- If no prior list exists, perform lightweight read-only recon: recurring TODO/FIXME patterns, half-finished features, unmet documented promises, and hot areas of recent Git churn.
- Never invent generic items lacking concrete evidence in code or user goals.

### Phase 3 — Standardize Candidates

Normalize each opportunity into a consistent schema:

| Field       | Meaning                                                                |
| ----------- | ---------------------------------------------------------------------- |
| Type        | Feature, milestone, technical track, spike/research, migration, choice |
| Outcome     | What becomes true for users, team, or system architecture              |
| Evidence    | Cited file:line, issue, audit finding, or user goal                    |
| First slice | Smallest cohesive, functional increment worth delivering first         |
| Dependency  | What must be finished first for this item to be safe and useful        |
| Risk        | Delivery, technical, product, or migration risk                        |
| Confidence  | HIGH / MEDIUM / LOW based on strength of evidence                      |
| Next step   | Technical discussion, refinement, spike, or plan (`writing-plans`)     |

Eliminate duplicates. Split oversized items. Reject generic suggestions that could apply to any random project.

### Phase 4 — Prioritize and Sequence

Order by **real leverage**:

1. Work that unblocks or derisks future deliveries.
2. High-impact, low-effort items backed by solid evidence.
3. Research spikes that eliminate major architectural uncertainties before commitment.
4. Risky or complex items only after prerequisites and test gates exist.

Use **Now / Next / Later / Not now**. Dates without historical capacity metrics are false precision.

### Phase 5 — Draft and Update Artifact

For persisted artifacts, resolve the destination in this order:

1. User-specified path.
2. Existing project convention.
3. `./ROADMAP.md` at project root (primary default).
4. `./docs/roadmaps/<slug>.md`.

Use the template in `assets/roadmap-template.md`. If the file already exists, update it while preserving history and marking superseded items rather than silently deleting context.

## Common Mistakes

| Mistake                                  | Correction                                                                  |
| ---------------------------------------- | --------------------------------------------------------------------------- |
| Treating the roadmap as a backlog dump   | Cut aggressively; keep high-level work and explicitly record deferred items |
| Inventing fictitious dates               | Use Now/Next/Later unless a real-capacity schedule is established           |
| Letting vague ideas through              | Require concrete evidence in the repository, issues, or user goals          |
| Prescribing detailed code implementation | Stop at sequencing and hand off to `writing-plans`                          |
| Hiding technical uncertainties           | Record confidence level and make open questions explicit                    |

## Quality Checklist

Before concluding:

- Target audience, horizon, and scope are clearly identified.
- Every item in "Now" has evidence and an explicit next action.
- Dependencies explain why this sequence was selected.
- The "Not now" section records discarded or deferred items with one-line justifications.
