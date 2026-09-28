---
name: reducing-entropy
description: >-
    Use when evaluating architectures, reviewing code, or planning refactorings — measures success by total code volume in the end state rather than immediate typing effort.
    Deliberately prioritizes deleting unnecessary code and fights entropy buildup.
---

# Reducing Entropy

More code attracts more code. Entropy accumulates. This skill directs the agent to pursue the smallest viable codebase.

**Central question:** _"What will the codebase look like AFTER this change?"_

## Before Starting

**Load at least one mindset from `references/`:**

1. List the files in the skill's `references/` directory.
2. Read the initial summary to determine which applies best to your context.
3. Load at least one mindset.
4. State briefly which mindset was consulted and its core principle.

## The Real Goal

The goal is **less total code in the final codebase** — not fewer keystrokes in the immediate moment.

- Writing 50 lines to enable deleting 200 lines = clear net win.
- Keeping 14 obsolete functions just to avoid rewriting 2 simple callers = net loss.
- "Avoiding rework at all costs" is not the goal. The goal is a smaller, leaner codebase.

**Evaluate the resulting end state, not the immediate effort of the diff.**

## The Three Essential Questions

### 1. What is the smallest codebase that solves this problem?

Do not ask merely "what is the smallest diff", but "what is the smallest resulting structure".

- Could this be solved with 2 functions instead of 14?
- Could this have 0 functions (deleting the feature if it is unused)?
- What can we delete once this is implemented?

### 2. Does the proposed change result in less total code?

Evaluate the net balance of lines and complexity before and after:

- "Better organized", but with significantly more code = increased entropy.
- "More flexible", but doubling the number of files = increased entropy.
- "Cleaner separation", but with 5 interfaces for 1 implementation = increased entropy.

### 3. What can we delete right now?

Every modification is an opportunity to eliminate dead or superseded code. Ask:

- What does this new implementation render obsolete?
- Which functions existed only to support the solution we are replacing?
- What is the maximum amount of code we can safely eradicate?

## Red Flags

- **"Better leave existing code untouched so we don't break things":** Status quo bias. The question is how much code you must maintain tomorrow, not fear of refactoring today.
- **"This adds flexibility for the future":** Flexibility for what? YAGNI (You Aren't Gonna Need It).
- **"Better separation of concerns":** More files and layers of indirection carry high cognitive overhead. Separation is not free.
- **"Easier to understand":** 14 moving parts are rarely easier to understand than 2 direct functions.

## When This Rule Does Not Apply

- The codebase is already strictly minimal for its purpose.
- The project follows strict idioms of an established framework (do not fight the framework).
- Legal, compliance, or regulatory requirements mandate specific audit structures.

---

**Prioritize deletion. Always measure the end state.**
