---
name: writing-error-messages
description: >-
    Use ao escrever, revisar ou reescrever mensagens de erro voltadas a humanos, mensagens de validação de formulários, estados vazios (empty states), falhas de autenticação, notificações de erro, textos de suporte e mensagens de erro em CLI ou APIs.
    Ajuda a produzir erros específicos, acionáveis, sem culpabilizar o usuário, acessíveis e seguros contra vazamento de dados sensíveis.
---

# Redação de Mensagens de Erro (Writing Error Messages)

## Início Rápido

Antes de redigir qualquer mensagem de erro, identifique:

1. **Público:** usuário final, administrador, desenvolvedor, agente de suporte ou operador de infraestrutura.
2. **Falha:** qual ação falhou e o que permaneceu intacto ou salvo com sucesso.
3. **Causa:** conhecida, desconhecida, corrigível pelo usuário, falha no servidor, serviço de terceiros ou sensível à segurança.
4. **Recuperação:** o que o leitor pode fazer agora, o que o sistema fará a seguir e onde obter suporte se o erro persistir.

Em seguida, adote esta estrutura:

```text
[O que aconteceu]
[Garantia de segurança, se útil]. [Por que aconteceu, se conhecido e seguro informar]. [Ação corretiva específica]. [Caminho alternativo se continuar falhando].
```

Exemplo:

```text
Não foi possível conectar sua conta
Suas alterações foram salvas, mas não conseguimos conectar a conta devido a uma instabilidade no nosso servidor. Tente conectar novamente. Se o problema continuar, entre em contato com o suporte.
```

## Regras Fundamentais

| Regra                                   | O que Fazer                                       | O que Evitar                                             |
| --------------------------------------- | ------------------------------------------------- | -------------------------------------------------------- |
| Diga o que aconteceu                    | "Não foi possível salvar seu arquivo."            | "Algo deu errado." genérico sem contexto                 |
| Informe o que não foi afetado           | "Seu rascunho continua salvo."                    | Deixar o usuário em dúvida se perdeu dados               |
| Aponte a ação corretiva                 | "Verifique o número do cartão e tente novamente." | "OK" ou "Fechar" como único caminho                      |
| Use linguagem simples                   | "Não foi possível conectar ao Google Drive."      | "Fetch failed" ou "status code 500" para usuários leigos |
| Não culpe o usuário                     | "O nome da organização é obrigatório."            | "Você esqueceu de preencher o nome."                     |
| Respeite a gravidade                    | Tom calmo, direto e profissional                  | "Ops!", piadinhas ou tom debochado                       |
| Seja específico quando seguro           | "Informe uma data no passado."                    | "Entrada inválida."                                      |
| Seja genérico quando a segurança exigir | "E-mail ou senha incorretos."                     | "O e-mail existe, mas a senha está errada."              |

## Anatomia da Mensagem

Use apenas os elementos que a situação exigir:

| Elemento            | Finalidade                    | Padrão                                                                                 |
| ------------------- | ----------------------------- | -------------------------------------------------------------------------------------- |
| Título              | Resumir a ação que falhou     | "Não foi possível salvar as alterações"                                                |
| Corpo               | Explicar causa e consequência | "Suas alterações continuam abertas, mas não puderam ser salvas porque a conexão caiu." |
| Ação primária       | Dizer ao leitor o que fazer   | "Tentar novamente", "Atualizar dados", "Escolher outro arquivo"                        |
| Caminho alternativo | Prover uma saída              | "Se o problema persistir, fale com o suporte."                                         |
| Detalhe diagnóstico | Ajudar suporte ou devs        | Código de erro, ID da requisição (`requestId`), logs                                   |

Mantenha o texto de corpo em UIs com 1 a 2 frases curtas. Detalhes de diagnóstico devem ir para seções expansíveis ou logs.

## Validação e Erros de Formulário

Para erros no nível de campo:

- Posicione a mensagem junto ao campo correspondente e resuma no topo em formulários longos.
- Use a mesma nomenclatura do rótulo (label) do campo para fácil identificação.
- Diga como corrigir, e não apenas que está errado.
- Preserve o texto já digitado pelo usuário para que ele apenas ajuste o erro.
- Não valide prematuramente antes de o usuário ter a chance razoável de terminar de digitar.

Bons padrões:

```text
Informe um endereço de e-mail válido
Informe uma data no passado
A senha deve ter pelo menos 12 caracteres
Selecione um arquivo menor que 10 MB
```

Evite:

```text
Este campo é obrigatório
Entrada inválida
Valor ilegal informado
Erro de validação
```

## Acessibilidade e Estados Vazios

- Posicione o erro visualmente no local onde o leitor já está focando.
- Nunca dependa apenas de cores (vermelho). Utilize texto explícito, ícones e atributos de acessibilidade (como `aria-describedby` e `aria-invalid`).
- Para páginas de formulários, mova o foco do leitor para o resumo de erros ao submeter.
- Não confunda resultado vazio com erro. Se a busca não encontrou registros, use um estado vazio amigável: "Nenhuma fatura encontrada" acompanhado do botão "Criar nova fatura".

## Portão de Segurança e Privacidade

Especificidade nem sempre é boa. Use mensagens deliberadamente genéricas quando detalhes puderem revelar existência de contas, credenciais, dados privados ou vetores de fraude.

Para autenticação e recuperação de senha:

```text
E-mail ou senha inválidos
Se houver uma conta associada a este e-mail, enviaremos as instruções de redefinição de senha.
```

Nunca revele:

```text
Esse e-mail está cadastrado, mas a senha está incorreta
Esta conta foi bloqueada por tentativas excessivas
Nenhuma conta encontrada para o e-mail informado
```

## Mensagens Voltadas a Desenvolvedores e CLI

Quando o leitor for técnico e puder agir sobre o erro, forneça detalhes estruturados:

```text
Não foi possível ler o arquivo de configuração
Esperava-se formato TOML em ./app.config.toml, mas foi encontrada sintaxe inválida na linha 12: aspas de fechamento ausentes.
Corrija a sintaxe e execute `app deploy` novamente.
```

Detalhes úteis:

- Qual comando, arquivo, variável ou recurso falhou.
- O que era esperado versus o que foi recebido.
- O menor comando ou passo corretivo para solucionar.
- ID da requisição ou caminho do log para depuração.

## Checklist Final

Antes de finalizar uma mensagem de erro, verifique:

1. O que aconteceu?
2. O usuário perdeu algo ou criou dados duplicados?
3. Por que aconteceu (se for seguro informar)?
4. Qual é a próxima ação recomendada?
5. O que acontece se o usuário não fizer nada?
6. Onde ele pode buscar ajuda se a correção não funcionar?
