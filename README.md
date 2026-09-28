# Repositório de Agentes, Regras e Skills do Antigravity

Repositório centralizado para armazenar, versionar e gerenciar subagentes, regras globais e biblioteca modular de skills utilizados no Antigravity e VS Code.

## Estrutura do Repositório

```text
agents/
├── agents/                          # Personas especializadas de subagentes
│   ├── accessibility-reviewer.md
│   ├── code-reviewer.md
│   └── security-auditor.md
├── rules/                           # Regras globais injetadas em todas as mensagens
│   └── AGENTS.md
├── scripts/                         # Utilitários de automação do repositório
│   └── configure_workspace.py       # Configurador declarativo automático (Windows e Linux)
├── skills/
│   ├── global/                      # CORE GLOBAL (~800 tokens) - Carregado em todos os projetos
│   │   ├── coding-standards/        # Qualidade técnica, Clean Code e padrões de engenharia
│   │   ├── comunicacao-clara/       # Postura didática, clareza e síntese sem enrolação
│   │   ├── grug-brained-dev/        # Anti-overengineering e redução de complexidade
│   │   ├── reducing-entropy/        # Combate a débito técnico e deleção de código morto
│   │   └── researching-codebases/   # Investigação de repositórios usando subagentes
│   ├── planning/                    # BIBLIOTECA: Planejamento, Auditoria e Roadmaps
│   │   ├── feature-planning-artifacts/
│   │   ├── improve/
│   │   ├── roadmap/
│   │   ├── roadmap-to-improve-plans/
│   │   ├── strategic-roadmap/
│   │   └── writing-plans/
│   ├── docs/                        # BIBLIOTECA: Redação e Documentação Técnica
│   │   ├── crafting-effective-readmes/
│   │   ├── diataxis/
│   │   ├── writing/
│   │   └── writing-error-messages/
│   ├── frontend/                    # BIBLIOTECA: Design e Visualização
│   │   ├── frontend-design-principles/
│   │   └── html-artifacts/
│   ├── meta/                        # BIBLIOTECA: Criação de Prompts e Customizações
│   │   ├── improving-prompts/
│   │   ├── skill-authoring/
│   │   └── writing-cli-skills/
│   └── stacks/                      # BIBLIOTECA: Linguagens, Frameworks e Infraestrutura
│       ├── coolify-compose/
│       ├── jj/
│       ├── rust/
│       ├── salsa/
│       ├── svelte5/
│       └── sveltekit/
└── README.md
```

---

## Conteúdo

### 1. Subagentes (`agents/`)

- `accessibility-reviewer.md`: Especialista em acessibilidade digital (a11y), diretrizes WCAG 2.1/2.2 (A, AA, AAA) e WAI-ARIA.
- `code-reviewer.md`: Especialista em análise estática de código, Clean Code e legibilidade.
- `security-auditor.md`: Especialista em OWASP Top 10 e AppSec.

### 2. Regras Globais (`rules/`)

- `AGENTS.md`: Diretrizes essenciais de desenvolvimento, segurança, comunicação e padrão obrigatório de Tailwind CSS aplicados a todos os projetos.

### 3. Biblioteca Modular de Skills (`skills/`)

Para manter o consumo de tokens baixo e evitar que o modelo hesite entre dezenas de opções irrelevantes, as skills são organizadas em duas camadas:

1. **Core Global (`skills/global/`):** Apenas 5 skills essenciais que moldam o comportamento base do modelo em qualquer contexto. Consomem apenas ~800 tokens do orçamento de personalizações.
2. **Biblioteca Sob Demanda (`skills/{planning,docs,frontend,meta,stacks}/`):** 21 skills especializadas que você pode ativar pontualmente apenas nos projetos onde fizerem sentido.

---

## Configuração e Automação Multiplataforma

O script [`scripts/configure_workspace.py`](scripts/configure_workspace.py) roda nativamente em **Windows, Linux e macOS** sem dependências externas (usa apenas a biblioteca padrão do Python). Ele oferece um menu interativo completo para gerenciar tanto a **Configuração Global** quanto a **Configuração por Workspace (Projeto)**.

```bash
# Iniciar o menu interativo:
python scripts/configure_workspace.py

# Ou já informando a pasta do projeto alvo diretamente:
python scripts/configure_workspace.py /caminho/do/projeto
python scripts/configure_workspace.py .
```

---

### Estrutura do Menu Interativo:

```text
=================================================================
  CONFIGURADOR DE AGENTES, REGRAS E SKILLS - ANTIGRAVITY
=================================================================
  Workspace Alvo: [Caminho do Projeto ou 'Não definido']
-----------------------------------------------------------------
  [1] Configuração Global (Vincular core global ao Antigravity)
  [2] Agents (Subagentes para o Workspace)
  [3] Rules (Regras para o Workspace)
  [4] Skills (Skills modulares para o Workspace)
  [5] Sair
-----------------------------------------------------------------
  [w] Definir / Alterar Workspace Alvo
=================================================================
```

> **Navegação:** Todas as opções contam com a opção `v` para voltar ao menu principal a qualquer momento.

---

### Detalhes das Opções:

#### 1. Configuração Global (Opção 1)

Automatiza a vinculação do core do repositório à pasta global de configurações do Antigravity (`~/.gemini/config/`), substituindo comandos manuais de terminal:

- **Pré-visualização Segura:** Lista primeiro todas as pastas de origem e destino antes de executar qualquer alteração.
- **Proteção de Regras Globais:** Os subagentes e o core de skills são atualizados diretamente, mas a pasta de **regras globais (`rules/`) possui confirmação obrigatória antes de substituir**, exibindo as regras existentes para que você nunca sobrescreva regras customizadas acidentalmente.
- **Execução Multiplataforma:** Cria automaticamente **Junctions** no Windows (`_winapi.CreateJunction` / `mklink /J`) e **Links Simbólicos** no Linux/macOS:
    - `~/.gemini/config/agents` $\leftarrow$ `agents/`
    - `~/.gemini/config/rules` $\leftarrow$ `rules/`
    - `~/.gemini/config/skills` $\leftarrow$ `skills/global/`

#### 2. Subagentes para o Workspace (Opção 2)

- Lista os subagentes disponíveis com títulos e descrições.
- Permite selecionar por números (ex: `1, 3`), por ID ou `all` para todos.
- Copia os subagentes para `.agents/agents/` e atualiza o `.gitignore` do projeto.

#### 3. Regras para o Workspace (Opção 3)

- Lista as diretrizes essenciais de desenvolvimento e padrões de código.
- Copia as regras selecionadas para `.agents/rules/` e atualiza o `.gitignore`.

#### 4. Skills Modulares para o Workspace (Opção 4)

- **100% Dinâmico e Sem Hardcode:** Escaneia a pasta `skills/` e monta automaticamente menus e submenus para cada categoria existente (seja `stacks`, `docs`, `planning` ou qualquer nova categoria que for adicionada ao repositório).
- **Submenus Individuais por Categoria:** Ao entrar em uma categoria, exibe suas skills com status visual (`[x]` ou `[ ]`), permitindo marcar/desmarcar itens por número, marcar todas (`all`), desmarcar (`limpar`) e voltar (`v`).
- **Persistência de Estado:** Carrega automaticamente as skills que já estavam configuradas no `.agents/skills.json` do workspace para que você possa inspecionar e alternar sem perder o que já havia configurado.
- Gera ou atualiza o manifesto declarativo `.agents/skills.json` e ajusta o `.gitignore`.

---

### Método 2: Declarativo Manual (`.agents/skills.json`)

Se preferir criar o arquivo na mão, basta adicionar o arquivo `.agents/skills.json` na raiz do seu projeto:

```json
{
    "entries": [
        {
            "path": "D:/Bibliotecas/GitHub/agents/skills/stacks",
            "include_only": ["svelte5", "sveltekit"]
        },
        {
            "path": "D:/Bibliotecas/GitHub/agents/skills/planning",
            "include_only": ["writing-plans"]
        },
        {
            "path": "D:/Bibliotecas/GitHub/agents/skills/frontend",
            "include_only": ["frontend-design-principles"]
        }
    ]
}
```

E garantir que a pasta `.agents/` está no seu `.gitignore`:

```text
# .gitignore
.agents/
```
