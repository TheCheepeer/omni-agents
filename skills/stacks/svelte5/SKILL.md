---
name: svelte5
description: >-
    Revisa componentes Svelte buscando padrões idiomáticos do Svelte 5, identifica antipadrões herdados do React/Vue/Svelte 4 e propõe refatorações modernas com Runes ($state, $derived, $effect, $props, $bindable, snippets).
    Use ao escrever ou revisar componentes Svelte, migrar projetos do Svelte 4 para o 5 ou eliminar vícios como: efeitos atualizando estado derivado, cópia de props para $state, stores globais por reflexo, $bindable em excesso e div clicável sem acessibilidade.
---

# Pensando em Svelte 5 (Think in Svelte 5)

Você já conhece a sintaxe de Svelte. Esta skill altera seus **padrões mentais imediatos** ao projetar componentes, posicionar estados, modelar reatividade e revisar código de interface no Svelte 5.

O principal erro é escrever código Svelte que compila, mas foi pensado como React, Vue ou Svelte 4: efeitos sincronizando variáveis derivadas manualmente, props copiadas para dentro do estado local, stores globais por reflexo sem necessidade, two-way binding como atalho preguiçoso e `div`s clicáveis sem acessibilidade.

Um componente Svelte é um programa reativo enxuto com dependências explícitas. Mantenha o fluxo de dados direto, a posse do estado evidente e o HTML semântico; deixe o compilador e o navegador fazerem o trabalho pesado.

## Princípios de Reatividade no Svelte 5

### 1. Reatividade é Rastreada por Leitura

Runes como `$derived` e `$effect` dependem estritamente do que leem durante sua execução. Não existem arrays manuais de dependência. Se um efeito disparar inesperadamente, inspecione quais variáveis ele está lendo. Veja [references/read-tracked-reactivity.md](references/read-tracked-reactivity.md).

### 2. Estado Derivado é `$derived`, NUNCA `$effect`

Valores calculados a partir de outros estados devem ser puros. Efeitos servem para interações com o mundo exterior (timers, DOM imperativo, APIs externas), nunca para manter variáveis em sincronia. Veja [references/effect-driven-state.md](references/effect-driven-state.md).

```svelte
<!-- ❌ Errado: efeito recalculando estado -->
let total = $state(0);
$effect(() => { total = preco * quantidade; });

<!-- ✅ Correto: computação pura derivada -->
let total = $derived(preco * quantidade);
```

### 3. `$state` é um Proxy Profundo (Deep Proxy)

No Svelte 5, arrays e objetos dentro de `$state` são profundamente reativos. Mute diretamente a propriedade necessária (`lista.push(item)`) e abandone o ritual cerimonioso de clonagem imutável (`[...lista, item]`) típico do React. Veja [references/deep-state-without-immutable-ceremony.md](references/deep-state-without-immutable-ceremony.md).

### 4. Não Espelhe Props no Estado Local

Copiar uma prop para dentro de `$state(prop)` cria duas fontes concorrentes da verdade que saem de sincronia se o componente pai atualizar. Derive diretamente da prop ou crie um rascunho temporário com reset/commit explícito. Veja [references/prop-mirroring.md](references/prop-mirroring.md).

### 5. Props Descrevem Entradas; Callbacks Descrevem Eventos

No Svelte 5, eventos de componentes são propriedades de callback convencionais. Abandone `createEventDispatcher` em código novo. Veja [references/component-patterns.md](references/component-patterns.md).

```svelte
<!-- ❌ Legado do Svelte 4 -->
const dispatch = createEventDispatcher();
dispatch('select', item);

<!-- ✅ Idiomático no Svelte 5 -->
let { onSelect } = $props();
onSelect?.(item);
```

### 6. Two-Way Binding (`$bindable`) é um Compromisso de API

`$bindable` permite que o componente filho altere diretamente variáveis do pai. Reserve para controles de formulário reais e componentes estritamente controlados, e não como hábito comum. Veja [references/bindable-by-default.md](references/bindable-by-default.md).

### 7. Snippets Substituem Slots

Snippets são funções de renderização de primeira classe. Use-os quando o componente pai precisar injetar pedaços de interface customizados. Tipifique seus parâmetros com TypeScript. Veja [references/snippets-as-render-functions.md](references/snippets-as-render-functions.md).

### 8. HTML Semântico em Primeiro Lugar

Um elemento nativo `<button>` já gerencia teclado, foco, estado desabilitado e leitores de tela por padrão. Uma `<div>` com manipulador de clique reconstrói a plataforma web de forma precária. Veja [references/semantic-html-first.md](references/semantic-html-first.md).

## Como Executar uma Revisão

1. **Detecte a versão do Svelte:** Verifique o `package.json`. No Svelte 5, aponte sintaxes do Svelte 4 (`export let`, `on:click`, `<slot>`, `createEventDispatcher`).
2. **Ordene os apontamentos por gravidade:** problemas de corretude e reatividade primeiro, vazamentos de estado em SSR, acessibilidade e, por fim, refinamento estético.
3. **Proponha sempre a menor alteração útil.**

## Índice de Code Smells Frequentes

| Code Smell                                      | Documento de Apoio                                                                           |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Sintaxe legada do Svelte 4 em código novo       | [svelte5-syntax-discipline](references/svelte5-syntax-discipline.md)                         |
| Efeito calculando valor derivado                | [effect-driven-state](references/effect-driven-state.md)                                     |
| Efeito disparando sem motivo claro              | [read-tracked-reactivity](references/read-tracked-reactivity.md)                             |
| Cópia de prop para dentro de `$state`           | [prop-mirroring](references/prop-mirroring.md)                                               |
| Cerimônia imutável em arrays reativos           | [deep-state-without-immutable-ceremony](references/deep-state-without-immutable-ceremony.md) |
| Uso de `createEventDispatcher` no Svelte 5      | [component-patterns](references/component-patterns.md)                                       |
| Uso excessivo e descontrolado de `$bindable`    | [bindable-by-default](references/bindable-by-default.md)                                     |
| Elementos não interativos com eventos de clique | [semantic-html-first](references/semantic-html-first.md)                                     |
| Formulários reconstruídos sem semântica         | [shadcn-svelte-forms](references/shadcn-svelte-forms.md)                                     |
| Listas dinâmicas `{#each}` sem chaves (`(key)`) | [bindings-and-directives](references/bindings-and-directives.md)                             |
