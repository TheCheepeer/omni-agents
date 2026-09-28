---
name: salsa
description: >-
    Mental model and architectural guide for Salsa, the incremental computation framework for Rust.
    Use when building or reviewing Salsa databases, tracked functions, input/tracked/interned structs, query pipelines, diagnostic accumulators, LSP cancellation support, red-green algorithms, and reactive on-demand compiler computation.
---

# Salsa: Incremental Computation in Rust

Salsa is a framework for **on-demand incremental recomputation** in Rust. You define pure inputs and pure functions over those inputs. Salsa memoizes the result of every call. When an input changes, it re-executes only the functions whose dependencies actually changed — reusing the rest of the memoized dependency graph.

Salsa powers [rust-analyzer](https://rust-analyzer.github.io/) (the official Rust LSP language server), [ty/Ruff](https://docs.astral.sh/ty/), and [Cairo](https://github.com/starkware-libs/cairo), delivering sub-millisecond query responses across massive codebases after small text edits.

## The Mental Model

```text
                    Salsa Database
                    ┌──────────────────────────────────────────────┐
 External world     │                                              │
 (editor, CLI,      │  Inputs ────→ Tracked Functions ────→ Output │
  filesystem)       │    │                 │                       │
        │           │    └──── memoized ───┘                       │
        │           │    dependencies tracked automatically        │
        ▼           └──────────────────────────────────────────────┘
 Mutate input                               │
 (new revision)                             ▼
                        Re-executes ONLY what changed
```

The core cycle:

```rust
let mut db = MyDatabase::default();

// 1. Create inputs
let file = SourceFile::new(&db, "fn main() {}".into(), path);

// 2. Compute (Salsa memoizes outputs and dependencies)
let result = analyze(&db, file);

// 3. Mutate an input (increments the database revision)
file.set_text(&mut db).to("fn main() { 42 }".into());

// 4. Recompute — Salsa reuses stable nodes
let result = analyze(&db, file); // Only reruns what depended on the text
```

## Core Concepts

### The Database (`#[salsa::db]`)

The central struct storing all intermediate caches, revisions, and state. It is the single source of truth — every Salsa query receives `&db` or `&mut db`.

### Inputs (`#[salsa::input]`)

External data feeding the computational graph (files read from disk, build flags). Inputs are the only nodes that accept direct external mutation.

```rust
#[salsa::input]
pub struct SourceFile {
    #[returns(ref)]
    pub text: String,
    pub path: PathBuf,
}
```

### Tracked Functions (`#[salsa::tracked]`)

Pure functions whose outputs are memoized in the database. Salsa automatically tracks which input fields and intermediate structs were accessed. On re-execution, it checks whether any dependency changed before recalculating.

### Tracked Structs (`#[salsa::tracked] struct`)

Intermediate entities allocated inside tracked functions (e.g. AST nodes, symbol definitions). They feature field-level change tracking and carry a `'db` lifetime.

### Interned Structs (`#[salsa::interned]`)

Deduplicated data mapped to compact numeric IDs (e.g. identifiers, path segments, type keys). Enables fast equality comparisons and hash lookups.

### Accumulators (`#[salsa::accumulator]`)

Side-channel structures for emitting diagnostics, lints, and compiler warnings from tracked functions without changing function return types.

### Red-Green Algorithm and Backdating

Every input mutation increments the database **revision**. When a tracked query is requested, Salsa evaluates upstream dependencies: if a recalculated intermediate result is identical to its previous value (**backdating**), change propagation terminates, saving compute time for downstream callers.

## Deep-Dive References

| Objective                                      | Supporting Document                                  |
| ---------------------------------------------- | ---------------------------------------------------- |
| Choosing between input, tracked, and interned  | [struct-selection.md](struct-selection.md)           |
| Designing query graphs and tracked functions   | [query-pipeline.md](query-pipeline.md)               |
| Database architecture and layered traits       | [database-architecture.md](database-architecture.md) |
| Handling cyclic / recursive queries            | [cycle-handling.md](cycle-handling.md)               |
| Cancellation support in LSP servers            | [cancellation.md](cancellation.md)                   |
| Fine-tuning cache reuse with durability levels | [durability.md](durability.md)                       |
| Testing incremental recomputation              | [incremental-testing.md](incremental-testing.md)     |
| Language Server Protocol integration           | [lsp-integration.md](lsp-integration.md)             |
| Production-grade compiler patterns             | [production-patterns.md](production-patterns.md)     |
