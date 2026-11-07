const campo = document.querySelector("#pergunta");
const formulario = document.querySelector("#formulario");
const menu = document.querySelector("#menu");
const status = document.querySelector("#status");
const painel = document.querySelector("#resposta");
const titulo = document.querySelector("#titulo-resposta");
const alerta = document.querySelector("#alerta");
const mensagem = document.querySelector("#mensagem");
const fontes = document.querySelector("#fontes");
const citacoes = document.querySelector("#citacoes");
const aviso = document.querySelector("#aviso");
const botoesEnvio = [...menu.querySelectorAll("button"), formulario.querySelector("button")];
let ocupado = false;

function texto(elemento, conteudo) {
  // As fichas usam apenas negrito dentro dos parágrafos e dos itens.
  for (const parte of conteudo.split(/(\*\*[^*]+\*\*)/g)) {
    if (parte.startsWith("**") && parte.endsWith("**") && parte.length > 4) {
      const destaque = document.createElement("strong");
      destaque.textContent = parte.slice(2, -2);
      elemento.append(destaque);
    } else {
      elemento.append(document.createTextNode(parte));
    }
  }
}

function exibir(dados) {
  titulo.textContent = dados.estado === "orientacao" ? "Orientação" : "Resposta";
  mensagem.replaceChildren();
  for (const bloco of dados.mensagem.split("\n\n")) {
    let lista;
    for (const [indice, linha] of bloco.split("\n").entries()) {
      const item = /^(\d+\.|-)\s+(.+)$/.exec(linha);
      if (item) {
        const tipo = item[1] === "-" ? "ul" : "ol";
        if (!lista || lista.localName !== tipo) {
          lista = document.createElement(tipo);
          mensagem.append(lista);
        }
        const li = document.createElement("li");
        texto(li, item[2]);
        lista.append(li);
      } else {
        lista = null;
        const elemento = document.createElement(indice === 0 && bloco.includes("\n") ? "h3" : "p");
        texto(elemento, linha);
        mensagem.append(elemento);
      }
    }
  }

  alerta.hidden = !dados.alerta_privacidade;
  alerta.textContent = "Evite informar dados pessoais no chat. Use apenas o portal ou o balcão oficial.";
  fontes.hidden = dados.citacoes.length === 0;
  citacoes.replaceChildren(...dados.citacoes.map(({ codigo, data_verificacao }) => {
    const item = document.createElement("li");
    const data = data_verificacao.split("-").reverse().join("/");
    item.textContent = `${codigo} · ${data}`;
    return item;
  }));
  aviso.textContent = dados.aviso;
  painel.hidden = false;
}

async function consultar(entrada) {
  if (ocupado) return;
  ocupado = true;
  const acionador = document.activeElement;
  for (const botao of botoesEnvio) botao.setAttribute("aria-disabled", "true");
  status.textContent = "Consultando as fichas…";
  painel.hidden = true;
  try {
    const requisicao = fetch("/api/orientacao", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entrada),
      cache: "no-store",
    });
    entrada = null;
    const retorno = await requisicao;
    exibir(await retorno.json());
  } catch {
    exibir({
      estado: "indisponivel",
      mensagem: "Não foi possível conectar ao atendimento. Tente novamente.",
      citacoes: [],
      alerta_privacidade: false,
      aviso: aviso.textContent,
    });
  } finally {
    ocupado = false;
    for (const botao of botoesEnvio) botao.removeAttribute("aria-disabled");
    if (document.activeElement === acionador) {
      status.textContent = "";
      titulo.focus();
    } else {
      status.textContent = "A resposta está disponível após o formulário.";
    }
  }
}

menu.addEventListener("click", (evento) => {
  const botao = evento.target.closest("[data-categoria]");
  if (botao) consultar({ origem: "menu", categoria: botao.dataset.categoria });
});

formulario.addEventListener("submit", (evento) => {
  evento.preventDefault();
  if (ocupado) return;
  const entrada = { origem: "texto", pergunta: campo.value };
  campo.value = "";
  consultar(entrada);
});

for (const exemplo of document.querySelectorAll("[data-exemplo]")) {
  exemplo.addEventListener("click", () => {
    campo.value = exemplo.textContent.trim();
    campo.focus();
  });
}
