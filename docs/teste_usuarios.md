# Roteiro do teste com participantes

**Coleta externa pendente.** Convide pelo menos cinco pessoas de fora do grupo. Reserve cerca de 15 minutos por sessão. Antes das sessões, configure a chave do Ollama Cloud e confirme que o menu e a pergunta livre funcionam. Use a mesma versão do protótipo em todas as sessões e separe as instruções das tarefas da chave de correção. [Convite para enviar](#convite-para-enviar) · [Instalação](../README.md#instalação-e-execução-no-windows)

Registre o hash completo do commit da rodada junto à ficha anônima. Use esse mesmo commit para iniciar a interface e executar uma cópia do notebook de reavaliação. Na raiz do projeto, `git rev-parse HEAD` identifica a versão em uso e `git status --short` permite confirmar que a cópia está limpa antes de iniciar a rodada. [Reproduzir a reavaliação](etapa_4.md#reproduzir)

## Instruções para ler em cada sessão

> Você vai testar um guia de documentos de uma central fictícia. Leia uma tarefa por vez e diga qual resposta encontrou. Você terá até três minutos por tarefa e pode parar a qualquer momento. Siga o caminho indicado quando houver um. Evite digitar nomes, números de documentos, contatos, endereços ou outros dados pessoais. Vamos registrar os tempos, os resultados e as notas de forma anônima. No fim, você vai responder a cinco perguntas sobre a facilidade de uso.

| Tarefa | Instrução |
| --- | --- |
| T1 · Menu | Use o menu para encontrar quais documentos são exigidos para a segunda via do RG. |
| T2 · Pergunta livre | Use o campo de pergunta para descobrir o custo e o prazo da segunda via da certidão de nascimento pelo portal. |
| T3 · Caminho livre | Descubra como solicitar um intérprete de Libras. |

## Aplicação e correção

1. Recarregue a página antes de cada tarefa. Alterne a ordem entre sessões, por exemplo T1–T2–T3, T2–T3–T1 e T3–T1–T2.
2. Entregue a instrução e inicie o cronômetro quando a pessoa começar a lê-la. Pare quando ela disser a resposta encontrada, desistir ou atingir 180 segundos. Evite indicar onde clicar ou como escrever a pergunta durante a tarefa.
3. Marque **A** se a resposta cobrir todos os pontos da chave, **E** se a pessoa der uma resposta incompleta ou incorreta e **NC** se desistir ou não responder dentro do limite. Registre o tempo em segundos e marque o motivo de NC como desistência ou limite.
4. Depois das três tarefas, peça à pessoa que localize o código e a data de uma ficha em uma resposta exibida, caso ainda não tenha feito isso. Aplique o questionário após encerrar a cronometragem das tarefas.

| Tarefa | Chave de correção reservada ao aplicador |
| --- | --- |
| T1 | Certidão de nascimento ou casamento, original ou cópia autenticada. Comprovante de residência dos últimos 90 dias. Para roubo ou furto, boletim de ocorrência. Para perda, declaração de extravio assinada no balcão. [FC-01](../referencia/FC-01_rg_segunda_via.md) |
| T2 | R$ 49,00 e 3 dias úteis pelo portal. [FC-05](../referencia/FC-05_certidoes.md) |
| T3 | Agendar com 48 horas de antecedência. [FC-07](../referencia/FC-07_regras_gerais.md) |

## Questionário

Use a mesma escala para todas as perguntas. **1** muito difícil, **2** difícil, **3** nem fácil nem difícil, **4** fácil, **5** muito fácil. Marque `—` se a pessoa pular a pergunta ou se ela não se aplicar à sessão.

1. Quão fácil foi encontrar a categoria de que você precisava?
2. Quão fácil foi fazer uma pergunta no campo de texto?
3. Quão fácil foi entender a orientação recebida?
4. Quão fácil foi localizar o código da ficha e sua data?
5. Quão fácil foi completar as tarefas sem ajuda?

## Ficha de registro anônima

Use uma linha por sessão real. Nas colunas das tarefas, anote o resultado e o tempo em segundos, por exemplo `A · 52 s` ou `NC · 180 s (limite)`. Nas últimas cinco colunas, registre a nota ou `—`. Identifique a sessão apenas pelo número, sem guardar vínculo com nomes ou contatos, gravações ou histórico de perguntas.

| Sessão | Ordem das tarefas | T1 | T2 | T3 | Q1 | Q2 | Q3 | Q4 | Q5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | | | | |
| 2 | | | | | | | | | |
| 3 | | | | | | | | | |
| 4 | | | | | | | | | |
| 5 | | | | | | | | | |

## Consolidação

- **Acerto nas tarefas.** Divida o total de A pelo total de tentativas, incluindo E e NC. Apresente a contagem por tarefa e o total.
- **Tempo.** Calcule a mediana dos segundos de A e E por tarefa. Mostre o número de tentativas, as NC e, dentro delas, quantas atingiram o limite. Use “sem tarefas concluídas” se a mediana não puder ser calculada.
- **Facilidade.** Apresente a média de cada pergunta com o número de notas válidas e a média geral das notas recebidas. Registre respostas ausentes separadamente.

Consolide apenas os registros das sessões externas nesta ficha. O relatório apresenta separadamente a simulação histórica e as medições técnicas do navegador. [Relatório da etapa 5](etapa_5.md)

## Convite para enviar

> Oi! Você toparia testar o Citizen Assist AI, um protótipo que estamos desenvolvendo para um trabalho da FIAP? A sessão leva cerca de 15 minutos, com três tarefas e cinco perguntas rápidas. O teste usa uma central fictícia e o registro é anônimo. Se topar, me responda por aqui para combinarmos um horário.
