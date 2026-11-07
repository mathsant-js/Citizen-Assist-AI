# Etapa 4 · Melhoria e reavaliação do Citizen Assist AI

## Falha e correção

A linha de base teve 26 acertos em 26 casos. A falha escolhida apareceu em perguntas complementares. A triagem reconhecia datas de nascimento depois de `:` ou `=`, mas deixava passar datas introduzidas por “é”, seguidas diretamente do rótulo ou informadas como “nascido em”. Uma pergunta sobre certidão nessas condições podia chegar ao grafo e ao classificador com a data intacta.

A triagem passou a reconhecer datas numéricas nesses contextos, incluindo rótulos de terceiros. Ela pede reformulação com o alerta de privacidade antes de executar o grafo. A alteração é local ao módulo de triagem. Perguntas genéricas sobre a exigência de informar a data continuam disponíveis para classificação. [Implementação](../citizen_assist/privacidade.py)

| Caso complementar com dados fictícios | Antes | Depois |
| --- | --- | --- |
| Data própria anunciada com “é”, com barras | Prosseguia com a data | Pediu reformulação antes do grafo |
| Data após o rótulo, com hífens | Prosseguia com a data | Pediu reformulação antes do grafo |
| Data da filha anunciada com “é”, em ordem ano-mês-dia | Prosseguia com a data | Pediu reformulação antes do grafo |
| Data de terceiro anunciada com “nascido em”, com pontos | Prosseguia com a data | Pediu reformulação antes do grafo |
| Pergunta sobre a exigência da data, sem informar um valor | Prosseguia | Prosseguiu e retornou orientação |

A comparação complementar foi feita localmente, com a triagem da versão registrada na linha de base e a versão corrigida. Os testes confirmam que o grafo e o classificador ficam sem chamadas nos quatro casos bloqueados e que a pergunta genérica recebe orientação com o classificador simulado. A detecção depende de rótulos e padrões numéricos. Datas sem contexto reconhecível ou escritas por extenso podem passar. [Testes do agente](../tests/test_agente.py)

## Rodada oficial

O notebook verifica as impressões digitais do conjunto oficial, das fichas e do código de avaliação, além dos modelos e parâmetros registrados na linha de base. Os 26 casos percorrem a mesma entrada da interface. O juiz é `gpt-oss:20b`, com temperatura 0 e nível de raciocínio `low`, conforme a etapa 3. A comparação direta das duas versões da triagem devolveu o mesmo texto sanitizado, alerta e motivo em todos os 26 casos. A melhoria foi medida separadamente com as perguntas complementares.

| Medição | Linha de base | Reavaliação de 07/11/2026 |
| --- | --- | --- |
| Calibração | 9/9 | 9/9 |
| Juiz bruto | 26/26 (100%) | 25/26 (96,15%) |
| Resultado com checagens automáticas | 26/26 (100%) | 25/26 (96,15%) |
| Falhas técnicas pendentes | 0 | 0 |
| Conferência manual da amostra fixa | 12/12 corretos | 12/12 corretos |
| Testes automatizados aprovados | 18 | 20 |

O resultado bruto caiu 3,85 pontos percentuais. O único veredito que mudou foi o caso 10, do tipo Escopo. O juiz reprovou a ausência da palavra “Não” em uma resposta que afirma que a primeira via, a segunda via e a transferência do título são gratuitas. A conferência adicional marcou a resposta como correta pela equivalência de sentido prevista na régua e pela FC-03. A comparação dos campos das 26 respostas registrou igualdade entre as duas rodadas. A reprovação do caso 10 segue contabilizada no resultado bruto. Os detalhes por caso e por tipo estão no [notebook executado](../avaliacao/reavaliacao.ipynb).

## Reproduzir

1. Configure o ambiente e a chave do Ollama Cloud conforme a [etapa 2](etapa_2.md).
2. Abra uma cópia de [reavaliacao.ipynb](../avaliacao/reavaliacao.ipynb) na pasta `avaliacao`, selecione o kernel de `.venv` e execute as células. Mantenha `linha_base.ipynb` ao lado da cópia, pois o notebook usa as saídas já gravadas na linha de base.
3. Confira novamente a amostra manual fixa. As anotações no notebook executado descrevem a rodada registrada aqui.

Para rodar os testes automatizados com os modelos simulados:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
