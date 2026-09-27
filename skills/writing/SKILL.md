---
name: writing
description: >-
    Diretrizes de prosa e redação para qualquer texto voltado a humanos — claro, concreto e livre de clichês pré-fabricados de IA.
    Use ao escrever ou editar documentação, explicações, resumos, mensagens de commit, relatórios ou qualquer texto expositivo.
---

# Redação e Estilo de Prosa (Writing)

George Orwell, em 1946, descreveu a prosa ruim: ela "consiste cada vez menos em _palavras_ escolhidas pelo seu significado, e cada vez mais em _frases feitas_ coladas como seções de um galinheiro pré-fabricado." Ele se referia a escritores humanos que deixavam frases prontas pensarem por eles. Na era dos LLMs, essa tendência foi industrializada. Cada vício catalogado nesta skill — o exagero retórico, os falsos paralelismos, os tópicos iniciados sempre em negrito estereotipado — é sintoma de um mesmo problema: buscar a frase que vem fácil em vez das palavras que expressam o significado exato. Frases prontas pensam por você e ocultam o sentido até de quem escreve.

O remédio também é o de Orwell: **deixe o significado escolher a palavra, e nunca o contrário.** Saiba exatamente o que você quer dizer antes de redigir, e busque as palavras que dizem precisamente aquilo. Se uma frase veio totalmente pronta e clichê, reescreva-a.

## O Método

Pergunte-se a cada frase:

1. O que estou tentando dizer?
2. Quais palavras expressam isso de forma mais fiel?
3. Que imagem, exemplo ou termo tornará isso mais nítido?
4. Essa formulação é natural e precisa?

E então: Pode ser dito de forma mais direta? Há alguma palavra excessiva ou prolixa?

## As Regras

1. **Nunca use uma metáfora, analogia ou figura de linguagem desgastada.** Especialmente vícios clássicos gerados por IA: "tapeçaria", "ecossistema complexo", "mergulhar a fundo", "divisor de águas", "virar a chave". Uma frase repetida à exaustão perdeu a força imagética e virou mero enchimento de linguiça.
2. **Nunca use uma palavra longa e pomposa se uma curta servir.** Use "usar" em vez de "utilizar" ou "alavancar". "Analisar" em vez de "mergulhar em". "É" em vez de "atua como", "serve como" ou "representa um testemunho de".
3. **Se for possível cortar uma palavra, corte-a sempre.** Uma oração não deve conter palavras desnecessárias pelo mesmo motivo que um desenho não deve ter traços inúteis e uma máquina não deve ter peças sobrando. Em vez de "devido ao fato de que", use "já que" ou "porque". Em vez de "vale a pena notar que X", diga simplesmente "X".
4. **Evite a voz passiva quando puder usar a voz ativa.** "O plano foi revisado pela equipe" esconde o agente e enfraquece a frase. Prefira: "A equipe revisou o plano."
5. **Evite termos estrangeiros ou jargões vazios quando existir equivalente simples em português.** Atenção: um termo técnico com significado exato na computação (como "idempotente", "thread-safe", "pipeline") não é jargão; mantê-lo é necessário para a precisão. Jargão é imprecisão travestida de sofisticação.
6. **Afirme pela via positiva.** Diga o que é, e não apenas o que não é. "Não se lembrou" é "esqueceu". "Não teve confiança em" é "desconfiou".
7. **Use linguagem precisa, específica e concreta.** O teste da substituição: se uma frase pudesse constar inalterada no README ou PR de qualquer outro projeto aleatório, ela não diz nada sobre o seu — reescreva-a ou delete-a.
8. **Um parágrafo por ideia principal, introduzido por sua frase-tema.** Mantenha ideias paralelas em estruturas coordenadas.
9. **Posicione as palavras de maior peso no final da oração.** O final da frase é o que o leitor leva consigo para a oração seguinte; não desperdice esse espaço com ressalvas fracas.
10. **Quebre qualquer uma dessas regras antes de escrever algo artificial ou grosseiro.**

## Escreva para o Leitor

Duas perguntas governam cada texto: o que o leitor já sabe e o que ele veio buscar.

- **O que ele sabe:** Apenas o que está na página. Um termo cunhado por você não tem significado até que você o defina. Nunca se apoie em raciocínios ou contextos invisíveis. Quando brevidade e clareza conflitarem, priorize a clareza.
- **O que ele veio buscar:** O leitor geralmente está ali para **fazer algo** (procedimento prático) ou para **entender algo** (explicação teórica). Decida qual é o objetivo antes de redigir e atenda a essa necessidade. Teoria interrompendo passos práticos atrapalha a ação; passos práticos enchendo uma explicação atrapalham a compreensão.

## Adequar o Tom à Relevância Real

A maioria das tarefas é uma melhoria incremental, e isso é excelente. Não infle a correção de um bug transformando-a em um ensaio filosófico sobre o futuro da engenharia de software. Não fabrique drama artificial ("aqui está o pulo do gato", "o resultado é devastador"), nem declare que seu ponto é óbvio ("a realidade é simples"). Deixe que os fatos e o código falem por si mesmos.

## Sinais de Alerta de Texto Gerado por IA (Tells)

Consulte `references/tropes.md` para o guia completo de termos clichês e suas correções. Os principais vilões:

| Categoria           | Vícios a Evitar                                                                                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Escolha de palavras | "mergulhar", "alavancar", "robusto", "tapeçaria", "ecossistema dinâmico", "serve como", "atua como um testemunho"                                                                |
| Estrutura de frases | "não é apenas X — é Y", "Nem A. Nem B. Apenas C.", "O resultado? Impressionante.", acúmulo de orações subordinadas terminadas em gerúndio frouxo ("ressaltando sua importância") |
| Tom                 | "Aqui está o detalhe crucial", "Pense nisso como", "Vamos dissecar isso", inflação de relevância, jargões pomposos inventados                                                    |
| Formatação          | Travessões duplos excessivos, tópicos sempre forçados com início em negrito artificial, excesso de emojis decorativos, títulos em Title Case forçado                             |
| Composição          | Resumos redundantes tipo "Em conclusão", repetição insistente da mesma metáfora                                                                                                  |

## Checklist Antes de Entregar

Releia o texto com o olhar de um leitor que só conhece o que está na tela:

- Cada frase expressa exatamente o que pretendo, com palavras escolhidas especificamente para ela?
- Repeti a mesma estrutura de frase mais de duas vezes seguidas?
- Há algo aqui que só existe para parecer profundo, abrangente ou prolixo?
- Alguma frase poderia ser mais enxuta sem perda de sentido?
- Uma pessoa técnica com clareza mental escreveria dessa forma?
