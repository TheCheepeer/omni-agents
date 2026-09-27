---
name: roadmap
description: >-
    Construa roadmaps de produto ou software orientados a evidências a partir do estado do repositório, tickets, ideias, auditorias ou metas do usuário.
    Prioriza e sequencia o trabalho em Agora/Próximo/Depois (Now/Next/Later), marcos (milestones), dependências, riscos e transição para execução.
    Use ao ser solicitado a criar roadmaps técnicos, planos de release, priorização de backlog ou converter saídas de ideação/auditoria em uma sequência de entrega. Não serve para implementar código diretamente nem escrever planos no nível de PR.
---

# Roadmap de Produto e Software (Roadmap)

Transforme metas, ideias candidatas, tickets, apontamentos de auditoria e documentos de design em uma visão clara e estratégica do que está por vir.

Um roadmap é composto por: **Direcionamento + Priorização + Dependências**. Ele indica quais capacidades, resultados ou frentes estratégicas são as próximas prováveis, por que importam e o que precisa acontecer antes que se tornem realidade. Não é uma lista de desejos sem critério, nem promessa arbitrária de datas, nem despejo desordenado de backlog.

Mantenha-se uma camada acima da skill `writing-plans`: defina a ordenação, as fatias de entrega, os portões de validação e as transições de responsabilidade; não prescreva código em detalhes aqui. Se um item precisar de definição de produto, direcione para ideação/brainstorm. Se houver dúvidas técnicas abertas, promova uma discussão técnica. Se a implementação já estiver decidida, direcione para `writing-plans`.

Nunca altere o código-fonte da aplicação. Escreva apenas os artefatos de roadmap.

## Fluxo de Trabalho

### Fase 1 — Definir o Horizonte e a Audiência

Identifique o contexto do roadmap:

- **Audiência:** mantenedor, product owner, agentes de implementação, time de engenharia ou liderança.
- **Horizonte temporal:** Agora / Próximo / Depois (Now / Next / Later) por padrão; use versões ou marcos com datas apenas se houver um calendário real de sprints/entregas.
- **Escopo:** repositório completo, área de produto, família de funcionalidades, débito técnico, lançamento ou migração.
- **Formato:** resposta direta no chat ou artefato persistido em arquivo.

### Fase 2 — Reconhecimento (Recon)

Reúna o material de origem antes de priorizar:

- Leia os documentos do projeto: `README.md`, `GEMINI.md`, `AGENTS.md`, ADRs, issues abertas e roadmaps anteriores.
- Se o roadmap derivar da skill `improve`, leia os apontamentos aprovados e notas de dependência.
- Se nenhuma lista prévia existir, faça um reconhecimento leve em modo somente-leitura: temas recorrentes de TODO/FIXME no código, recursos pela metade, promessas documentadas não entregues e áreas de alta alteração recente.
- Não invente itens genéricos sem evidência sólida no código ou nas metas do usuário.

### Fase 3 — Padronizar os Candidatos

Converta cada oportunidade para a mesma estrutura:

| Campo          | Significado                                                                            |
| -------------- | -------------------------------------------------------------------------------------- |
| Tipo           | Funcionalidade, marco (milestone), frente técnica, pesquisa/spike, migração ou decisão |
| Resultado      | O que passa a ser verdade para os usuários, time ou arquitetura do sistema             |
| Evidência      | Arquivo e linha citados, ticket, apontamento de auditoria ou meta do usuário           |
| Primeira fatia | O menor incremento coeso e funcional que vale a pena entregar primeiro                 |
| Dependência    | O que precisa estar pronto antes para que este item seja útil e seguro                 |
| Risco          | Risco de entrega, técnico, de produto ou de migração                                   |
| Confiança      | ALTA / MÉDIA / BAIXA com base na força das evidências                                  |
| Próximo passo  | Discussão técnica, refinamento, pesquisa ou elaboração de plano (`writing-plans`)      |

Elimine duplicatas. Divida itens grandes demais. Rejeite sugestões genéricas que caberiam em qualquer outro projeto aleatório.

### Fase 4 — Priorizar e Sequenciar

Ordene pela **alavancagem real**:

1. Trabalhos que desbloqueiam ou reduzem o risco de entregas futuras.
2. Itens de alto impacto e baixo esforço apoiados em evidências sólidas.
3. Spikes de pesquisa que eliminam grandes incertezas arquiteturais antes do compromisso.
4. Itens arriscados ou complexos somente após os pré-requisitos e testes de validação existirem.

Utilize as colunas **Agora / Próximo / Depois / Não agora** (Now / Next / Later / Not now). Datas sem histórico de capacidade são apenas falsa precisão.

### Fase 5 — Redigir e Atualizar o Artefato

Para artefatos persistidos, resolva o destino nesta ordem:

1. Caminho especificado pelo usuário.
2. Convenção existente no projeto.
3. `./ROADMAP.md` na raiz do projeto (padrão principal).
4. `./docs/roadmaps/<slug>.md`.

Utilize o modelo em `assets/roadmap-template.md`. Se o arquivo já existir, atualize-o preservando o histórico e marcando itens superados em vez de apagar contexto silenciosamente.

## Erros Comuns

| Erro                                     | Como Corrigir                                                                                          |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Tratar o roadmap como despejo de backlog | Corte agressivamente; mantenha apenas o trabalho de alto nível e registre itens adiados explicitamente |
| Inventar datas fictícias                 | Use Agora/Próximo/Depois a menos que haja um cronograma com capacidade real                            |
| Deixar passar ideias vagas               | Exija evidências no repositório, em tickets ou nas metas do usuário                                    |
| Descrever a implementação detalhada      | Pare no sequenciamento e repasse para `writing-plans`                                                  |
| Esconder incertezas técnicas             | Registre o nível de confiança e explicite as dúvidas                                                   |

## Checklist de Qualidade

Antes de concluir:

- O roadmap possui público, horizonte e escopo bem identificados.
- Cada item em "Agora" possui evidência clara e próxima ação definida.
- As dependências explicam por que essa sequência foi escolhida.
- A seção "Não agora" registra itens descartados ou postergados com sua justificativa em uma linha.
