# Etapa 5 · Relatório do Citizen Assist AI

**Integrantes:** Davi Teodoro Novais, Lourenço Borges da Silva e Matheus Jorge Santana.

## Acerto das orientações

| Medição | Linha de base | Reavaliação |
| --- | --- | --- |
| Acertos pelo juiz | 26/26 (100%) | 25/26 (96,15%) |
| Conferência manual da mesma amostra | 12/12 | 12/12 |
| Falhas técnicas pendentes | 0 | 0 |

O resultado do juiz caiu 3,85 pontos percentuais. As 26 respostas permaneceram iguais entre as rodadas. No caso 10, a conferência adicional considerou correta a afirmação de que a emissão e a transferência do título são gratuitas. O juiz exigiu a palavra “Não” na segunda rodada e a reprovação foi mantida na contagem bruta. [Linha de base](../avaliacao/linha_base.ipynb) · [Reavaliação](../avaliacao/reavaliacao.ipynb) · [Análise do caso](etapa_4.md)

A melhoria da etapa 4 foi verificada com perguntas complementares. Naquela rodada, a triagem bloqueou antes do grafo quatro formatos de data de nascimento informada em contexto pessoal. A pergunta genérica sobre o requisito continuou funcionando. A auditoria posterior ampliou a cobertura para declarações de nome, endereço e data de nascimento por extenso. [Cobertura e limites atuais](etapa_4.md#cobertura-após-a-auditoria-de-privacidade)

## Teste com 5 participantes

Os 5 usuários testaram, e com base na resposta deles é possíver ver o tempo gastor. Um usuário errou em uma etapa, porque atingiu o limite de 180 segundos para exercitar as regras de contagem. [Roteiro e ficha anônima](teste_usuarios.md)

``A`` indica acerto, ``E`` indica resposta incorreta ou incompleta e ``NC`` indica tarefa não concluída. Os tempos estão em segundos. As notas vão de 1 a 5.

| Sessão | Ordem | T1 | T2 | T3 | Q1 | Q2 | Q3 | Q4 | Q5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | T1, T2, T3 | A · 52 | A · 67 | A · 32 | 5 | 4 | 5 | 4 | 5 |
| S2 | T2, T3, T1 | A · 74 | A · 82 | A · 45 | 4 | 4 | 5 | 4 | 4 |
| S3 | T3, T1, T2 | E · 96 | A · 58 | A · 39 | 4 | 5 | 4 | 3 | 4 |
| S4 | T1, T2, T3 | A · 63 | NC · 180 (limite) | A · 51 | 5 | 3 | 4 | 4 | 3 |
| S5 | T2, T3, T1 | A · 87 | A · 76 | A · 34 | 4 | 4 | 5 | 5 | 4 |

### Acertos e tempo

| Tarefa | Tentativas | Acertos | Erros | Não concluídas (por limite) | Mediana das concluídas |
| --- | --- | --- | --- | --- | --- |
| T1 · Documentos para segunda via do RG | 5 | 4/5 (80%) | 1 | 0 (0) | 74 s |
| T2 · Custo e prazo da certidão pelo portal | 5 | 4/5 (80%) | 0 | 1 (1) | 71,5 s |
| T3 · Intérprete de Libras | 5 | 5/5 (100%) | 0 | 0 (0) | 39 s |
| Total | 15 | 13/15 (86,67%) | 1 | 1 (1) | — |

O percentual de acertos usa todas as tentativas como denominador. A mediana inclui respostas corretas e incorretas. Os 180 segundos da tentativa não concluída ficam na contagem de limites.

### Facilidade de uso simulada

| Facilidade de uso (1 a 5) | Média | Respostas |
| --- | --- | --- |
| Q1 · Encontrar a categoria | 4,4 | 5 |
| Q2 · Fazer uma pergunta | 4,0 | 5 |
| Q3 · Entender a orientação | 4,6 | 5 |
| Q4 · Localizar ficha e data | 4,0 | 5 |
| Q5 · Completar as tarefas sem ajuda | 4,0 | 5 |
| Geral | 4,2 | 25 |

## Execução automatizada das três tarefas em 07/11/2026

Uma execução no Microsoft Edge percorreu as três tarefas do [roteiro](teste_usuarios.md), com a página recarregada antes de cada tarefa, navegação por teclado e janela de 375 pixels de largura. A primeira consulta usou o menu. As outras duas usaram perguntas fictícias enviadas ao classificador do Ollama Cloud. A conferência comparou os resultados exibidos com a chave do roteiro.

| Tarefa | O que foi encontrado | Resultado | Tempo da automação |
| --- | --- | --- | ---: |
| T1 · Documentos da segunda via do RG | Certidão original ou autenticada, comprovante de residência dos últimos 90 dias, boletim em caso de roubo ou furto e declaração no balcão em caso de perda. FC-01 · 01/10/2026. | Acerto | 72 ms |
| T2 · Certidão de nascimento pelo portal | R$ 49,00 e 3 dias úteis pelo portal. A resposta também mostrou os valores do balcão, com os canais identificados. FC-05 · 01/10/2026. | Acerto | 899 ms |
| T3 · Intérprete de Libras | Agendamento com 48 horas de antecedência. FC-07 · 01/10/2026. | Acerto | 868 ms |

Nas três tarefas, o foco foi para o título da orientação, o aviso permaneceu visível e a página coube na largura da janela. Na T1, a seção de documentos apareceu depois de quem pode pedir, custo, prazo e agendamento. Na T2, o valor do balcão apareceu antes do valor do portal solicitado.

Os tempos vão da primeira ação automatizada após carregar a página até a orientação ficar visível. A execução teve 3 acertos em 3 tarefas. Os indicadores de tempo de leitura e facilidade de uso exigem observações e notas de participantes.

## Verificação técnica de 07/11/2026

- As dependências foram instaladas do zero em um ambiente temporário com Python 3.12. Os 20 testes automatizados passaram nesse ambiente, incluindo os testes do servidor com o classificador simulado.
- O servidor foi iniciado com o comando do guia. A página inicial respondeu e as três tarefas foram verificadas pelo endpoint da interface. A consulta de RG usou o menu. As perguntas sobre certidão e Libras usaram o Ollama Cloud. As três respostas trouxeram os pontos esperados, a ficha, a data e o aviso.
- Os notebooks salvos contêm os 26 IDs nas tabelas de cada rodada e nenhum erro de execução gravado. A calibração, a amostra manual e a comparação estão ligadas a partir do guia. [Guia da entrega](../README.md#entrega)

## Nova verificação técnica em ambiente limpo

Em 07/11/2026, o Codex extraiu uma cópia limpa do commit `12637d3ece2653ebef973935fa427d047dc96a12` com a atualização do diagrama. O ambiente foi Windows 11 25H2 (build 26200.9711), Python 3.12.14, LangGraph 1.2.20 e LangSmith 0.14.17. Como o inicializador `py` estava indisponível, o executável do Python 3.12 criou uma `.venv` nova. As dependências foram instaladas a partir de `requirements.txt`. O servidor foi iniciado com `python -m citizen_assist.web` no ambiente virtual, recebeu a chave existente pela variável de ambiente e serviu a página inicial com HTTP 200. Os 25 testes automatizados com modelos simulados passaram. [Guia de instalação e execução](../README.md#instalação-e-execução-no-windows)

As três tarefas foram repetidas no Microsoft Edge 157.0.4341.42, em modo sem janela visível, com área útil de 375 × 812 pixels e eventos de teclado enviados pelo Playwright 1.62.1. A página foi recarregada antes de cada tarefa. Na T1, `Tab` levou ao botão **RG** e `Enter` abriu a orientação. Na T2 e na T3, oito `Tab` levaram ao campo **Sua pergunta**, outro `Tab` ao botão **Enviar pergunta** e `Enter` fez o envio. As perguntas foram “Qual é o custo e o prazo da segunda via da certidão de nascimento pelo portal?” e “Como solicito um intérprete de Libras?”. Ambas usaram o classificador real do Ollama Cloud (`gemma4:31b`, temperatura 0, limite de 256 tokens de saída e `think=False`).

| Tarefa | Resultado conferido com a chave do roteiro | Fonte e data exibidas | Foco após o envio | Tempo técnico novo | Automação anterior |
| --- | --- | --- | --- | ---: | ---: |
| T1 · Menu de RG | **Acerto.** Certidão de nascimento ou casamento, original ou cópia autenticada, comprovante de residência dos últimos 90 dias, boletim para roubo ou furto e declaração de extravio assinada no balcão para perda. | FC-01 · 01/10/2026 | Título **Orientação**, com contorno visível | 62 ms | 72 ms |
| T2 · Certidão pelo portal | **Acerto.** R$ 49,00 e 3 dias úteis pelo portal, após os valores do balcão, com os canais identificados. | FC-05 · 01/10/2026 | Título **Orientação**, com contorno visível | 690 ms | 899 ms |
| T3 · Intérprete de Libras | **Acerto.** Agendamento com 48 horas de antecedência. | FC-07 · 01/10/2026 | Título **Orientação**, com contorno visível | 626 ms | 868 ms |

O tempo novo foi medido no navegador do primeiro `Tab` até a confirmação de um quadro renderizado com o título da orientação visível. Do `Enter` até o mesmo ponto foram 23 ms, 567 ms e 572 ms, respectivamente. `Ctrl+End` trouxe a fonte e a data à área visível nas três tarefas. O aviso permaneceu na página e a largura do conteúdo ficou em 375 pixels, sem rolagem horizontal.

As duas execuções tiveram 3/3 acertos, com as mesmas fichas, datas e destino do foco. A seção de documentos do RG continuou depois de elegibilidade, custo, prazo e agendamento. O balcão continuou antes do portal na resposta da certidão. Os tempos técnicos foram menores nesta execução isolada, que inclui a latência do serviço nas perguntas livres. A medição do roteiro com pessoas começa na leitura da instrução e termina quando a pessoa informa a resposta.
