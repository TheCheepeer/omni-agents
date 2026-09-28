---
name: jj
description: >-
    Jujutsu (jj) — the modern Git-compatible version control system.
    Activate ONLY when a .jj/ directory is present in the project or when jj/jujutsu is explicitly mentioned by the user. DO NOT activate in plain Git repos without .jj/.
    Use for any VCS operation in jj-managed projects: commit, push, pull, branch, bookmark, rebase, squash, merge, diff, log, status, working copy, Change ID, revsets, and workspaces.
compatibility: "Requires a Jujutsu-managed repository (.jj/ present in project root)"
metadata:
    version: "1.0.0"
    requires-path: ".jj/"
---

# Version Control with Jujutsu (jj)

Jujutsu is a modern, Git-compatible version control system featuring first-class mutable history, automatic file tracking, and an operation log that makes every action reversible.

**Target version: jj 0.36+**

## Jujutsu Mental Model

1. **The working copy is already a commit (`@`).** There is no staging index (`git add`). File edits on disk are automatically tracked in the working copy commit (`@`) upon running any `jj` command.
2. **Change IDs are stable; Commit IDs change.** Every commit has two identifiers:
    - **Change ID:** remains stable across rebases, squashes, and history rewrites (rendered as lowercase letters k-z, e.g. `tqpwlqmp`). **Always prefer using Change IDs.**
    - **Commit ID:** SHA content hash (changes on rewrite, identical to a Git commit hash).
3. **History is inherently mutable.** Commits can be rewritten freely; child commits rebase automatically. Past states are preserved in the operation log (`jj op log`).
4. **Bookmarks are not Git branches.** Bookmarks do not automatically move forward as you create new commits. They track rewrites, but must be explicitly advanced before pushing.
5. **Conflicts do not halt work.** Jujutsu records merge conflicts directly in commits. You can resolve conflict markers whenever convenient without blocking unrelated work.

## Mandatory Rules for Automated Agents

1. **Always provide `-m` for messages.** Never invoke commands that open a terminal editor (`nano`, `vim`). Commands requiring `-m`: `jj new -m "..."`, `jj describe -m "..."`, `jj commit -m "..."`, `jj squash -m "..."`.
2. **Avoid interactive subcommands.** Commands like bare `jj split` or `jj squash -i` block execution. Always specify explicit file paths.
3. **Verify state after mutations.** Run `jj st` after any `squash`, `rebase`, `abandon`, or `restore` operation.
4. **Single-quote revset expressions:** Always quote revsets: `jj log -r 'mine() & ::@'`.

## Daily Workflow

The development loop: **describe -> code -> new commit -> repeat.**

```bash
jj describe -m "feat: add user validation"
# edit files normally — tracked automatically without git add
jj st && jj diff
jj new -m "feat: add error handling"
```

### Organizing and Cleaning History

```bash
jj squash -m "feat: clean combined commit"  # squashes working copy into parent
jj absorb                                   # automatically routes hunks to ancestors
jj abandon @                               # discards a failed experiment
```

### Pushing Changes to Remote (GitHub/GitLab)

```bash
jj bookmark set my-feature -r @
jj git push -b my-feature
```

## Essential Commands

| Action                        | Jujutsu Command                                                  |
| ----------------------------- | ---------------------------------------------------------------- |
| Check status                  | `jj st`                                                          |
| View diff / log               | `jj diff` / `jj log`                                             |
| Describe current commit       | `jj describe -m "message"`                                       |
| Start new commit              | `jj new -m "task description"`                                   |
| Edit an existing commit       | `jj edit <change-id>`                                            |
| Squash into parent            | `jj squash`                                                      |
| Distribute changes to parents | `jj absorb`                                                      |
| Discard commit                | `jj abandon <change-id>`                                         |
| Undo last operation           | `jj undo`                                                        |
| View operation log            | `jj op log`                                                      |
| Restore prior operation state | `jj op restore <op-id>`                                          |
| Create / move bookmark        | `jj bookmark create <name> -r @` / `jj bookmark set <name> -r @` |
| Sync with remote              | `jj git push -b <bookmark>` / `jj git fetch`                     |

## How to Undo Operations

```bash
jj undo                      # undoes the most recent operation
jj op log                    # lists recent operations with IDs
jj op restore <op-id>        # restores repo to the exact state at that op-id
jj evolog -r <change-id>     # displays the evolution history of a specific change
```

## Repository Identification

- `.jj/` present = Jujutsu repository.
- Both `.jj/` and `.git/` present = colocated repository. Always use `jj` commands. Git's "detached HEAD" warning in colocated repositories is normal; actual state is reflected by `jj log`.

## Supporting Documents

- [references/git-to-jj.md](references/git-to-jj.md) — Git-to-Jujutsu command translation dictionary.
- [references/bookmarks.md](references/bookmarks.md) — Complete guide to bookmarks and GitHub integration.
- [references/conflicts.md](references/conflicts.md) — Resolving merge conflicts in Jujutsu.
- [references/revsets.md](references/revsets.md) — Query language and filters (revsets).
