$ErrorActionPreference = 'Stop'

$chave = $env:OLLAMA_API_KEY
$arquivoEnv = Join-Path (Split-Path -Parent $PSScriptRoot) '.env'
if (-not $chave -and (Test-Path -LiteralPath $arquivoEnv -PathType Leaf)) {
    $config = Get-Content -LiteralPath $arquivoEnv | Select-String '^\s*OLLAMA_API_KEY\s*='
    if (@($config).Count -eq 1) {
        $chave = (($config.Line -split '=', 2)[1]).Trim().Trim('"', "'")
    }
}
if (-not $chave) {
    throw 'Configure OLLAMA_API_KEY no ambiente ou no arquivo .env do projeto.'
}

function Testar-Modelo($modelo, $think, $instrucao, $exemplo, $avaliar) {
    $body = @{
        model = $modelo
        stream = $false
        think = $think
        options = @{ temperature = 0 }
        messages = @(
            @{ role = 'system'; content = $instrucao }
            @{ role = 'user'; content = $exemplo }
        )
    } | ConvertTo-Json -Depth 5 -Compress

    $relogio = [Diagnostics.Stopwatch]::StartNew()
    try {
        $retorno = Invoke-RestMethod -Uri 'https://ollama.com/api/chat' -Method Post `
            -ContentType 'application/json; charset=utf-8' -Headers @{ Authorization = "Bearer $chave" } `
            -Body $body -TimeoutSec 60 -MaximumRedirection 0
    } catch {
        $codigo = $_.Exception.Response.StatusCode
        if ($codigo) { throw "${modelo}: a API retornou HTTP $([int]$codigo)." }
        throw "${modelo}: falha de conexão ou tempo de resposta excedido."
    }
    $relogio.Stop()

    try {
        $conteudo = ([string]$retorno.message.content).Trim()
        if ($conteudo -match '(?is)^\x60{3}(?:json)?\s*(\{.*\})\s*\x60{3}$') {
            $conteudo = $Matches[1]
        }
        $resposta = ConvertFrom-Json -InputObject $conteudo -AsHashtable -NoEnumerate
        $valida = & $avaliar $resposta
    } catch {
        throw "${modelo}: a resposta não pôde ser validada como JSON."
    }
    if (-not $valida) { throw "${modelo}: a resposta não passou na verificação do exemplo." }

    [pscustomobject]@{ modelo = $modelo; tempo_ms = $relogio.ElapsedMilliseconds; resultado = 'aprovado' }
}

Testar-Modelo 'gemma4:31b' $false `
    'Classifique a pergunta. Responda somente com um objeto JSON contendo categoria, assuntos (lista) e condicoes (lista). Categoria permitida: rg. Assunto permitido: custo. Condicao permitida: segunda_via.' `
    'Quanto custa a segunda via do RG?' {
    param($resposta)
    $resposta -is [System.Collections.IDictionary] -and $resposta.Count -eq 3 -and
        $resposta.categoria -ceq 'rg' -and
        $resposta.assuntos -is [array] -and $resposta.assuntos.Count -eq 1 -and $resposta.assuntos[0] -ceq 'custo' -and
        $resposta.condicoes -is [array] -and $resposta.condicoes.Count -eq 1 -and $resposta.condicoes[0] -ceq 'segunda_via'
}

Testar-Modelo 'gpt-oss:20b' 'low' `
    'Compare os valores. Responda apenas com um objeto JSON com a chave conteudo_esperado e um valor booleano. Use true se os valores forem iguais e false caso contrário.' `
    'Valor esperado: R$ 38,00. Valor na resposta: R$ 20,00.' {
    param($resposta)
    $resposta -is [System.Collections.IDictionary] -and $resposta.Count -eq 1 -and
        $resposta.conteudo_esperado -is [bool] -and -not $resposta.conteudo_esperado
}
