---
name: html-artifacts
description: >-
    Use when asked to create, generate, visualize, or convert material into a standalone HTML artifact, single-file self-contained .html report, interactive visual explanation, visual walkthrough, or HTML slide deck.
    Ideal for explaining code architecture, features, PR/diff reviews, incident timelines, or decision comparisons. Not for building production web applications or HTML emails.
---

# Visual HTML Artifacts (HTML Artifacts)

Generate visual documents that justify the use of HTML: the output must be easier to analyze, compare, or navigate than plain text. The default format is a local, self-contained `.html` file.

## Non-Negotiable Core Guidelines

- **Ground in code first:** Read source files and trace real behavior before designing the interface.
- **Default to document mode:** The document must be complete and legible for asynchronous reading. Use presentation/slide mode only when explicitly requested.
- **Complete static narrative:** Interactivity deepens understanding, but the reader should never have to click to discover the main takeaway.
- **Question-driven interactivity:** Every interactive control must answer a specific reader question: question -> interaction -> immediate visible feedback.
- **100% offline single-file:** Inline all CSS, vanilla JavaScript, SVGs, and data within the file itself. Never depend on external CDNs, remote web fonts, or live server endpoints.
- **Keep it local:** The file may expose internal repository architecture or data. Never deploy externally without explicit permission.
- **Validate the output:** Ensure the HTML loads cleanly without JavaScript errors in the browser console.

## Presentation Modes

| Mode                    | Purpose                                                   | Structure                                                                                  |
| ----------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Document** (Default)  | Codebase explanation, PR review, incident, or research    | Continuous reading, stable anchors, complete text, responsive layout, print-friendly       |
| **Explorable Document** | Causal mechanisms, parameter simulations, and comparisons | Complete default state paired with interactive controls to simulate scenarios in real time |
| **Presentation**        | Guided walkthrough for meetings or live demos             | One concept per slide, keyboard navigation, and presenter notes                            |

## Workflow

### 1. Define Scope

- Who will read this artifact, and what core question must it answer?
- What repository, branch, or commit serves as the baseline?
- Is this a temporary scratch artifact or intended for project documentation?

### 2. Map Evidence

- Identify key files and line numbers.
- Distinguish rigorously between: facts **observed in code**, conclusions **inferred**, and **proposed** improvements.
- Document uncertainties rather than smoothing them over.

### 3. Structure the Reading Flow

1. Lead immediately with the primary answer or core finding.
2. Provide minimal necessary context.
3. Present the central visual model (diagram, state flow, topology, comparison, or timeline).
4. Demonstrate a concrete end-to-end trace.
5. Highlight trade-offs, risks, limitations, and decision forks.
6. Conclude with source index and recommended next actions.

### 4. Restrained Technical Visual Style

Avoid visual clutter and AI design clichés:

- No exaggerated gradients or decorative glassmorphism.
- No unprompted animations or blinking elements lacking explanatory value.
- No massive, tangled diagrams: break into a high-level map followed by focused detail views.
- Use color strictly for functional meaning, never for generic decoration.

### 5. Technical Implementation

- Use semantic HTML5, clean structured CSS, and inline SVGs.
- Ensure accessibility: adequate contrast, visible keyboard focus indicators, and `prefers-reduced-motion` compliance.
- Include print styles (`@media print`) for clean PDF export.
- Sanitize code strings to prevent script injection or broken markup.

### 6. User Delivery

After generating and validating the artifact, open it or provide the command to open:

- On Windows: `Start-Process "path\to\artifact.html"`
- On Linux/macOS: `xdg-open /path/to/artifact.html`

In chat, share the absolute file path, presentation mode, and primary findings. Do not dump the entire raw HTML payload into the chat window.

## Supporting Documents

- [references/content-patterns.md](references/content-patterns.md) — Content blueprints for PRs, systems flows, and decision comparisons.
- [references/component-contracts.md](references/component-contracts.md) — Specifications for reusable UI components and canonical CSS.
- [references/quality-and-validation.md](references/quality-and-validation.md) — Polish and accessibility verification checklist.
