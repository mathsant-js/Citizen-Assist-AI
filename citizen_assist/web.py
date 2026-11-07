"""Interface HTTP local. Recebe perguntas somente em POST, sem logs de acesso."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path

from .agente import Agente, resposta

ENDERECO = "127.0.0.1"
PORTA = 8000
ASSETS = Path(__file__).with_name("interface")
ARQUIVOS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/estilo.css": ("estilo.css", "text/css; charset=utf-8"),
    "/interface.js": ("interface.js", "text/javascript; charset=utf-8"),
}


class RequisicaoInvalida(ValueError):
    pass


class Interface(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def send_error(self, code, *_args, **_kwargs):
        self._enviar_json(code, resposta("entrada_invalida", "Solicitação inválida."))

    def _enviar(self, status: int, tipo: str, corpo: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; frame-ancestors 'none'; form-action 'none'; base-uri 'none'",
        )
        self.end_headers()
        self.wfile.write(corpo)

    def _enviar_json(self, status: int, dados: dict) -> None:
        self._enviar(status, "application/json; charset=utf-8", json.dumps(dados, ensure_ascii=False).encode("utf-8"))

    def _origem_local(self) -> bool:
        porta = self.server.server_port
        hosts = {f"{ENDERECO}:{porta}", f"localhost:{porta}"}
        host = self.headers.get("Host")
        origem = self.headers.get("Origin")
        return host in hosts and (origem is None or origem == f"http://{host}")

    def do_GET(self) -> None:
        if not self._origem_local() or self.path not in ARQUIVOS:
            self._enviar(404, "text/plain; charset=utf-8", b"Recurso indisponivel.")
            return
        arquivo, tipo = ARQUIVOS[self.path]
        self._enviar(200, tipo, (ASSETS / arquivo).read_bytes())

    def _ler_entrada(self) -> object:
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if not 0 < tamanho <= 8192 or self.headers.get_content_type() != "application/json":
                raise ValueError
            return json.loads(self.rfile.read(tamanho).decode("utf-8"))
        except (ValueError, OSError, RecursionError):
            raise RequisicaoInvalida() from None

    def do_POST(self) -> None:
        if not self._origem_local() or self.path != "/api/orientacao":
            self._enviar_json(404, resposta("entrada_invalida", "Recurso indisponível."))
            return

        try:
            resultado = self.server.agente.responder(self._ler_entrada())
        except RequisicaoInvalida:
            self._enviar_json(400, resposta("entrada_invalida", "Não foi possível ler a pergunta. Tente novamente."))
            return
        except Exception:
            # Não registrar exceções da solicitação, que podem carregar dados de entrada.
            self._enviar_json(500, resposta("indisponivel", "O atendimento está indisponível. Tente novamente."))
            return
        self._enviar_json(200, resultado)


class ServidorLocal(ThreadingHTTPServer):
    def __init__(self, agente: Agente, porta: int = PORTA):
        super().__init__((ENDERECO, porta), Interface)
        self.agente = agente

    def get_request(self):
        conexao, endereco = super().get_request()
        conexao.settimeout(10)
        return conexao, endereco

    def handle_error(self, *_args):
        # Evita que falhas da conexão escrevam dados da solicitação no terminal.
        pass


def main() -> None:
    with ServidorLocal(Agente()) as servidor:
        print(f"Citizen Assist AI disponível em http://{ENDERECO}:{servidor.server_port}", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
