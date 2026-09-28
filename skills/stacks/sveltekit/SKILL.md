---
name: sveltekit
description: >-
    Mindset shift for SvelteKit applications ("Thinking in SvelteKit").
    Use when writing or reviewing routes (+page, +layout, +server), data loading functions, form actions, authentication with cookies and sessions, API endpoints, error handling and redirects with throw, server-side rendering (SSR), and progressive enhancement.
    Delegates to the svelte5 skill for component internals, runes, and accessibility.
---

# Thinking in SvelteKit (Think in SvelteKit)

SvelteKit is not merely Svelte with folders. It is a comprehensive application boundary system: the filesystem structure defines data ownership and security, server code remains strictly on the server, form mutations leverage native progressive enhancement, and redirects/errors operate as first-class control flow.

The primary failure mode is treating SvelteKit as a traditional client-side SPA with loose backend helper functions: fetching sensitive database records via `fetch` inside component `onMount`; assuming an authenticated layout automatically protects sibling API endpoints; returning complex class instances from `load`; calling `redirect()` without throwing it; and building forms that depend entirely on client JavaScript.

Use this skill for structural SvelteKit decisions. Delegate to **svelte5** for component internals (runes, snippets, DOM events, and accessibility).

## SvelteKit Mental Model

### 1. Filenames Define Behavior and Security Boundaries

Files like `+page.svelte`, `+layout.server.ts`, `+page.server.ts`, and `+server.ts` determine exactly where code executes and who has access to invoke it. See [references/file-naming.md](references/file-naming.md).

### 2. Route Groups Organize Policy, Not URLs

Groups like `(app)` and `(auth)` establish authentication boundaries and layout shells without altering browser URLs. Keep authenticated application routes under a protected layout and authentication screens outside it. See [references/layout-patterns.md](references/layout-patterns.md).

### 3. Layouts Protect Pages, NOT Endpoints

A protected `+layout.server.ts` guards child rendered pages. It does NOT guard sibling or child `+server.ts` API endpoints; every API route must independently authenticate its caller. See [references/auth.md](references/auth.md).

### 4. Server-Owned Data Loads on the Server

Database queries, API secrets, and user session lookups belong exclusively in `+page.server.ts` or `+layout.server.ts`, never in client-side `fetch` calls inside browser components. See [references/load-functions.md](references/load-functions.md).

```ts
// ❌ Anti-pattern: client component fetching sensitive data in browser
onMount(async () => {
    user = await (await fetch("/api/user")).json();
});

// ✅ Correct: +page.server.ts — server queries securely and passes data down
export const load = async ({ locals }) => {
    return { user: await locals.getUser() };
};
```

### 5. `load` Returns Pure Data, Not Behavior

Return only JSON-serializable data from server `load` functions. Never return class instances with methods, raw functions, or database connection handles. See [references/serialization.md](references/serialization.md).

### 6. Redirects and Errors Must Be Thrown

In SvelteKit 2, `redirect()` and `error()` return control-flow exceptions that MUST be thrown with `throw`. Invoking them without `throw` is a silent bug that allows execution to continue. See [references/errors-and-redirects.md](references/errors-and-redirects.md).

```ts
// ❌ Bug: missing throw — execution continues
if (!locals.user) redirect(303, "/login");

// ✅ Correct: halts execution and routes to login
if (!locals.user) throw redirect(303, "/login");
```

### 7. Form Actions as the Default Mutation Mechanism

For data mutations, prefer standard HTML forms combined with `actions` in `+page.server.ts`. The form functions even when JavaScript is disabled or loading; `use:enhance` progressively enhances the experience with optimistic feedback and loading indicators. See [references/form-actions.md](references/form-actions.md).

### 8. Boundary Validation on the Server

Always validate payloads on the server. When errors occur, return `fail(400, { errors })` so the form component can render inline validation messages without a full page reload. See [references/forms-validation.md](references/forms-validation.md).

## Quick Best Practices Checklist

- Are secrets and direct database calls isolated to `*.server.ts` files?
- Do `load` functions return only plain, serializable data?
- Are all `redirect()` and `error()` invocations preceded by `throw`?
- Does every `+server.ts` validate its own authorization independent of layouts?
- Does the form submit and work without client-side JavaScript?
- Are browser globals (`window`, `localStorage`) guarded against running during SSR?

## Supporting Documents Index

[File Naming Conventions](references/file-naming.md) · [Layout Patterns](references/layout-patterns.md) · [Load Functions](references/load-functions.md) · [Form Actions](references/form-actions.md) · [Form Validation](references/forms-validation.md) · [Authentication & Sessions](references/auth.md) · [Errors & Redirects](references/errors-and-redirects.md) · [Serialization](references/serialization.md) · [SSR & Hydration](references/ssr-hydration.md) · [Remote Functions](references/remote-functions.md)
