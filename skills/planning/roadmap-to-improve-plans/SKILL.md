---
name: roadmap-to-improve-plans
description: >-
    Use ao transformar um roadmap, prioridades de repositório, arquitetura ou oportunidades selecionadas em lotes agrupados de planos de melhoria numerados para futuros executores.
    Gera índices README.md, planos no formato 001-*.md/NNN, memorandos (memo-*.md), portões de verificação de testes, checagens de divergência (drift checks), condições de PARADA (STOP conditions) e notas de transição para executores.
---

# Do Roadmap aos Planos de Melhoria (Roadmap to Improve Plans)

Converta oportunidades selecionadas de um roadmap estratégico em lotes estruturados de planos de melhoria numerados. Esta é a etapa de planejamento detalhado: preserve o julgamento de auditoria e os diagnósticos de arquitetura de cada oportunidade, detalhando-os no nível de precisão necessário para que futuros executores atuem com total segurança.

Trate a escrita de planos como meta-engenharia: o resultado deve aprimorar os ciclos futuros de execução, transportando impacto esperado, riscos, hipóteses de design, verificações contra regressão, limites de autonomia e condições de parada.

## Fontes e Referências

Antes de redigir os planos, consulte o que for pertinente:

- O arquivo `.agents/ROADMAP.md` (ou equivalente no projeto).
- A skill `improve` para recuperar a postura original da auditoria: categoria, evidência, impacto, esforço, risco, confiança e esboço da solução.
- A skill `coding-standards` para nomear os padrões violados e garantias arquiteturais.
- Documentos e comandos do projeto: `GEMINI.md`, `AGENTS.md`, `README.md`, ADRs, scripts de build/teste e pipelines de CI.

## Fluxo de Trabalho

### 1. Selecionar o Escopo do Planejamento

- Inicie a partir das oportunidades aprovadas no roadmap.
- Trate cada diretório de esforço como um lote coeso de melhoria: um tema central, um resultado claro, um índice `README.md`.
- Separe funcionalidades ou objetivos não correlacionados em lotes distintos.
- Respeite a ordem de dependências do roadmap; não transforme tudo em tarefas paralelas indiscriminadas.

### 2. Reconciliar com o Estado Atual

- Verifique o estado atual do repositório no controle de versão (Git) para não planejar sobre código defasado.
- Reabra e valide as evidências de código citadas no roadmap.
- Identifique os comandos exatos de compilação, linter e testes.
- Nunca copie chaves ou senhas para os planos; mencione apenas o arquivo e a linha.

### 3. Decompor em Planos Numerados (`NNN-*.md`)

- Cada plano `NNN-*.md` deve representar uma alteração do tamanho de um Pull Request, aplicável de forma independente ou com dependência clara de um plano anterior.
- Prefira fatias verticais e funcionais a reescritas horizontais camada por camada.
- Para planos de arquitetura, explicite o diagnóstico: atrito atual, teste de deleção, ganho de localidade e nível de recomendação.
- Não finja que uma decisão técnica em aberto está pronta para execução direta. Encaminhe dúvidas arquiteturais para spikes de pesquisa ou memos de design.

### 4. Escrever o Índice e os Planos

- Salve preferencialmente em `.agents/plans/improvements/<slug-do-esforco>/` (ou na convenção adotada pelo projeto).
- Use [references/index-template.md](references/index-template.md) para o `README.md`.
- Use [references/plan-template.md](references/plan-template.md) para cada plano numerado.
- Use [references/memo-template.md](references/memo-template.md) para registrar decisões e forks de design.

### 5. Definir Fronteiras de Autonomia

- No índice do lote, aponte os planos que exigem maior cuidado ou decisões de negócio antes de codificar.
- Para cada plano, explicite: o que pode ser executado rotineiramente pelo agente, o que requer revisão de design e o que exige aprovação humana direta.

## Requisitos de Cada Plano

Todo plano numerado deve ser autocontido para um executor sem histórico da sessão anterior:

- Justificativa, impacto e retorno esperado.
- Evidências do estado atual (`arquivo:linha`).
- Estado final desejado.
- Escopo incluído e explicitamente fora de escopo.
- Sequência de passos de implementação no tamanho de um PR.
- Comandos exatos de verificação automatizada.
- Limite de autonomia (execução rotineira, revisão de design ou aprovação humana).
- Condições de PARADA (STOP conditions) para suposições incorretas ou testes falhando.
- Abordagens descartadas e por que não foram escolhidas.
- Orientações de entrega para uma nova sessão de execução.

## Critérios de Conclusão

O lote de planejamento está pronto quando o índice explica a ordem de execução e a maturidade de cada plano, cada plano numerado pode ser entregue a um executor limpo e tarefas com incertezas arquiteturais estão devidamente sinalizadas para revisão prévia.
