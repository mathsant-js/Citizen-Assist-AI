"""Cliente da API direta do Ollama Cloud."""

import http.client
import json
import os
from pathlib import Path
import re

MODELO = "gemma4:31b"
OPCOES_CLASSIFICADOR = {"temperature": 0, "num_predict": 256}
ARQUIVO_ENV = Path(__file__).resolve().parents[1] / ".env"


class OllamaIndisponivel(Exception):
    """Falha de configuração, transporte ou resposta da API."""


class ClassificadorIndisponivel(OllamaIndisponivel):
    """O classificador não retornou uma intenção utilizável."""


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
    try:
        return solicitar_json(
            instrucao, pergunta, modelo=MODELO, think=False,
            opcoes=OPCOES_CLASSIFICADOR, timeout=20,
        )
    except OllamaIndisponivel:
        raise ClassificadorIndisponivel() from None


def solicitar_json(
    instrucao: str, entrada: str, *, modelo: str, think: bool | str, opcoes: dict, timeout: int,
) -> object:
    chave = _ler_chave()
    if not chave or chave == "insira_sua_chave_aqui":
        raise OllamaIndisponivel("chave ausente")

    corpo = json.dumps({
        "model": modelo,
        "stream": False,
        "think": think,
        "options": opcoes,
        "messages": [
            {"role": "system", "content": instrucao},
            {"role": "user", "content": entrada},
        ],
    }).encode("utf-8")
    conexao = http.client.HTTPSConnection("ollama.com", timeout=timeout)
    try:
        conexao.request("POST", "/api/chat", corpo, {
            "Authorization": f"Bearer {chave}",
            "Content-Type": "application/json",
        })
        resposta = conexao.getresponse()
        if resposta.status != 200:
            raise OllamaIndisponivel(f"HTTP {resposta.status}")
        conteudo = json.loads(resposta.read(65536))["message"]["content"].strip()
        bloco = re.fullmatch(r"```(?:json)?\s*(\{.*\})\s*```", conteudo, re.IGNORECASE | re.DOTALL)
        return json.loads(bloco[1] if bloco else conteudo)
    except (OSError, http.client.HTTPException):
        raise OllamaIndisponivel("falha de conexão") from None
    except (ValueError, KeyError, TypeError, AttributeError):
        raise OllamaIndisponivel("resposta inválida da API") from None
    finally:
        conexao.close()
