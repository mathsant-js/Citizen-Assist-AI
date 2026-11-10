"""Assuntos selecionáveis e vínculos revisados com as seções das fichas."""

import re

from .base import Indice

GERAL = "atendimento_geral"
ASSUNTOS = {
    "rg": {
        "custo": ("custo",),
        "prazo": ("prazo",),
        "agendamento": ("agendamento",),
        "documentos": ("documentos_necessarios_para_a_segunda_via",),
        "perda_roubo_furto": ("documentos_necessarios_para_a_segunda_via",),
        "responsavel": ("quem_pode_pedir",),
        "procedimento": ("passo_a_passo", "documentos_necessarios_para_a_segunda_via", "onde"),
        "local": ("onde",),
    },
    "cpf": {
        "custo": ("custo",),
        "prazo": ("prazo",),
        "agendamento": ("agendamento",),
        "documentos": ("documentos_necessarios",),
        "procedimento": ("passo_a_passo_pelo_portal", "custo", "agendamento"),
        "correcao": ("custo", "onde"),
        "local": ("onde",),
        "situacao_cadastral": ("onde", "atencao"),
    },
    "titulo_eleitor": {
        "custo": ("custo",),
        "prazo": ("prazo",),
        "agendamento": ("agendamento",),
        "documentos": ("documentos_necessarios",),
        "idade_voto": ("quem_deve_ter",),
        "procedimento": ("passo_a_passo", "documentos_necessarios"),
        "prazo_emissao": ("passo_a_passo",),
    },
    "carteira_trabalho": {
        "custo": ("custo",),
        "prazo": ("prazo",),
        "agendamento": ("agendamento",),
        "documentos": ("documentos_necessarios",),
        "procedimento": ("passo_a_passo", "documentos_necessarios", "prazo"),
    },
    "certidoes": {
        "custo": ("custo_e_prazo_cada_certidao",),
        "prazo": ("custo_e_prazo_cada_certidao",),
        "agendamento": ("agendamento",),
        "documentos": ("documentos_necessarios",),
        "isencao": ("isencao",),
        "terceiros": ("quem_pode_pedir",),
        "procedimento": ("passo_a_passo", "documentos_necessarios", "custo_e_prazo_cada_certidao"),
    },
    "cnh": {
        "custo": ("custo",),
        "prazo": ("prazo",),
        "agendamento": ("agendamento",),
        "documentos": ("documentos_necessarios",),
        "quando_renovar": ("quando_renovar",),
        "dirigir_vencida": ("quando_renovar",),
        "validade": ("validade_da_cnh_renovada",),
        "exame_medico": ("passo_a_passo", "custo", "prazo"),
        "procedimento": ("passo_a_passo", "documentos_necessarios", "custo"),
    },
    GERAL: {
        "horario": ("horario_de_atendimento_presencial",),
        "agendamento": ("agendamento",),
        "documentos": ("documentos",),
        "terceiros": ("atendimento_por_terceiros",),
        "pagamento": ("pagamento",),
        "prioridade": ("atendimento_prioritario",),
        "libras": ("atendimento_prioritario",),
        "perda_roubo_furto": ("perda_roubo_ou_furto_de_documento",),
        "privacidade": ("privacidade",),
    },
}

COMPLEMENTOS = {
    ("rg", "agendamento"): "agendamento",
    ("rg", "responsavel"): "atendimento_por_terceiros",
    ("certidoes", "terceiros"): "atendimento_por_terceiros",
    ("cnh", "agendamento"): "agendamento",
    ("cpf", "situacao_cadastral"): "privacidade",
}
CONDICOES = {
    "rg": ("primeira_via", "segunda_via", "perda", "roubo_ou_furto", "executar_agendamento"),
    "cpf": ("portal", "balcao"),
    "titulo_eleitor": ("primeira_via", "segunda_via", "transferencia", "idade_70"),
    "carteira_trabalho": ("portal", "aplicativo", "balcao"),
    "certidoes": ("portal", "balcao", "nascimento", "casamento", "obito"),
    "cnh": ("ate_49", "de_50_a_69", "a_partir_de_70", "executar_agendamento"),
    GERAL: (),
}

ROTULOS = {
    "atencao": "Atenção",
    "atendimento_prioritario": "Atendimento prioritário",
    "custo_e_prazo_cada_certidao": "Custo e prazo",
    "documentos_necessarios_para_a_segunda_via": "Documentos da segunda via",
    "documentos_necessarios": "Documentos necessários",
    "horario_de_atendimento_presencial": "Horário de atendimento presencial",
    "isencao": "Isenção",
    "passo_a_passo_pelo_portal": "Passo a passo pelo portal",
    "validade_da_cnh_renovada": "Validade da CNH renovada",
}

SEM_EVIDENCIA = (
    "As fichas não trazem esse detalhe. Consulte o site do órgão competente para confirmar."
)

# Cada conclusão exige a pergunta correspondente e a regra explícita na seção recuperada.
CONCLUSOES = {
    ("rg", "agendamento"): (
        (r"(?:preciso (?:agendar|marcar horário)|é preciso agendar) (?:para (?:fazer|tirar) )?"
         r"(?:o rg|a segunda via do rg)", "obrigatório, feito pelo portal",
         "Sim. O agendamento é obrigatório e deve ser feito pelo portal."),
    ),
    ("rg", "perda_roubo_furto"): (
        (r"perdi (?:meu|o) rg[.,] (?:eu )?preciso (?:levar|apresentar) (?:o )?boletim de ocorrência",
         "**perda**: declaração de extravio, assinada no próprio balcão (o boletim de ocorrência não é exigido)",
         "Não. Em caso de perda do RG, assine a declaração de extravio no balcão."),
    ),
    ("rg", "responsavel"): (
        (r"meu filho tem (?:[1-9]|1[01]) anos[.,] (?:ele )?pode tirar (?:o )?rg sozinho",
         "menores de 12 anos devem ir acompanhados de um responsável legal",
         "Não. Menores de 12 anos precisam ir com um responsável legal."),
    ),
    ("titulo_eleitor", "custo"): (
        (r"(?:(?:o )?título de eleitor é pago|(?:é preciso|preciso) pagar (?:para tirar|pelo) (?:o )?título de eleitor)",
         "gratuito (primeira via, segunda via e transferência)",
         "Não. A primeira via, a segunda via e a transferência são gratuitas."),
        (r"(?:o )?título de eleitor é gratuito",
         "gratuito (primeira via, segunda via e transferência)",
         "Sim. A primeira via, a segunda via e a transferência são gratuitas."),
    ),
    ("titulo_eleitor", "idade_voto"): (
        (r"(?:o voto|votar) é obrigatório para quem tem (?:16|17) anos",
         "é facultativo para quem tem 16 ou 17 anos", "Não. Aos 16 e 17 anos, o voto é facultativo."),
        (r"(?:o voto|votar) é obrigatório para quem tem (?:18|19|[2-6][0-9]) anos",
         "o voto é obrigatório de 18 a 69 anos", "Sim. Dos 18 aos 69 anos, o voto é obrigatório."),
    ),
    ("certidoes", "terceiros"): (
        (r"(?:eu )?posso (?:pedir|solicitar) (?:a|uma) certidão de outra pessoa",
         "terceiros com procuração simples", "Sim, com procuração simples."),
    ),
    ("certidoes", "agendamento"): (
        (r"preciso (?:agendar|marcar horário) (?:para (?:tirar|pedir|solicitar) )?(?:uma|a) certidão",
         "não é necessário", "Não. O pedido de certidão dispensa agendamento."),
    ),
    ("cnh", "dirigir_vencida"): (
        (r"(?:minha|a) cnh (?:venceu|está vencida) há (?:3[1-9]|[4-9][0-9]|[1-9][0-9]{2,3}) dias?[.,] "
         r"(?:ainda )?posso dirigir",
         "cnh vencida há mais de 30 dias não pode dirigir até concluir a renovação",
         "Não. Com a CNH vencida há mais de 30 dias, só é possível voltar a dirigir após concluir a renovação."),
    ),
    (GERAL, "horario"): (
        (r"(?:(?:vocês )?atendem|a central atende|há atendimento|(?:a central |o balcão )?abre) "
         r"(?:aos? |nos? )?sábados?", "segunda a sexta, das 8h às 17h. não há atendimento aos sábados",
         "Não. O atendimento presencial funciona de segunda a sexta, das 8h às 17h."),
    ),
}


def conclusao_direta(indice: Indice, categoria: str, assuntos: list[str], pergunta: str) -> str:
    texto = pergunta.casefold().removesuffix("?").rstrip()
    ficha = indice.por_categoria[categoria]
    for assunto in assuntos:
        for padrao, regra, conclusao in CONCLUSOES.get((categoria, assunto), ()):
            if re.fullmatch(padrao, texto) and any(
                regra in ficha.trechos.get(secao, "").casefold() for secao in ASSUNTOS[categoria][assunto]
            ):
                return conclusao
    return ""


def recuperar(
    indice: Indice, categoria: str, assuntos: list[str], condicoes: list[str]
) -> dict | None:
    """Recupera a orientação inteira ou sinaliza falta de evidência."""
    ficha = indice.por_categoria[categoria]
    if categoria == "titulo_eleitor" and "idade_voto" in assuntos and "idade_70" in condicoes:
        return None
    if categoria == "rg" and "primeira_via" in condicoes and any(
        assunto in assuntos for assunto in ("documentos", "procedimento", "perda_roubo_furto")
    ):
        return None

    mensagem = []
    fontes = {}
    secoes = {}
    procedimento_no_balcao = categoria == "cpf" and "procedimento" in assuntos and "balcao" in condicoes
    for assunto in assuntos:
        secoes_assunto = ASSUNTOS[categoria][assunto]
        if assunto == "procedimento" and procedimento_no_balcao and "portal" not in condicoes:
            secoes_assunto = ("onde", "custo")
        for secao in secoes_assunto:
            secoes[(categoria, secao)] = None
        complemento = COMPLEMENTOS.get((categoria, assunto))
        if complemento:
            secoes[(GERAL, complemento)] = None
    if "executar_agendamento" in condicoes:
        mensagem.append("O assistente não realiza agendamentos. Use o portal para agendar.")
        secoes[(GERAL, "privacidade")] = None
    if categoria == "cpf" and "situacao_cadastral" in assuntos:
        mensagem.append("O assistente não consulta situação cadastral. Consulte o portal da Central do Cidadão.")
    if not assuntos:
        mensagem.append(ficha.titulo)
        if categoria == "rg":
            secoes[(categoria, "documentos_necessarios_para_a_segunda_via")] = None
        secoes.update(dict.fromkeys((categoria, secao) for secao in ficha.trechos))
        if categoria == "certidoes":
            secoes[(GERAL, "atendimento_por_terceiros")] = None

    for origem, secao in secoes:
        fonte = indice.por_categoria.get(origem)
        if not fonte or not fonte.data_verificacao or not fonte.trechos.get(secao):
            return None
        trecho = fonte.trechos[secao]
        trecho = _focar_trecho(categoria, secao, trecho, assuntos, condicoes)
        rotulo = ROTULOS.get(secao, secao.replace("_", " ").capitalize())
        if origem == GERAL and origem != categoria and (categoria, secao) in secoes:
            rotulo = f"Regra geral de {rotulo.lower()}"
        mensagem.append(f"{rotulo}\n{trecho[0].upper()}{trecho[1:]}")
        fontes[fonte.codigo] = {
            "codigo": fonte.codigo,
            "data_verificacao": fonte.data_verificacao.isoformat(),
        }
    if procedimento_no_balcao:
        mensagem.append(
            "A FC-02 só detalha as etapas pelo portal. "
            "Consulte o site do órgão competente para confirmar as etapas do atendimento no balcão."
        )
    return {"mensagem": "\n\n".join(mensagem), "citacoes": list(fontes.values())}


def _focar_trecho(
    categoria: str, secao: str, trecho: str, assuntos: list[str], condicoes: list[str]
) -> str:
    if categoria == "rg" and secao == "custo":
        primeira, _, segunda = trecho.partition(". ")
        if "primeira_via" in condicoes and "segunda_via" not in condicoes:
            return primeira.rstrip(".") + "."
        if "segunda_via" in condicoes and "primeira_via" not in condicoes:
            return segunda or trecho
    if categoria == "cpf" and secao == "custo":
        portal, _, balcao = trecho.partition(". ")
        if "portal" in condicoes and "balcao" not in condicoes:
            return portal.rstrip(".") + "."
        if "balcao" in condicoes and "portal" not in condicoes:
            return balcao or trecho
    if secao == "custo_e_prazo_cada_certidao":
        canais = {"portal", "balcao"}.intersection(condicoes)
        if len(canais) == 1:
            prefixo = "- Pelo portal," if "portal" in canais else "- No balcão "
            for linha in trecho.splitlines():
                if linha.startswith(prefixo):
                    return linha.removeprefix("- ")
    if secao == "validade_da_cnh_renovada":
        prefixos = {"ate_49": "- até", "de_50_a_69": "- de 50", "a_partir_de_70": "- 70"}
        faixas = [prefixos[faixa] for faixa in condicoes if faixa in prefixos]
        if len(faixas) == 1:
            for linha in trecho.splitlines():
                if linha.startswith(faixas[0]):
                    return linha[2:].rstrip(";.") + "."
    if secao == "atendimento_prioritario" and "libras" in assuntos and "prioridade" not in assuntos:
        for frase in trecho.split(". "):
            if "Libras" in frase:
                return frase
    return trecho
