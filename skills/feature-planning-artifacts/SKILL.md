---
name: feature-planning-artifacts
description: >-
    Use ao criar ou iterar artefatos de planejamento em etapas para funcionalidades complexas: discussão de design (design discussion), esboço estrutural (structure outline), plano final para executores (final plan) ou pesquisa técnica exploratória.
    Fatia o trabalho em camadas verticais executáveis, estabelece portões de revisão com o usuário entre cada estágio e aprofunda itens de alto valor antes de escrever código.
---

# Artefatos de Planejamento de Funcionalidades (Feature Planning Artifacts)

Crie ou atualize artefatos de planejamento estruturados em estágios para demandas que exigem pesquisa prévia, julgamento de arquitetura, fatiamento vertical e um plano seguro antes da implementação.

Esta skill **não** é um gerador de planos em passo único descartável. Ela deve receber um escopo, realizar reconhecimento prévio, redigir ou atualizar o artefato do estágio atual e **parar no portão de revisão**. Não avance para o próximo estágio até que o atual tenha sido aceito pelo usuário ou que ele peça explicitamente para prosseguir.

Trate o planejamento como meta-engenharia: cada documento deve tornar a implementação futura mais segura ao definir critérios de sucesso, explicitar decisões de arquitetura e prever verificações contra regressão.

## Fontes e Referências

Antes de produzir ou atualizar os artefatos, utilize:

- O item selecionado no roadmap, card de oportunidade ou plano preliminar.
- Artefatos anteriores existentes para este mesmo esforço (discussão de design, esboço ou rascunhos de plano).
- A skill `coding-standards` como fonte canônica de vocabulário e padrões de código.
- Documentos do projeto: `GEMINI.md`, `AGENTS.md`, `README.md`, ADRs e estado atual do Git.
- Modelos canônicos em [references/artifact-templates.md](references/artifact-templates.md).

## O Contrato dos Estágios

Avance sempre pelo menor estágio que produza progresso sólido:

| Estágio                           | Quando Usar                                                 | Entrada                                        | Saída Resultante                                              | Portão de Parada                                            |
| --------------------------------- | ----------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------- |
| **Perguntas de Pesquisa**         | Incertezas amplas sobre como o sistema funciona hoje        | Pedido do usuário ou item de roadmap           | Perguntas precisas sobre o comportamento atual do código      | Parar após as perguntas; aguardar aprovação para pesquisar  |
| **Pesquisa Técnica**              | Dúvidas levantadas precisam ser respondidas pelo código     | Perguntas de pesquisa                          | Relatório puramente descritivo do código atual                | Parar após a pesquisa; recomendar discussão de design       |
| **Discussão de Design**           | A funcionalidade exige decisões de arquitetura e trade-offs | Pesquisa ou contexto suficiente do repositório | Opções, recomendação, decisões resolvidas e dúvidas em aberto | Parar para revisão humana; NÃO fazer o esboço ainda         |
| **Esboço de Estrutura (Outline)** | O design foi aprovado ou possui recomendação clara          | Discussão de design aceita                     | Fatias verticais de implementação                             | Parar para revisão humana; NÃO escrever o plano final ainda |
| **Plano Final de Execução**       | O esboço estrutural foi aprovado                            | Esboço aceito                                  | Plano autocontido e seguro para qualquer executor             | Parar para transição de execução                            |

Se o usuário disser apenas "planeje isso", comece por uma **discussão de design**, a menos que as incertezas sejam tão grandes que perguntas de pesquisa devam vir antes. Não gere tudo de uma vez sem pausas.

## Estrutura de Arquivos e Destino

Agrupe o pacote de artefatos em `.agents/plans/features/<slug-da-funcionalidade>/`:

```txt
.agents/plans/features/<slug-da-funcionalidade>/README.md
.agents/plans/features/<slug-da-funcionalidade>/001-design-discussion.md
.agents/plans/features/<slug-da-funcionalidade>/002-structure-outline.md
.agents/plans/features/<slug-da-funcionalidade>/003-plan.md
```

Se pesquisas descritivas foram necessárias:

```txt
.agents/plans/features/<slug-da-funcionalidade>/001-research-questions.md
.agents/plans/features/<slug-da-funcionalidade>/002-research.md
.agents/plans/features/<slug-da-funcionalidade>/003-design-discussion.md
```

Crie ou atualize exatamente **um artefato principal** por interação, junto com o `README.md` de índice do pacote.

## Fluxo Detalhado por Estágio

1. **Definir o Estágio Atual:** Avalie os arquivos existentes. Se houver uma discussão de design em revisão, itere sobre ela em vez de criar um esboço. Defina o critério de sucesso antes de escrever.
2. **Pesquisa Técnica:** Mantenha a pesquisa estritamente descritiva (o que existe hoje no código, fluxos de dados, testes e restrições). Sem recomendações ou opiniões nessa etapa.
3. **Discussão de Design:** Apresente o estado atual, o estado final desejado, não-objetivos explícitos, alternativas avaliadas, recomendação técnica e perguntas em aberto. Marque como `status: in-review` e solicite a validação do usuário.
4. **Esboço Estrutural (Structure Outline):** Após aprovação do design, fatie a entrega em fases verticais. Aponte os arquivos tocados, assinaturas essenciais e testes por fase.
5. **Plano Final:** A partir do esboço aceito, elabore o plano final à prova de executores, contendo comandos exatos de teste, condições de parada e limites de autonomia.

## Portões de Revisão com o Usuário

Use falas diretas ao encerrar o estágio:

- **Após perguntas de pesquisa:** _"Estas são as dúvidas sobre o comportamento atual do sistema que investigarei a seguir."_
- **Após pesquisa:** _"Aqui está o mapeamento descritivo do código atual; as recomendações de solução serão elaboradas na discussão de design."_
- **Após discussão de design:** _"Por favor, revise a abordagem recomendada, as opções descartadas e as dúvidas pendentes antes de estruturarmos as fases de implementação."_
- **Após esboço de estrutura:** _"Revise as fatias verticais de entrega e os testes de cada fase antes de gerarmos o plano detalhado."_
- **Após plano final:** _"O plano está concluído e pronto para execução segura."_

## Critérios de Conclusão

O pacote de planejamento está finalizado quando cada documento cumpriu seu papel e passou pelo seu respectivo portão de validação, permitindo que a funcionalidade seja codificada sem atritos conceituais ou dúvidas ocultas.
