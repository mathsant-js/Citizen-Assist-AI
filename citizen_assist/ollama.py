"""Cliente da API direta do Ollama Cloud, usado apenas para classificação."""

import http.client
import json
import os
from pathlib import Path
import re

MODELO = "gemma4:31b"
ARQUIVO_ENV = Path(__file__).resolve().parents[1] / ".env"


class ClassificadorIndisponivel(Exception):
    """Falha de configuração, transporte ou resposta da API."""


def _ler_chave() -> str:
    chave = os.environ.get("OLLAMA_API_KEY", "").strip()
    if chave:
        return chave
    try:
        linhas = ARQUIVO_ENV.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError):
        return ""
    for linha in linhas:
        nome, separador, valor = linha.partition("=")
        if separador and nome.strip() == "OLLAMA_API_KEY":
            return valor.strip().strip("\"'")
    return ""


def classificar_ollama(instrucao: str, pergunta: str) -> object:
    chave = _ler_chave()
    if not chave or chave == "insira_sua_chave_aqui":
        raise ClassificadorIndisponivel()

    corpo = json.dumps({
        "model": MODELO,
        "stream": False,
        "think": False,
        "options": {"temperature": 0, "num_predict": 256},
        "messages": [
            {"role": "system", "content": instrucao},
            {"role": "user", "content": pergunta},
        ],
    }).encode("utf-8")
    conexao = http.client.HTTPSConnection("ollama.com", timeout=20)
    try:
        conexao.request("POST", "/api/chat", corpo, {
            "Authorization": f"Bearer {chave}",
            "Content-Type": "application/json",
        })
        resposta = conexao.getresponse()
        if resposta.status != 200:
            raise ClassificadorIndisponivel()
        conteudo = json.loads(resposta.read(65536))["message"]["content"].strip()
        bloco = re.fullmatch(r"```(?:json)?\s*(\{.*\})\s*```", conteudo, re.IGNORECASE | re.DOTALL)
        return json.loads(bloco[1] if bloco else conteudo)
    except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError, AttributeError):
        raise ClassificadorIndisponivel() from None
    finally:
        conexao.close()
