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
│   └── link-skill.ps1               # Helper para vincular skills a qualquer projeto
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
> ```powershell
> cmd /c rmdir "C:\Users\User\.gemini\config\skills"
> New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\skills" -Target "D:\Bibliotecas\GitHub\agents\skills\global"
> ```

---

## Como Selecionar e Ativar Skills por Projeto (Workspace Target)

Você tem **três maneiras simples** de ativar skills específicas em um repositório de trabalho sem precisar sujar sua configuração global.

### Método 1: Script Automático (Recomendado - Mais Rápido)

Utilize o script [`scripts/link-skill.ps1`](file:///d:/Bibliotecas/GitHub/agents/scripts/link-skill.ps1) fornecido neste repositório. Ele localiza a skill em qualquer categoria da biblioteca e cria o link simbólico na pasta `.agents/skills` do projeto alvo:

```powershell
# Estando dentro do repositório 'agents', passe o caminho do seu projeto e as skills desejadas:
.\scripts\link-skill.ps1 -ProjectPath "D:\Projetos\meu-app" -Skill svelte5, sveltekit, frontend-design-principles

# Ou, se o PowerShell já estiver aberto na raiz do seu projeto:
D:\Bibliotecas\GitHub\agents\scripts\link-skill.ps1 -Skill rust, salsa, writing-plans
```

---

### Método 2: Declarativo Nativo (`.agents/skills.json`)

O Antigravity possui suporte nativo a arquivos de configuração JSON no workspace. Esse método é ideal caso você queira versionar no Git quais skills o seu projeto utiliza, sem depender de criar pastas ou Junctions no sistema de arquivos.

Crie um arquivo chamado `.agents/skills.json` na raiz do seu projeto:

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

O Antigravity lerá esse manifesto automaticamente ao abrir o projeto e carregará apenas as skills declaradas no `include_only`.

---

### Método 3: Junction Manual no PowerShell

Se preferir rodar manualmente no terminal na raiz do projeto:

```powershell
# Cria a pasta .agents/skills no projeto
New-Item -ItemType Directory -Path ".\.agents\skills" -Force

# Conecta uma skill apontando o Target para a pasta correspondente
New-Item -ItemType Junction -Path ".\.agents\skills\svelte5" -Target "D:\Bibliotecas\GitHub\agents\skills\stacks\svelte5"
New-Item -ItemType Junction -Path ".\.agents\skills\writing-plans" -Target "D:\Bibliotecas\GitHub\agents\skills\planning\writing-plans"
```
