---
name: crafting-effective-readmes
description: >-
    Use ao redigir, estruturar ou melhorar arquivos README.md.
    Nem todo README tem o mesmo objetivo — fornece modelos e diretrizes adequados ao público-alvo e ao tipo de projeto (código aberto, interno, pessoal ou de configuração).
---

# Criação de READMEs Eficazes (Crafting Effective READMEs)

## Visão Geral

READMEs respondem às dúvidas que o seu público terá. Públicos diferentes exigem informações diferentes — um contribuidor de um projeto Open Source precisa de um contexto muito diferente do que você mesmo daqui a seis meses abrindo uma pasta de configurações.

**Sempre pergunte:** Quem vai ler este arquivo e o que essa pessoa precisa saber para ter sucesso?

## Processo

### Etapa 1: Identificar a Demanda

Identifique qual tarefa de documentação está em andamento:

| Tarefa          | Quando Usar                                                           |
| --------------- | --------------------------------------------------------------------- |
| **Criação**     | Projeto novo, sem nenhum README ainda                                 |
| **Adição**      | Necessidade de documentar um novo recurso, comando ou guia            |
| **Atualização** | Funcionalidades mudaram ou dependências/passos ficaram desatualizados |
| **Revisão**     | Auditoria para validar se o README reflete a realidade do código      |

### Etapa 2: Perguntas Específicas por Tarefa

**Ao criar o README inicial:**

1. Qual é o tipo de projeto? (veja Tipos de Projeto abaixo)
2. Que problema o projeto resolve em uma única frase?
3. Qual é o caminho mais rápido para chegar a "está funcionando" (quickstart)?
4. Há algum pré-requisito ou destaque essencial?

**Ao adicionar uma nova seção:**

1. O que exatamente precisa ser documentado?
2. Onde essa informação se encaixa logicamente na estrutura atual?
3. Quem é o principal interessado nesta seção?

**Ao atualizar conteúdo existente:**

1. O que mudou no código ou na arquitetura?
2. Leia o README atual e aponte as seções obsoletas.
3. Proponha as alterações pontuais sem remover o que ainda é válido.

**Ao revisar e auditar:**

1. Leia o README atual.
2. Compare com os arquivos de configuração reais (`package.json`, `Cargo.toml`, scripts de build).
3. Sinalize discrepâncias ou comandos quebrados.

### Etapa 3: Validação com o Usuário

Ao concluir o rascunho, valide sempre: **"Há mais algum detalhe, restrição de ambiente ou contexto específico que você gostaria de incluir?"**

## Tipos de Projeto

| Tipo                         | Público-Alvo                                 | Seções Principais                                                         | Modelo de Referência      |
| ---------------------------- | -------------------------------------------- | ------------------------------------------------------------------------- | ------------------------- |
| **Open Source**              | Contribuidores e usuários externos           | Instalação, Uso, Como Contribuir, Licença                                 | `templates/oss.md`        |
| **Pessoal**                  | Você no futuro e visitantes de portfólio     | O que faz, Stack técnica, Decisões de design                              | `templates/personal.md`   |
| **Interno / Corporativo**    | Colegas de equipe e novos desenvolvedores    | Setup local, Arquitetura, Runbooks, Variáveis de ambiente                 | `templates/internal.md`   |
| **Configurações / Dotfiles** | Você no futuro (precisando lembrar do setup) | O que está aqui, Por que foi configurado assim, Como estender, Pegadinhas | `templates/xdg-config.md` |

Se o tipo de projeto não for evidente, esclareça antes de assumir um modelo genérico de Open Source.

## Seções Essenciais (Presentes em Todo README)

Todo README precisa, no mínimo:

1. **Nome do Projeto** — Título claro e autoexplicativo
2. **Descrição** — O que é e por que existe, em 1 a 2 frases diretas
3. **Uso / Início Rápido** — Como executar ou usar imediatamente com exemplos concretos

## Documentos de Apoio

- `section-checklist.md` — Checklist de seções recomendadas por tipo de projeto
- `style-guide.md` — Erros comuns em READMEs e orientações de escrita
- `using-references.md` — Guia de aprofundamento e modelos detalhados
