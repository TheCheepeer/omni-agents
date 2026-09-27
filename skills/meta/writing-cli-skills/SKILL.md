---
name: writing-cli-skills
description: >-
    Use ao criar uma skill de agente que encapsula uma ferramenta de linha de comando (CLI) ou binário de terminal.
    Orienta a exploração prática da ferramenta, estrutura de instalação e uso, descrições ricas em gatilhos para ativação semântica, comandos agrupados por tarefa, divulgação progressiva (progressive disclosure) e checklist de publicação.
---

# Criação de Skills para Ferramentas CLI (Writing CLI Skills)

Como criar uma skill de alta qualidade para empacotar e ensinar ferramentas de linha de comando (CLI) para agentes de IA.

## Início Rápido

1. **Instale a ferramenta e teste na prática** — não apenas leia a documentação. Testar comandos reais revela comportamentos, pegadinhas e valores padrão que os manuais omitem.
2. Execute `--help` em cada subcomando principal.
3. Teste as operações mais frequentes do dia a dia.
4. Anote o que for contraintuitivo ou surpreendente.
5. Copie o modelo em `references/template.md` para a nova pasta da skill.
6. Preencha as seções baseando-se na experiência prática de uso.
7. Remova seções irrelevantes.

```bash
# 1. Teste a ferramenta no terminal
minha-cli --help
minha-cli subcomando --help

# 2. Localização da skill no Gemini/Antigravity:
# No projeto: .agents/skills/minha-cli/SKILL.md
# Globalmente: ~/.gemini/config/skills/minha-cli/SKILL.md
```

## O Que NÃO Fazer

- Não cole a saída bruta do `--help` sem filtro — resuma apenas o que é útil.
- Não documente todas as dezenas de flags obscuras — foque nos 80% dos casos de uso reais.
- Não inclua comandos que você não testou e validou pessoalmente.
- Mantenha o arquivo `SKILL.md` principal com menos de 500 linhas para não sobrecarregar a janela de contexto.

## Seções da Skill

### Obrigatórias

| Seção                | Finalidade                                                                           |
| -------------------- | ------------------------------------------------------------------------------------ |
| **Frontmatter YAML** | `name` e `description` rica em termos de gatilho para o modelo decidir quando ativar |
| **Instalação**       | Como obter ou compilar o executável nos diferentes sistemas operacionais             |
| **Uso Principal**    | Os 80% dos fluxos e comandos mais frequentes                                         |

### Recomendadas

| Seção                 | Quando Incluir                                                                |
| --------------------- | ----------------------------------------------------------------------------- |
| Pré-requisitos        | A ferramenta exige tokens de API, contas ou dependências do sistema           |
| Formatos de Saída     | A ferramenta suporta flags como `--json` para facilitar o parsing pelo agente |
| Dicas e Pegadinhas    | Comandos interativos que travam o terminal e devem ser evitados pelo agente   |
| Diagnóstico de Falhas | Como ativar modo de depuração (`--verbose`, `--debug`)                        |
| Desinstalação         | Onde a ferramenta grava arquivos de configuração persistentes                 |

## Boas Descrições de Frontmatter

Inclua frases de intenção para que o agente saiba exatamente quando carregar a skill:

```yaml
# ✅ Bom: descritivo e com cenários claros de uso
description: Monitora feeds RSS em busca de atualizações. Use ao acompanhar blogs técnicos, verificar novos posts ou construir fluxos de leitura de feeds.

# ❌ Ruim: genérico demais
description: Ferramenta de RSS.
```

## Organização dos Comandos

Agrupe os comandos por **tarefa do usuário**, e não em ordem alfabética da CLI:

- Visualizar / Listar
- Criar / Adicionar
- Atualizar / Editar
- Excluir / Remover
- Buscar / Filtrar

## Divulgação Progressiva (Progressive Disclosure)

Mantenha o `SKILL.md` enxuto e conciso. Mova manuais extensos para a pasta `references/`:

```text
minha-cli/
├── SKILL.md                 # Fluxos essenciais e rápidos
├── references/
│   ├── config-avancada.md   # Detalhes aprofundados de configuração
│   └── api-reference.md     # Todas as flags e opções raras
└── scripts/
    └── helper.sh            # Scripts utilitários de automação
```

## Checklist de Publicação da Skill

- [ ] Frontmatter possui `name` (kebab-case) e `description` com frases de gatilho.
- [ ] Comandos de instalação testados.
- [ ] Inclui comando de verificação da instalação (`tool --version`).
- [ ] Caminho de arquivos de configuração e variáveis de ambiente documentados.
- [ ] Exemplos realistas com comandos e formatos de saída esperados.
- [ ] Flags que geram saídas JSON documentadas (preferenciais para agentes).
- [ ] Avisos contra comandos interativos que travam o terminal.
- [ ] Arquivo principal mantido enxuto, com referências na pasta `references/`.
