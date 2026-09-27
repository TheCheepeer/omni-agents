---
name: improving-prompts
description: >-
    Use ao otimizar arquivos GEMINI.md, AGENTS.md, prompts de sistema, comandos customizados ou arquivos de skills.
    Diagnostica primeiro a falha concreta de comportamento e depois aplica as melhores práticas documentadas de engenharia de prompt (instruções explícitas, contexto/motivação, controle de verbosidade, exemplos formatados e tamanho enxuto) em vez de inventar alterações cosméticas.
---

# Otimização e Melhoria de Prompts (Improving Prompts)

## Visão Geral

Aplique as melhores práticas documentadas de engenharia de prompt aos arquivos existentes. Não invente "melhorias" cosméticas — identifique o comportamento com falha real e aplique a orientação correta.

## Quando Usar

- Otimização de arquivos `GEMINI.md` ou `AGENTS.md`.
- Refinamento de instruções em skills e comandos.
- Correção de prompts que o modelo não está obedecendo ou ignorando.
- Encurtamento de regras muito longas ou infladas.

## Quando NÃO Usar

- Escrever novos prompts do zero (apenas siga as boas práticas diretamente).
- O prompt atual já funciona bem e o usuário não relatou nenhum problema.

## O Problema Central

Sem esta skill, os agentes tendem a:

- Inventar "boas práticas" genéricas da internet.
- Fazer alterações estruturais sem saber o que estava quebrado.
- Adicionar complexidade assumindo que "mais texto = melhor".
- Mudar coisas apenas para demonstrar serviço, em vez de resolver um problema real.

## Pare se Você Pegar a Si Mesmo Pensando:

| Pensamento                                                   | Realidade                                                                 |
| ------------------------------------------------------------ | ------------------------------------------------------------------------- |
| "Está vago / fora do padrão / inconsistente"                 | Não é acionável. Qual comportamento específico falhou?                    |
| "Já entendi o suficiente / vou assumir o que o usuário quer" | Se você não consegue citar a falha concreta, você não sabe. Pergunte.     |
| "Eu sou o especialista / eu escreveria diferente"            | Preferência pessoal não substitui um problema real. Você não é o usuário. |
| "Estrutura é sempre melhor"                                  | Estrutura resolve problemas estruturais, não todos os problemas.          |
| "Isso é obviamente uma melhoria"                             | O que é óbvio para você pode quebrar o fluxo do usuário.                  |

## Processo Obrigatório

### Etapa 1: Entender Antes de Mudar

Antes de QUALQUER modificação:

1. Pergunte qual comportamento específico está aquém do esperado.
2. Pergunte o que o prompt deveria alcançar que não está alcançando hoje.
3. Se o usuário disser "apenas melhore de forma geral", peça pelo menos um exemplo de falha concreta.

**O que conta como falha concreta:**

- "O modelo ignora minha instrução de ser conciso" ✓
- "O modelo apenas sugere alterações em vez de aplicar as edições no código" ✓

### Etapa 2: Aplicar Princípios Comprovados

- **Seja explícito com o escopo:** Modelos modernos seguem instruções ao pé da letra. Especifique se a regra vale para todas as seções ou apenas para um caso.
- **Explique o PORQUÊ (Motivação):** Explicar o motivo de uma regra ajuda o modelo a generalizar corretamente. Em vez de apenas "NUNCA use elipses", use: "Não use reticências porque o motor de text-to-speech não consegue pronunciá-las".
- **Atenção aos exemplos:** Exemplos são imitados à risca, inclusive vícios indesejados. Forneça de 2 a 3 exemplos perfeitamente alinhados ao resultado esperado.
- **Controle a verbosidade explicitamente:** Indique se a resposta deve ser curta, objetiva ou detalhada com justificativas.
- **Modere palavras em tom agressivo:** Evite usar "CRÍTICO: VOCÊ DEVE OBRIGATORIAMENTE" em todo lugar. Modelos tendem a hiperfocar e ignorar o restante do prompt quando expostos a linguagem em pânico. Prefira: "Use X quando Y".

### Etapa 3: Preservar o que Já Funciona

- NÃO reestruture seções que não apresentam problemas.
- NÃO adicione complexidade a menos que ela resolva uma falha relatada.
- Mantenha os exemplos do usuário se eles demonstram o comportamento correto.

### Etapa 4: Propor Alterações com Justificativa

Para cada alteração, declare:

1. Qual boa prática foi aplicada.
2. Qual problema concreto ela resolve.
3. O antes e depois.

## Tabela Rápida: Problema → Solução

| Problema Observado                           | Correção Recomendada                                                                     |
| -------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Resposta restrita demais / não generaliza    | Especifique o escopo explicitamente ("aplique a todos os arquivos", "em todos os casos") |
| O agente não explica o raciocínio            | Peça explicitamente para declarar os motivos antes da conclusão                          |
| O agente é verboso demais                    | Instrua: "Seja conciso" ou "Responda em no máximo 3 frases"                              |
| O agente sugere mas não aplica alterações    | Troque "Você pode sugerir..." pelo imperativo "Execute as alterações nos arquivos"       |
| Uma regra é ignorada                         | Adicione a motivação (explique POR QUE essa regra é importante)                          |
| Arquivo de regras longo demais (>200 linhas) | Remova regras redundantes que o modelo já segue naturalmente por bom senso               |
