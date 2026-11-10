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

A comparação complementar foi feita localmente, com a triagem da versão registrada na linha de base e a versão corrigida naquela rodada. As quatro datas rotuladas foram bloqueadas e a pergunta genérica recebeu orientação com o classificador simulado. A cobertura da triagem atual está descrita a seguir.

### Cobertura após a auditoria de privacidade

Antes da alteração, um `POST /api/orientacao` com a pergunta fictícia “Marina Ficticia, como agendo Libras?” retornou orientação com `alerta_privacidade: false`. O classificador simulado recebeu a frase inteira. O mesmo texto apareceu em `messages[1].content` no corpo da requisição simulada ao Ollama. Com a correção, essa entrada recebe o pedido de reformulação e `alerta_privacidade: true` antes de iniciar o grafo. O teste HTTP verifica que o classificador recebe zero chamadas nesse caso. [Teste HTTP](../tests/test_web.py)

A interface envia a pergunta como JSON para `POST /api/orientacao`. O servidor lê o corpo e chama `Agente.responder`, que valida a entrada e executa a triagem antes de montar o estado do grafo. Quando o dado pode ser separado com segurança, o estado recebe `[dado omitido]` no lugar do dado. O nó de intenção retira os trechos mascarados antes de chamar o classificador e conserva o tipo de documento quando ele ajuda a identificar o serviço. `classificar_ollama` usa esse texto como mensagem de usuário no `POST /api/chat`. Quando sobram indícios de dados pessoais misturados à pergunta ou falta uma pergunta útil, a triagem responde localmente. [Interface](../citizen_assist/interface/interface.js) · [Servidor](../citizen_assist/web.py) · [Triagem](../citizen_assist/privacidade.py) · [Agente](../citizen_assist/agente.py) · [Cliente Ollama](../citizen_assist/ollama.py)

| Caso fictício | Resultado após a correção |
| --- | --- |
| Nome sem rótulo no início ou no meio da pergunta, como “Marina Ficticia”, “Íris da Silveira” e “Caio Q. Imaginário” | Pede reformulação com alerta. |
| Nome ou nascimento em declaração separada, como “Me chamo Pessoa Exemplo” ou “Nasci em 12 de março de 1990” | Mascara a declaração antes do grafo. O classificador recebe a pergunta de serviço. |
| Endereço declarado como “Endereço: Av. Inventada, 45”, com variantes `R.`, `Trav.` e `av` sem ponto | Mascara o trecho. Se o endereço aparecer dentro da pergunta ou tiver pontuação ambígua, pede reformulação. |
| E-mail de exemplo, telefone com DDD e nono dígito separado, WhatsApp e CEP em trechos isolados | Mascara o contato e retira o trecho da mensagem ao classificador. O teste HTTP confere o texto exato no corpo enviado ao Ollama simulado. |
| CPF com e sem pontuação, algarismos de largura cheia, RG com dígito final X, número em grupos de quatro e CNPJ formatado | Mascara o número isolado. Quando há rótulo de documento, conserva o tipo como contexto. Um número intercalado na pergunta, um RG de formato incerto ou um e-mail com “[arroba]” exige reformulação. |
| Idades de 49, 50, 69 e 70 anos para a validade da CNH e perguntas sobre exigência de data de nascimento, e-mail ou comprovante de residência | O classificador simulado recebe a pergunta completa, sem alerta. Os testes de CNH conferem a validade da faixa etária na resposta. |

A suíte local passou com 28 testes. Os testes conferem a mensagem exata recebida pelo classificador simulado, a ausência de chamada nos bloqueios, o mascaramento antes do grafo e a limpeza do estado final quando o classificador falha. Os casos oficiais 22 e 23 conservaram alerta, orientação e citações esperadas via classificação local. A comparação antes e depois produziu os mesmos resultados de triagem para os 26 casos, e o arquivo do golden dataset foi preservado. A suíte usa chamadas externas simuladas. [Testes do agente](../tests/test_agente.py) · [Testes HTTP](../tests/test_web.py) · [Testes da avaliação](../tests/test_avaliacao.py)

A triagem usa padrões de texto. Nomes de uma palavra, nomes sem rótulo inteiramente em minúsculas ou maiúsculas, endereços sem indícios de logradouro, datas sem contexto de nascimento e grafias fora dos padrões podem passar. Expressões legítimas com iniciais maiúsculas também podem parecer nomes. A separação de declarações depende da pontuação e, para nomes, endereços e datas rotuladas, do início reconhecível da pergunta de serviço. Entradas com várias declarações consecutivas ou abreviações internas como `Av. Dr.` podem exigir reformulação.

## Rodada oficial de 07/11/2026

A rodada da versão preparada para entrega está registrada separadamente no [notebook da versão final](../avaliacao/reavaliacao_final.ipynb) e na [comparação da etapa 5](etapa_5.md#acerto-das-orientações).

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

Para repetir a rodada da versão final, siga o mesmo procedimento com uma cópia de [reavaliacao_final.ipynb](../avaliacao/reavaliacao_final.ipynb). Para conferir o conjunto diretamente com o enunciado, mantenha `1CC-Citizen_Assist_AI(2).docx` em Downloads ou indique o caminho do arquivo na variável de ambiente `CITIZEN_ENUNCIADO` antes de abrir o Jupyter. Refaça a conferência manual da amostra e das divergências com as novas respostas.

Para rodar os testes automatizados com os modelos simulados:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
