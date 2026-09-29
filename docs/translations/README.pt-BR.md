# omni-agents (Português do Brasil)

> Traduções: [English](../../README.md) | Português (Brasil) | [Español](README.es.md)

Hub centralizado e agnóstico para versionar, gerenciar e distribuir subagentes, regras de desenvolvimento e biblioteca modular de skills para múltiplos ambientes de desenvolvimento assistido por IA.

---

## Ferramentas Suportadas

O sistema unifica a gestão de contexto e exporta automaticamente para os formatos nativos de cada assistente:

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

## Estrutura do Repositório

```text
omni-agents/
├── agents/                          # Personas especializadas de subagentes
│   ├── accessibility-reviewer.md
│   ├── code-reviewer.md
│   └── security-auditor.md
├── rules/                           # Perfis modulares de regras (um AGENTS.md por pasta)
│   ├── general/                     # Diretrizes gerais de engenharia (Inglês)
│   │   └── AGENTS.md
│   └── pt-br-dev/                   # Diretrizes para desenvolvimento em Português Brasileiro
│       └── AGENTS.md
├── scripts/                         # Configurador declarativo e adaptadores
│   ├── configure_workspace.py       # Menu interativo e orquestrador CLI
│   ├── i18n.py                      # Mecanismo desacoplado de internacionalização
│   ├── languages/                   # Catálogos de tradução localizados (en.json, pt.json...)
│   └── targets/                     # Módulos adaptadores por ferramenta
│       ├── __init__.py              # Registro central de adaptadores
│       ├── base.py                  # Contratos e utilitários de filesystem
│       ├── antigravity.py           # Adaptador Google Antigravity
│       ├── claude.py                # Adaptador Claude Code (CLAUDE.md)
│       ├── cursor.py                # Adaptador Cursor (.cursor/rules/*.mdc)
│       ├── copilot.py               # Adaptador GitHub Copilot
│       └── universal.py             # Adaptador Universal, Kiro, OpenCode e Codex
├── skills/
│   ├── global/                      # CORE GLOBAL (~800 tokens) - Essenciais para qualquer projeto
│   │   ├── coding-standards/        # Qualidade técnica, Clean Code e padrões de engenharia
│   │   ├── comunicacao-clara/       # Postura didática, clareza e síntese sem enrolação
│   │   ├── grug-brained-dev/        # Anti-overengineering e redução de complexidade
│   │   ├── reducing-entropy/        # Combate a débito técnico e deleção de código morto
│   │   └── researching-codebases/   # Investigação de repositórios usando subagentes
│   ├── planning/                    # BIBLIOTECA: Planejamento, Auditoria e Roadmaps
│   ├── docs/                        # BIBLIOTECA: Redação e Documentação Técnica
│   ├── frontend/                    # BIBLIOTECA: Design, Visualização e Tailwind CSS
│   ├── meta/                        # BIBLIOTECA: Criação de Prompts e Customizações
│   └── stacks/                      # BIBLIOTECA: Linguagens, Frameworks e Infraestrutura
├── docs/
│   └── translations/                # Versões traduzidas da documentação
│       ├── README.pt-BR.md
│       └── README.es.md
└── README.md                        # Documentação principal em inglês
```

---

## Conteúdo

### 1. Subagentes (`agents/`)

- `accessibility-reviewer.md`: Especialista em acessibilidade digital (a11y), diretrizes WCAG 2.1/2.2 (A, AA, AAA) e WAI-ARIA.
- `code-reviewer.md`: Especialista em análise estática de código, Clean Code e legibilidade.
- `security-auditor.md`: Especialista em OWASP Top 10 e AppSec.

### 2. Perfis de Regras (`rules/`)

Organizados em pastas modulares por perfil, contendo cada uma seu arquivo de contrato `AGENTS.md`:

- `pt-br-dev/AGENTS.md`: Diretrizes de desenvolvimento, segurança, comunicação em português brasileiro, respeito rigoroso a acentuação e pontuação, proibição estrita de emojis e padrão obrigatório de Tailwind CSS.
- `general/AGENTS.md`: Diretrizes universais em inglês para projetos e equipes internacionais, Clean Code, segurança e arquitetura sólida.

### 3. Biblioteca Modular de Skills (`skills/`)

Para manter o consumo de tokens baixo e evitar que o modelo hesite entre dezenas de opções irrelevantes:

1. **Core Global (`skills/global/`):** 5 skills essenciais que moldam o comportamento base do modelo em qualquer contexto. Consomem apenas ~800 tokens.
2. **Biblioteca Sob Demanda (`skills/{planning,docs,frontend,meta,stacks}/`):** Skills especializadas que você pode ativar pontualmente apenas nos projetos onde fizerem sentido.

---

## Instalação

Instale o `omni-agents` como um comando CLI global em seu sistema com apenas uma linha:

### Instaladores de Comando Único

- **Windows (PowerShell):**
    ```powershell
    irm https://raw.githubusercontent.com/TheCheepeer/omni-agents/main/install.ps1 | iex
    ```
- **Linux / macOS:**
    ```bash
    curl -fsSL https://raw.githubusercontent.com/TheCheepeer/omni-agents/main/install.sh | bash
    ```

### Via Gerenciadores de Pacotes (`pipx` / `uv`)

```bash
pipx install omni-agents-cli
# Ou utilizando o uv:
uv tool install omni-agents-cli
```

Uma vez instalado, execute `omni-agents` (ou simplesmente `omni`) em qualquer terminal do sistema.

---

## Configuração e Automação Multiplataforma

A ferramenta pode ser executada globalmente através do comando **`omni-agents`** (ou `omni`), ou diretamente pelo script fonte [`scripts/configure_workspace.py`](../../scripts/configure_workspace.py) dentro do repositório clonado (zero dependências externas).

### 1. Modo Interativo (TUI / GUI)

```bash
# Iniciar o menu interativo globalmente:
omni-agents

# Ou dentro do repositório clonado:
python scripts/configure_workspace.py

# Ou informando a pasta do projeto alvo diretamente:
omni-agents /caminho/do/projeto
omni-agents .
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
  [1] Configuração Global da Máquina (Antigravity e Claude)
  [2] Subagentes para o Workspace
  [3] Regras para o Workspace
  [4] Skills Modulares para o Workspace
  [s] Sincronizar Tudo (Sync em todas as ferramentas ativas)
  [c] Limpeza / Desinstalação por Ferramenta
  [l] Idioma / Language: [PT-BR | EN]
  [5] Sair
-----------------------------------------------------------------
  [w] Definir / Alterar Workspace Alvo
=================================================================
```

---

### 2. Modo Linha de Comando (CLI / Automação)

O configurador pode ser executado diretamente em scripts ou rotinas de CI/CD:

```bash
# Listar todas as ferramentas suportadas:
python scripts/configure_workspace.py --list-tools

# Sincronizar workspace para todas as ferramentas ativas salvas:
python scripts/configure_workspace.py /caminho/do/projeto --sync

# Configurar para uma ferramenta específica:
python scripts/configure_workspace.py /caminho/do/projeto --tool cursor --sync
python scripts/configure_workspace.py /caminho/do/projeto --tool claude --sync
python scripts/configure_workspace.py /caminho/do/projeto --tool copilot --sync

# Configurar todas as ferramentas simultaneamente (Multi-Tool):
python scripts/configure_workspace.py /caminho/do/projeto --tool all --sync

# Limpar/desinstalar configurações de uma ferramenta sem afetar as outras:
python scripts/configure_workspace.py /caminho/do/projeto --tool cursor --clean
python scripts/configure_workspace.py /caminho/do/projeto --clean  # Remove todas

# Aplicar configuração global da máquina:
python scripts/configure_workspace.py --global
python scripts/configure_workspace.py --tool claude --global

# Forçar idioma da interface:
python scripts/configure_workspace.py --lang pt
python scripts/configure_workspace.py --lang en
```

---

### 3. Cenários Estratégicos

#### Trabalho em Equipe (Multi-Tool no mesmo repositório)

Em equipes onde desenvolvedores usam ambientes diferentes (por exemplo, um desenvolvedor no Cursor, outro no VS Code com Copilot e outro no Antigravity), utilize a opção `[all]` ou `--tool all`. O script cria os arquivos de configuração para cada assistente a partir da mesma fonte de regras, garantindo consistência sem atrito.

#### Sincronização Rápida (Sync)

Ao atualizar regras ou skills no repositório central, execute `--sync` no projeto para atualizar os arquivos consolidados (como `CLAUDE.md`, `copilot-instructions.md` e `.cursor/rules/`) instantaneamente.

#### Persistência de Estado

As preferências de cada workspace são salvas em `.agents/workspace_state.json` (adicionado automaticamente ao `.gitignore`), permitindo rastrear quais ferramentas estão ativas no projeto.

---

## Documentação Técnica

Para guias detalhados e referências de engenharia (em inglês), consulte:

- [Arquitetura e Design](../architecture.md): Resolução de componentes em camadas, vinculação de sistemas de arquivos e padrões de adaptadores.
- [Referência de Linha de Comando (CLI)](../cli.md): Sintaxe completa, parâmetros, navegação interativa (TUI) e automação CI/CD sem interface.
- [Configuração e Extensões](../configuration.md): Esquema do `config.json`, personalizações em `custom/`, catálogo remoto e atualizações.
- [Guia de Contribuição e Padrões](../contributing.md): Configuração do ambiente local, diretrizes de código, novos adaptadores e internacionalização.

---

## Créditos e Agradecimentos

Diversas skills presentes neste repositório foram adaptadas a partir de:

- [agent-skills](https://github.com/joshuadavidthomas/agent-skills) por Josh Thomas (Licença MIT).
- [The Grug Brained Developer](https://grugbrain.dev/) por Colin McDonnell.
- [Framework Diátaxis](https://diataxis.fr/) por Daniele Procida.

Consulte o arquivo [NOTICE](../../NOTICE) para as declarações formais de direitos autorais e licenças de terceiros.

---

## Licença

Distribuído sob a licença Apache 2.0. Consulte o arquivo [LICENSE](../../LICENSE) para mais detalhes.
