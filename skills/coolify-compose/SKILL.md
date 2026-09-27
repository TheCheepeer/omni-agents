---
name: coolify-compose
description: >-
    Converta arquivos Docker Compose padrão em modelos (templates) compatíveis com o Coolify.
    Use ao criar serviços para o Coolify, converter docker-compose.yml para implantação no Coolify, configurar variáveis mágicas de credenciais e URL (SERVICE_URL, SERVICE_PASSWORD) ou diagnosticar erros em stacks do Coolify.
---

# Docker Compose no Coolify (Coolify Compose)

Converta arquivos padrão do Docker Compose em modelos compatíveis com o Coolify, com geração automática e segura de credenciais, roteamento dinâmico de URLs e deploy simplificado.

## Dois Modos de Implantação

O Coolify suporta duas formas de implantar arquivos compose:

### 1. Compose Direto (Raw Mode — Colar YAML)

Você cola o YAML diretamente na interface do Coolify.

- **Suporta:** `image:`, variáveis mágicas do Coolify, âncoras YAML (`&`, `*`), arquivos embutidos via `content:`.
- **Não suporta:** diretiva `build:` (exige imagens pré-compiladas), arquivos de configuração externos no disco.
- **Uso ideal:** deploys rápidos, serviços prontos do Docker Hub sem customização de imagem.

### 2. Modo Repositório Git (Git Repository Mode)

Você aponta o Coolify para um repositório Git contendo o `compose.yml` e o código.

- **Suporta tudo do Docker Compose padrão:** `build:` a partir de Dockerfile, montagem de arquivos locais com caminhos relativos, variáveis mágicas do Coolify e múltiplos serviços integrados.
- **Uso ideal:** aplicações próprias com Dockerfile customizado, projetos complexos com arquivos de configuração no repositório.

## Início Rápido

Todo template do Coolify deve iniciar com metadados de cabeçalho e variáveis mágicas:

```yaml
# documentation: https://exemplo.com/docs
# slogan: Descrição concisa do serviço
# category: backend
# tags: api, database, docker
# logo: svgs/meu-servico.svg
# port: 3000

services:
    app:
        image: meurepositorio/app:latest
        environment:
            - SERVICE_URL_APP_3000 # Gera a URL pública e configura o proxy reverso para a porta 3000
            - DATABASE_URL=postgres://${SERVICE_USER_POSTGRES}:${SERVICE_PASSWORD_POSTGRES}@db:5432/meubanco
        depends_on:
            db:
                condition: service_healthy
        healthcheck:
            test:
                [
                    "CMD",
                    "wget",
                    "-q",
                    "--spider",
                    "http://localhost:3000/health",
                ]
            interval: 5s
            timeout: 10s
            retries: 10

    db:
        image: postgres:16-alpine
        environment:
            - POSTGRES_USER=$SERVICE_USER_POSTGRES
            - POSTGRES_PASSWORD=$SERVICE_PASSWORD_POSTGRES
        healthcheck:
            test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER}"]
            interval: 5s
            timeout: 10s
            retries: 10
```

## Checklist de Conversão

Ao converter um `docker-compose.yml` tradicional:

1. **Substitua senhas fixas por variáveis mágicas:**
    - Troque `POSTGRES_PASSWORD=senha123` por `POSTGRES_PASSWORD=$SERVICE_PASSWORD_POSTGRES`.
2. **Substitua URLs por variáveis mágicas:**
    - Adicione `- SERVICE_URL_APP_3000` e use `APP_URL=$SERVICE_URL_APP`.
3. **Remova a seção `ports:` de serviços com proxy:**
    - O Traefik embutido do Coolify gerencia o roteamento de portas. Mantenha `ports:` apenas se precisar expor portas TCP/UDP diretas (como SSH ou portas não-HTTP).
4. **Adicione Healthchecks obrigatórios:**
    - O Coolify usa healthchecks para saber quando o container está pronto e rotear o tráfego sem downtime.
5. **Configure `depends_on` com condição de saúde:**
    - Use `condition: service_healthy` em vez de dependência simples de inicialização.

## Referência de Variáveis Mágicas

O Coolify gera valores automáticos baseados no padrão `SERVICE_<TIPO>_<IDENTIFICADOR>`:

| Tipo          | Exemplo                    | Valor Resultante                                     |
| ------------- | -------------------------- | ---------------------------------------------------- |
| `PASSWORD`    | `SERVICE_PASSWORD_DB`      | Senha aleatória segura                               |
| `PASSWORD_64` | `SERVICE_PASSWORD_64_KEY`  | Senha aleatória de 64 caracteres                     |
| `USER`        | `SERVICE_USER_ADMIN`       | Nome de usuário aleatório de 16 caracteres           |
| `BASE64_64`   | `SERVICE_BASE64_64_SECRET` | String aleatória de 64 caracteres                    |
| `HEX_32`      | `SERVICE_HEX_32_KEY`       | Chave hexadecimal de 64 caracteres                   |
| `URL`         | `SERVICE_URL_APP_3000`     | Declaração da URL + proxy na porta 3000              |
| `FQDN`        | `SERVICE_FQDN_APP`         | Apenas o domínio (`app.exemplo.com`), sem `https://` |

> [!IMPORTANT]
> **Atenção à sintaxe de declaração vs referência:**
>
> - Declare COM a porta: `- SERVICE_URL_APP_3000`
> - Referencie SEM a porta: `APP_URL=$SERVICE_URL_APP`
> - Use hifens e não sublinhados antes do número da porta: `SERVICE_URL_MEU-APP_3000` (correto).

## Extensões Nativas do Coolify

### Criar Diretório Automaticamente

```yaml
volumes:
    - type: bind
      source: ./data
      target: /app/data
      is_directory: true
```

### Criar Arquivo Embutido com Conteúdo (`content:`)

Útil no modo direto (sem Git) para injetar configurações:

```yaml
volumes:
    - type: bind
      source: ./config.json
      target: /app/config.json
      content: |
          {"chave": "${SERVICE_PASSWORD_APP}"}
```

### Excluir do Health Check (Containers de Migração)

Para containers efêmeros que rodam scripts e encerram:

```yaml
services:
    migrate:
        command: ["npm", "run", "migrate"]
        exclude_from_hc: true
```

## Solução de Problemas Frequentes

- **Erro "No Available Server":** Verifique os logs e se o healthcheck está configurado e respondendo com status 200/0.
- **Variáveis não aparecem na interface:** Utilize a sintaxe com chaves `${VAR}` para torná-las editáveis na UI do Coolify.
- **Roteamento de porta não funciona:** Certifique-se de que a porta no `SERVICE_URL_APP_PORTA` corresponde exatamente à porta em que a aplicação escuta dentro do container, e remova a diretiva `ports:`.

## Documentos de Apoio

- [references/magic-variables.md](references/magic-variables.md) — Lista completa de todos os tipos de variáveis mágicas.
- [references/categories.md](references/categories.md) — Categorias oficiais válidas para o cabeçalho.
