---
name: researching-codebases
description: >-
    Use when answering complex questions about a codebase that require exploring multiple modules or tracing flow across components.
    Coordinates parallel research subagents to locate, analyze, and synthesize technical findings with precise file and line references.
---

# Deep Codebase Research

Coordinate parallel subagents to investigate complex questions of architecture, data flow, and implementation across a codebase.

## When to Use

- Questions spanning multiple files, microservices, or packages.
- "How does feature X work internally?", requiring tracing calls end-to-end.
- Searching for patterns, idioms, or recurring conventions across the repository.
- Understanding entity lifecycles or architectural decisions.

## When NOT to Use

- Simple "where is file X?" queries — use direct search commands instead.
- Questions localized to a single file — read that file directly.
- Purely external or web lookups — consult web documentation directly.

## Workflow

### 0. Check Prior Research (Optional)

Before breaking down a broad research inquiry, check whether past investigations already exist:

1. Check for a `.research/` directory in the project or `~/.gemini/research/`.
2. If relevant past reports exist, leverage their findings rather than investigating from scratch.
3. Consult `research-tools.md` for note retrieval utilities.

### 1. Read Mentioned Files First

If the user mentions specific files or directories in the query, read those files completely before spawning subagents. This establishes the necessary vocabulary and scope to decompose the investigation.

### 2. Decompose the Inquiry

Break down the investigation into parallel, independent threads:

- Which architectural layers are involved (frontend, backend, database, API contracts)?
- Do we need call graph tracing, data-shape analysis, or test suite examples?
- Consult `agent-selection.md` to pick appropriate subagent specializations.

### 3. Launch Subagents in Parallel

Invoke concurrent subagents for independent investigation tracks (in Antigravity, use `invoke_subagent` with type `research` or equivalent).

**Wait for all tracks to return before composing the final synthesis.**

### 4. Synthesize and Answer

Combine findings into a structured, cohesive response:

- Direct, objective answer to the original question.
- Precise references in `path/to/file:line` format (or Markdown links).
- Clear diagrams or explanations showing connections between components.
- Open questions or identified edge-case limitations.

### 5. Save Technical Note (Optional)

For deep investigations with high future value to the team, offer:

> _"Would you like me to save this technical investigation into a research document (in `.research/`)?"_

For quick, targeted lookups, deliver the answer directly in chat without extra ceremony.

## Common Pitfalls to Avoid

- **Spawning subagents before reading initial context:** Always inspect user-provided files first.
- **Synthesizing prematurely:** Wait until all subagents have reported back.
- **Over-documenting simple queries:** Short answers do not require generated markdown artifacts.
- **Unnecessary sequential execution:** If research areas are independent, investigate them in parallel.
