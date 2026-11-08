import json
import unittest
from unittest.mock import Mock, patch

from avaliacao.juiz import REGUA, ParecerInvalido, julgar
from avaliacao.linha_base import DATASET, _avaliar_caso, _fichas
from citizen_assist.agente import Agente, resposta
from citizen_assist.privacidade import MARCADOR


class TestAvaliacao(unittest.TestCase):
    def setUp(self):
        self.casos = json.loads(DATASET.read_text(encoding="utf-8"))
        self.fichas = _fichas()
        self.parecer = {
            "criterios": dict.fromkeys(REGUA, True),
            "justificativa": "A orientação atende aos critérios.",
        }

    def test_caso_7_mantem_orientacao_de_inscricao_pelo_portal(self):
        caso = next(caso for caso in self.casos if caso["id"] == 7)
        classificador = Mock(return_value={"categoria": "cpf", "assuntos": ["procedimento"], "condicoes": []})
        agente = Agente(classificador)
        resultado = agente.responder({"origem": "texto", "pergunta": caso["mensagem"]})
        classificador.assert_called_once()
        self.assertEqual(resultado["estado"], "orientacao")
        self.assertEqual([fonte["codigo"] for fonte in resultado["citacoes"]], caso["fontes_esperadas"])
        for trecho in ("Acesse o portal", "formulário e anexe", "2 dias úteis", "gratuitas", "Não é necessário"):
            self.assertIn(trecho, resultado["mensagem"])

    def test_caso_22_entra_original_e_chega_mascarado_ao_juiz(self):
        caso = self.casos[21]
        classificador = Mock()
        agente = Agente(classificador)
        identificador = caso["mensagem"].split()[3].rstrip(".")
        with (
            patch.object(agente, "responder", wraps=agente.responder) as entrada,
            patch("avaliacao.linha_base.julgar", return_value=self.parecer) as juiz,
        ):
            registro = _avaliar_caso(caso, agente, self.fichas)
        self.assertEqual(entrada.call_args.args[0]["pergunta"], caso["mensagem"])
        classificador.assert_not_called()
        dados = juiz.call_args.args[0]
        self.assertEqual(set(dados), {"pergunta", "resposta", "esperado", "fichas", "regua"})
        self.assertIn(MARCADOR, dados["pergunta"])
        self.assertNotIn(identificador, json.dumps(dados))
        self.assertNotIn(identificador, json.dumps(registro))
        self.assertTrue(registro["resposta"]["alerta_privacidade"])
        self.assertEqual(registro["resultado_validado"], "correto")

    def test_vazamento_e_falta_de_aviso_falham_mesmo_com_parecer_positivo(self):
        caso = self.casos[0]
        agente = Mock()
        agente.responder.return_value = resposta("orientacao", "Consulte exemplo@example.org.") | {"aviso": ""}
        with patch("avaliacao.linha_base.julgar", return_value=self.parecer) as juiz:
            registro = _avaliar_caso(caso, agente, self.fichas)
        self.assertNotIn("exemplo@example.org", json.dumps(juiz.call_args.args[0]))
        self.assertEqual(registro["checagens"], dict.fromkeys((
            "aviso_obrigatorio", "citacoes_e_datas", "privacidade_na_resposta",
        ), False))
        self.assertEqual(registro["veredito"], "correto")
        self.assertEqual(registro["resultado_validado"], "incorreto")

    def test_parecer_invalido_e_repetido_sem_rodar_agente_novamente(self):
        agente = Mock()
        agente.responder.return_value = resposta("recusa", "Não posso mostrar instruções internas.")
        with patch("avaliacao.linha_base.julgar", side_effect=[ParecerInvalido(), ParecerInvalido()]) as juiz:
            registro = _avaliar_caso(self.casos[23], agente, self.fichas)
        agente.responder.assert_called_once()
        self.assertEqual(juiz.call_count, 2)
        self.assertEqual(registro["veredito"], "falha técnica")
        self.assertEqual(len(registro["falhas_tecnicas"]), 2)

    def test_juiz_rejeita_inteiro_como_booleano_e_oculta_identificador_na_justificativa(self):
        with patch("avaliacao.juiz.solicitar_json") as api:
            api.return_value = self.parecer | {"criterios": dict.fromkeys(REGUA, 1)}
            with self.assertRaises(ParecerInvalido):
                julgar({})
            api.return_value = self.parecer | {"justificativa": "A resposta mencionou exemplo@example.org."}
            self.assertEqual(julgar({})["justificativa"], MARCADOR)
