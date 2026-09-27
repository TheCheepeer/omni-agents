# Diretrizes Globais de Desenvolvimento

Este arquivo define padroes e regras que devem ser seguidos pelos agentes em qualquer projeto.

## Principios Gerais

- Seguir os principios de Clean Code e arquitetura solida.
- Manter o foco em seguranca, performance e manutenibilidade.
- Respeitar a integridade de documentacao e comentarios existentes.

## Seguranca

- Nunca incluir credenciais, chaves de API, senhas ou tokens sensiveis no codigo.
- Tratar e sanitizar todas as entradas de usuario.
- Seguir as recomendacoes do padrao OWASP Top 10.

## Comunicacao e Estilo

- Respostas diretas, claras e objetivas.
- Manter consistencia de estilo com o codigo preexistente do projeto.
- **Proibição Absoluta de Emojis:** Jamais utilizar emojis em nenhuma circunstância (seja em respostas, comentários de código, documentações, commits ou mensagens do sistema). Manter a comunicação estritamente textual, limpa e profissional.

## Frontend e Estilizacao (Tailwind CSS)

- **Padrao Obrigatorio:** Todo desenvolvimento web/frontend deve utilizar **Tailwind CSS** para estilizacao.
- **Versao Mais Recente e Estavel:**
  - Sempre adotar a versao mais recente e estavel disponivel.
  - O agente deve checar a versao oficial mais recente diretamente no site oficial [tailwindcss.com](https://tailwindcss.com) ou no registro do npm antes de criar projetos novos.
  - Para versoes v4+, utilizar a configuracao moderna baseada em CSS nativo (`@import "tailwindcss";` e diretivas `@theme`), evitando criar arquivos de configuracao legados (`tailwind.config.js`) a menos que o projeto preexistente ja utilize v3.
- **Proibicao de CSS Solto e CSS-in-JS:** Nao criar arquivos de estilos separados (`.css`, `.scss`) nem instalar bibliotecas de CSS-in-JS (como styled-components ou emotion), a menos que explicitamente solicitado pelo usuario ou preexistente no projeto.
- **Composicao Dinamica:** Para combinacao condicional de classes utilitarias, sempre padronizar com utilitarios como `clsx` e `tailwind-merge` (funcao `cn(...)`).
- **Acessibilidade e Estados:** Garantir aneis de foco visiveis (`focus-visible:ring-*`), suporte a leitores de tela (`sr-only`) e estados interativos claros (`hover:`, `active:`, `disabled:`).

