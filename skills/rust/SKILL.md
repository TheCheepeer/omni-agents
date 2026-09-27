---
name: rust
description: >-
    Mudança de modelo mental para programação idiomática em Rust ("Pensando em Rust").
    Use ao escrever ou revisar código Rust para ir além do mero "compilou" e adotar padrões idiomáticos: modelagem de domínio com tipos e newtypes, eliminação de estados ilegais, borrow checker e ownership sem clone() desnecessário, tratamento de erros estruturados com thiserror/anyhow, traits vs enums, async/Tokio correto, unsafe justificado e fronteiras de API.
---

# Pensando em Rust (Thinking in Rust)

Você já conhece a sintaxe de Rust. O objetivo desta skill é mudar os **padrões mentais imediatos** ao modelar um domínio, gerenciar ownership, projetar APIs ou cruzar fronteiras de dados.

O principal modo de falha é escrever código que compila, mas foi pensado como se fosse Python, Java, TypeScript ou C: uso de `String` crua para conceitos de domínio; `bool` para representar estados; trait objects para conjuntos finitos fechados; `Error(String)` para qualquer falha; curingas `_ =>` em todos os blocos `match`; loops por índice; valores sentinela; getters e setters em todos os campos; `clone()` automático para calar o compilador; `unsafe` como atalho para fugir das restrições de design. Esses códigos compilam, mas estão conceitualmente errados.

Ao revisar código Rust, avalie primeiro a forma do programa: quais invariantes estão representadas no sistema de tipos, quem é o dono de cada valor, quais estados se tornaram impossíveis, como os erros cruzam as fronteiras e se alguma saída fácil está mascarando um erro de design.

## O Modelo Mental do Rust

### Modelar o Domínio nos Tipos

1. **Toda string com significado de domínio deve ser um Newtype:** `String` crua apaga o significado. O compilador não sabe diferenciar um e-mail de um nome de usuário ou URL. Encapsule-a, valide na construção e mantenha o campo interno privado. Veja [references/newtypes-and-domain-types.md](references/newtypes-and-domain-types.md).
2. **Parâmetros booleanos são mentirosos — use Enums:** `true` e `false` não comunicam nada no local da chamada e não suportam um terceiro estado futuro. Substitua flags por variantes nomeadas. Veja [references/bool-to-enum.md](references/bool-to-enum.md).
3. **Todo estado de desconhecimento deve ser explícito:** `Option<bool>` tem três estados sem nenhum nome claro. Coleções vazias podem significar "já verificado e vazio" ou "ainda não verificado". Crie variantes nomeadas. Veja [references/option-bool-to-enum.md](references/option-bool-to-enum.md).
4. **Todo `match` no seu próprio enum deve ser exaustivo — evite curingas `_ =>`:** Curingas silenciam o compilador quando você adiciona novas variantes no futuro. Liste cada variante explicitamente. Veja [references/exhaustive-matching.md](references/exhaustive-matching.md).
5. **Erros são fatos de domínio — nunca use `Error(String)`:** Erros em string destroem a estrutura. Quem chama não consegue tratar, tentar novamente ou testar. Bibliotecas devem expor enums tipados com `thiserror`; aplicações adicionam contexto com `anyhow`. Veja [error-handling.md](error-handling.md).
6. **Faça Parse, não apenas validação (Parse, don't validate):** A validação checa o dado e joga fora a prova. O parsing checa o dado e devolve um tipo refinado que garante o invariante para sempre. Veja [references/parse-dont-validate.md](references/parse-dont-validate.md).
7. **Enums são a ferramenta primária de modelagem:** Uma struct com campo `kind` e vários campos `Option` é sempre um enum esperando para nascer. Veja [references/enums-as-modeling-tool.md](references/enums-as-modeling-tool.md).
8. **Conjuntos fechados são Enums, não Trait Objects:** Se você conhece todas as variantes em tempo de compilação, use um enum (despacho estático sem custo, matching exaustivo). Use `dyn Trait` apenas se o conjunto for genuinamente aberto para extensões externas. Veja [traits.md](traits.md).
9. **Fronteiras traduzem; o núcleo modela:** Camadas de Serde, FFI, CLI, HTTP e banco de dados devem converter DTOs para tipos ricos de domínio antes de passar para a lógica central. Veja [serde.md](serde.md) e [interop.md](interop.md).

### Expressar Ownership e Intenção de API

10. **Empreste por padrão (`&T`) — tome posse (`T`) somente quando intencional:** Aceite `&str`, `&[T]` e `&Path` em vez de tipos alocados, a menos que precise armazenar, transformar ou transferir posse. Veja [references/borrow-by-default.md](references/borrow-by-default.md).
11. **Assinaturas de função são contratos de posse:** A assinatura deve revelar quem é dono, quem empresta, quem altera e quanto tempo os valores duram (lifetimes). Veja [references/function-signatures.md](references/function-signatures.md).
12. **`clone()` não é ferramenta de design:** Clone para posse independente real, transferência entre threads ou armazenamento de cópias intencionais. Não use `clone()` apenas porque o erro E0382 apareceu. Veja [ownership.md](ownership.md).
13. **Reestruture a posse antes de apelar para `Rc<RefCell<T>>`:** `RefCell` troca checagem em tempo de compilação por pânicos em tempo de execução. Tente dividir borrows, usar fases de leitura seguidas de escrita ou IDs/índices. Veja [references/ownership-before-refcell.md](references/ownership-before-refcell.md).
14. **Código assíncrono é para espera de E/S, não para trabalho pesado de CPU:** Nunca bloqueie o runtime assíncrono (Tokio). Use E/S assíncrona, `spawn_blocking` para chamadas síncronas rápidas e Rayon ou threads dedicadas para processamento pesado de CPU. Veja [async.md](async.md).
15. **Unsafe e Atômicos exigem justificativas formais por escrito:** Todo bloco `unsafe` deve ter comentários `// SAFETY:` demonstrando por que os invariantes são preservados. Valide com Miri. Veja [atomics.md](atomics.md) e [unsafe.md](unsafe.md).

### Expressar Intenção no Controle de Fluxo

16. **Iteradores em vez de loops com índice:** `for i in 0..v.len()` mascara intenção e gera risco de erro off-by-one. Use adaptadores funcionais: `.iter()`, `.enumerate()`, `.windows()`, `.zip()`. Veja [references/iterators-over-indexing.md](references/iterators-over-indexing.md).
17. **`Option<T>` em vez de valores sentinela:** Evite `-1`, `""` ou `0` para representar ausência de valor. O sistema de tipos existe para isso. Veja [references/option-over-sentinels.md](references/option-over-sentinels.md).
18. **Módulos são namespaces, não blocos `impl` vazios:** Uma struct vazia com métodos associados é apenas uma classe Java disfarçada. Use funções soltas dentro de módulos. Veja [references/impl-namespace.md](references/impl-namespace.md).
19. **Campos públicos superam getters e setters triviais:** Se qualquer valor de um campo for válido, torne-o `pub`. Se houver invariante a proteger, crie o método acessor seguindo o padrão de nomenclatura do Rust: `item.nome()`, e não `item.get_nome()`. Veja [references/getter-setter.md](references/getter-setter.md).

## Checklist Rápido de Revisão de Código

1. **Dado de domínio em tipo primitivo?** → Converta para Newtype ou Enum.
2. **Booleanos ou `Option<bool>` soltos?** → Crie variantes claras de enum.
3. **Curinga `_ =>` no seu próprio enum?** → Torne o `match` exaustivo.
4. **Validação repetida em vários lugares?** → Faça o parse na fronteira uma única vez.
5. **Borrow checker contornado com `clone()` ou `unsafe`?** → Reestruture a posse dos dados.
6. **Função pública recebe `String` mas só lê?** → Troque por `&str`.
7. **Biblioteca retornando erro genérico em string?** → Defina enum tipado com `thiserror`.
8. **Código assíncrono bloqueando a thread?** → Mova para `spawn_blocking` ou E/S assíncrona real.
9. **Campos ou módulos com visibilidade pública sem critério?** → Restrinja para `pub(crate)` e exponha uma fachada limpa.

## Índice de Documentos de Apoio

- **[ownership.md](ownership.md)** — Resolução de erros de borrow checker, lifetimes, smart pointers e convenções de clone.
- **[error-handling.md](error-handling.md)** — `thiserror` vs `anyhow`, tratamento estruturado e limites de pânico.
- **[traits.md](traits.md)** e **[type-design.md](type-design.md)** — Despacho dinâmico vs estático, typestate e newtypes.
- **[async.md](async.md)**, **[atomics.md](atomics.md)** e **[unsafe.md](unsafe.md)** — Concorrência segura, ordenação de memória e invariantes Miri.
- **[serde.md](serde.md)**, **[interop.md](interop.md)** e **[project-structure.md](project-structure.md)** — DTOs de fronteira, FFI e organização de crates.
