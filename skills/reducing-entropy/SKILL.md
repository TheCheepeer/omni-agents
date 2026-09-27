---
name: reducing-entropy
description: >-
    Use ao avaliar arquiteturas, revisar código ou planejar refatorações — mede o sucesso pelo volume total de código no estado final, e não pelo esforço imediato.
    Prioriza deliberadamente a deleção de código desnecessário e combate o acúmulo de entropia.
---

# Redução de Entropia (Reducing Entropy)

Mais código atrai mais código. A entropia se acumula. Esta skill orienta o agente a buscar sempre a menor base de código possível.

**Pergunta central:** _"Como a base de código ficará DEPOIS desta mudança?"_

## Antes de Começar

**Carregue pelo menos uma mentalidade da pasta `references/`:**

1. Liste os arquivos no diretório `references/` da skill.
2. Leia a descrição inicial para escolher qual se aplica melhor ao caso.
3. Carregue pelo menos uma delas.
4. Declare brevemente qual mentalidade foi consultada e seu princípio-chave.

## O Objetivo Real

O objetivo é **menos código total na base de código final** — e não menos código para digitar no momento presente.

- Escrever 50 linhas para conseguir apagar 200 linhas = vitória líquida evidente.
- Manter 14 funções obsoletas apenas para não reescrever 2 funções simples = derrota líquida.
- "Evitar retrabalho a qualquer custo" não é a meta. A meta é uma base de código menor e mais enxuta.

**Avalie o estado final resultante, e não o esforço da alteração.**

## As Três Perguntas Essenciais

### 1. Qual é a menor base de código que resolve este problema?

Não pergunte apenas "qual é a menor alteração pontual", mas sim "qual é a menor estrutura resultante".

- Isso poderia ser resolvido com 2 funções em vez de 14?
- Isso poderia ter 0 funções (deletando a funcionalidade se ela for inútil)?
- O que podemos excluir se implementarmos isso?

### 2. A alteração proposta resulta em menos código total?

Avalie o saldo de linhas e complexidade antes e depois:

- "Mais bem organizado", mas com muito mais código = aumento de entropia.
- "Mais flexível", mas com o dobro de arquivos = aumento de entropia.
- "Separação mais limpa", mas com 5 interfaces para 1 implementação = aumento de entropia.

### 3. O que podemos deletar agora?

Toda alteração é uma oportunidade para remover código morto ou superado. Pergunte-se:

- O que esta nova implementação torna obsoleto?
- Quais funções só existiam por causa da solução que estamos substituindo?
- Qual é o máximo de código que conseguimos erradicar com segurança?

## Sinais de Alerta (Red Flags)

- **"Melhor manter o que já existe para não mexer":** Viés do status quo. A questão é o total de código a manter no futuro, não o medo de refatorar.
- **"Isso adiciona flexibilidade para o futuro":** Flexibilidade para quê? Princípio YAGNI (You Aren't Gonna Need It).
- **"Melhor separação de responsabilidades":** Mais arquivos e camadas de indireção custam caro cognitivamente. Separação não é de graça.
- **"Mais fácil de entender":** Ter 14 partes móveis raramente é mais fácil de entender do que ter 2 funções diretas.

## Quando Esta Regra Não se Aplica

- A base de código já é estritamente minimalista para o que faz.
- O projeto segue convenções rígidas de um framework bem estabelecido (não lute contra o framework).
- Requisitos legais, regulatórios ou de conformidade exigem auditoria e estruturas específicas.

---

**Priorize a deleção. Meça sempre o estado final.**
