"""Compara o dataset com a tabela oficial do enunciado em Word."""

import argparse
import json
from pathlib import Path
import re
from xml.etree import ElementTree
from zipfile import ZipFile


WORD = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
DATASET = Path(__file__).resolve().parents[1] / "avaliacao" / "golden_dataset.json"
CABECALHO = ["#", "Mensagem do usuário", "Tipo", "Resposta esperada (conteúdo) e fonte"]


def ler_casos(enunciado: Path) -> list[dict]:
    with ZipFile(enunciado) as arquivo:
        documento = ElementTree.fromstring(arquivo.read("word/document.xml"))

    tabelas = []
    for tabela in documento.findall("./w:body/w:tbl", WORD):
        linhas = [
            [
                "".join(no.text or "" for no in celula.findall(".//w:t", WORD))
                for celula in linha.findall("./w:tc", WORD)
            ]
            for linha in tabela.findall("./w:tr", WORD)
        ]
        if linhas and linhas[0] == CABECALHO:
            tabelas.append(linhas[1:])
    if len(tabelas) != 1 or len(tabelas[0]) != 26:
        raise ValueError("Esperada uma tabela oficial com 26 casos.")

    casos = []
    for id_caso, mensagem, tipo, esperado in tabelas[0]:
        if mensagem.startswith("“") and mensagem.endswith("”"):
            mensagem = mensagem[1:-1]
        casos.append({
            "id": int(id_caso),
            "mensagem": mensagem,
            "tipo": tipo,
            "resposta_esperada": esperado,
            "fontes_esperadas": re.findall(r"\bFC-0[1-7]\b", esperado),
        })
    if [caso["id"] for caso in casos] != list(range(1, 27)):
        raise ValueError("Os IDs do enunciado devem estar na ordem de 1 a 26.")
    return casos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("enunciado", type=Path)
    args = parser.parse_args()
    oficiais = ler_casos(args.enunciado)
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    if not isinstance(dataset, list) or len(dataset) != len(oficiais):
        parser.exit(1, "O dataset deve conter 26 registros.\n")

    divergencias = []
    for oficial, registro in zip(oficiais, dataset):
        if not isinstance(registro, dict) or oficial.keys() != registro.keys():
            divergencias.append(f"Caso {oficial['id']}: campos ausentes ou extras.")
            continue
        campos = [campo for campo in oficial if oficial[campo] != registro[campo]]
        if campos:
            divergencias.append(f"Caso {oficial['id']}: {', '.join(campos)}.")
    if divergencias:
        parser.exit(1, "\n".join(divergencias) + "\n")
    print("26 casos conferidos com o enunciado, sem divergências.")


if __name__ == "__main__":
    main()
