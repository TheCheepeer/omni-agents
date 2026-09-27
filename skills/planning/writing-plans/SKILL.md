---
name: writing-plans
description: >-
    Escreva arquivos de planos de implementação autocontidos que um executor independente (mesmo outro modelo ou sessão limpa) consiga executar sem o contexto prévio do autor.
    Divide o trabalho em planos do tamanho de um Pull Request, com portões de verificação (testes/lint), condições de PARADA (STOP conditions) e protocolo de memorandos para bifurcações de design.
    Use ao ser solicitado a escrever ou criar planos, transformar especificações/tickets em planos de execução ou quando outra skill transferir o planejamento. Não serve para decidir arbitrariamente o que construir nem para executar diretamente.
---

# Elaboração de Planos de Implementação (Writing Plans)

Você está escrevendo planos para um executor que não viu esta conversa, não acompanhou a exploração prévia da base de código e não conhece planos irmãos — podendo inclusive ser um modelo mais leve ou uma nova sessão limpa. Escreva sempre pensando nesse executor: o contexto da sessão se perde ao reiniciar, e um plano detalhado custa apenas uma leitura rápida, enquanto um plano ambíguo inviabiliza a execução correta.

Planos são **baseados em intenção: resultados acima de prescrições rígidas**. Especifique o que deve ser verdadeiro ao final, aponte os arquivos e símbolos exatos, indique arquivos exemplares existentes no projeto para serem imitados e estabeleça um comando de verificação para cada etapa. Dê ao executor clareza do objetivo e espaço para aplicar a melhor implementação técnica.

Esta skill inicia quando o _escopo_ ("o quê") já foi decidido, pelo menos em linhas gerais — um pedido do usuário, um ticket, um RFC ou alinhamento de design. Ela não é responsável pela ideação inicial ou debate arquitetural do zero. Se faltar uma decisão para o plano, investigue primeiro na base de código; apenas dúvidas que não puderem ser resolvidas pelo código devem ser perguntadas ao usuário — uma por vez, com sua recomendação clara.

Durante o planejamento, escreva apenas no diretório de destino dos planos. Não altere o código-fonte da aplicação enquanto estiver planejando.

## Onde os planos devem ser salvos

Resolva o destino nesta ordem de precedência (use o primeiro que existir):

1. Convenção explícita do projeto — diretório existente com planos ou caminho indicado em `GEMINI.md` ou `AGENTS.md`.
2. Variável de ambiente `$AGENTS_PLANS_DIR`, se definida.
3. `./docs/plans/`, caso a pasta `./docs/` exista.
4. `./plans/` (crie o diretório se não existir).
5. Se não estiver claramente dentro de um projeto, pergunte ao usuário.

## Reconhecimento Prévio (Recon)

Antes de redigir qualquer plano, descubra o que todo plano precisa conter:

- **Comandos exatos de build, teste, lint e typecheck** — verificados na configuração real do repositório (`package.json`, `justfile`, `Makefile`, `noxfile`, CI), sem adivinhar. Eles serão os portões de verificação de cada etapa.
- **Convenções e arquivos exemplares** — tratamento de erros, nomenclatura, estrutura de testes, com pelo menos um arquivo de exemplo real para cada padrão que o executor deverá seguir.
- **VCS em uso e a revisão atual.** Registre no plano a versão/commit base e um comando de checagem de divergência (diff dos caminhos afetados).

Se o repositório não tiver comandos de verificação funcionando, aponte isso — configurar um portão de verificação pode precisar ser o primeiro plano.

## Decomposição do Trabalho

**Um plano = uma alteração independente e revisável** — aproximadamente o tamanho de um Pull Request coeso, deixando a base de código estável e os testes passando ao término. Se a demanda for maior, divida-a em múltiplos planos numerados, explicitando as dependências (planos preparatórios que preparam o terreno antes da alteração principal).

Você decide como fatiar o trabalho em unidades entregáveis; você não decide unilateralmente o escopo do que deve ser feito.

## Estrutura de Arquivos

Dimensione a estrutura ao tamanho do esforço:

- **Plano único**: arquivo único em `<destino>/<slug-do-plano>.md`. Sem índice nem numeração.
- **Múltiplos planos**: subdiretório próprio — `<destino>/<slug-do-esforco>/NNN-<slug-da-etapa>.md` com um `README.md` que serve de índice. A numeração é sequencial, monotônica e nunca renumerada; a ordem de execução fica no índice.
- Memorandos (memos) ficam ao lado dos planos como `memo-<slug>.md`.

## Redação

Consulte [references/plan-template.md](references/plan-template.md) antes de redigir o primeiro plano. Para projetos multiplano, escreva o índice por último usando [references/index-template.md](references/index-template.md).

Código nos planos: **esboços e assinaturas em vez de implementações completas**. Pseudocódigo, assinaturas de funções, tipos e interfaces comunicam a intenção sem fingir que foram testados em runtime. Códigos em prosa excessivamente longos envelhecem rápido e podem induzir o executor a copiar erros literais. Escreva código integral apenas quando houver um requisito rígido inevitável, indicando o ponteiro `arquivo:linha` de referência.

## Protocolo de Memos: Decisões Durante a Execução

Planos que encontrem bifurcações imprevistas durante a execução acionam o protocolo de memorandos:

- **Parte do executor**: embutida em cada plano (as condições de PARADA / STOP conditions). Ao encontrar uma decisão arquitetural não prevista, o executor para e registra o estado atual, objetivo e dúvidas pendentes.
- **Sua parte**: ao receber o retorno da dúvida, investigue a base de código, elabore um `memo-<slug>.md` ao lado dos planos usando [references/memo-template.md](references/memo-template.md) — veredito primeiro, evidências com `arquivo:linha`, alternativas descartadas — e então ajuste ou crie os planos afetados, registrando no índice.

## Reconciliação de Planos Existentes

Antes de escrever, leia o diretório de destino. Se já existirem planos para esse esforço, reconcilie em vez de duplicar: modifique os planos existentes se for adição direta, marque planos superados no índice e numere o novo trabalho na sequência.
