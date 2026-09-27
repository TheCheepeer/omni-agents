# Repositorio de Agentes, Regras e Skills do Antigravity

Repositorio centralizado para armazenar, versionar e gerenciar subagentes, regras globais e skills utilizados no Antigravity e VS Code.

## Estrutura do Repositorio

```text
agents/
├── agents/
│   ├── accessibility-reviewer.md
│   ├── code-reviewer.md
│   └── security-auditor.md
├── rules/
│   └── AGENTS.md
├── skills/
│   ├── coding-standards/
│   ├── comunicacao-clara/
│   ├── coolify-compose/
│   ├── crafting-effective-readmes/
│   ├── diataxis/
│   ├── feature-planning-artifacts/
│   ├── frontend-design-principles/
│   ├── grug-brained-dev/
│   ├── html-artifacts/
│   ├── improve/
│   ├── improving-prompts/
│   ├── jj/
│   ├── reducing-entropy/
│   ├── researching-codebases/
│   ├── roadmap/
│   ├── roadmap-to-improve-plans/
│   ├── rust/
│   ├── salsa/
│   ├── skill-authoring/
│   ├── strategic-roadmap/
│   ├── svelte5/
│   ├── sveltekit/
│   ├── writing/
│   ├── writing-cli-skills/
│   ├── writing-error-messages/
│   └── writing-plans/
└── README.md
```

## Conteudo

### 1. Subagentes (`agents/`)

- `accessibility-reviewer.md`: Especialista em acessibilidade digital (a11y), diretrizes WCAG 2.1/2.2 (A, AA, AAA) e WAI-ARIA. Realiza auditoria estatica de interfaces/componentes, apresenta diagnostico com impacto assistivo, solicita autorizacao para correcoes e opera em loop iterativo controlado.
- `code-reviewer.md`: Especialista em analise de codigo, padroes de design, Clean Code e melhorias de legibilidade.
- `security-auditor.md`: Especialista em OWASP Top 10 e AppSec. Realiza auditoria estatica, emite diagnosticos prévios, pede autorizacao antes de aplicar correcoes e executa verificacao iterativa com parada controlada.

### 2. Regras Globais (`rules/`)

- `AGENTS.md`: Diretrizes e padroes de desenvolvimento, seguranca e comunicacao aplicados a todos os projetos.

### 3. Skills do Antigravity (`skills/`)

Coleção com 26 skills modulares para capacitar os agentes em fluxos de trabalho avançados, incluindo:

- **Escrita & Comunicação:** `comunicacao-clara`, `writing`, `writing-plans`, `crafting-effective-readmes`, `writing-error-messages`, `diataxis`.
- **Qualidade & Engenharia:** `coding-standards`, `reducing-entropy`, `improve`, `researching-codebases`, `frontend-design-principles`, `grug-brained-dev`.
- **Planejamento & Roadmaps:** `strategic-roadmap`, `roadmap`, `roadmap-to-improve-plans`, `feature-planning-artifacts`.
- **Tecnologias & Ferramentas:** `coolify-compose`, `html-artifacts`, `jj`, `rust`, `salsa`, `svelte5`, `sveltekit`.
- **Meta-Skills & Prompts:** `improving-prompts`, `writing-cli-skills`, `skill-authoring`.

## Como Usar: Rules, Skills e Agentes

Entenda como o Antigravity consome cada componente e como interagir com eles no dia a dia:

### 1. Regras (Rules) — 100% Automáticas

- **Comportamento:** As regras são injetadas **automaticamente** no contexto do modelo em todas as interações. Você **não** precisa pedir para o agente lê-las.
- **Escopo e Precedência:**
    - **Globais:** Arquivos em `~/.gemini/config/rules/` (como o [`rules/AGENTS.md`](file:///d:/Bibliotecas/GitHub/agents/rules/AGENTS.md)) aplicam-se a todas as sessões em qualquer projeto nesta máquina.
    - **Locais (Workspace):** Arquivos `AGENTS.md` ou `GEMINI.md` na raiz ou em subpastas de um repositório têm precedência sobre as globais para aquele escopo específico.
- **Finalidade:** Padrões inegociáveis, segurança (nunca versionar chaves ou credenciais) e convenções arquiteturais (ex.: Clean Code, uso obrigatório de Tailwind CSS moderno).

### 2. Habilidades (Skills) — Sob Demanda (Divulgação Progressiva)

- **Comportamento:** Para economizar tokens de contexto, as skills **não** são carregadas integralmente de início. O agente recebe apenas um índice contendo o `name` e a `description` de cada uma.
- **Como ativar:**
    - **Automático (Semântico):** Se a sua dúvida ou tarefa coincidir com o propósito descrito em uma skill (ex.: revisar componentes Svelte 5, auditar débito técnico ou gerar um compose do Coolify), o próprio agente detecta a relevância e lê o respectivo `SKILL.md` por conta própria.
    - **Explícito:** Você pode solicitar diretamente no prompt: _"Use a skill strategic-roadmap para analisar o repositório"_ ou _"Siga a skill coolify-compose"_.
- **Onde residem:** Pastas em `skills/<nome>/SKILL.md` (globais em `~/.gemini/config/skills/` ou locais em `.agents/skills/`).

### 3. Subagentes (Agents) — Especialistas e Paralelismo

- **Comportamento:** Instâncias auxiliares de IA com papéis e ferramentas específicas para executar tarefas em segundo plano ou em isolamento, evitando poluir o contexto da conversa principal.
- **Como usar:**
    - **Invocação Autônoma:** O agente principal pode acionar subagentes (como `research`) para pesquisas extensas na base de código ou documentação externa.
    - **A seu pedido:** Você pode pedir diretamente: _"Invoque um subagente especialista em segurança para auditar as rotas de autenticação"_.
    - **Personas Customizadas:** Arquivos em `agents/` (ex.: [`accessibility-reviewer.md`](file:///d:/Bibliotecas/GitHub/agents/agents/accessibility-reviewer.md), [`security-auditor.md`](file:///d:/Bibliotecas/GitHub/agents/agents/security-auditor.md)) padronizam o fluxo de auditoria, diagnóstico prévio e correção autorizada.

## Como Conectar ao Antigravity no Windows

Para vincular este repositorio a configuracao global do Antigravity no Windows, execute no PowerShell:

```powershell
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\agents" -Target "D:\Bibliotecas\GitHub\agents\agents"
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\rules" -Target "D:\Bibliotecas\GitHub\agents\rules"
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\skills" -Target "D:\Bibliotecas\GitHub\agents\skills"
```
