---
name: improving-prompts
description: >-
    Use when optimizing GEMINI.md, AGENTS.md, system prompts, custom slash commands, or skill files.
    Diagnoses concrete behavioral failures first and applies documented prompt engineering best practices (explicit instructions, context/motivation, verbosity constraints, formatted examples, and compact length) rather than making cosmetic changes.
---

# Improving Prompts

## Overview

Apply documented prompt engineering best practices to existing instruction files. Do not invent cosmetic "improvements" — identify the concrete behavioral defect first and apply the appropriate remedy.

## When to Use

- Optimizing `GEMINI.md` or `AGENTS.md` files.
- Refining instructions in skills and custom commands.
- Correcting prompts that the model ignores or disobeys.
- Trimming rules that are excessively long or bloated.

## When NOT to Use

- Writing brand new prompts from scratch (apply best practices directly).
- The current prompt works reliably and the user reported no failure.

## The Core Problem

Without this skill, agents tend to:

- Invent generic, unverified "best practices" from the internet.
- Restructure prompts without knowing what behavior was actually broken.
- Add complexity assuming "more words = better instruction".
- Mutate instructions to demonstrate activity rather than solving an observed defect.

## Catch Yourself Thinking:

| Thought                                             | Reality                                                                      |
| --------------------------------------------------- | ---------------------------------------------------------------------------- |
| "It feels vague / non-standard / inconsistent"      | Not actionable. What specific behavior failed?                               |
| "I know enough / I will assume what the user wants" | If you cannot point to a concrete failure, you do not know. Ask.             |
| "I am the expert / I would write it differently"    | Stylistic preference does not replace a functional defect. You are not user. |
| "More structure is always better"                   | Structure solves structural issues, not all problems.                        |
| "This is obviously an improvement"                  | What is obvious to you may disrupt the user's workflow.                      |

## Mandatory Process

### Step 1: Understand Before Changing

Before ANY modification:

1. Ask what specific behavior fell short of expectations.
2. Ask what the prompt was supposed to achieve that it currently fails to deliver.
3. If the user asks for a general improvement, request at least one concrete failure example.

**What qualifies as a concrete failure:**

- "The model ignores my instruction to be concise" [x]
- "The model only suggests diffs instead of editing the files directly" [x]

### Step 2: Apply Proven Principles

- **Be explicit about scope:** Modern models follow instructions literally. State whether a rule applies to all files or only to specific cases.
- **Explain the WHY (Motivation):** Explaining the reason behind a rule helps the model generalize correctly. Instead of "NEVER use ellipses", use: "Do not use ellipses because the text-to-speech engine fails to pronounce them".
- **Curate few-shot examples carefully:** Models emulate formatting and quirks. Provide 2 to 3 examples strictly aligned with the target behavior.
- **Constrain verbosity explicitly:** State whether responses should be concise, direct, or detailed with rationales.
- **Moderate aggressive phrasing:** Avoid plastering "CRITICAL: YOU MUST AT ALL COSTS" everywhere. Models overfocus and ignore surrounding context when flooded with panicked language. Prefer: "Use X when Y".

### Step 3: Preserve What Already Works

- DO NOT restructure sections that exhibit no failure.
- DO NOT add complexity unless it directly resolves a reported issue.
- Retain existing user examples if they demonstrate valid behavior.

### Step 4: Propose Changes with Rationale

For each change, declare:

1. Which best practice was applied.
2. What concrete problem it resolves.
3. The before-and-after comparison.

## Quick Reference: Problem -> Solution

| Observed Defect                              | Recommended Fix                                                                    |
| -------------------------------------------- | ---------------------------------------------------------------------------------- |
| Overly narrow response / fails to generalize | State scope explicitly ("apply across all files", "in all instances")              |
| Agent fails to explain reasoning             | Explicitly prompt to state reasoning prior to the final answer                     |
| Agent is excessively verbose                 | Instruct: "Be concise" or "Respond in at most 3 sentences"                         |
| Agent suggests diffs without applying them   | Replace "You can suggest..." with imperative "Apply changes directly to the files" |
| A specific rule is routinely ignored         | Add motivation (explain WHY the rule is critical)                                  |
| Rules file is bloated (>200 lines)           | Remove redundant rules that the model follows naturally via common sense           |
