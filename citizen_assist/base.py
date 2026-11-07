"""Índice das fichas oficiais do exercício, carregadas dos Markdown originais."""

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re
import unicodedata


PASTA_REFERENCIA = Path(__file__).resolve().parents[1] / "referencia"
CATEGORIAS = {
    "FC-01": "rg",
    "FC-02": "cpf",
    "FC-03": "titulo_eleitor",
    "FC-04": "carteira_trabalho",
    "FC-05": "certidoes",
    "FC-06": "cnh",
    "FC-07": "atendimento_geral",
}
SECAO = re.compile(r"^\*\*(?P<rotulo>[^*]+):\*\*[ \t]*", re.MULTILINE)
FONTE = re.compile(
    r"Central do Cidadão de Aurora, ficha (FC-\d{2}), versão de (\d{2}/\d{2}/\d{4})\."
)


def _normalizar(texto: str) -> str:
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore")
    return "_".join(re.findall(r"[a-z0-9]+", sem_acentos.decode().lower()))


@dataclass(frozen=True)
class Ficha:
    codigo: str
    categoria: str
    titulo: str
    data_verificacao: date
    palavras_chave: tuple[str, ...]
    trechos: dict[str, str]


@dataclass(frozen=True)
class Indice:
    por_categoria: dict[str, Ficha]
    por_palavra_chave: dict[str, tuple[str, ...]]

    def categorias_para(self, palavra_chave: str) -> tuple[str, ...]:
        """Retorna todas as categorias associadas a um termo, inclusive ambiguidades."""
        return self.por_palavra_chave.get(_normalizar(palavra_chave), ())


def _carregar_ficha(arquivo: Path, codigo: str, categoria: str) -> Ficha:
    texto = arquivo.read_text(encoding="utf-8-sig")
    titulo = re.fullmatch(rf"# {codigo} — (.+)", texto.partition("\n")[0])
    if not titulo:
        raise ValueError(f"{arquivo.name}: título ou código inválido")

    secoes = list(SECAO.finditer(texto))
    trechos = {}
    for posicao, secao in enumerate(secoes):
        fim = secoes[posicao + 1].start() if posicao + 1 < len(secoes) else len(texto)
        chave = _normalizar(secao["rotulo"])
        conteudo = texto[secao.end():fim].strip()
        if not chave or not conteudo or chave in trechos:
            raise ValueError(f"{arquivo.name}: seção vazia ou duplicada")
        trechos[chave] = conteudo

    fonte = FONTE.fullmatch(trechos.pop("fonte", ""))
    if not fonte or fonte[1] != codigo:
        raise ValueError(f"{arquivo.name}: fonte ou código de origem inválido")
    data_verificacao = datetime.strptime(fonte[2], "%d/%m/%Y").date()

    termos = trechos.pop("palavras_chave", "").split(",")
    palavras_chave = tuple(termo.strip() for termo in termos if termo.strip())
    if codigo == "FC-07" and not palavras_chave:
        # A ficha geral não tem seção de palavras-chave. Use os próprios assuntos.
        palavras_chave = (*trechos, "Libras")
    if not palavras_chave or not trechos:
        raise ValueError(f"{arquivo.name}: faltam palavras-chave ou trechos")

    return Ficha(codigo, categoria, titulo[1], data_verificacao, palavras_chave, trechos)


def carregar_indice(pasta: Path = PASTA_REFERENCIA) -> Indice:
    """Lê somente FC-01 a FC-07 e preserva o texto completo de cada seção."""
    fichas = {}
    palavras_chave: dict[str, list[str]] = {}
    for codigo, categoria in CATEGORIAS.items():
        arquivos = list(pasta.glob(f"{codigo}_*.md"))
        if len(arquivos) != 1 or not arquivos[0].is_file():
            raise ValueError(f"{codigo}: esperado exatamente um arquivo Markdown")

        ficha = _carregar_ficha(arquivos[0], codigo, categoria)
        fichas[categoria] = ficha
        for termo in dict.fromkeys(map(_normalizar, ficha.palavras_chave)):
            palavras_chave.setdefault(termo, []).append(categoria)

    return Indice(
        por_categoria=fichas,
        por_palavra_chave={
            termo: tuple(categorias) for termo, categorias in palavras_chave.items()
        },
    )
