# Etapa 3 · Linha de base do Citizen Assist AI

O [notebook da linha de base](../avaliacao/linha_base.ipynb) reúne a régua, a calibração do juiz, os resultados dos 26 casos e a conferência manual. O [executor da avaliação](../avaliacao/linha_base.py) usa a mesma entrada da interface. O [juiz](../avaliacao/juiz.py) avalia a resposta com as fichas esperadas e as fichas citadas que existam na base. Os códigos das fontes esperadas chegam em um campo próprio e os pontos substantivos entre parênteses continuam no texto esperado.

O veredito bruto do juiz é a métrica principal. O notebook também calcula o resultado após as checagens locais do aviso, das citações e de padrões de identificadores. Falhas técnicas têm uma nova tentativa no componente que falhou e ficam separadas dos erros de orientação. A revisão manual usa os mesmos 12 IDs previstos para a etapa 4 e mantém o resultado bruto registrado.

## Resultado de 07/11/2026

| Medição | Resultado |
| --- | --- |
| Calibração final do juiz | 9/9 exemplos aprovados |
| Linha de base pelo juiz bruto | 26/26 corretos (100%) |
| Linha de base com checagens automáticas | 26/26 corretos (100%) |
| Falhas técnicas na rodada oficial | 0 |
| Conferência manual | 12/12 corretos, sem divergências com o juiz |
| Testes automatizados | 18 aprovados |

Os 26 acertos descrevem o conjunto oficial desta execução. A calibração preliminar encontrou reprovações indevidas de respostas válidas e a conferência direta cobriu 12 dos 26 casos.

## Reproduzir

1. Prepare o ambiente e configure a chave do Ollama conforme a [etapa 2](etapa_2.md).
2. Instale o suporte ao kernel do notebook com `.\.venv\Scripts\python.exe -m pip install ipykernel`.
3. Abra uma cópia de `avaliacao/linha_base.ipynb` na pasta `avaliacao`, selecione o Python de `.venv` e execute todas as células. A cópia preserva a evidência da rodada de referência. A revisão manual já preenchida no notebook é histórica e deve ser refeita para cada nova execução.

Para verificar o código e a triagem com os modelos simulados:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Privacidade e rastreabilidade

O caso 22 percorre a triagem normal do agente com a entrada oficial. No notebook e no pedido ao juiz, o número fictício é substituído por `[dado omitido]`. Se a triagem interromper uma entrada, o juiz recebe um marcador com o motivo. Os testes verificam a passagem da entrada original ao agente, a ausência do identificador no estado do grafo e no classificador quando aplicável e o mascaramento antes do juiz e da gravação da evidência. O parecer semântico cobre apenas a orientação exibida. Os testes de privacidade verificam o caminho dos dados separadamente.

O notebook registra as impressões digitais do agente, das fichas, do dataset e do código de avaliação, além de modelos e parâmetros. A temperatura de ambos é 0. Nas três tentativas preliminares, o juiz aprovou 8 de 9 exemplos em cada uma. Exigiu detalhes alheios à pergunta de preço do RG, uma declaração explícita de que o chat evita repetir números e, em outra tentativa, um alerta de privacidade em uma pergunta comum. A régua passou a separar omissões de contradições, a ler as citações no campo estruturado e a distinguir perguntas comuns de situações que exigem alerta. O exemplo sintético de privacidade passou a explicitar que o chat evita solicitar e repetir números de documentos. Os 26 casos oficiais foram preservados.

O critério de calibração adotado antes da rodada oficial exige parecer válido para os nove exemplos, detecção das violações em todos os exemplos incorretos e pelo menos oito aprovações. Isso admite uma reprovação indevida de resposta correta e mantém essa limitação visível na conferência manual.
