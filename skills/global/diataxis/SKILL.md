---
name: diataxis
description: >-
    Estruture, classifique e redija documentação técnica utilizando o framework Diátaxis.
    Use ao escrever documentações, READMEs, guias práticos, tutoriais, manuais passo a passo, referências de API ou ao organizar a arquitetura de documentação de um projeto.
    Também serve para auditar, reestruturar e separar conteúdos misturados entre tutoriais, how-to, referência e explicação.
---

# Framework Diátaxis para Documentação Técnica

Aplique a metodologia sistemática do Diátaxis para estruturar e redigir documentações claras e de alta utilidade.

## Os Quatro Tipos de Documentação

O Diátaxis identifica exatamente quatro categorias, definidas por dois eixos fundamentais:

|                         | **Aquisição de conhecimento** (estudo) | **Aplicação prática** (trabalho) |
| ----------------------- | -------------------------------------- | -------------------------------- |
| **Ação** (fazer)        | **Tutorial**                           | **Guia Prático (How-to)**        |
| **Cognição** (entender) | **Explicação**                         | **Referência**                   |

### 1. Tutoriais — Orientados ao Aprendizado

Escreva tutoriais como lições práticas. Conduza o aprendiz pela mão através de uma experiência guiada onde ele adquire habilidades fazendo.

- Use a primeira pessoa do plural ("Nós vamos instalar...", "Vamos criar...").
- Mostre onde o usuário vai chegar logo no início.
- Entregue resultados visíveis com frequência e rapidez.
- Reduza explicações teóricas ao mínimo essencial — coloque links para elas.
- Foque no caso concreto e evite alternativas ou bifurcações.
- Busque confiabilidade total (deve funcionar perfeitamente de primeira).

Consulte `references/tutorials.md` para o guia completo.

### 2. Guias Práticos (How-to) — Orientados a Metas

Escreva guias práticos como receitas e instruções diretas para um usuário já competente atingir um objetivo específico do mundo real.

- Dê títulos claros: "Como [alcançar o objetivo X]".
- Use imperativos condicionais ("Se desejar X, execute Y").
- Assuma competência prévia — não ensine fundamentos básicos aqui.
- Oculte detalhes desnecessários: usabilidade prática > completude enciclopédica.
- Permita flexibilidade e cite alternativas viáveis.

Consulte `references/how-to-guides.md` para o guia completo.

### 3. Referência — Orientada à Informação

Escreva a documentação de referência como uma descrição técnica austera da arquitetura e das interfaces. Deve ser consultada pontualmente, não lida linearmente.

- Apenas descreva de forma neutra e precisa — sem tom opinativo.
- Adote padrões padronizados e consistentes em todas as páginas.
- Espelhe a estrutura real do software (módulos, funções, parâmetros).
- Forneça exemplos de código para ilustrar sintaxe, não para ensinar conceitos.

Consulte `references/reference.md` para o guia completo.

### 4. Explicação — Orientada à Compreensão

Escreva explicações para aprofundar o entendimento conceitual. Responda à pergunta: _"Pode me explicar como e por que isso funciona?"_

- Conecte o tema a tópicos correlatos e arquitetura geral.
- Forneça contexto histórico e motivação: por que foi feito dessa forma.
- Fale _sobre_ o assunto (título: "Sobre o mecanismo X").
- Admita perspectivas arquiteturais e trade-offs de design.
- Mantenha limites bem definidos — não misture passos práticos de instalação.

Consulte `references/explanation.md` para o guia completo.

## A Bússola: Como Decidir em Caso de Dúvida

Faça duas perguntas simples para classificar qualquer conteúdo:

1. **Ação ou Cognição?** O objetivo principal é _fazer_ algo ou _compreender_ algo?
2. **Aquisição ou Aplicação?** O leitor está _aprendendo_ pela primeira vez ou _trabalhando_ para resolver uma demanda imediata?

O cruzamento dessas respostas define o quadrante correto. Consulte `references/compass.md` para critérios detalhados.

## Como Aplicar no Dia a Dia

1. **Classifique o conteúdo** usando as perguntas da bússola.
2. **Identifique misturas indevidas** — o texto está tentando ensinar e resolver um problema avançado ao mesmo tempo?
3. **Separe conteúdos mistos** — retire parágrafos teóricos de tutoriais e mova passos de comando para fora de referências puras.
4. **Aplique os princípios do quadrante escolhido**.
5. **Crie hiperlinks entre os documentos** em vez de embutir blocos de outros tipos.

Nunca crie pastas ou seções vazias de cada quadrante sem necessidade real. Deixe a estrutura emergir naturalmente do conteúdo do projeto.

## Erros Mais Comuns

| Erro                                         | Por que Falha                                                    | Correção                                                               |
| -------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Tutorial que explica teoria demais           | A explicação quebra o ritmo prático do aprendiz                  | Mova a teoria para um documento de Explicação e coloque um link        |
| How-to que ensina comandos básicos           | Usuários experientes perdem tempo com introduções óbvias         | Assuma competência ou separe em Tutorial + How-to                      |
| Referência com opiniões e conselhos          | Quem consulta a API precisa de fatos brutos e assinaturas        | Mova conselhos arquiteturais para uma Explicação                       |
| Explicação misturada na Referência           | Dilui ambas: a referência fica verbosa e a explicação incompleta | Separe em arquivos distintos                                           |
| "Começando" que é apenas um tour de recursos | Sem objetivo claro de aprendizado                                | Escolha um resultado prático para o usuário construir do início ao fim |

## Regras Críticas

- **Nunca misture os quatro tipos no mesmo bloco de texto.** Cada tipo possui tom, finalidade e formato próprios.
- **O estado mental do leitor importa.** Estudo vs. Trabalho é a distinção fundamental. Tutoriais e Explicações atendem ao modo de estudo; Guias How-to e Referência atendem ao modo de trabalho.
- **Conecte com links** em vez de duplicar conteúdo entre seções.

## Aprofundamento por Módulo

Consulte os arquivos da pasta `references/` conforme necessário:

| Tema                                    | Arquivo de Apoio                                  |
| --------------------------------------- | ------------------------------------------------- |
| Redação de tutoriais                    | `references/tutorials.md`                         |
| Redação de guias práticos               | `references/how-to-guides.md`                     |
| Redação de documentos de referência     | `references/reference.md`                         |
| Redação de explicações e conceitos      | `references/explanation.md`                       |
| Ferramenta da bússola decisória         | `references/compass.md`                           |
| Diferença entre Tutorial e How-to       | `references/tutorials-how-to.md`                  |
| Diferença entre Referência e Explicação | `references/reference-explanation.md`             |
| Fundamentos e mapeamento bidimensional  | `references/map.md` e `references/foundations.md` |
