# Repositorio de Agentes e Regras do Antigravity

Repositorio centralizado para armazenar, versionar e gerenciar subagentes e regras globais utilizados no Antigravity e VS Code.

## Estrutura do Repositorio

```text
agents/
├── agents/
│   ├── code-reviewer.md
│   └── security-auditor.md
├── rules/
│   └── AGENTS.md
└── README.md
```

## Conteudo

### 1. Subagentes (`agents/`)

- `code-reviewer.md`: Especialista em analise de codigo, padroes de design, Clean Code e melhorias de legibilidade.
- `security-auditor.md`: Especialista em OWASP Top 10 e AppSec. Realiza auditoria estatica, emite diagnosticos prévios, pede autorizacao antes de aplicar correcoes e executa verificacao iterativa com parada controlada.

### 2. Regras Globais (`rules/`)

- `AGENTS.md`: Diretrizes e padroes de desenvolvimento, seguranca e comunicacao aplicados a todos os projetos.

## Como Conectar ao Antigravity no Windows

Para vincular este repositorio a configuracao global do Antigravity no Windows, execute no PowerShell:

```powershell
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\agents" -Target "D:\Bibliotecas\GitHub\agents\agents"
New-Item -ItemType Junction -Path "C:\Users\User\.gemini\config\rules" -Target "D:\Bibliotecas\GitHub\agents\rules"
```
