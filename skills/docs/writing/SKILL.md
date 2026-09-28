---
name: writing
description: >-
    Prose and writing guidelines for human-facing technical communication — clear, concrete, and free from prefabricated AI clichés.
    Use when writing or editing documentation, explanations, summaries, commit messages, reports, or any expository prose.
---

# Writing and Prose Style (Writing)

In 1946, George Orwell described bad prose: it "consists less and less of _words_ chosen for the sake of their meaning, and more and more of _phrases_ tacked together like the sections of a prefabricated henhouse." He was describing human writers who let prefabricated phrases do their thinking. In the LLM era, this phenomenon has been industrialized. Every vice cataloged in this skill — rhetorical inflation, false parallelism, bullet points mechanically bolding the first two words — stems from the same failure: reaching for the easiest available phrase instead of selecting the words that capture exact meaning. Canned phrases think for you and obscure meaning from reader and writer alike.

The remedy is also Orwell's: **let the meaning choose the word, never the other way around.** Know what you want to say before writing, and find the words that say precisely that. If a sentence comes prepackaged and cliché, rewrite it.

## The Method

Ask yourself with every sentence:

1. What am I trying to say?
2. What words will express it best?
3. What image, example, or term makes it clearer?
4. Is this formulation fresh and precise?

And then: Could it be said more directly? Is there any unnecessary word?

## The Rules

1. **Never use a worn-out metaphor, simile, or idiom.** Especially classic LLM tropes: "tapestry", "complex ecosystem", "dive deep", "game changer", "testament to". An overused phrase loses imagistic power and becomes empty filler.
2. **Never use a long word where a short one will do.** Use "use" instead of "utilize" or "leverage". "Inspect" instead of "dive into". "Is" instead of "serves as" or "stands as a testament to".
3. **If it is possible to cut a word out, always cut it.** A sentence should contain no unnecessary words, for the same reason a drawing should have no unnecessary lines and a machine no unnecessary parts. Instead of "due to the fact that", write "since" or "because". Instead of "it is worth noting that X", simply state "X".
4. **Never use the passive where you can use the active.** "The plan was reviewed by the team" obscures the actor and weakens the sentence. Prefer: "The team reviewed the plan."
5. **Never use foreign phrases or jargon if you can think of an everyday English equivalent.** Note: a technical term with precise computational meaning (such as "idempotent", "thread-safe", "pipeline") is not jargon; retaining it is necessary for precision. Jargon is imprecision posing as sophistication.
6. **State things positively.** Say what something is, not merely what it is not. "Did not remember" is "forgot". "Did not trust" is "distrusted".
7. **Use precise, specific, and concrete language.** The substitution test: if a sentence could appear verbatim in the README or PR of any other project, it says nothing about yours — rewrite it or delete it.
8. **One paragraph per core idea, introduced by its topic sentence.** Keep parallel concepts in parallel grammatical structures.
9. **Place emphatic words at the end of the sentence.** The end of the clause is what echoes in the reader's mind; do not waste that terminal spot with weak qualifiers.
10. **Break any of these rules sooner than say anything outright barbarous.**

## Write for the Reader

Two questions govern all prose: what the reader already knows, and what they came looking for.

- **What they know:** Only what is on the page. A coined term has no meaning until defined. Never lean on invisible internal reasoning or private context. When brevity and clarity conflict, choose clarity.
- **What they came looking for:** The reader is usually here to **do something** (practical steps) or **understand something** (conceptual explanation). Identify the goal before drafting and serve that specific need. Theory interrupting practical instructions blocks action; instructions cluttering an explanation impede understanding.

## Match Tone to Actual Significance

Most tasks represent incremental improvements, and that is excellent. Do not inflate a bug fix into a philosophical treatise on the future of software engineering. Do not manufacture artificial drama ("here is the kicker", "the result is devastating"), nor declare your point self-evident ("the reality is simple"). Let facts, tests, and code speak for themselves.

## AI Writing Tells and Red Flags

Consult `references/tropes.md` for the full guide to cliché terms and fixes. Common offenders:

| Category       | Tells to Avoid                                                                                                                                      |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Word choice    | "dive into", "leverage", "robust", "tapestry", "dynamic ecosystem", "serves as", "stands as a testament"                                            |
| Sentence shape | "not only X, but Y", "Neither A. Nor B. Just C.", "The result? Astonishing.", loose dangling participial clauses ("highlighting its importance")    |
| Tone           | "Here's the kicker", "Think of it as", "Let's unpack this", inflated significance, invented buzzwords                                               |
| Formatting     | Excessive em-dashes, mechanically bolding the first two words of every bullet point, gratuitous decorative emojis, artificial Title Case everywhere |
| Composition    | Redundant summaries ("In conclusion"), hammering the same metaphor repeatedly                                                                       |

## Pre-Handoff Checklist

Reread your text through the eyes of a reader who knows only what is visible on screen:

- Does each sentence express exactly what I intend, with words chosen specifically for it?
- Have I repeated the exact same sentence structure more than twice in a row?
- Is anything here solely to sound profound, exhaustive, or formal?
- Could any sentence be trimmed without losing meaning?
- Would a clear-headed technical practitioner write it this way?
