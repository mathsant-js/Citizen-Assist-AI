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
DADO_INCERTO = re.compile(
    r"\b(?:me chamo|(?:meu|seu) nome (?:completo )?(?:é|e|:)|nome completo\s*:|"
    r"(?:nome(?: completo)? (?:da|do) [^:!?]{1,40}|nome)\s*:|"
    r"(?:moro|resido|nasci) (?:em|no|na)|(?:data de nascimento|nascid[oa])\s*[:=]|"
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
    texto, documentos = DOCUMENTO_ROTULADO.subn(r"\1 " + MARCADOR, texto)
    texto, identificadores = IDENTIFICADORES.subn(MARCADOR, texto)
    alerta = bool(documentos or identificadores or OFERTA_DE_DADOS.search(texto))
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
