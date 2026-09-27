---
name: coding-standards
description: >-
    Use ao revisar qualidade de código, avaliar se uma refatoração ou design é sólido, identificar code smells ou julgar trade-offs de arquitetura.
    Identifica interfaces rasas, modelos de estado inválidos, fronteiras nebulosas, efeitos colaterais ocultos, contratos fracos de erro, excesso de mocks, abstrações prematuras e código aparentemente limpo que mascara modelos conceituais ruins.
---

# Padrões e Diretrizes de Código (Coding Standards)

> "Assim, programas devem ser escritos para que pessoas os leiam, e apenas incidentalmente para que máquinas os executem."  
> — Abelson e Sussman, _Structure and Interpretation of Computer Programs_

> "A esse respeito, vale destacar que o objetivo de abstrair não é ser vago, mas criar um novo nível semântico no qual se possa ser absolutamente preciso."  
> — Edsger W. Dijkstra, _The Humble Programmer_

Código bom resolve um problema real através de um modelo que seres humanos conseguem entender, usar, alterar e consertar. Ele expressa a verdade na granularidade correta: conceitos nomeados onde importam, estados válidos explícitos, fronteiras bem traduzidas, consequências visíveis, falhas classificadas, comportamento verificado e estruturas desnecessárias deletadas.

Incorpore boas práticas conceituais sem o cerimonial vazio: torne estados ilegais irrepresentáveis (inspirado em linguagens com tipagem forte como Rust); crie módulos de domínio sólidos; construa barreiras anticorrupção nas integrações. Traduza essas ideias para os recursos nativos da linguagem do projeto.

## Princípios Fundamentais

- **Código comunica um modelo mental.** Nomes, tipos, módulos, testes e interfaces devem revelar o que é verdadeiro no domínio de negócio e o que nunca deve acontecer.
- **Represente o significado na granularidade correta.** Torne distinções importantes explícitas; não transforme cada tipo primitivo, detalhe de parser ou artefato de banco em vocabulário de domínio.
- **Torne estados e transições válidas explícitos.** Prefira uniões discriminadas, enums ou máquinas de estado explícitas em vez de flags booleanas cegas, múltiplos campos nulos soltos e dependências temporais implícitas.
- **Construa módulos profundos (Deep Modules).** Encapsule comportamentos coesos atrás de interfaces simples em fronteiras reais. Um wrapper superficial que apenas repassa chamadas só dá outro nome ao mesmo trabalho.
- **Traduza dados nas fronteiras.** Dados externos, persistidos em banco, vindos de APIs ou de frameworks devem ser validados e convertidos (parse, don't validate) para o modelo interno antes de atingirem a lógica central.
- **Torne as consequências e efeitos colaterais visíveis.** E/S, mutabilidade, tempo, requisições de rede, assincronicidade, retentativas e consumo de recursos devem ser evidentes onde afetam o raciocínio.
- **Trate erros como parte integral do design.** Falhas de negócio esperadas pertencem aos contratos da interface; bugs de programação e falhas de infraestrutura exigem diagnóstico e recuperação distintos.
- **Verifique o comportamento real.** Testes devem provar comportamento, invariantes, transições e modos de falha através de fronteiras reais observáveis, e não encenar coreografias de mocks internos frágeis.
- **Delete o que não carrega significado.** Elimine generalizações especulativas, labirintos de indireção, camadas obsoletas e código exclusivo de teste que não protege nenhum contrato real.

## Violações Críticas Não Negociáveis

A menos que haja uma restrição física documentada, trate como falha de design:

- Dados brutos externos fluindo pela lógica de negócio central.
- Estados ilegais ou impossíveis representáveis como valores normais em tempo de execução.
- Detalhes privados de parsing, armazenamento ou infraestrutura vazando para o vocabulário público da API.
- Camada intermediária que apenas repassa chamadas sem agregar valor (pass-through wrapper apresentado como "arquitetura").
- Efeitos colaterais graves ou falhas esperadas ocultos de quem chama a função.
- Testes que provam apenas o arranjo de mocks e espiões em vez do resultado observável.

## Falácias Comuns a Rejeitar

- **"O dado já foi validado antes":** Faça o parsing na fronteira e passe o tipo refinado para dentro. Impeça que código interno possa ser chamado com o formato errado.
- **"Este é apenas o formato do banco/API":** Formatos de borda devem ficar na borda; não os deixe contaminar o modelo de domínio sem necessidade.
- **"O código antigo lança exceção solta, então lancei também":** Mantenha compatibilidade externa onde obrigatório, mas isole internamente novas lógicas diferenciando falhas esperadas de falhas críticas.
- **"Essa interface nos dá flexibilidade futura":** Uma abstração só se justifica quando há variação real de comportamento, tradução de fronteira ou necessidade legítima de substituição em testes.
- **"Mocks isolam o código":** Mocks excessivos geralmente isolam as coisas erradas e quebram ao menor refactor inofensivo. Prefira focar em entradas e saídas observáveis.
- **"Um comentário de supressão de linter/tipo resolve":** Supressões exigem justificativa estrita e invariante de segurança demonstrada.

## Como Conduzir uma Revisão

1. **Entenda o contexto do código local.** Siga as convenções existentes quando elas comunicam bem o modelo; mude-as conscientemente quando perpetuam um modelo falho.
2. **Classifique a preocupação:** modelo de domínio, estado, modularidade, fronteiras, efeitos, erros, testes ou complexidade.
3. **Identifique o ônus para quem chama ou mantém o código.**
4. **Proponha a menor alteração honesta.** Não simplifique mentindo sobre os requisitos; não hipermodele a ponto de obscurecer a intenção.
5. **Verifique o comportamento com testes confiáveis.**
6. **Remova andaimes obsoletos.**

Um apontamento de revisão só é válido se indicar o trecho concreto, o impacto real para quem mantém, o princípio violado e a menor solução viável.

## Mapa de Referências Aprofundadas

Para análises detalhadas, consulte apenas os arquivos relevantes em `references/`:

| Tópico                                                 | Documento de Apoio                                               |
| ------------------------------------------------------ | ---------------------------------------------------------------- |
| Vocabulário e termos compartilhados                    | [`references/vocabulary.md`](references/vocabulary.md)           |
| Modelagem de domínio e granularidade                   | [`references/domain-modeling.md`](references/domain-modeling.md) |
| Flags, campos nulos, combinações inválidas e estados   | [`references/state.md`](references/state.md)                     |
| Módulos profundos, limites e responsabilidades         | [`references/modules.md`](references/modules.md)                 |
| Fronteiras de API/Banco, parsing, DTOs e validação     | [`references/boundaries.md`](references/boundaries.md)           |
| Efeitos colaterais, mutações, async e idempotência     | [`references/effects.md`](references/effects.md)                 |
| Tratamento de erros esperados vs bugs e diagnósticos   | [`references/error-handling.md`](references/error-handling.md)   |
| Testes comportamentais vs mocks frágeis                | [`references/verification.md`](references/verification.md)       |
| Complexidade excessiva, overengineering e indireções   | [`references/complexity.md`](references/complexity.md)           |
| Manutenibilidade, refatoração segura e compatibilidade | [`references/maintainability.md`](references/maintainability.md) |
