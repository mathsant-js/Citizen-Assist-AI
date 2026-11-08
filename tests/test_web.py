from contextlib import redirect_stderr, redirect_stdout
import http.client
from io import StringIO
import json
from threading import Thread
import unittest
from unittest.mock import Mock

from citizen_assist.agente import AVISO, Agente
from citizen_assist.base import CATEGORIAS
from citizen_assist.ollama import ClassificadorIndisponivel
from citizen_assist.privacidade import MARCADOR
from citizen_assist.web import ENDERECO, ServidorLocal


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.classificador = Mock(return_value={
            "categoria": "atendimento_geral", "assuntos": ["libras"], "condicoes": [],
        })
        servidor = ServidorLocal(Agente(self.classificador), porta=0)
        self.addCleanup(servidor.server_close)
        thread = Thread(target=servidor.serve_forever, kwargs={"poll_interval": 0.05})
        thread.start()
        self.addCleanup(thread.join)
        self.addCleanup(servidor.shutdown)
        self.http = http.client.HTTPConnection(ENDERECO, servidor.server_port, timeout=5)
        self.addCleanup(self.http.close)

    def requisitar(self, metodo, caminho, corpo=None):
        self.http.request(metodo, caminho, corpo, {"Content-Type": "application/json"})
        resposta = self.http.getresponse()
        self.assertEqual(resposta.getheader("Cache-Control"), "no-store")
        return resposta.status, resposta.read().decode("utf-8")

    def consultar(self, entrada, status_esperado=200):
        status, corpo = self.requisitar("POST", "/api/orientacao", json.dumps(entrada))
        self.assertEqual(status, status_esperado)
        resposta = json.loads(corpo)
        self.assertEqual(resposta["aviso"], AVISO)
        return resposta

    def test_pagina_e_sete_categorias(self):
        status, pagina = self.requisitar("GET", "/")
        self.assertEqual(status, 200)
        for codigo, categoria in CATEGORIAS.items():
            with self.subTest(categoria=categoria):
                self.assertIn(f'data-categoria="{categoria}"', pagina)
                resposta = self.consultar({"origem": "menu", "categoria": categoria})
                self.assertEqual(resposta["estado"], "orientacao")
                self.assertIn({"codigo": codigo, "data_verificacao": "2026-10-01"}, resposta["citacoes"])
        self.classificador.assert_not_called()

    def test_pergunta_livre_chega_ao_modelo_sem_identificador(self):
        dado = "exemplo@example.org"
        resposta = self.consultar({"origem": "texto", "pergunta": f"{dado}. Como agendo Libras?"})
        self.assertEqual(resposta["estado"], "orientacao")
        self.assertTrue(resposta["alerta_privacidade"])
        self.assertEqual(resposta["citacoes"], [{"codigo": "FC-07", "data_verificacao": "2026-10-01"}])
        self.assertIn("48 horas", resposta["mensagem"])
        self.assertNotIn("gestantes", resposta["mensagem"])
        self.assertNotIn(dado, json.dumps(resposta))
        self.classificador.assert_called_once()
        self.assertNotIn(dado, self.classificador.call_args.args[1])

    def test_ambiguidade_e_indisponibilidade(self):
        self.classificador.side_effect = ClassificadorIndisponivel()
        resposta = self.consultar({"origem": "texto", "pergunta": "Segunda via?"})
        self.assertEqual(resposta["estado"], "pedir_esclarecimento")
        self.classificador.assert_not_called()
        resposta = self.consultar({"origem": "texto", "pergunta": "Como agendo Libras?"})
        self.assertEqual(resposta["estado"], "indisponivel")
        self.assertEqual(resposta["citacoes"], [])
        self.assertIn("menu", resposta["mensagem"])
        resposta = self.consultar({"origem": "menu", "categoria": "atendimento_geral"})
        self.assertEqual(resposta["estado"], "orientacao")

    def test_json_invalido_recebe_aviso(self):
        status, corpo = self.requisitar("POST", "/api/orientacao", "{")
        self.assertEqual(status, 400)
        resposta = json.loads(corpo)
        self.assertEqual(resposta["estado"], "entrada_invalida")
        self.assertEqual(resposta["aviso"], AVISO)
        self.classificador.assert_not_called()

    def test_falhas_http_com_dado_ficticio_nao_expoem_o_conteudo(self):
        dado = "Praça Fictícia"
        pergunta = "Como agendo Libras?"
        saida, erros = StringIO(), StringIO()
        with redirect_stdout(saida), redirect_stderr(erros), self.assertNoLogs(level="DEBUG"):
            resposta = self.consultar({
                "origem": "texto", "pergunta": f"Meu endereço residencial é {dado}, {pergunta}",
            })
            self.assertEqual(resposta["estado"], "pedir_esclarecimento")
            self.assertTrue(resposta["alerta_privacidade"])
            self.assertNotIn(dado, str(resposta))
            self.classificador.assert_not_called()

            json_invalido = f'{{"pergunta": "{dado}"'.encode("utf-8")
            status, corpo = self.requisitar("POST", "/api/orientacao", json_invalido)
            self.assertEqual(status, 400)
            self.assertNotIn(dado, corpo)
            self.classificador.assert_not_called()

            entrada = {"origem": "texto", "pergunta": f"Meu endereço residencial é {dado}. {pergunta}"}
            for falha, status in ((ClassificadorIndisponivel(dado), 200), (RuntimeError(dado), 500)):
                with self.subTest(status=status):
                    self.classificador.reset_mock()
                    self.classificador.side_effect = falha
                    resposta = self.consultar(entrada, status)
                    self.assertEqual(resposta["estado"], "indisponivel")
                    self.assertEqual(resposta["citacoes"], [])
                    self.assertNotIn(dado, str(resposta))
                    self.classificador.assert_called_once()
                    self.assertEqual(self.classificador.call_args.args[1], f"{MARCADOR}. {pergunta}")
        self.assertEqual(saida.getvalue(), "")
        self.assertEqual(erros.getvalue(), "")
