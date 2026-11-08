"""Triagem local. A pergunta original nunca entra no grafo."""

import re
import unicodedata

LIMITE_PERGUNTA = 500
MARCADOR = "[dado omitido]"

IDENTIFICADORES = re.compile(
    r"(?<![\w@])[\w.+%-]+\s*@\s*[\w.-]+\s*\.\s*[a-z]{2,}\b"
    r"|(?<!\d)\d{3}[.\s-]?\d{3}[.\s-]?\d{3}[-.\s]?\d{2}(?!\d)"
    r"|(?<![\w\d])(?:\+?55[ .-]?)?(?:\(\d{2}\)|\d{2})[ .-]?\d{4,5}[ .-]?\d{4}(?!\d)"
    r"|(?<![\w\d])\d{4,5}[- ]?\d{4}(?!\d)"
    r"|(?<!\d)\d{6,}(?!\d)",
    re.IGNORECASE,
)
DOCUMENTO_ROTULADO = re.compile(
    r"\b((?:(?:meu|minha|seu|sua|o|a)\s+)?(?:RG|CPF|CNH|CTPS|"
    r"título de eleitor|número (?:do|de) documento))"
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
    rf"(?:(?:meu|seu) )?{ROTULO_ENDERECO}\s*(?:[:=]|\bé\b(?!\s+"
    r"(?:necess[aá]rio|obrigat[oó]rio|exigido|solicitado|pedido)\b))\s*"
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
# Uma declaração isolada pode ser retirada inteira. Pontuação interna ambígua
# (por exemplo, abreviações de logradouro) fica para a verificação de indícios.
DADO_DELIMITADO = re.compile(
    rf"(?:^|(?<=[.!?;] ))(?:{NOME_DECLARADO}{PALAVRA_NOME}(?: {PALAVRA_NOME})*"
    rf"|{ENDERECO_DECLARADO}{LOGRADOURO} [^.!?;@]+?"
    rf"|{NASCIMENTO_DECLARADO}(?:{DATA_NUMERICA}|{DATA_POR_EXTENSO}))"
    r"(?=[.!?;] (?:como|quanto|qual|quais|onde|quando|posso|preciso|o que|é preciso)\b[^.!?;]*\?"
    r"|[.!]?$)",
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
    r"(?:rua|avenida|travessa|alameda|rodovia|r\.|av\.)\s+[^?!;]{1,70}\d|"
    r"(?:cep|senha|endere[cç]o|telefone|celular|e-?mail|número (?:do|de) documento)"
    r"\s*(?:[:=]|\bé\b)(?!\s*\[dado omitido\])\s*\S|"
    r"(?:meu|minha|seu|sua)\s+(?:rg|cpf|cnh|ctps|título de eleitor)"
    r"\s*(?:[:=]|\bé\b)(?!\s*\[dado omitido\])\s*\S|"
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
    if DADO_INCERTO.search(texto) or "@" in texto:
        return "", True, "privacidade"

    contexto = texto.replace(MARCADOR, "")
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

    if alerta and re.fullmatch(
        r"(?:(?:meu|minha|o|a)\s+)?(?:cpf|rg|cnh|ctps|telefone|celular|e-?mail)?"
        r"\s*(?:é|[:=])?\s*[.!?]*\s*", contexto, re.IGNORECASE
    ):
        return "", True, "privacidade"
    return texto, alerta, None
