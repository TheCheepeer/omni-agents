---
name: skill-authoring
description: >-
    Use ao criar, redigir, refinar ou depurar skills para agentes de IA.
    Orienta a estrutura de arquivos e frontmatter de SKILL.md, redação de descrições ricas em gatilhos para ativação semântica, organização de instruções com divulgação progressiva (progressive disclosure), validação estrutural e resolução de problemas quando uma skill não ativa ou é ignorada pelo modelo.
---

# Criação e Manutenção de Skills (Skill Authoring)

Utilize este guia como manual de referência para criar, auditar e manter skills de alto impacto para agentes de IA.

Uma skill é considerada concluída quando carrega apenas para as solicitações corretas, fornece instruções claras sem desperdiçar tokens na janela de contexto e baseia suas orientações em evidências reais.

Os agentes de IA leem `name` e `description` antes de ler o corpo do arquivo. O conteúdo principal só é carregado na memória quando a descrição corresponde à tarefa do usuário. Referências, scripts e modelos são lidos sob demanda. Escreva sempre respeitando essa ordem de carregamento.

## Escolha o Fluxo Adequado

| Objetivo                                                | Leitura Inicial                                    | Recursos Secundários                                                                             |
| ------------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Criar uma skill simples do zero                         | [workflows/create.md](workflows/create.md)         | [templates/simple.md](templates/simple.md), [references/patterns.md](references/patterns.md)     |
| Criar/atualizar a partir de docs e histórico do projeto | [workflows/synthesize.md](workflows/synthesize.md) | [README.md](README.md), [references/examples.md](references/examples.md)                         |
| Revisar ou auditar uma skill existente                  | [references/rules.md](references/rules.md)         | [references/examples.md](references/examples.md), [spec/specification.md](spec/specification.md) |
| Verificar se a skill ativa e responde corretamente      | [workflows/test.md](workflows/test.md)             | [workflows/debug.md](workflows/debug.md) se falhar                                               |
| Diagnosticar skill que não ativa ou é ignorada          | [workflows/debug.md](workflows/debug.md)           | [spec/specification.md](spec/specification.md)                                                   |
| Aprimorar skill após falha concreta em sessão           | [workflows/refine.md](workflows/refine.md)         | [references/rules.md](references/rules.md)                                                       |

## Regras Cardeais de Qualidade

1. **A descrição deve conter palavras-chave de gatilho:** Sem termos claros, o agente nunca saberá quando ativar a skill.
2. **A descrição cita capacidades e condições, não passos:** O agente pode se apegar a resumos do frontmatter em vez de ler o corpo detalhado se a descrição tentar resumir o passo a passo.
3. **A descrição usa a 3ª pessoa:** Ela é injetada como metadado de contexto ("Use ao...", "Guia para..."), e não como fala do agente.
4. **O nome deve ser idêntico ao da pasta:** Em formato kebab-case (`nome-da-skill`).
5. **Instruções críticas ficam no topo:** Em arquivos extensos, informações do final podem perder peso de atenção.
6. **`SKILL.md` deve ser enxuto:** O contexto em tempo de execução é valioso; mova documentações complementares para `references/`.
7. **Referências devem ser explicitamente linkadas no Markdown:** Links relativos facilitam a navegação pelo agente.
8. **Precisão antes de volume:** Mais arquivos e textos prolixos frequentemente diminuem a confiabilidade do agente.

## Anatomia de uma Skill

```text
nome-da-skill/
├── SKILL.md              # Ponto de entrada obrigatório (instruções essenciais)
├── README.md             # Opcional: contexto para mantenedores humanos
├── references/           # Opcional: manuais técnicos detalhados sob demanda
├── scripts/              # Opcional: scripts utilitários executáveis
└── assets/               # Opcional: modelos, esquemas e arquivos estáticos
```

Distribuição recomendada do conteúdo:

- **`SKILL.md`:** Frontmatter YAML e regras operacionais essenciais.
- **`references/*.md`:** Manuais e explicações aprofundadas que o agente só lê quando necessário.
- **`scripts/*`:** Operações repetitivas e determinísticas que scripts resolvem melhor que texto.
- **`assets/*`:** Templates de saída, schemas JSON e exemplos brutos.

## Como Escrever Descrições Eficazes no Frontmatter

A descrição decide se a skill será carregada ou ignorada. Siga esta fórmula:

```yaml
description: >-
    Use ao [condições de ativação] — [capacidades específicas].
    Trata [formatos de arquivo, contextos, sintomas, termos correlatos].
```

**Exemplo Recomendado:**

```yaml
description: >-
    Use ao trabalhar com arquivos PDF — extração de texto, preenchimento de formulários e união de documentos.
    Lida com arquivos .pdf, relatórios digitalizados e campos de formulário.
```

**Exemplo a Evitar:**

```yaml
description: Processa PDFs extraindo texto e gerando relatórios.
```

## Divulgação Progressiva (Progressive Disclosure)

| Camada       | Conteúdo                   | Quando Carrega                        | Objetivo                                  |
| ------------ | -------------------------- | ------------------------------------- | ----------------------------------------- |
| **Camada 1** | `name` + `description`     | Sempre (injetado no contexto inicial) | Decisão de ativação rápida e precisa      |
| **Camada 2** | Corpo de `SKILL.md`        | Ao disparar a skill                   | Fluxo principal, regras e exemplos        |
| **Camada 3** | `references/` e `scripts/` | Sob demanda                           | Aprofundamento cirúrgico de tópicos raros |

## Estrutura do Corpo do `SKILL.md`

Escreva para um agente que já possui capacidade de raciocínio. Não ensine o óbvio. Forneça:

1. **Escolha:** identifique o caminho ou modo de ação rapidamente.
2. **Ação:** passos imperativos claros e critérios de decisão.
3. **Exemplo:** um modelo concreto e bem implementado.
4. **Proteções (Guards):** erros comuns, falsos positivos e pegadinhas.
5. **Verificação:** comando ou teste que comprova o sucesso da tarefa.

Prefira tabelas, listas de checagem e exemplos diretos a parágrafos conceituais longos.
