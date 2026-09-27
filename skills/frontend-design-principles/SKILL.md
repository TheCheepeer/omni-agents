---
name: frontend-design-principles
description: >-
    Use ao construir ou revisar interfaces frontend (UI) — dashboards, painéis administrativos, landing pages, sites institucionais e aplicações web.
    Orienta decisões de design específicas do domínio (tipografia intencional, universo cromático, tokens semânticos de CSS, layout, profundidade e espaçamento) em vez de entregar designs genéricos de IA.
    Encaminha para referências de produto (app.md) ou marketing (marketing.md) conforme o contexto.
---

# Princípios de Design Frontend (Frontend Design Principles)

Construa interfaces com intenção, identidade e refinamento artesanal.

## Escopo e Roteamento

Após este arquivo, consulte o guia específico para o contexto:

- **`app.md`** — dashboards, painéis administrativos, telas de configurações, ferramentas internas, produtos SaaS e interfaces ricas em dados (tabelas, formulários, listas) onde os usuários trabalham com frequência.
- **`marketing.md`** — landing pages, páginas de conversão, anúncios de produto e peças criativas onde a primeira impressão visual é o fator crítico.

## Por que este processo existe

Modelos de linguagem tendem por padrão a gerar interfaces previsíveis e genéricas — cartões brancos com sombras exageradas e ícones azuis. O processo abaixo força você a tomar decisões intencionais de design antes de escrever o código.

## Onde os Padrões Genéricos se Escondem

- **Tipografia não é apenas um contêiner — ela É o design.** Um sistema de confeitaria artesanal e um terminal financeiro buscam "clareza tipográfica", mas um deve ser caloroso e orgânico enquanto o outro é frio e milimetricamente denso.
- **Navegação não cerca o produto — ela É o produto.** Onde o usuário está, para onde pode ir e o que importa mais. Uma tela isolada sem contexto é apenas uma demo de componente, não um produto real.
- **Dados comunicam significado.** Um anel de progresso e um contador textual podem mostrar "3 de 10"; um conta uma história de evolução, o outro apenas ocupa espaço.
- **Nomes de tokens CSS são decisões de design:** Ao ler apenas as variáveis CSS, deve ser possível adivinhar o universo do produto:

```css
/* ❌ Genérico — poderia ser qualquer projeto clichê */
--gray-700: #333;
--surface-2: #fafafa;

/* ✅ Semântico e alinhado ao domínio */
--ink: #18181b;
--parchment: #fdfbf7;
```

## Etapas Obrigatórias Antes de Gerar Código

Não escreva código de interface antes de resolver:

### 1. Responder às Perguntas de Intenção

- **Quem é este ser humano?** Não diga apenas "usuários". Descreva a pessoa real — em que ambiente ela está, o que estava fazendo antes e o que precisa fazer logo após.
- **Qual é a tarefa a cumprir?** O verbo central: aprovar pagamentos, auditar deploy, tabular faturas.
- **Qual deve ser a sensação da interface?** Fuja do clichê "limpa e moderna". Defina sensações concretas: quente como papel kraft? densa e funcional como uma planilha de Bloomberg? minimalista e afiada como uma lâmina cirúrgica?

### 2. Definir os Quatro Pilares do Design

- **Domínio:** pelo menos 5 conceitos e termos reais do ecossistema do produto.
- **Universo de Cor:** cores que existem naturalmente no mundo físico do produto (ao menos 5 tons).
- **Assinatura:** um elemento único (visual, estrutural ou de microinteração) que só faria sentido neste produto específico.
- **Padrões a Rejeitar:** 3 escolhas óbvias e clichês de UI que você se compromete a NÃO usar nesta tela.

### 3. Confirmar a Direção

Apresente a direção para o usuário antes de despejar centenas de linhas de código, validando se a identidade visual atende à expectativa.

## Testes de Validação da Interface

- **Teste da Substituição:** se você trocar a fonte e as cores pelo padrão cinza/azul do Tailwind/Bootstrap, alguém notaria? Onde a troca passar despercebida é onde faltou intenção.
- **Teste do Desfoque (Squint Test):** aperte os olhos ou desfoque a visão. A hierarquia de pesos e áreas continua nítida?
- **Teste de Assinatura:** aponte exatamente em quais componentes a identidade própria do produto está presente.
- **Teste dos Tokens:** suas variáveis de estilo pertencem à identidade única desta marca ou parecem um template genérico?

## Fundamentos de Acabamento e Refinamento

- **Camadas sutis de elevação:** transições de superfície extremamente suaves e discretas (como visto em Linear, Vercel e Supabase).
- **Bordas elegantes:** bordas finas e sutis que desaparecem até que o olhar busque a estrutura.
- **Cores com propósito:** tons neutros constroem a estrutura; cores de destaque carregam significado. Um destaque intencional vale mais do que cinco cores aleatórias.

## Antipadrões Universais a Evitar

- Sombras projetadas gigantes e escuras (`box-shadow: 0 25px 50px ...` artificial).
- Bordas decorativas muito grossas e chamativas (2px+ aleatórios).
- Múltiplas cores de destaque competindo pela atenção.
- Mistura descuidada de profundidade (sombras pesadas concorrendo com bordas duras).
- Espaçamentos inconsistentes fora de uma escala matemática coerente.

## Documentos de Aprofundamento

- `references/principles.md` — valores concretos de CSS para profundidade, tipografia, espaçamento e modo escuro.
- `app.md` — diretrizes focadas em aplicações SaaS, dashboards e telas de alta densidade.
- `marketing.md` — diretrizes para landing pages e páginas de conversão.
