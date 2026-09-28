---
name: diataxis
description: >-
    Structure, classify, and author technical documentation using the Diátaxis framework.
    Use when writing documentation, READMEs, how-to guides, tutorials, step-by-step manuals, API references, or organizing documentation architecture.
    Also used to audit, restructure, and untangle mixed content across tutorials, how-to guides, reference, and explanation.
---

# Diátaxis Framework for Technical Documentation

Apply the systematic Diátaxis methodology to structure and author clear, highly usable technical documentation.

## The Four Documentation Types

Diátaxis identifies exactly four categories, defined along two fundamental axes:

|                         | **Knowledge acquisition** (study) | **Practical application** (work) |
| ----------------------- | --------------------------------- | -------------------------------- |
| **Action** (doing)      | **Tutorial**                      | **How-to Guide**                 |
| **Cognition** (knowing) | **Explanation**                   | **Reference**                    |

### 1. Tutorials — Learning-Oriented

Write tutorials as guided practical lessons. Lead the learner by the hand through a structured experience where they acquire skills by doing.

- Use first-person plural ("We will install...", "Let's create...").
- Show where the user will arrive right from the start.
- Deliver visible results frequently and quickly.
- Minimize theoretical explanations — link to them instead.
- Stick to the concrete path and avoid forks or alternatives.
- Ensure total reliability (it must work flawlessly on the first try).

See `references/tutorials.md` for the complete guide.

### 2. How-to Guides — Goal-Oriented

Write how-to guides as recipes and direct instructions for an already competent user to solve a specific real-world problem.

- Use clear titles: "How to [achieve goal X]".
- Use conditional imperatives ("If you want X, run Y").
- Assume prior competence — do not teach fundamentals here.
- Omit unnecessary details: practical usability > encyclopedic completeness.
- Allow flexibility and note viable alternatives.

See `references/how-to-guides.md` for the complete guide.

### 3. Reference — Information-Oriented

Write reference documentation as austere technical descriptions of architecture and interfaces. It should be consulted on demand, not read linearly.

- Describe neutrally and precisely — no conversational or opinionated tone.
- Maintain consistent, standardized formatting across all entries.
- Mirror the software's actual structure (modules, functions, parameters).
- Provide code snippets to illustrate syntax, not to teach concepts.

See `references/reference.md` for the complete guide.

### 4. Explanation — Understanding-Oriented

Write explanations to deepen conceptual understanding. Answer the question: _"Can you explain how and why this works?"_

- Connect the topic to related areas and overall architecture.
- Provide historical context and motivation: why it was built this way.
- Talk _about_ the subject (title: "About mechanism X").
- Discuss architectural perspectives and design trade-offs.
- Maintain strict boundaries — do not mix in practical step-by-step installation steps.

See `references/explanation.md` for the complete guide.

## The Compass: Deciding When in Doubt

Ask two simple questions to categorize any piece of content:

1. **Action or Cognition?** Is the primary objective to _do_ something or to _understand_ something?
2. **Acquisition or Application?** Is the reader _learning_ for the first time or _working_ to solve an immediate problem?

The intersection of these answers determines the correct quadrant. Consult `references/compass.md` for detailed criteria.

## Day-to-Day Application

1. **Classify the content** using compass questions.
2. **Identify improper mixing** — is the text trying to teach while simultaneously solving an advanced operational problem?
3. **Separate mixed content** — strip theoretical paragraphs out of tutorials; move command steps out of pure references.
4. **Apply the chosen quadrant's principles**.
5. **Hyperlink between documents** rather than inlining alien blocks.

Never create empty folders or sections for each quadrant without real necessity. Let the structure emerge naturally from project needs.

## Common Mistakes

| Mistake                                       | Why It Fails                                                    | Correction                                                         |
| --------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------ |
| Tutorial explaining too much theory           | Explanation breaks the learner's practical momentum             | Move theory to an Explanation document and link to it              |
| How-to teaching basic commands                | Experienced users waste time reading obvious introductions      | Assume competence or separate into Tutorial + How-to               |
| Reference with opinions and design advice     | API consumers need raw facts, parameters, and signatures        | Move architectural guidance to an Explanation document             |
| Explanation mixed into Reference              | Dilutes both: reference becomes bloated, explanation incomplete | Split into distinct files                                          |
| "Getting Started" that is just a feature tour | No clear learning outcome or deliverable                        | Pick a concrete project for the user to build from start to finish |

## Critical Rules

- **Never mix the four types in the same text block.** Each type has its own distinct tone, purpose, and structure.
- **The reader's mental state matters.** Study vs. Work is the fundamental distinction. Tutorials and Explanations serve study mode; How-to Guides and References serve work mode.
- **Connect with links** instead of duplicating content across sections.

## Deep Dive by Module

Consult documents in `references/` as needed:

| Topic                                    | Supporting Document                                 |
| ---------------------------------------- | --------------------------------------------------- |
| Authoring tutorials                      | `references/tutorials.md`                           |
| Authoring how-to guides                  | `references/how-to-guides.md`                       |
| Authoring reference documentation        | `references/reference.md`                           |
| Authoring explanations and concepts      | `references/explanation.md`                         |
| Compass decision tool                    | `references/compass.md`                             |
| Difference between Tutorial and How-to   | `references/tutorials-how-to.md`                    |
| Difference between Reference and Explain | `references/reference-explanation.md`               |
| Foundations and 2D mapping               | `references/map.md` and `references/foundations.md` |
