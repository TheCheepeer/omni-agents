---
name: researching-codebases
description: >-
    Use ao responder a perguntas complexas sobre uma base de código que exijam explorar múltiplos módulos ou rastrear o fluxo entre componentes.
    Coordena subagentes de pesquisa em paralelo para localizar, analisar e sintetizar descobertas técnicas com referências precisas de arquivos e linhas.
---

# Pesquisa Aprofundada em Bases de Código (Researching Codebases)

Coordene subagentes em paralelo para responder a perguntas complexas de arquitetura, fluxo de dados e implementação na base de código.

## Quando Usar

- Dúvidas que atravessam múltiplos arquivos, microsserviços ou pacotes.
- "Como o recurso X funciona internamente?", exigindo rastrear chamadas de ponta a ponta.
- Busca por padrões, convenções ou exemplos recorrentes no projeto.
- Compreensão do ciclo de vida de entidades ou decisões arquiteturais.

## Quando NÃO Usar

- Perguntas simples de "onde fica o arquivo X?" — busque diretamente com comandos de busca.
- Dúvidas restritas a um único arquivo — leia o arquivo diretamente.
- Pesquisas puramente externas ou na web — consulte a documentação web diretamente.

## Fluxo de Trabalho

### 0. Consultar pesquisas anteriores (opcional)

Antes de decompor uma nova pergunta de pesquisa ampla, verifique se já existem investigações anteriores salvas:

1. Verifique se existe a pasta `.research/` no projeto ou `~/.gemini/research/`.
2. Se houver relatórios anteriores pertinentes, aproveite as conclusões em vez de reexplorar do zero.
3. Consulte `research-tools.md` para utilitários de busca de notas.

### 1. Ler arquivos citados inicialmente

Se o usuário citar arquivos ou diretórios específicos na pergunta, leia esses arquivos por completo antes de disparar subagentes. Isso fornece o vocabulário e o escopo necessários para decompor a tarefa.

### 2. Decompor a pergunta

Divida a investigação em tarefas paralelas e independentes:

- Quais camadas do sistema estão envolvidas (frontend, backend, banco, contratos de API)?
- Precisamos de mapeamento de chamadas, análise de dados ou exemplos de testes?
- Consulte `agent-selection.md` para direcionar a especialidade adequada.

### 3. Disparar subagentes em paralelo

Invoque subagentes simultâneos para as frentes independentes (no Antigravity, utilize a ferramenta `invoke_subagent` com tipo `research` ou equivalente).

**Aguarde o retorno de todas as frentes antes de redigir a síntese final.**

### 4. Sintetizar e responder

Agrupe as descobertas em uma resposta estruturada e coesa:

- Resposta direta e objetiva à dúvida original.
- Referências precisas no formato `caminho/do/arquivo:linha` (ou links no padrão Markdown).
- Diagrama ou descrição clara das conexões entre componentes.
- Pontos em aberto ou limitações identificadas.

### 5. Salvar nota técnica (opcional)

Para investigações profundas de alto valor para o time, ofereça:

> _"Deseja que eu salve esta análise técnica em um documento de pesquisa (em `.research/` no projeto)?"_

Para dúvidas rápidas e pontuais, entregue a resposta diretamente no chat sem burocracia.

## Erros Comuns a Evitar

- **Disparar subagentes antes de ler o contexto inicial:** Leia primeiro os arquivos que o usuário já indicou.
- **Não aguardar todas as investigações terminarem:** Sintetize somente após todas as frentes responderem.
- **Documentar excessivamente respostas simples:** Respostas curtas não precisam de arquivos `.md` gerados.
- **Execução sequencial desnecessária:** Se as áreas de pesquisa são independentes, consulte-as em paralelo.
