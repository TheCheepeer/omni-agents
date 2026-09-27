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
│   ├── coolify-compose/
│   ├── crafting-effective-readmes/
│   ├── diataxis/
│   ├── english-please/
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

- **Escrita & Comunicação:** `english-please`, `writing`, `writing-plans`, `crafting-effective-readmes`, `writing-error-messages`, `diataxis`.
- **Qualidade & Engenharia:** `coding-standards`, `reducing-entropy`, `improve`, `researching-codebases`, `frontend-design-principles`, `grug-brained-dev`.
- **Planejamento & Roadmaps:** `strategic-roadmap`, `roadmap`, `roadmap-to-improve-plans`, `feature-planning-artifacts`.
- **Tecnologias & Ferramentas:** `coolify-compose`, `html-artifacts`, `jj`, `rust`, `salsa`, `svelte5`, `sveltekit`.
- **Meta-Skills & Prompts:** `improving-prompts`, `writing-cli-skills`, `skill-authoring`.

## Como Conectar ao Antigravity no Windows

Para vincular este repositorio a configuracao global do Antigravity no Windows, execute no PowerShell:

```powershell
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\agents" -Target "D:\Bibliotecas\GitHub\agents\agents"
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\rules" -Target "D:\Bibliotecas\GitHub\agents\rules"
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\skills" -Target "D:\Bibliotecas\GitHub\agents\skills"
```
