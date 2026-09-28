---
name: rust
description: >-
    Mindset shift for idiomatic Rust engineering ("Thinking in Rust").
    Use when writing or reviewing Rust code to move beyond "it compiles" toward idiomatic patterns: domain modeling with types and newtypes, eliminating illegal states, borrow checker and ownership without gratuitous clone(), structured error handling with thiserror/anyhow, traits vs enums, correct async/Tokio, justified unsafe with invariants, and clean API boundaries.
---

# Thinking in Rust

You already know Rust syntax. The objective of this skill is shifting your **immediate mental defaults** when modeling a domain, managing ownership, designing APIs, or crossing data boundaries.

The primary failure mode is writing code that compiles, but was conceived as Python, Java, TypeScript, or C: using raw `String` for domain entities; boolean flags to indicate phase; trait objects for closed sets; `Error(String)` for every failure; wildcard `_ =>` in all `match` blocks; index loops; sentinel values; getters and setters on all fields; knee-jerk `.clone()` to appease the compiler; and `unsafe` as a shortcut to bypass design constraints. Such code compiles, but it is conceptually fragile.

When reviewing Rust code, assess program structure first: which invariants are enforced by the type system, who owns each value, which states are unrepresentable, how errors cross boundaries, and whether shortcuts mask design flaws.

## The Rust Mental Model

### Model the Domain in Types

1. **Every domain string must be a Newtype:** Raw `String` erases meaning. The compiler cannot distinguish an email from a username or URL. Encapsulate it, validate at construction, and keep the inner field private. See [references/newtypes-and-domain-types.md](references/newtypes-and-domain-types.md).
2. **Boolean parameters lie — use Enums:** `true` and `false` communicate nothing at call sites and cannot accommodate a third state later. Replace boolean flags with named variants. See [references/bool-to-enum.md](references/bool-to-enum.md).
3. **Every unknown state must be explicit:** `Option<bool>` represents three states without clear names. Empty collections can mean "checked and empty" or "not yet checked". Model with named variants. See [references/option-bool-to-enum.md](references/option-bool-to-enum.md).
4. **Matches on owned enums must be exhaustive — avoid wildcards (`_ =>`):** Wildcard arms silence compiler warnings when new variants are added later. Match every variant explicitly. See [references/exhaustive-matching.md](references/exhaustive-matching.md).
5. **Errors are domain facts — never use `Error(String)`:** String errors destroy structure. Callers cannot branch, retry, or test them reliably. Libraries should expose typed enums using `thiserror`; applications add context with `anyhow`. See [error-handling.md](error-handling.md).
6. **Parse, don't validate:** Validation inspects data and discards the proof. Parsing inspects data and returns a refined type that guarantees the invariant indefinitely. See [references/parse-dont-validate.md](references/parse-dont-validate.md).
7. **Enums are the primary modeling tool:** A struct with a `kind` field and optional fields is an enum waiting to be born. See [references/enums-as-modeling-tool.md](references/enums-as-modeling-tool.md).
8. **Closed sets are Enums, not Trait Objects:** If all variants are known at compile time, use an enum (zero-cost static dispatch, exhaustive matching). Reserve `dyn Trait` only for genuinely open extension points. See [traits.md](traits.md).
9. **Boundaries translate; the core models:** Serde, FFI, CLI, HTTP, and database layers must convert DTOs into rich domain types before passing them inward. See [serde.md](serde.md) and [interop.md](interop.md).

### Express Ownership and API Intent

10. **Borrow by default (`&T`) — take ownership (`T`) only with intent:** Accept `&str`, `&[T]`, and `&Path` instead of allocated types unless you must store, transform, or consume them. See [references/borrow-by-default.md](references/borrow-by-default.md).
11. **Function signatures are ownership contracts:** Signatures should make it immediately clear who owns, borrows, mutates, and how long values persist (lifetimes). See [references/function-signatures.md](references/function-signatures.md).
12. **`clone()` is not an architectural tool:** Clone for genuine independent ownership, cross-thread message passing, or intentional duplicates. Do not call `.clone()` merely to silence error E0382. See [ownership.md](ownership.md).
13. **Restructure ownership before resorting to `Rc<RefCell<T>>`:** `RefCell` trades compile-time verification for runtime panics. Try splitting borrows, using read phases followed by write phases, or referencing entities via IDs. See [references/ownership-before-refcell.md](references/ownership-before-refcell.md).
14. **Async code is for I/O waits, not heavy CPU computation:** Never block the Tokio runtime thread pool. Use async I/O, `spawn_blocking` for short synchronous calls, and Rayon or dedicated threads for CPU-bound computation. See [async.md](async.md).
15. **Unsafe and Atomics require formal written justification:** Every `unsafe` block must include a `// SAFETY:` comment proving why invariants are upheld. Verify with Miri. See [atomics.md](atomics.md) and [unsafe.md](unsafe.md).

### Express Intent in Control Flow

16. **Iterators over indexed loops:** `for i in 0..v.len()` obscures intent and risks off-by-one errors. Use functional combinators: `.iter()`, `.enumerate()`, `.windows()`, `.zip()`. See [references/iterators-over-indexing.md](references/iterators-over-indexing.md).
17. **`Option<T>` over sentinel values:** Never use `-1`, `""`, or `0` to denote absence. The type system exists for this. See [references/option-over-sentinels.md](references/option-over-sentinels.md).
18. **Modules are namespaces, not empty `impl` blocks:** An empty struct holding static helper methods is an object-oriented holdover. Use free functions organized in modules. See [references/impl-namespace.md](references/impl-namespace.md).
19. **Public fields beat trivial getters and setters:** If any field value is valid, make it `pub`. If an invariant must be protected, create an accessor following Rust naming idioms: `item.name()`, not `item.get_name()`. See [references/getter-setter.md](references/getter-setter.md).

## Quick Code Review Checklist

1. **Domain data stored in raw primitives?** -> Convert to Newtype or Enum.
2. **Loose booleans or `Option<bool>`?** -> Create an explicit named enum.
3. **Wildcard `_ =>` on your own enum?** -> Make match exhaustive.
4. **Validation repeated across callers?** -> Parse at boundary once.
5. **Borrow checker circumvented with `.clone()` or `unsafe`?** -> Restructure ownership.
6. **Public function takes owned `String` but only reads?** -> Change to `&str`.
7. **Library returning generic string errors?** -> Define typed enum with `thiserror`.
8. **Async runtime blocked by synchronous work?** -> Offload to `spawn_blocking` or Rayon.
9. **Unrestricted public items leaking?** -> Narrow to `pub(crate)` and expose clean facade.

## Supporting Documents Index

- **[ownership.md](ownership.md)** — Resolving borrow checker errors, lifetimes, smart pointers, and cloning discipline.
- **[error-handling.md](error-handling.md)** — `thiserror` vs `anyhow`, structured patterns, and panic boundaries.
- **[traits.md](traits.md)** and **[type-design.md](type-design.md)** — Dynamic vs static dispatch, typestate, and newtypes.
- **[async.md](async.md)**, **[atomics.md](atomics.md)**, and **[unsafe.md](unsafe.md)** — Safe concurrency, memory ordering, and Miri invariants.
- **[serde.md](serde.md)**, **[interop.md](interop.md)**, and **[project-structure.md](project-structure.md)** — Boundary DTOs, FFI, and crate architecture.
