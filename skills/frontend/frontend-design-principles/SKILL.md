---
name: frontend-design-principles
description: >-
    Use when building or reviewing frontend user interfaces (UI) — dashboards, admin panels, landing pages, marketing sites, and web applications.
    Guides domain-specific design decisions (intentional typography, color palettes, semantic CSS tokens, layout, depth, and spacing) rather than default generic AI aesthetics.
    Routes to product (app.md) or marketing (marketing.md) references based on context.
---

# Frontend Design Principles

Build interfaces with intention, character, and crafted polish.

## Scope and Routing

After reading this overview, consult the context-specific guide:

- **`app.md`** — dashboards, admin panels, settings pages, internal tools, SaaS products, and data-dense interfaces (tables, forms, feeds) where users perform repetitive daily work.
- **`marketing.md`** — landing pages, conversion funnels, product announcements, and creative showcases where visual first impressions and brand differentiation are paramount.

## Why This Process Exists

Language models default to predictable, generic interfaces — rounded white cards with exaggerated drop shadows and standard blue accents. The process below requires deliberate design decisions before writing UI code.

## Where Generic Defaults Hide

- **Typography is not just a container — it IS the design.** An artisan bakery platform and a financial trading terminal both pursue "typographic clarity", yet one must feel warm and tactile while the other must be precise, cold, and tabular.
- **Navigation does not frame the product — it IS the product.** Where the user is, where they can go, and what matters most. An isolated screen without contextual hierarchy is just a component demo, not a usable tool.
- **Data communicates meaning.** A progress ring and a text counter might both display "3 of 10"; one conveys an unfolding story, the other merely fills space.
- **CSS token names reflect design choices:** Reading CSS variables alone should reveal the product's domain:

```css
/* ❌ Generic — could belong to any random template */
--gray-700: #333;
--surface-2: #fafafa;

/* ✅ Semantic and domain-aligned */
--ink: #18181b;
--parchment: #fdfbf7;
```

## Mandatory Steps Before Writing Code

Resolve these questions before writing interface code:

### 1. Answer Intent Questions

- **Who is this human?** Do not just say "users". Describe the real person — their physical environment, what they were doing immediately before, and what they must accomplish next.
- **What is the core task?** The central action verb: approve payments, audit deploy logs, reconcile invoices.
- **What should the interface feel like?** Reject lazy labels like "clean and modern". Define concrete sensory qualities: warm like kraft paper? dense and functional like a Bloomberg terminal? minimal and surgical?

### 2. Define the Four Design Pillars

- **Domain:** at least 5 authentic domain terms from the product's specific ecosystem.
- **Color Universe:** colors derived naturally from the physical world of the product (at least 5 distinct tones).
- **Signature:** one distinctive element (visual treatment, structural pattern, or micro-interaction) that belongs uniquely to this product.
- **Patterns to Reject:** 3 generic UI clichés you commit to avoiding in this interface.

### 3. Confirm Direction

Present this design direction to the user before generating hundreds of lines of code, validating that the visual identity aligns with expectations.

## Interface Validation Tests

- **Substitution Test:** if you swapped the font and colors for default gray/blue Tailwind or Bootstrap utilities, would anyone notice? Where the swap is invisible is where design intention is missing.
- **Squint Test:** squint or blur your vision. Does the visual hierarchy of weights and functional zones remain distinct?
- **Signature Test:** point out exactly which components embody the product's bespoke character.
- **Token Test:** do your style tokens reflect a unique brand system or an off-the-shelf template?

## Craft and Polish Fundamentals

- **Subtle Elevation Layers:** exceedingly gentle, layered surface shifts (as seen in Linear, Vercel, and Supabase).
- **Crisp Borders:** fine, subtle borders that recede until the eye seeks structural division.
- **Purposeful Color:** neutral tones construct structure; accent colors carry functional meaning. One intentional accent outperforms five competing saturated colors.

## Universal Anti-Patterns to Avoid

- Oversized, muddy drop shadows (`box-shadow: 0 25px 50px ...`).
- Decorative borders thicker than necessary (unmotivated 2px+ strokes).
- Competing accent colors fighting for equal attention.
- Incoherent elevation layering (heavy drop shadows combined with harsh flat borders).
- Inconsistent spacing outside a disciplined scale.

## Supporting Documents

- `references/principles.md` — concrete CSS values for elevation, typography scales, spacing, and dark mode.
- `app.md` — guidelines focused on SaaS products, dashboards, and high-density screens.
- `marketing.md` — guidelines for landing pages, conversion funnels, and brand showcases.
