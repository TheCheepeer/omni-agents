---
name: jj
description: >-
    Jujutsu (jj) — o sistema de controle de versão moderno compatível com Git.
    Ative SOMENTE quando um diretório .jj/ estiver presente no projeto ou quando jj/jujutsu for citado explicitamente pelo usuário. NÃO ative em repositórios Git comuns sem a pasta .jj/.
    Use para qualquer operação de VCS em projetos gerenciados por jj: commit, push, pull, branch, bookmark, rebase, squash, merge, diff, log, status, cópia de trabalho (working copy), Change ID, revsets e workspaces.
compatibility: "Requer um repositório gerenciado pelo Jujutsu (.jj/ presente na raiz do projeto)"
metadata:
    version: "1.0.0"
    requires-path: ".jj/"
---

# Controle de Versão com Jujutsu (jj)

Jujutsu é um sistema de controle de versão moderno, totalmente compatível com Git, que possui commits mutáveis, rastreamento automático de arquivos e um histórico de operações (`operation log`) que torna qualquer ação reversível.

**Versão alvo: jj 0.36+**

## Modelo Mental do Jujutsu

1. **A cópia de trabalho já é um commit (`@`).** Não existe área de staging (`git add`). Qualquer alteração salva em arquivo é imediatamente registrada no commit atual (`@`) ao rodar qualquer comando do `jj`.
2. **Change IDs são estáveis; Commit IDs mudam.** Cada commit tem dois identificadores:
    - **Change ID:** estável mesmo após rebases, squashes e reescritas de histórico (identificado por letras de k a z, ex: `tqpwlqmp`). **Sempre prefira usar Change IDs.**
    - **Commit ID:** hash de conteúdo SHA (muda a cada reescrita, equivale ao commit hash do Git).
3. **Histórico é naturalmente mutável.** Commits podem ser reescritos sem medo; os commits filhos sofrem rebase automático. Versões antigas ficam salvas no histórico de operações (`jj op log`).
4. **Bookmarks não são branches do Git.** Bookmarks não avançam sozinhos quando você cria novos commits. Eles acompanham reescritas, mas devem ser movidos explicitamente antes de fazer push.
5. **Conflitos não travam o trabalho.** O Jujutsu permite criar commits com conflitos de mesclagem. Você pode resolver os marcadores de conflito com calma quando quiser, sem interromper o fluxo.

## Regras Obrigatórias para Agentes Automatizados

1. **Sempre passe `-m` para mensagens.** Nunca execute comandos interativos que abram o editor de texto do terminal (`nano`, `vim`). Comandos que exigem `-m`: `jj new -m "..."`, `jj describe -m "..."`, `jj commit -m "..."`, `jj squash -m "..."`.
2. **Evite comandos interativos.** Comandos como `jj split` (sem especificar arquivos) ou `jj squash -i` congelam a execução. Especifique sempre os caminhos de arquivo explicitamente.
3. **Verifique o estado após mutações.** Execute `jj st` após qualquer operação de `squash`, `rebase`, `abandon` ou `restore`.
4. **Use aspas simples em revsets:** Sempre use aspas: `jj log -r 'mine() & ::@'`.

## Fluxo de Trabalho Diário

O ciclo de desenvolvimento: **descrever → programar → novo commit → repetir.**

```bash
jj describe -m "feat: adicionar validacao de usuario"
# edite os arquivos normalmente — sao rastreados automaticamente sem precisar de add
jj st && jj diff
jj new -m "feat: adicionar tratamento de erros"
```

### Limpar e Organizar o Histórico

```bash
jj squash -m "feat: mensagem limpa final"  # une a copia de trabalho ao commit pai
jj absorb                                   # distribui os hunks automaticamente para os ancestrais corretos
jj abandon @                               # descarta um experimento que deu errado
```

### Enviar Alterações para o Remoto (GitHub/GitLab)

```bash
jj bookmark set minha-feature -r @
jj git push -b minha-feature
```

## Tabela de Comandos Essenciais

| Ação                           | Comando Jujutsu                                                  |
| ------------------------------ | ---------------------------------------------------------------- |
| Verificar status               | `jj st`                                                          |
| Ver diff / log                 | `jj diff` / `jj log`                                             |
| Descrever commit atual         | `jj describe -m "mensagem"`                                      |
| Iniciar novo commit            | `jj new -m "descricao da tarefa"`                                |
| Editar commit antigo           | `jj edit <change-id>`                                            |
| Unir com commit pai            | `jj squash`                                                      |
| Distribuir alterações nos pais | `jj absorb`                                                      |
| Descartar commit               | `jj abandon <change-id>`                                         |
| Desfazer última operação       | `jj undo`                                                        |
| Ver histórico de operações     | `jj op log`                                                      |
| Restaurar estado anterior      | `jj op restore <op-id>`                                          |
| Criar/mover bookmark           | `jj bookmark create <nome> -r @` / `jj bookmark set <nome> -r @` |
| Sincronizar com remoto         | `jj git push -b <bookmark>` / `jj git fetch`                     |

## Como Recuperar Estados Anteriores (Undo)

```bash
jj undo                      # desfaz a ultima operacao realizada
jj op log                    # lista todas as operacoes recentes com seus IDs
jj op restore <op-id>        # volta a base exatamente para como estava naquele op-id
jj evolog -r <change-id>     # mostra a evolucao historica de uma mudanca especifica
```

## Identificação de Repositórios

- Pasta `.jj/` presente = repositório Jujutsu.
- Pastas `.jj/` e `.git/` juntas = repositório colocalizado (colocated). Use sempre comandos `jj`. O aviso de "HEAD desacoplada" do Git é normal nesses repositórios; o estado real é o exibido por `jj log`.

## Documentos de Apoio

- [references/git-to-jj.md](references/git-to-jj.md) — Dicionário de tradução de comandos do Git para o Jujutsu.
- [references/bookmarks.md](references/bookmarks.md) — Guia completo de bookmarks e integração com GitHub.
- [references/conflicts.md](references/conflicts.md) — Resolução de conflitos no Jujutsu.
- [references/revsets.md](references/revsets.md) — Linguagem de consulta e filtros (revsets).
