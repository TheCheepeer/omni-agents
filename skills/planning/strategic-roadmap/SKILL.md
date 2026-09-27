---
name: strategic-roadmap
description: >-
    Use quando o usuário perguntar "no que devo trabalhar neste repositório?", "o que vale a pena fazer a seguir?", pedir auditoria de repositório, prioridades de débito técnico, arquitetura ou descoberta estratégica de oportunidades fundamentadas no código.
    Gera o artefato de roadmap com sequenciamento Agora/Próximo/Depois (Now/Next/Later), itens descartados com justificativa e recomendação do próximo artefato. Não é para roadmaps comerciais comuns de produto.
---

# Roadmap Estratégico do Repositório (Strategic Roadmap)

Gere o planejamento do trabalho que realmente vale a pena ser executado em um repositório. Trata-se de uma etapa de julgamento sênior baseada em auditoria: minere a documentação do projeto, planos antigos, branches ativas e a arquitetura do código; analise oportunidades nas diversas categorias de melhoria; expanda as ideias trazidas pelo usuário; gere oportunidades não óbvias; descarte ideias de baixo valor e sequencie o trabalho mais vantajoso.

Trate este trabalho como meta-engenharia: prefira melhorias estruturais que aprimorem os ciclos futuros de trabalho, a verificação automatizada, as fronteiras de autonomia e a qualidade da base de código em vez de apenas tarefas pontuais.

## Fontes e Referências

Antes de produzir o roadmap, utilize as skills e referências correspondentes:

- `improve` para auditoria orientada a evidências e vereditos de "não vale a pena fazer agora".
- `coding-standards` como fonte canônica de vocabulário e padrões arquiteturais (módulos profundos, limites de estado, tradução de fronteira).
- Documentação do projeto: `GEMINI.md`, `AGENTS.md`, `README.md`, ADRs e issues abertas.

## Fluxo de Trabalho

### 1. Definir o Escopo e os Objetivos do Repositório

- Identifique o repositório específico e os artefatos existentes.
- Defina o que significa "melhor" para este projeto: valor para o usuário final, velocidade de entrega, robustez da verificação de testes, redução de complexidade ou confiabilidade operacional.
- Inclua as ideias trazidas pelo usuário como pontos de partida, e não como a lista definitiva.
- Se o objetivo principal não estiver nítido, faça uma pergunta breve de alinhamento antes de classificar os itens.

### 2. Reconhecimento sem Alterações

- Leia o contexto e planos existentes antes de julgar.
- Identifique comandos de teste e build, branches ativas e áreas de maior alteração recente no Git.
- **Não altere código-fonte.** Produza apenas o artefato de roadmap.
- Se credenciais ou segredos forem encontrados, cite apenas o caminho e a linha; nunca transcreva valores sensíveis.

### 3. Auditoria de Oportunidades

- Avalie as categorias fundamentais: corretude/bugs, segurança, performance, testes, débito técnico, migrações, ferramentas e documentação.
- Identifique decisões que a equipe fica rediscutindo repetidamente; proponha políticas estáveis ou ADRs para consolidar o alinhamento.
- Use critérios objetivos de arquitetura: onde o entendimento exige pular entre dezenas de arquivos, onde a interface é quase tão complexa quanto a implementação interna e onde fronteiras vazam detalhes.
- Não proponha interfaces finais nesta fase: registre o atrito, a direção recomendada e o próximo artefato de planejamento.

### 4. Validação e Sequenciamento

- Abra o código citado para confirmar cada oportunidade; nunca confie cegamente em saídas não verificadas.
- Ordene por **alavancagem**: impacto dividido pelo esforço provável, ponderado pela confiança técnica.
- Estabeleça a autonomia por risco: o que pode ser delegado a executores rotineiros, o que exige revisão cuidadosa de design e o que exige aprovação humana direta.
- Registre formalmente as ideias descartadas ou postergadas para evitar que sejam redescobertas e rediscutidas inutilmente em auditorias futuras.

### 5. Redigir o Roadmap

- Crie o arquivo `.agents/ROADMAP.md` (ou local equivalente do projeto) usando o modelo em [references/roadmap-template.md](references/roadmap-template.md).
- Prefira a divisão temporal **Agora / Próximo / Depois** (Now / Next / Later) em vez de datas fictícias.
- Todo item deve indicar o próximo artefato de encaminhamento: `roadmap-to-improve-plans`, `feature-planning-artifacts`, `spike de pesquisa`, `decisão do usuário` ou `descartar`.

## Critérios de Conclusão

O roadmap estratégico está concluído quando qualquer desenvolvedor ou agente futuro puder escolher o próximo item de trabalho sem precisar refazer toda a varredura do repositório: as melhores oportunidades estão ranqueadas com evidências, as ideias descartadas estão justificadas e a próxima etapa de planejamento está explícita.
