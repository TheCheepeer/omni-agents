# omni-agent

Hub centralizado e agnostico para versionar, gerenciar e distribuir subagentes, regras de desenvolvimento e biblioteca modular de skills para multiplos ambientes de desenvolvimento assistido por IA.

---

## Ferramentas Suportadas

O sistema unifica a gestao de contexto e exporta automaticamente para os formatos nativos de cada assistente:

| Ferramenta             | Identificador | Escopo             | Arquivos e Destinos Gerados                                           |
| :--------------------- | :------------ | :----------------- | :-------------------------------------------------------------------- |
| **Google Antigravity** | `antigravity` | Global + Workspace | `.agents/` (`skills.json`, `rules/`, `agents/`) e `~/.gemini/config/` |
| **Claude Code**        | `claude`      | Global + Workspace | `CLAUDE.md` na raiz do projeto e `~/.claude/CLAUDE.md`                |
| **Cursor IDE**         | `cursor`      | Workspace          | `.cursor/rules/*.mdc` (com metadados de globs e alwaysApply)          |
| **GitHub Copilot**     | `copilot`     | Workspace          | `.github/copilot-instructions.md` consolidado                         |
| **Universal**          | `universal`   | Workspace          | `AGENTS.md` padronizado na raiz do projeto                            |
| **Kiro**               | `kiro`        | Workspace          | `AGENTS.md` e pasta `.kiro/`                                          |
| **OpenCode**           | `opencode`    | Workspace          | `AGENTS.md` e pasta `.opencode/`                                      |
| **Codex (OpenAI)**     | `codex`       | Workspace          | `AGENTS.md` otimizado para o ecossistema Codex                        |

---

## Estrutura do Repositorio

```text
omni-agent/
├── agents/                          # Personas especializadas de subagentes
│   ├── accessibility-reviewer.md
│   ├── code-reviewer.md
│   └── security-auditor.md
├── rules/                           # Regras e diretrizes globais
│   └── AGENTS.md
├── scripts/                         # Configurador declarativo e adaptadores
│   ├── configure_workspace.py       # Menu interativo e orquestrador CLI
│   └── targets/                     # Modulos adaptadores por ferramenta
│       ├── __init__.py              # Registro central de adaptadores
│       ├── base.py                  # Contratos e utilitarios de filesystem
│       ├── antigravity.py           # Adaptador Google Antigravity
│       ├── claude.py                # Adaptador Claude Code (CLAUDE.md)
│       ├── cursor.py                # Adaptador Cursor (.cursor/rules/*.mdc)
│       ├── copilot.py               # Adaptador GitHub Copilot
│       └── universal.py             # Adaptador Universal, Kiro, OpenCode e Codex
├── skills/
│   ├── global/                      # CORE GLOBAL (~800 tokens) - Essenciais para qualquer projeto
│   │   ├── coding-standards/        # Qualidade tecnica, Clean Code e padroes de engenharia
│   │   ├── comunicacao-clara/       # Postura didatica, clareza e sintese sem enrolacao
│   │   ├── grug-brained-dev/        # Anti-overengineering e reducao de complexidade
│   │   ├── reducing-entropy/        # Combate a debito tecnico e delecao de codigo morto
│   │   └── researching-codebases/   # Investigacao de repositorios usando subagentes
│   ├── planning/                    # BIBLIOTECA: Planejamento, Auditoria e Roadmaps
│   ├── docs/                        # BIBLIOTECA: Redacao e Documentacao Tecnica
│   ├── frontend/                    # BIBLIOTECA: Design, Visualizacao e Tailwind CSS
│   ├── meta/                        # BIBLIOTECA: Criacao de Prompts e Customizacoes
│   └── stacks/                      # BIBLIOTECA: Linguagens, Frameworks e Infraestrutura
└── README.md
```

---

## Conteudo

### 1. Subagentes (`agents/`)

- `accessibility-reviewer.md`: Especialista em acessibilidade digital (a11y), diretrizes WCAG 2.1/2.2 (A, AA, AAA) e WAI-ARIA.
- `code-reviewer.md`: Especialista em analise estatica de codigo, Clean Code e legibilidade.
- `security-auditor.md`: Especialista em OWASP Top 10 e AppSec.

### 2. Regras Globais (`rules/`)

- `AGENTS.md`: Diretrizes essenciais de desenvolvimento, seguranca, comunicacao, proibicao de emojis e padrao obrigatorio de Tailwind CSS.

### 3. Biblioteca Modular de Skills (`skills/`)

Para manter o consumo de tokens baixo e evitar que o modelo hesite entre dezenas de opcoes irrelevantes:

1. **Core Global (`skills/global/`):** 5 skills essenciais que moldam o comportamento base do modelo em qualquer contexto. Consomem apenas ~800 tokens.
2. **Biblioteca Sob Demanda (`skills/{planning,docs,frontend,meta,stacks}/`):** Skills especializadas que voce pode ativar pontualmente apenas nos projetos onde fizerem sentido.

---

## Configuracao e Automacao Multiplataforma

O script [`scripts/configure_workspace.py`](scripts/configure_workspace.py) roda nativamente em **Windows, Linux e macOS** sem dependencias externas (apenas a biblioteca padrao do Python).

### 1. Modo Interativo (TUI / GUI)

```bash
# Iniciar o menu interativo:
python scripts/configure_workspace.py

# Ou informando a pasta do projeto alvo diretamente:
python scripts/configure_workspace.py /caminho/do/projeto
python scripts/configure_workspace.py .
```

#### Estrutura do Menu Interativo:

```text
=================================================================
  CONFIGURADOR MULTI-TOOL DE AGENTES, REGRAS E SKILLS
=================================================================
  Workspace Alvo:     [Caminho do Projeto]
  Ferramentas Ativas: antigravity, cursor, claude
-----------------------------------------------------------------
  [t] Selecionar Ferramentas Alvo (Antigravity, Cursor, Claude...)
  [1] Configuracao Global da Maquina (Antigravity e Claude)
  [2] Subagentes para o Workspace
  [3] Regras para o Workspace
  [4] Skills Modulares para o Workspace
  [s] Sincronizar Tudo (Sync em todas as ferramentas ativas)
  [c] Limpeza / Desinstalacao por Ferramenta
  [5] Sair
-----------------------------------------------------------------
  [w] Definir / Alterar Workspace Alvo
=================================================================
```

---

### 2. Modo Linha de Comando (CLI / Automacao)

O configurador pode ser executado diretamente em scripts ou rotinas de CI/CD:

```bash
# Listar todas as ferramentas suportadas:
python scripts/configure_workspace.py --list-tools

# Sincronizar workspace para todas as ferramentas ativas salvas:
python scripts/configure_workspace.py /caminho/do/projeto --sync

# Configurar para uma ferramenta especifica:
python scripts/configure_workspace.py /caminho/do/projeto --tool cursor --sync
python scripts/configure_workspace.py /caminho/do/projeto --tool claude --sync
python scripts/configure_workspace.py /caminho/do/projeto --tool copilot --sync

# Configurar todas as ferramentas simultaneamente (Multi-Tool):
python scripts/configure_workspace.py /caminho/do/projeto --tool all --sync

# Limpar/desinstalar configuracoes de uma ferramenta sem afetar as outras:
python scripts/configure_workspace.py /caminho/do/projeto --tool cursor --clean
python scripts/configure_workspace.py /caminho/do/projeto --clean  # Remove todas

# Aplicar configuracao global da maquina:
python scripts/configure_workspace.py --global
python scripts/configure_workspace.py --tool claude --global
```

---

### 3. Cenarios Estrategicos

#### Trabalho em Equipe (Multi-Tool no mesmo repositorio)

Em equipes onde desenvolvedores usam ambientes diferentes (por exemplo, um desenvolvedor no Cursor, outro no VS Code com Copilot e outro no Antigravity), utilize a opcao `[all]` ou `--tool all`. O script cria os arquivos de configuracao para cada assistente a partir da mesma fonte de regras, garantindo consistencia sem atrito.

#### Sincronizacao Rapida (Sync)

Ao atualizar regras ou skills no repositorio central, execute `--sync` no projeto para atualizar os arquivos consolidados (como `CLAUDE.md`, `copilot-instructions.md` e `.cursor/rules/`) instantaneamente.

#### Persistencia de Estado

As preferencias de cada workspace sao salvas em `.agents/workspace_state.json` (adicionado automaticamente ao `.gitignore`), permitindo rastrear quais ferramentas estao ativas no projeto.

---

## Licenca

Distribuido sob a licenca Apache 2.0. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
