"""Triagem local. A pergunta original nunca entra no grafo."""

import re
import unicodedata

LIMITE_PERGUNTA = 500
MARCADOR = "[dado omitido]"

IDENTIFICADORES = re.compile(
    r"(?<![\w@])[\w.+%-]+\s*@\s*[\w-]+(?:\.[\w-]+)*(?:\.|\s+\.\s*)[a-z]{2,}\b"
    r"|(?<!\w)(?:\+?55[ .-]?)?\(\d{2}\)[ .-]?(?:\d[ .-]?)?\d{4}[ .-]?\d{4}\b"
    r"|(?<!\w)\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"
    r"|(?<!\w)(?!\d{4}-\d{2}-\d{2}\b|\d{1,2}[.-]\d{1,2}[.-]\d{4}\b)"
    r"\+?\d(?:[ .-]?\d){7,}(?:[ .-]?x)?\b(?![./-]\w)"
    r"|(?<!\d)\d{6,}(?!\d)",
    re.IGNORECASE,
)
DOCUMENTO = r"(?:RG|CPF|CNH|CTPS|CNPJ|título de eleitor|número (?:do|de) documento)"
POSSE = r"(?:(?:meu|minha|seu|sua|o|a)\s+)?"
CONTATO = r"(?:cep|contato|telefone|celular|whatsapp|e-?mail)"
REQUISITO = r"(?:necess[aá]ri[oa]|obrigat[oó]ri[oa]|exigid[oa]|solicitad[oa]|pedid[oa])\b"
DOCUMENTO_ROTULADO = re.compile(
    rf"\b({POSSE}{DOCUMENTO})"
    r"\s*(?:(?:(?:é|e)\s+|[:=#]\s*|n[º°o.]\s*)(?=\d)|(?=(?:\d[ ./-]?){4}\d))"
    r"\d[\dXx]*(?:[ ./-][\dXx]+)*\b(?![./-][\w])",
    re.IGNORECASE,
)
NOME_DECLARADO = (
    r"(?:eu sou\s+(?=(?-i:[A-ZÀ-ÖØ-Þ]))|me chamo\s+|"
    r"(?:meu|seu) nome(?: completo)?\s*(?:[ée]\b|:)\s*|nome(?: completo)?\s*:\s*)"
)
ROTULO_ENDERECO = r"endere[cç]o(?:\s+(?:residencial|comercial|completo))?"
ENDERECO_DECLARADO = (
    rf"(?:(?:meu|seu) )?{ROTULO_ENDERECO}\s*(?:[:=]|\bé\b(?!\s+{REQUISITO}))\s*"
)
ROTULO_NASCIMENTO = r"data de nascimento(?: d[aeo] [^.!?;:=]{1,40}?)?"
NASCIMENTO_DECLARADO = (
    rf"(?:(?:(?:a|minha|sua) )?{ROTULO_NASCIMENTO}(?:\s*(?:[:=]|\b[ée]\b)\s*|\s+)"
    r"|(?:nasci|nascid[oa])(?: em| (?:no )?dia)?\s+)"
)
NUMERAL = (
    r"(?:primeiro|um|dois|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|"
    r"catorze|quatorze|quinze|dezesseis|dezessete|dezoito|dezenove|vinte|trinta|quarenta|"
    r"cinquenta|sessenta|setenta|oitenta|noventa|cem|cento|trezentos|duzentos|quatrocentos|"
    r"quinhentos|seiscentos|setecentos|oitocentos|novecentos|mil)"
)
DIA_POR_EXTENSO = rf"(?:\d{{1,2}}|{NUMERAL}(?: e {NUMERAL})?)"
MES = r"(?:janeiro|fevereiro|mar[cç]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)"
DATA_POR_EXTENSO = rf"{DIA_POR_EXTENSO} de {MES} de (?:\d{{4}}|{NUMERAL}(?: (?:e )?{NUMERAL})*)"
DATA_NUMERICA = r"\d{1,4}[./-]\d{1,2}[./-]\d{1,4}"
PALAVRA_NOME = r"[^\W\d_]+(?:[-'’][^\W\d_]+)*"
LOGRADOURO = r"(?:rua|avenida|travessa|alameda|rodovia|pra[cç]a|estrada|largo)"
ABREVIACAO_LOGRADOURO = r"(?:r|av|trav?|al|rod|p[çc]a|estr)"
INICIO_PERGUNTA = r"(?:como|quanto|qual|quais|onde|quando|posso|preciso|o que|que documentos|é preciso)"
NOME_CAPITALIZADO = rf"(?=[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]){PALAVRA_NOME}"
NOME_SEM_ROTULO = re.compile(
    rf"\b{NOME_CAPITALIZADO} (?:(?:d[aeos]|das|dos|e|[A-ZÀ-ÖØ-Þ]\.) )*{NOME_CAPITALIZADO}\b"
)
TERMOS_DO_SERVICO = re.compile(
    r"\b(?:primeira via|segunda via|carteira de (?:identidade|trabalho)|t[ií]tulo de eleitor|"
    r"certid[aã]o de (?:nascimento|casamento|[oó]bito)|data de nascimento|comprovante de resid[eê]ncia|"
    r"documento (?:original|oficial)(?: com foto)?|documento com foto|boletim de ocorr[eê]ncia|"
    r"nome completo|endere[cç]o residencial|dados pessoais|"
    r"l[ií]ngua brasileira de sinais|central (?:do cidad[aã]o|eleitoral)|posto de identifica[cç][aã]o|"
    r"cartório central|bom dia|boa tarde|boa noite)\b",
    re.IGNORECASE,
)
DADO_DELIMITADO = re.compile(
    rf"(?:^|(?<=[.!?;] ))(?:{NOME_DECLARADO}{PALAVRA_NOME}(?: {PALAVRA_NOME})*"
    rf"|{ENDERECO_DECLARADO}(?:{LOGRADOURO} |{ABREVIACAO_LOGRADOURO}(?:\.\s*| ))[^.!?;@]+?"
    rf"|{NASCIMENTO_DECLARADO}(?:{DATA_NUMERICA}|{DATA_POR_EXTENSO}))"
    rf"(?=[.!?;] {INICIO_PERGUNTA}\b[^.!?;]*\?"
    r"|[.!]?$)",
    re.IGNORECASE,
)
DADO_ISOLADO = re.compile(
    rf"(?:^|(?<=[.!?;] ))(?:(?P<documento>{POSSE}{DOCUMENTO})\s+|"
    rf"{POSSE}{CONTATO}\s*(?:[:=]|\bé\b)?\s*)?"
    rf"{re.escape(MARCADOR)}(?:[.!?;](?: |$)|$)",
    re.IGNORECASE,
)
DADO_INCERTO = re.compile(
    rf"\b(?:{NOME_DECLARADO}|{ENDERECO_DECLARADO}(?!\s*\[dado omitido\])|"
    r"(?:nome(?: completo)? (?:da|do) [^:!?]{1,40}|nome)\s*:|"
    rf"(?:meu|seu) {ROTULO_ENDERECO} (?:fica (?:em|na|no)\b|(?:e )?{LOGRADOURO}\b)|"
    r"(?:moro|resido|nasci|nascid[oa]) (?:em|no|na)\b|nascid[oa]\s*[:=]|"
    rf"{ROTULO_NASCIMENTO}\s*[:=]|"
    rf"(?:minha|sua) {ROTULO_NASCIMENTO} [ée]\s+(?!"
    r"(?:necess[aá]ria|obrigat[oó]ria|exigida|solicitada|pedida)\b)|"
    rf"{NASCIMENTO_DECLARADO}(?:{DATA_NUMERICA}\b|{DIA_POR_EXTENSO} de\b)|"
    rf"(?:{LOGRADOURO}|{ABREVIACAO_LOGRADOURO})\s+[^.!?;]{{1,70}}\d|"
    rf"{ABREVIACAO_LOGRADOURO}\.\s*{PALAVRA_NOME}|"
    rf"(?:{CONTATO}|senha)\s*[:=]\s*(?!{INICIO_PERGUNTA}\b)\S|"
    rf"(?:{CONTATO}|senha)\s+é\s+(?!{REQUISITO})\S|"
    rf"{DOCUMENTO}\s*(?:[:=]|\bé\b)\s*[^\s.!?;]*\d|"
    r"arroba\s*[\])]|arroba\s+[\w.-]+\s+ponto\s+[a-z]{2,}\b|"
    r"\d[ .()/-]+\d[ .()/-]+\d[ .()/-]+\d[ .()/-]+\d)",
    re.IGNORECASE,
)
OFERTA_DE_DADOS = re.compile(
    r"\b(?:passar|informar|enviar|mandar|digitar|dar)\b[^.!?]{0,45}"
    r"\b(?:endere[cç]o|telefone|celular|e-?mail|senha|CPF|dados pessoais)\b",
    re.IGNORECASE,
)
TEXTO_ININTELIGIVEL = re.compile(
    r"[a-zA-Z]{2,}|[áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ]", re.IGNORECASE
)


def contem_identificador(texto: str) -> bool:
    return bool(IDENTIFICADORES.search(texto) or DOCUMENTO_ROTULADO.search(texto))


def pergunta_para_classificador(texto: str) -> str:
    """Retira trechos mascarados, preservando o tipo de documento como contexto."""
    return DADO_ISOLADO.sub(
        lambda trecho: trecho[0].replace(f" {MARCADOR}", "") if trecho["documento"] else "",
        texto,
    ).strip()


def triar_pergunta(pergunta: str) -> tuple[str, bool, str | None]:
    """Retorna texto sanitizado, indicador de privacidade e motivo de interrupção."""
    if len(pergunta) > LIMITE_PERGUNTA:
        return "", False, "limite"

    texto = unicodedata.normalize("NFKC", pergunta)
    texto = " ".join("".join(c for c in texto if unicodedata.category(c) != "Cf").split())
    if len(texto) > LIMITE_PERGUNTA:
        return "", False, "limite"
    texto, declaracoes = DADO_DELIMITADO.subn(MARCADOR, texto)
    texto, documentos = DOCUMENTO_ROTULADO.subn(r"\1 " + MARCADOR, texto)
    texto, identificadores = IDENTIFICADORES.subn(MARCADOR, texto)
    alerta = bool(declaracoes or documentos or identificadores or OFERTA_DE_DADOS.search(texto))
    contexto = DADO_ISOLADO.sub("", texto)
    if (
        MARCADOR in contexto or "@" in contexto or DADO_INCERTO.search(contexto)
        or NOME_SEM_ROTULO.search(TERMOS_DO_SERVICO.sub(" ", contexto))
    ):
        return "", True, "privacidade"

    palavras = re.findall(r"[^\W\d_]+", contexto, re.UNICODE)
    if not TEXTO_ININTELIGIVEL.search(contexto) or (
        palavras and all(
            (
                not re.search(r"[aeiouáàâãéêíóôõúü]", palavra, re.IGNORECASE)
                and palavra.casefold() not in {"rg", "cpf", "cnh", "ctps"}
            )
            or palavra.casefold() in {"asdf", "asdfgh", "qwerty", "abc"}
            or len(set(palavra.casefold())) == 1
            for palavra in palavras
        )
    ):
        return "", alerta, "privacidade" if alerta else "ininteligivel"

    return texto, alerta, None
