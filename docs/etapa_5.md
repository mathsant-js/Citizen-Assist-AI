# Etapa 5 · Relatório do Citizen Assist AI

**Integrantes:** Davi Teodoro Novais, Lourenço Borges da Silva e Matheus Jorge Santana.

## Acerto das orientações

| Medição | Linha de base | Reavaliação |
| --- | --- | --- |
| Acertos pelo juiz | 26/26 (100%) | 25/26 (96,15%) |
| Conferência manual da mesma amostra | 12/12 | 12/12 |
| Falhas técnicas pendentes | 0 | 0 |

O resultado do juiz caiu 3,85 pontos percentuais. As 26 respostas permaneceram iguais entre as rodadas. No caso 10, a conferência adicional considerou correta a afirmação de que a emissão e a transferência do título são gratuitas. O juiz exigiu a palavra “Não” na segunda rodada e a reprovação foi mantida na contagem bruta. [Linha de base](../avaliacao/linha_base.ipynb) · [Reavaliação](../avaliacao/reavaliacao.ipynb) · [Análise do caso](etapa_4.md)

A melhoria da etapa 4 foi verificada com perguntas complementares. A triagem passou a bloquear, antes do grafo, quatro formatos testados de data de nascimento informada em contexto pessoal. A pergunta genérica sobre o requisito continuou funcionando. Datas sem rótulo reconhecível ou escritas por extenso ainda podem passar. [Correção e limites](etapa_4.md#falha-e-correção)

## Simulação do teste com participantes

Os registros abaixo são fictícios. As cinco sessões foram simuladas para demonstrar o cálculo dos indicadores. A simulação inclui um erro e uma tarefa que atingiu o limite de 180 segundos para exercitar as regras de contagem. O critério de aceite do plano ainda exige cinco participantes externos reais. [Roteiro e ficha anônima](teste_usuarios.md)

A indica acerto, E indica resposta incorreta ou incompleta e NC indica tarefa não concluída. Os tempos estão em segundos. As notas vão de 1 a 5.

| Sessão simulada | Ordem | T1 | T2 | T3 | Q1 | Q2 | Q3 | Q4 | Q5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | T1, T2, T3 | A · 52 | A · 67 | A · 32 | 5 | 4 | 5 | 4 | 5 |
| S2 | T2, T3, T1 | A · 74 | A · 82 | A · 45 | 4 | 4 | 5 | 4 | 4 |
| S3 | T3, T1, T2 | E · 96 | A · 58 | A · 39 | 4 | 5 | 4 | 3 | 4 |
| S4 | T1, T2, T3 | A · 63 | NC · 180 (limite) | A · 51 | 5 | 3 | 4 | 4 | 3 |
| S5 | T2, T3, T1 | A · 87 | A · 76 | A · 34 | 4 | 4 | 5 | 5 | 4 |

### Acerto e tempo simulados

| Tarefa | Tentativas | Acertos | Erros | Não concluídas (por limite) | Mediana das concluídas |
| --- | --- | --- | --- | --- | --- | --- |
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

## Verificação técnica de 07/11/2026

- As dependências foram instaladas do zero em um ambiente temporário com Python 3.12. Os 20 testes automatizados passaram nesse ambiente, incluindo os testes do servidor com o classificador simulado.
- O servidor foi iniciado com o comando do guia. A página inicial respondeu e as três tarefas foram verificadas pelo endpoint da interface. A consulta de RG usou o menu. As perguntas sobre certidão e Libras usaram o Ollama Cloud. As três respostas trouxeram os pontos esperados, a ficha, a data e o aviso.
- Os notebooks salvos contêm os 26 IDs nas tabelas de cada rodada e nenhum erro de execução gravado. A calibração, a amostra manual e a comparação estão ligadas a partir do guia. [Guia da entrega](../README.md#entrega)

A reprodução independente permanece pendente. Para registrá-la, peça a outra pessoa que siga o guia de instalação, abra a interface e confirme os dois caminhos descritos no teste rápido. [Guia de instalação e execução](../README.md#instalação-e-execução-no-windows)
