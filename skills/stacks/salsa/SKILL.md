---
name: salsa
description: >-
    Modelo mental e guia de arquitetura para o Salsa, o framework de computação incremental para Rust.
    Use ao construir ou revisar bancos de dados Salsa, funções rastreadas (tracked functions), structs de entrada/rastreadas/internadas (input/tracked/interned structs), pipelines de consulta, acumuladores de diagnóstico, suporte a cancelamento em LSPs, algoritmos red-green e computação sob demanda reativa em compiladores.
---

# Salsa: Computação Incremental em Rust

Salsa é um framework para **recomputação incremental sob demanda** em Rust. Você define entradas puras e funções puras sobre essas entradas. O Salsa memoriza o resultado de cada chamada. Quando uma entrada muda, ele reexecuta apenas as funções cujas dependências realmente foram alteradas — ignorando e reutilizando todo o restante.

O Salsa é o motor por trás do [rust-analyzer](https://rust-analyzer.github.io/) (o servidor de linguagem LSP oficial do Rust), do [ty/Ruff](https://docs.astral.sh/ty/) e do [Cairo](https://github.com/starkware-libs/cairo), permitindo respostas em milissegundos mesmo em bases de código gigantes após pequenas edições de texto.

## O Modelo Mental

```text
                    Banco de Dados Salsa (Salsa Database)
                    ┌──────────────────────────────────────────────┐
 Mundo externo      │                                              │
 (editor, CLI,      │  Entradas ──→ Funções Rastreadas ──→ Saída   │
  sistema de arqs)  │    │                 │                       │
        │           │    └──── memorizado ─┘                       │
        │           │  dependências rastreadas automaticamente     │
        ▼           └──────────────────────────────────────────────┘
 Alterar entrada                            │
 (nova revisão)                             ▼
                        Reexecuta APENAS o que mudou
```

O ciclo central:

```rust
let mut db = MyDatabase::default();

// 1. Criar entradas
let file = SourceFile::new(&db, "fn main() {}".into(), path);

// 2. Computar (Salsa memoriza tudo)
let result = analyze(&db, file);

// 3. Alterar uma entrada (inicia uma nova "revisao")
file.set_text(&mut db).to("fn main() { 42 }".into());

// 4. Recomputar — Salsa reutiliza os nós estáveis
let result = analyze(&db, file); // Só roda o que dependia do texto
```

## Conceitos Fundamentais

### O Banco de Dados (`#[salsa::db]`)

A struct que armazena todos os caches e estados intermediários. É a fonte única da verdade — toda operação do Salsa recebe `&db` ou `&mut db`.

### Entradas (`#[salsa::input]`)

Dados externos que alimentam o sistema (arquivos lidos do disco, flags de compilação). São os únicos nós que sofrem mutação direta.

```rust
#[salsa::input]
pub struct SourceFile {
    #[returns(ref)]
    pub text: String,
    pub path: PathBuf,
}
```

### Funções Rastreadas (`#[salsa::tracked]`)

Funções puras cujos retornos são armazenados em cache. O Salsa registra automaticamente quais entradas e campos foram lidos. Ao reexecutar, ele checa se alguma dependência mudou.

### Structs Rastreadas (`#[salsa::tracked] struct`)

Entidades intermediárias geradas dentro de funções rastreadas (como uma função AST ou classe). Possuem rastreamento de alteração por campo e recebem o tempo de vida `'db`.

### Structs Internadas (`#[salsa::interned]`)

Dados idênticos recebem o mesmo ID numérico compacto (como símbolos, nomes de variáveis e identificadores de tipo). Permite comparações de igualdade extremamente rápidas.

### Acumuladores (`#[salsa::accumulator]`)

Canal lateral para emitir diagnósticos e avisos de compilação a partir de funções rastreadas sem poluir o tipo de retorno da função.

### Algoritmo Red-Green e Backdating

Cada mutação em uma entrada incrementa o contador de **revisão**. Ao consultar uma função rastreada, o Salsa avalia as dependências: se o resultado recalculado for idêntico ao valor antigo (**backdating**), a propagação de mudanças é interrompida, economizando tempo computacional nos nós dependentes.

## Onde se Aprofundar

| Objetivo                                       | Documento de Apoio                                   |
| ---------------------------------------------- | ---------------------------------------------------- |
| Escolher entre input, tracked e interned       | [struct-selection.md](struct-selection.md)           |
| Projetar grafo de queries e funções rastreadas | [query-pipeline.md](query-pipeline.md)               |
| Arquitetura do banco e traits em camadas       | [database-architecture.md](database-architecture.md) |
| Lidar com consultas cíclicas/recursivas        | [cycle-handling.md](cycle-handling.md)               |
| Suporte a cancelamento em LSPs                 | [cancellation.md](cancellation.md)                   |
| Otimização com níveis de durabilidade          | [durability.md](durability.md)                       |
| Testar reutilização incremental                | [incremental-testing.md](incremental-testing.md)     |
| Integração com Language Server Protocol        | [lsp-integration.md](lsp-integration.md)             |
| Padrões para escala de produção                | [production-patterns.md](production-patterns.md)     |
