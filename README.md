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

## Configuração Global do Antigravity (Windows)

Execute uma única vez no PowerShell para vincular as regras, subagentes e o core de skills globais:

```powershell
# Cria junctions para os subagentes e regras globais
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\agents" -Target "D:\Bibliotecas\GitHub\agents\agents"
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\rules" -Target "D:\Bibliotecas\GitHub\agents\rules"

# Vincula EXCLUSIVAMENTE a pasta global de skills
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\skills" -Target "D:\Bibliotecas\GitHub\agents\skills\global"
```

> **Se precisar atualizar uma junction já existente:**
>
> ```powershell
> cmd /c rmdir "C:\Users\User\.gemini\config\skills"
> New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\skills" -Target "D:\Bibliotecas\GitHub\agents\skills\global"
> ```

---

## Como Selecionar e Ativar Skills por Projeto (Workspace Target)

Você pode escolher e ativar as skills, subagentes e regras de forma totalmente declarativa ou automática.

### Método 1: Configurador Automático Multiplataforma (Recomendado)

O script [`scripts/configure_workspace.py`](file:///d:/Bibliotecas/GitHub/agents/scripts/configure_workspace.py) roda nativamente em **Windows e Linux**, sem precisar instalar nenhuma biblioteca adicional (usa a biblioteca padrão do Python):

```bash
# Execute no terminal:
python scripts/configure_workspace.py
```

#### O que o script faz:

1. **Janela de Seleção:** Abre automaticamente uma janela gráfica nativa do sistema operacional para você selecionar a pasta do seu repositório alvo (ou aceita o argumento `-t /caminho/do/projeto`).
2. **Escaneamento Dinâmico de Categorias:** Lê a pasta `skills/` e identifica automaticamente as categorias existentes com base no nome das pastas (`stacks`, `planning`, `docs`, `frontend`, `meta`, etc.), além dos `agents` e `rules`.
3. **Seleção Interativa:** Exibe um menu numerado no terminal permitindo selecionar:
    - Por números (ex.: `1, 4, 12`)
    - Por categorias inteiras (ex.: `stacks, planning`)
    - Ou selecionar tudo com `all`
4. **Gera o Manifesto Declarativo:** Cria o arquivo `.agents/skills.json` no projeto alvo apontando para as categorias e skills escolhidas.
5. **Copia Agentes e Regras:** Se você selecionou subagentes ou regras, copia os arquivos `.md` correspondentes para `.agents/agents/` e `.agents/rules/`.
6. **Atualiza o `.gitignore`:** Verifica se o arquivo `.gitignore` do projeto alvo já ignora `.agents/`. Se não estiver ignorando, adiciona a linha automaticamente.

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
