---
name: html-artifacts
description: >-
    Use quando o usuário solicitar criar, gerar, visualizar ou transformar um material em um artefato HTML independente, relatório .html em arquivo único autocontido, explicação visual interativa, passo a passo visual ou apresentação em slides HTML.
    Ideal para explicar arquitetura de código, funcionalidades, revisões de PR/diff, linhas do tempo de incidentes ou comparações de decisões. Não serve para criar aplicações web completas em produção nem emails HTML.
---

# Artefatos HTML Visuais (HTML Artifacts)

Gere documentos visuais que justifiquem o uso de HTML: o resultado deve ser mais fácil de analisar, comparar ou manipular do que texto puro. O padrão é gerar um arquivo `.html` local e autocontido.

## Diretrizes Fundamentais Não Negociáveis

- **Fundamente-se no código primeiro:** Leia os arquivos de origem e rastreie o comportamento antes de desenhar a interface.
- **Padrão em modo documento:** O documento deve ser completo e claro para leitura assíncrona. Use modo apresentação apenas se solicitado explicitamente.
- **Narrativa estática completa:** A interatividade pode aprofundar a explicação, mas o leitor não deve depender de cliques para descobrir a conclusão principal.
- **Interatividade orientada a dúvidas:** Cada controle deve responder a uma pergunta do leitor: dúvida → ação → resposta visível imediata.
- **Arquivo 100% offline em arquivo único:** Embuta CSS, JavaScript vanilla, SVGs e dados no próprio arquivo. Não dependa de CDNs externas, fontes remotas ou chamadas a servidores.
- **Mantenha local:** O arquivo pode conter dados do código ou arquitetura. Nunca publique externamente sem permissão expressa.
- **Valide o arquivo final:** Certifique-se de que o HTML abre sem erros de script no console.

## Modos de Apresentação

| Modo                     | Finalidade                                                 | Estrutura                                                                                     |
| ------------------------ | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Documento** (Padrão)   | Explicação de código, PR, incidente ou pesquisa            | Leitura contínua, com âncoras estáveis, texto completo, responsivo e amigável para impressão  |
| **Documento Explorável** | Mecanismos causais, simulação de parâmetros e comparativos | Estado padrão completo acompanhado de controles para simular cenários e ver respostas visuais |
| **Apresentação**         | Roteiro guiado para reuniões ou demonstrações              | Um conceito por tela, navegação por teclado e notas de apoio                                  |

## Fluxo de Trabalho

### 1. Definir o Escopo

- Quem lerá este artefato e qual é a dúvida central que ele deve responder?
- Qual é o repositório, branch ou commit de referência?
- O arquivo será temporário ou salvo em pasta de documentação do projeto?

### 2. Mapear as Evidências

- Identifique os arquivos-chave e números de linha envolvidos.
- Diferencie com precisão: fatos **observados no código**, conclusões **inferidas** e melhorias **propostas**.
- Registre incertezas em vez de escondê-las.

### 3. Estruturar a Linha de Leitura

1. Comece direto com a resposta principal ou o objetivo do documento.
2. Forneça o contexto mínimo necessário.
3. Apresente o modelo visual central (fluxo, topologia, comparação ou linha do tempo).
4. Demonstre um exemplo concreto de ponta a ponta.
5. Aponte riscos, limitações e pontos de decisão.
6. Encerre com o índice de fontes e próximas ações recomendadas.

### 4. Estilo Visual Sóbrio e Técnico

Evite poluição visual e clichês de IA:

- Nada de gradientes exagerados ou efeitos de vidro (glassmorphism) desnecessários.
- Nada de animações automáticas ou elementos que piscam sem valor explicativo.
- Nada de diagramas gigantes e confusos: divida em uma visão panorâmica seguida de detalhes focados.
- Use cores para transmitir significado funcional, nunca como mera decoração.

### 5. Implementação Técnica

- Utilize HTML semântico, CSS moderno estruturado e SVGs inline.
- Suporte a acessibilidade: contraste adequado, foco visível no teclado e suporte a `prefers-reduced-motion`.
- Estilos de impressão (`@media print`) limpos para exportação em PDF.
- Higienize strings de código para evitar injeções e quebras de sintaxe.

### 6. Entrega ao Usuário

Após gerar e validar o arquivo, abra-o ou forneça o comando para abrir:

- No Windows: `Start-Process "caminho\para\artefato.html"`
- No Linux/macOS: `xdg-open /caminho/para/artefato.html`

Informe no chat: o caminho absoluto do arquivo, o modo do documento e os principais pontos validados. Não cole o código HTML inteiro no chat.

## Documentos de Apoio

- [references/content-patterns.md](references/content-patterns.md) — Modelos de conteúdo para PRs, fluxos e comparações.
- [references/component-contracts.md](references/component-contracts.md) — Especificações de componentes reutilizáveis e CSS canônico.
- [references/quality-and-validation.md](references/quality-and-validation.md) — Checklist de refinamento visual e acessibilidade.
