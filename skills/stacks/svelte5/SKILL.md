---
name: svelte5
description: >-
    Reviews Svelte components for idiomatic Svelte 5 patterns, identifies legacy React/Vue/Svelte 4 anti-patterns, and proposes modern refactorings using Runes ($state, $derived, $effect, $props, $bindable, snippets).
    Use when writing or reviewing Svelte components, migrating projects from Svelte 4 to 5, or eliminating code smells like: effects updating derived state, prop-mirroring into $state, reflex global stores, overused $bindable, and inaccessible clickable divs.
---

# Thinking in Svelte 5 (Think in Svelte 5)

You already know Svelte syntax. This skill shifts your **immediate mental defaults** when designing components, positioning state, modeling reactivity, and reviewing UI code in Svelte 5.

The primary defect is writing Svelte code that compiles, but was conceived as React, Vue, or Svelte 4: effects manually synchronizing derived variables, props mirrored into local state, reflex global stores without need, two-way bindings as lazy shortcuts, and unsemantic clickable `div`s.

A Svelte component is a lean reactive program with explicit data flow. Keep data flow direct, state ownership evident, and HTML semantic; let the compiler and browser handle mechanical work.

## Reactivity Principles in Svelte 5

### 1. Reactivity is Read-Tracked

Runes such as `$derived` and `$effect` depend strictly on values read during synchronous execution. There are no manual dependency arrays. If an effect triggers unexpectedly, inspect which reactive values it synchronously reads. See [references/read-tracked-reactivity.md](references/read-tracked-reactivity.md).

### 2. Derived State is `$derived`, NEVER `$effect`

Values computed from other reactive state must be pure computations. Effects are reserved for talking to the outside world (timers, imperative DOM, external APIs), never for keeping internal variables in sync. See [references/effect-driven-state.md](references/effect-driven-state.md).

```svelte
<!-- ❌ Anti-pattern: effect recalculating state -->
let total = $state(0);
$effect(() => { total = price * quantity; });

<!-- ✅ Correct: pure derived computation -->
let total = $derived(price * quantity);
```

### 3. `$state` is a Deep Proxy

In Svelte 5, arrays and objects inside `$state` are deeply reactive proxies. Mutate properties directly (`list.push(item)`) and discard the ceremonial immutable cloning (`[...list, item]`) typical of React. See [references/deep-state-without-immutable-ceremony.md](references/deep-state-without-immutable-ceremony.md).

### 4. Do Not Mirror Props into Local State

Copying a prop into `$state(prop)` establishes two competing sources of truth that diverge whenever the parent component updates. Derive directly from the prop or maintain a distinct draft with explicit commit/reset mechanics. See [references/prop-mirroring.md](references/prop-mirroring.md).

### 5. Props Describe Inputs; Callbacks Describe Events

In Svelte 5, component events are standard callback props. Eliminate `createEventDispatcher` in new code. See [references/component-patterns.md](references/component-patterns.md).

```svelte
<!-- ❌ Legacy Svelte 4 -->
const dispatch = createEventDispatcher();
dispatch('select', item);

<!-- ✅ Idiomatic Svelte 5 -->
let { onSelect } = $props();
onSelect?.(item);
```

### 6. Two-Way Binding (`$bindable`) is an API Commitment

`$bindable` grants a child component permission to mutate parent state directly. Reserve it for genuine form inputs and tightly controlled components, not as a casual shortcut. See [references/bindable-by-default.md](references/bindable-by-default.md).

### 7. Snippets Replace Slots

Snippets are first-class render functions. Use them when parents need to supply custom markup fragments. Type their parameters with standard TypeScript. See [references/snippets-as-render-functions.md](references/snippets-as-render-functions.md).

### 8. Semantic HTML First

A native `<button>` manages keyboard navigation, focus indicators, disabled state, and screen readers automatically. A `<div>` with an `onclick` handler clumsily reinvents the platform. See [references/semantic-html-first.md](references/semantic-html-first.md).

## How to Conduct a Review

1. **Detect Svelte version:** Check `package.json`. In Svelte 5, flag Svelte 4 legacy patterns (`export let`, `on:click`, `<slot>`, `createEventDispatcher`).
2. **Order findings by severity:** correctness and reactivity bugs first, SSR state leaks, accessibility defects, and visual/idiomatic polish last.
3. **Propose the smallest useful change.**

## Common Code Smells Index

| Code Smell                                     | Supporting Document                                                                          |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Svelte 4 legacy syntax in modern code          | [svelte5-syntax-discipline](references/svelte5-syntax-discipline.md)                         |
| Effect calculating derived state               | [effect-driven-state](references/effect-driven-state.md)                                     |
| Effect triggering unexpectedly                 | [read-tracked-reactivity](references/read-tracked-reactivity.md)                             |
| Mirroring prop into local `$state`             | [prop-mirroring](references/prop-mirroring.md)                                               |
| Immutable cloning ceremony on reactive state   | [deep-state-without-immutable-ceremony](references/deep-state-without-immutable-ceremony.md) |
| Using `createEventDispatcher` in Svelte 5      | [component-patterns](references/component-patterns.md)                                       |
| Indiscriminate use of `$bindable`              | [bindable-by-default](references/bindable-by-default.md)                                     |
| Non-interactive elements with click handlers   | [semantic-html-first](references/semantic-html-first.md)                                     |
| Rebuilding forms without native semantics      | [shadcn-svelte-forms](references/shadcn-svelte-forms.md)                                     |
| Dynamic `{#each}` lists without keys (`(key)`) | [bindings-and-directives](references/bindings-and-directives.md)                             |
