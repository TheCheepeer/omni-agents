---
name: sveltekit
description: >-
    Mudança de modelo mental para aplicações em SvelteKit ("Pensando em SvelteKit").
    Use ao escrever ou revisar rotas (+page, +layout, +server), funções de carregamento de dados (load functions), ações de formulário (form actions), autenticação com cookies e sessões, endpoints de API, tratamento de erros e redirecionamentos com throw, renderização no servidor (SSR) e aprimoramento progressivo (progressive enhancement).
    Delega para a skill svelte5 para questões de componentes individuais, runes e acessibilidade.
---

# Pensando em SvelteKit (Think in SvelteKit)

O SvelteKit não é apenas Svelte com pastas. Ele é um sistema completo de fronteiras de aplicação: a estrutura de arquivos define a propriedade e segurança dos dados, código de servidor permanece no servidor, envios de formulário funcionam com aprimoramento progressivo nativo e redirecionamentos/erros fazem parte do fluxo de controle.

O principal erro é tratar o SvelteKit como uma SPA tradicional client-side com funções auxiliares de backend soltas: buscar dados restritos do banco via `fetch` no `onMount` dos componentes; achar que proteger um layout protege automaticamente os endpoints de API; retornar instâncias complexas de classes no `load`; chamar `redirect()` sem lançar (`throw`); e criar formulários dependentes exclusivamente de JavaScript.

Use esta skill para decisões estruturais do SvelteKit. Use a skill **svelte5** para o interior dos componentes (runes, snippets, eventos de DOM e acessibilidade).

## O Modelo Mental do SvelteKit

### 1. Nomes de Arquivo Definem Comportamento e Limites

Arquivos como `+page.svelte`, `+layout.server.ts`, `+page.server.ts` e `+server.ts` decidem exatamente onde o código é executado e quem tem permissão para chamá-lo. Veja [references/file-naming.md](references/file-naming.md).

### 2. Grupos de Rotas Organizam Políticas, Não URLs

Grupos como `(app)` e `(auth)` definem fronteiras de autenticação e layout sem alterar a URL do navegador. Mantenha rotas protegidas sob um layout autenticado e páginas de login/cadastro fora desse grupo. Veja [references/layout-patterns.md](references/layout-patterns.md).

### 3. Layouts Protegem Páginas, NÃO Endpoints

Um `+layout.server.ts` protegido protege as páginas filhas renderizadas. Ele NÃO protege endpoints irmãos ou filhos `+server.ts`; cada endpoint de API deve validar sua própria autenticação explicitamente. Veja [references/auth.md](references/auth.md).

### 4. Dados Pertencentes ao Servidor Carregam no Servidor

Consultas a bancos de dados, chaves secretas de API e sessões de usuário pertencem exclusivamente a `+page.server.ts` ou `+layout.server.ts`, e nunca a chamadas `fetch` dentro de componentes no navegador. Veja [references/load-functions.md](references/load-functions.md).

```ts
// ❌ Errado: componente buscando dados restritos no navegador
onMount(async () => {
    usuario = await (await fetch("/api/usuario")).json();
});

// ✅ Correto: +page.server.ts — o servidor busca com seguranca e entrega para a pagina
export const load = async ({ locals }) => {
    return { usuario: await locals.obterUsuario() };
};
```

### 5. `load` Retorna Dados Puros, Não Comportamentos

Retorne apenas dados serializáveis (JSON-safe) do `load` do servidor. Não retorne instâncias de classes, funções ou conexões de banco de dados. Veja [references/serialization.md](references/serialization.md).

### 6. Redirecionamentos e Erros São Lançados com `throw`

No SvelteKit 2, `redirect()` e `error()` retornam objetos de controle de fluxo que DEVEM ser lançados com `throw`. Chamadas soltas sem `throw` são bugs graves que continuam a execução da página. Veja [references/errors-and-redirects.md](references/errors-and-redirects.md).

```ts
// ❌ Errado: chamada sem throw — continua a execucao
if (!locals.user) redirect(303, "/login");

// ✅ Correto: lanca a excecao de controle de fluxo
if (!locals.user) throw redirect(303, "/login");
```

### 7. Ações de Formulário (Form Actions) como Padrão

Para envio e mutação de dados, prefira formulários HTML nativos combinados com `actions` no `+page.server.ts`. O formulário deve funcionar mesmo com JavaScript desabilitado; o `use:enhance` serve para aprimorar a experiência visual (estados de carregamento e foco). Veja [references/form-actions.md](references/form-actions.md).

### 8. Validação na Fronteira do Servidor

Sempre valide os dados no servidor. Ao encontrar erros, retorne `fail(400, { erros })` para que o componente exiba os erros de campo sem recarregar a página inteira. Veja [references/forms-validation.md](references/forms-validation.md).

## Checklist Rápido de Boas Práticas

- Segredos ou chamadas diretas de banco de dados estão isolados em arquivos `*.server.ts`?
- As funções de `load` retornam apenas dados serializáveis?
- Todos os `redirect()` e `error()` são acompanhados de `throw`?
- Cada `+server.ts` valida sua própria sessão sem depender de layouts?
- O formulário foi testado e funciona com JavaScript desabilitado?
- Variáveis globais do navegador (`window`, `localStorage`) estão protegidas contra execução durante o SSR?

## Índice de Documentos de Apoio

[Nomenclatura de Arquivos](references/file-naming.md) · [Padrões de Layout](references/layout-patterns.md) · [Funções de Carga (Load)](references/load-functions.md) · [Ações de Formulário](references/form-actions.md) · [Validação de Formulários](references/forms-validation.md) · [Autenticação e Sessões](references/auth.md) · [Erros e Redirecionamentos](references/errors-and-redirects.md) · [Serialização](references/serialization.md) · [SSR e Hidratação](references/ssr-hydration.md) · [Funções Remotas](references/remote-functions.md)
