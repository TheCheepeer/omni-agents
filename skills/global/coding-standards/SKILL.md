---
name: coding-standards
description: >-
    Use when reviewing code quality, evaluating whether a refactoring or design is sound, identifying code smells, or judging architectural trade-offs.
    Identifies shallow interfaces, invalid state models, fuzzy boundaries, hidden side effects, weak error contracts, mock-heavy tests, premature abstractions, and seemingly clean code masking poor mental models.
---

# Coding Standards and Architectural Guidelines

> "Programs must be written for people to read, and only incidentally for machines to execute."  
> — Abelson and Sussman, _Structure and Interpretation of Computer Programs_

> "The purpose of abstracting is not to be vague, but to create a new semantic level in which one can be absolutely precise."  
> — Edsger W. Dijkstra, _The Humble Programmer_

Good code solves a real problem through a model that humans can understand, use, change, and fix. It expresses truth at the right granularity: named concepts where they matter, explicit valid states, well-translated boundaries, visible consequences, classified failures, verified behavior, and deleted unnecessary scaffolding.

Incorporate sound conceptual patterns without empty ceremony: make illegal states unrepresentable (inspired by strongly typed languages like Rust); build deep domain modules; establish anti-corruption layers at integrations. Translate these principles using the idiomatic, native features of the project's language.

## Core Principles

- **Code communicates a mental model.** Names, types, modules, tests, and interfaces must reveal what is true in the business domain and what must never happen.
- **Represent meaning at the right granularity.** Make critical distinctions explicit; do not elevate every raw primitive, parser nuance, or database column into domain vocabulary.
- **Make valid states and transitions explicit.** Prefer tagged unions, enums, or explicit state machines over blind boolean flags, loose nullable fields, and implicit temporal ordering.
- **Build deep modules.** Encapsulate cohesive behaviors behind simple interfaces at real boundaries. A shallow wrapper that merely forwards calls just gives another name to the same work.
- **Parse at boundaries.** External data, persisted database records, API payloads, and framework objects must be validated and converted (parse, don't validate) into the internal domain model before reaching core business logic.
- **Make consequences and side effects visible.** I/O, mutability, time, network requests, asynchronous execution, retries, and resource consumption must be evident where they affect reasoning.
- **Treat errors as an integral part of design.** Expected domain failures belong in interface contracts; programming bugs and infrastructure crashes require separate diagnostic and recovery paths.
- **Verify real behavior.** Tests must prove behavior, invariants, state transitions, and failure modes across observable boundaries, rather than orchestrating fragile internal mock choreographies.
- **Delete whatever carries no meaning.** Eliminate speculative generalizations, labyrinths of indirection, obsolete layers, and test-only scaffolding that protects no real contract.

## Critical Non-Negotiable Violations

Unless there is a documented physical or environmental constraint, treat as a design failure:

- Raw, unvalidated external data flowing directly into core business logic.
- Illegal or impossible domain states representable as normal runtime values.
- Private parsing, persistence, or infrastructure details leaking into the public API vocabulary.
- Intermediary layers that merely pass calls through without adding value (pass-through wrappers disguised as "architecture").
- Severe side effects or expected business failures hidden from the caller.
- Tests that verify only mock arrangement and call counts rather than observable outcomes.

## Common Fallacies to Reject

- **"The data was already validated earlier":** Parse at the boundary and pass the refined type inward. Prevent internal functions from ever being invokable with invalid formats.
- **"This is just the database/API schema format":** Boundary shapes belong at the edge; never let them contaminate the domain model unnecessarily.
- **"Legacy code throws unhandled exceptions, so I did too":** Maintain external compatibility where mandatory, but isolate internal new logic by differentiating expected failures from unexpected panics.
- **"This interface gives us future flexibility":** An abstraction is justified only when there is real behavioral variation, a boundary translation, or a legitimate test substitution need.
- **"Mocks isolate the unit of code":** Excessive mocks isolate the wrong things and break on the most harmless refactoring. Focus on observable inputs and outputs.
- **"A linter/type suppression comment solves it":** Suppressions require strict justification and a demonstrated safety invariant.

## How to Conduct a Review

1. **Understand local context.** Respect established conventions when they communicate the model well; challenge them deliberately when they perpetuate a flawed model.
2. **Classify the concern:** domain model, state, modularity, boundaries, side effects, error handling, verification, or complexity.
3. **Identify the burden on the caller or future maintainer.**
4. **Propose the smallest honest change.** Do not oversimplify by ignoring requirements; do not hyper-model to the point of obscuring intent.
5. **Verify behavior with reliable tests.**
6. **Remove obsolete scaffolding.**

A review finding is only valid if it points to a concrete code location, demonstrates real impact on maintainability, cites the violated principle, and offers the smallest viable solution.

## Deep Dive Reference Map

For detailed analysis, consult only the relevant documents in `references/`:

| Topic                                                | Supporting Document                                              |
| ---------------------------------------------------- | ---------------------------------------------------------------- |
| Shared vocabulary and terms                          | [`references/vocabulary.md`](references/vocabulary.md)           |
| Domain modeling and granularity                      | [`references/domain-modeling.md`](references/domain-modeling.md) |
| Flags, nullable fields, invalid states, and machines | [`references/state.md`](references/state.md)                     |
| Deep modules, boundaries, and cohesion               | [`references/modules.md`](references/modules.md)                 |
| API/DB boundaries, parsing, DTOs, and validation     | [`references/boundaries.md`](references/boundaries.md)           |
| Side effects, mutations, async, and idempotency      | [`references/effects.md`](references/effects.md)                 |
| Expected errors vs bugs and diagnostics              | [`references/error-handling.md`](references/error-handling.md)   |
| Behavioral testing vs fragile mocks                  | [`references/verification.md`](references/verification.md)       |
| Accidental complexity and premature indirections     | [`references/complexity.md`](references/complexity.md)           |
| Maintainability, safe refactoring, and compatibility | [`references/maintainability.md`](references/maintainability.md) |
