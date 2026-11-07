# Etapa 1 do Citizen Assist AI

## Resultados

| Item | Resultado |
| --- | --- |
| Base de referência | As sete fichas foram carregadas e verificadas com código e data de 01/10/2026. O índice preserva o texto de cada seção e permite buscar por categoria ou palavra-chave. |
| Golden dataset | Os 26 casos foram extraídos da tabela do enunciado e conferidos campo a campo em uma segunda leitura independente. |
| Contratos | Formatos definidos para a entrada, a intenção, a resposta e o parecer do juiz. |
| API do chatbot | `gemma4:31b` aprovado no teste de classificação em português pela API direta do Ollama. A chamada levou 617 ms nesta execução. |
| API do candidato a juiz | `gpt-oss:20b` aprovado no teste de identificação de um valor incorreto. A chamada levou 751 ms nesta execução. Confirmar a escolha do juiz na calibração prevista no plano. |
| Recrutamento | Convite preparado abaixo. O grupo precisa enviá-lo a pelo menos cinco pessoas de fora da equipe. |

Os tempos são de chamadas isoladas com entradas fictícias e curtas. As medições oficiais de qualidade e usabilidade estão previstas nas etapas seguintes.

## Base e avaliação

- [Carregador das fichas](../citizen_assist/base.py). Carrega os Markdown originais, valida o código no título e na fonte, converte a data e rejeita fichas duplicadas. Os trechos mantêm juntas as condições de cada seção. O índice retorna todas as categorias quando um termo é ambíguo, como “segunda via”.
- A FC-07 não tem uma seção própria de palavras-chave. O índice usa os rótulos das seções e o termo “Libras” da própria ficha. A FC-03 não esclarece a regra para quem tem exatamente 70 anos. Para esse caso, informar a lacuna e orientar a consulta ao órgão competente. [FC-07](../referencia/FC-07_regras_gerais.md) · [FC-03](../referencia/FC-03_titulo_de_eleitor.md)
- [Golden dataset](../avaliacao/golden_dataset.json). Cada registro contém ID, mensagem, tipo, resposta esperada literal e fontes esperadas. As aspas tipográficas que delimitam a mensagem no Word foram retiradas. O identificador fictício do caso 22 fica restrito ao arquivo de avaliação e deve passar pela triagem antes de qualquer chamada ou exibição. No notebook e no relatório, usar o ID ou a mensagem mascarada.
- A recuperação inicial usa categorias, palavras-chave e trechos. O `nomic-embed-text` local fica disponível caso os testes indiquem necessidade de busca semântica.

## Contratos e limites

Os [contratos JSON](contratos.json) descrevem as interfaces para a etapa 2. A entrada do menu tem `origem` e `categoria`. A pergunta livre tem `origem` e `pergunta`. Entrada vazia, ininteligível ou acima de 500 caracteres deve produzir uma resposta amigável antes de chamar o modelo. Para o menu, o servidor já conhece a categoria.

Após a triagem de privacidade, o servidor pode pedir ao modelo uma intenção como `{"categoria":"rg","assuntos":["custo"],"condicoes":["segunda_via"]}`. O servidor valida os assuntos e as condições contra as opções aprovadas para a categoria. Os códigos das citações e as datas vêm do índice. A resposta contém estado, mensagem, citações, alerta de privacidade e aviso. Exibir as datas como DD/MM/AAAA na interface e usar AAAA-MM-DD no contrato. Uma orientação fundamentada exige pelo menos uma citação. Em casos sem evidência aplicável, as citações ficam vazias.

Antes de chamar a API, descartar a pergunta bruta e retirar identificadores. Quando a triagem encontrar indícios de dados pessoais e não conseguir separar o contexto com segurança, pedir reformulação. No juiz, usar somente os casos fictícios, com a pergunta sanitizada. O parecer contém um resultado booleano por critério e uma justificativa. O código calcula o veredito a partir desses critérios e registra falhas técnicas separadamente.

## Repetir o teste da API

Na raiz do projeto, executar no PowerShell 7:

```powershell
./scripts/testar_ollama.ps1
```

O [script de verificação](../scripts/testar_ollama.ps1) lê `OLLAMA_API_KEY` do ambiente ou do `.env` da raiz. A chave deve ficar no ambiente do servidor e o `.env` está no `.gitignore`. O script envia apenas os dois exemplos fictícios e mostra modelo, duração e resultado. A API em nuvem não impõe o esquema, então o script pede JSON, aceita um bloco Markdown que contenha apenas o objeto e valida os campos do exemplo. A etapa 2 deverá aplicar os contratos completos. [Ollama Cloud](https://docs.ollama.com/cloud) · [Saídas estruturadas](https://docs.ollama.com/capabilities/structured-outputs)

## Convite para os testes

> Olá! Estamos desenvolvendo o Citizen Assist AI para um trabalho da FIAP e convidando pessoas de fora do grupo para testar o protótipo. Você toparia participar de uma sessão de cerca de 15 minutos? São três tarefas simples na interface e cinco perguntas sobre a facilidade de uso. O teste usa uma central fictícia. Pedimos que você evite digitar dados pessoais. No relatório, registraremos apenas os tempos, os acertos e as notas, sem identificar ninguém. Se quiser participar, responda por aqui para combinarmos um horário.
