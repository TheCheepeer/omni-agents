# Repositório de Agentes, Regras e Skills do Antigravity

Repositório centralizado para armazenar, versionar e gerenciar subagentes, regras globais e skills utilizados no Antigravity e VS Code.

## Estrutura do Repositório

```text
agents/
├── agents/
│   ├── accessibility-reviewer.md
│   ├── code-reviewer.md
│   └── security-auditor.md
├── rules/
│   └── AGENTS.md
├── skills/
│   ├── global/                      # Skills transversais aplicadas em todos os projetos
│   │   ├── coding-standards/
│   │   ├── comunicacao-clara/
│   │   ├── crafting-effective-readmes/
│   │   ├── diataxis/
│   │   ├── feature-planning-artifacts/
│   │   ├── frontend-design-principles/
│   │   ├── grug-brained-dev/
│   │   ├── html-artifacts/
│   │   ├── improve/
│   │   ├── improving-prompts/
│   │   ├── reducing-entropy/
│   │   ├── researching-codebases/
│   │   ├── roadmap/
│   │   ├── roadmap-to-improve-plans/
│   │   ├── skill-authoring/
│   │   ├── strategic-roadmap/
│   │   ├── writing/
│   │   ├── writing-cli-skills/
│   │   ├── writing-error-messages/
│   │   └── writing-plans/
│   └── stacks/                      # Skills específicas de tecnologias/ferramentas
│       ├── coolify-compose/
│       ├── jj/
│       ├── rust/
│       ├── salsa/
│       ├── svelte5/
│       └── sveltekit/
└── README.md
```

## Conteúdo

### 1. Subagentes (`agents/`)

- `accessibility-reviewer.md`: Especialista em acessibilidade digital (a11y), diretrizes WCAG 2.1/2.2 (A, AA, AAA) e WAI-ARIA. Realiza auditoria estática de interfaces/componentes, apresenta diagnóstico com impacto assistivo, solicita autorização para correções e opera em loop iterativo controlado.
- `code-reviewer.md`: Especialista em análise de código, padrões de design, Clean Code e melhorias de legibilidade.
- `security-auditor.md`: Especialista em OWASP Top 10 e AppSec. Realiza auditoria estática, emite diagnósticos prévios, pede autorização antes de aplicar correções e executa verificação iterativa com parada controlada.

### 2. Regras Globais (`rules/`)

- `AGENTS.md`: Diretrizes e padrões de desenvolvimento, segurança, comunicação e padrão obrigatório de Tailwind CSS aplicados a todos os projetos.

### 3. Skills do Antigravity (`skills/`)

As habilidades são separadas estrategicamente entre **Globais** e **Específicas por Stack**:

#### A. Skills Globais (`skills/global/`)
Habilidades transversais e agnósticas de tecnologia. Estão conectadas à configuração global do Antigravity e disponíveis em qualquer conversa:
- **Escrita & Comunicação:** `comunicacao-clara`, `writing`, `writing-plans`, `crafting-effective-readmes`, `writing-error-messages`, `diataxis`.
- **Qualidade & Engenharia:** `coding-standards`, `reducing-entropy`, `improve`, `researching-codebases`, `frontend-design-principles`, `grug-brained-dev`.
- **Planejamento & Roadmaps:** `strategic-roadmap`, `roadmap`, `roadmap-to-improve-plans`, `feature-planning-artifacts`.
- **Visualização & Meta-Skills:** `html-artifacts`, `improving-prompts`, `writing-cli-skills`, `skill-authoring`.

#### B. Skills por Stack / Ferramenta (`skills/stacks/`)
Habilidades focadas em linguagens, frameworks ou ferramentas específicas. Não ficam ativas no escopo global para **economizar orçamento de tokens (customization budget)** e evitar poluição de contexto em projetos de outras tecnologias:
- **Linguagens & Frameworks:** `rust`, `salsa`, `svelte5`, `sveltekit`.
- **Ferramentas de Infra & VCS:** `coolify-compose`, `jj`.

---

## Como Usar: Rules, Skills e Agentes

### 1. Regras (Rules) — 100% Automáticas

- **Comportamento:** As regras são injetadas **automaticamente** no contexto do modelo em todas as interações. Você **não** precisa pedir para o agente lê-las.
- **Escopo e Precedência:**
    - **Globais:** Arquivos em `~/.gemini/config/rules/` (como o [`rules/AGENTS.md`](file:///d:/Bibliotecas/GitHub/agents/rules/AGENTS.md)) aplicam-se a todas as sessões em qualquer projeto nesta máquina.
    - **Locais (Workspace):** Arquivos `AGENTS.md` ou `GEMINI.md` na raiz ou em subpastas de um repositório têm precedência sobre as globais para aquele escopo específico.
- **Finalidade:** Padrões inegociáveis, segurança (nunca versionar chaves ou credenciais) e convenções arquiteturais (ex.: Clean Code, uso obrigatório de Tailwind CSS moderno).

### 2. Habilidades (Skills) — Sob Demanda (Divulgação Progressiva)

- **Comportamento:** Para economizar tokens de contexto, as skills **não** são carregadas integralmente de início. O agente recebe apenas um índice contendo o `name` e a `description` de cada uma.
- **Como ativar:**
    - **Automático (Semântico):** Se a sua dúvida ou tarefa coincidir com o propósito descrito em uma skill (ex.: auditar débito técnico ou redigir documentação), o próprio agente detecta a relevância e lê o respectivo `SKILL.md` por conta própria.
    - **Explícito:** Você pode solicitar diretamente no prompt: _"Use a skill strategic-roadmap para analisar o repositório"_.

---

## Como Conectar ao Antigravity no Windows

### 1. Configuração Global (Executar uma vez no PowerShell)

Para vincular este repositório à configuração global do Antigravity no Windows:

```powershell
# Cria junctions para os subagentes e regras globais
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\agents" -Target "D:\Bibliotecas\GitHub\agents\agents"
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\rules" -Target "D:\Bibliotecas\GitHub\agents\rules"

# Vincula SOMENTE a pasta de skills globais (mantendo o orçamento de tokens leve)
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\skills" -Target "D:\Bibliotecas\GitHub\agents\skills\global"
```

> **Nota para atualização:** Se a junction `config\skills` já apontava para a pasta raiz anterior de `skills`, remova o link antigo e recrie apontando para `global`:
> ```powershell
> cmd /c rmdir "C:\Users\User\.gemini\config\skills"
> New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\skills" -Target "D:\Bibliotecas\GitHub\agents\skills\global"
> ```

---

### 2. Como Ativar Skills de Stack em Projetos Específicos

Quando você estiver trabalhando em um projeto que utilize uma das tecnologias de `skills/stacks/` (ex.: Svelte 5 ou Rust), conecte a skill diretamente na pasta do projeto:

#### Opção A: Via Junction (Recomendado - Mantém sincronizado com este repositório)

Abra o PowerShell na raiz do seu projeto e execute:

```powershell
# Cria a pasta .agents\skills no repositório do seu projeto
New-Item -ItemType Directory -Path ".\.agents\skills" -Force

# Exemplo: Ativando Svelte 5 e SvelteKit no projeto atual
New-Item -ItemType Junction -Path ".\.agents\skills\svelte5" -Target "D:\Bibliotecas\GitHub\agents\skills\stacks\svelte5"
New-Item -ItemType Junction -Path ".\.agents\skills\sveltekit" -Target "D:\Bibliotecas\GitHub\agents\skills\stacks\sveltekit"

# Exemplo: Ativando Rust e Salsa em um projeto Rust
New-Item -ItemType Junction -Path ".\.agents\skills\rust" -Target "D:\Bibliotecas\GitHub\agents\skills\stacks\rust"
New-Item -ItemType Junction -Path ".\.agents\skills\salsa" -Target "D:\Bibliotecas\GitHub\agents\skills\stacks\salsa"
```

#### Opção B: Cópia Direta

Se preferir versionar a skill dentro do repositório do projeto:

```powershell
Copy-Item -Recurse "D:\Bibliotecas\GitHub\agents\skills\stacks\svelte5" ".\.agents\skills\"
```
