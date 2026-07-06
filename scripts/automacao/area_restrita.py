"""Automação da Área Restrita do TCE (novaarearestrita.tce.rn.gov.br).

Distribuição de processos eletrônicos no setor sem cliques: replica os POSTs
que os botões do site fazem (frame botoesNOVO.asp apenas seta form1.oculto e
submete o form principal).

Uso:
    python -m scripts.automacao.area_restrita distribuir 12345/2024 [12346/2024 ...] [--dry-run]
    python -m scripts.automacao.area_restrita informacao 12345/2024 --pdf caminho.pdf [--dry-run]
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from urllib.parse import urljoin

import requests
import urllib3
from lxml import html as lxml_html

from ccd.config import load_env

BASE = "https://novaarearestrita.tce.rn.gov.br/"
# tile "Proc./ Doc. Eletrônico no Setor" da Mesa Eletrônica
PAGINA_SETOR = (
    BASE + "SISTEMAS/Processo/ProcessonoSetor.asp"
    "?tcenet_Sistema=Administrativo&tcenet_Modulo=Processo"
    "&qsSetor=CCD&qsEletronico=S&seletivo=&qsTipoConsulta="
)
# Administrativo > Informações > Cadastrar Informação Digitalizada
PAGINA_DIGITALIZAR = (
    BASE + "SISTEMAS/Informacoes/DigitalizarInformacao.asp"
    "?tcenet_Sistema=Administrativo&tcenet_Modulo=Informacoes"
)
MODELO_TITULO = "InformacaoInstrutiva"
MODELO_RESUMO = "Informação instrutiva...."


class AreaRestrita:
    """Sessão autenticada na Área Restrita (Basic Auth + cookie ASP)."""

    def __init__(self) -> None:
        load_env()
        urllib3.disable_warnings()
        self.s = requests.Session()
        self.s.auth = (os.environ["AR_USER"], os.environ["AR_PASS"])
        self.s.verify = False  # TLS interceptado pelo proxy corporativo
        self._get(BASE + "telaPrincipalMenu.asp")  # estabelece ASPSESSIONID

    def _get(self, url: str) -> requests.Response:
        r = self.s.get(url, timeout=60)
        r.raise_for_status()
        r.encoding = "windows-1252"
        return r

    def _post(self, url: str, data: dict) -> requests.Response:
        # ASP clássico espera windows-1252; requests enviaria UTF-8 e corromperia acentos
        payload = {k: str(v).encode("windows-1252", "replace") for k, v in data.items()}
        r = self.s.post(url, data=payload, timeout=120)
        r.raise_for_status()
        r.encoding = "windows-1252"
        return r

    @staticmethod
    def _form(resp: requests.Response) -> tuple[str, dict]:
        """(url_acao, campos) do form1, serializado como o navegador envia."""
        doc = lxml_html.fromstring(resp.text)
        forms = [f for f in doc.forms if (f.get("name") or f.get("id") or "").lower() == "form1"]
        form = forms[0] if forms else doc.forms[0]
        action = urljoin(resp.url, form.get("action") or resp.url)
        campos: dict[str, str] = {}
        for el in form.xpath(".//input | .//select | .//textarea"):
            name = el.get("name")
            if not name:
                continue
            if el.tag == "input":
                tipo = (el.get("type") or "text").lower()
                if tipo in ("checkbox", "radio"):
                    if el.get("checked") is not None:
                        campos[name] = el.get("value") or "on"
                elif tipo not in ("button", "submit", "image", "reset"):
                    campos[name] = el.get("value") or ""
            elif el.tag == "select":
                marcada = el.xpath(".//option[@selected]/@value")
                todas = el.xpath(".//option/@value")
                campos[name] = marcada[0] if marcada else (todas[0] if todas else "")
            else:  # textarea
                campos[name] = el.text or ""
        return action, campos

    @staticmethod
    def _mensagem(resp: requests.Response) -> str:
        alerts = re.findall(r"alert\('([^']+)'\)", resp.text)
        if alerts:
            return "; ".join(dict.fromkeys(alerts))
        return f"(sem alert; HTTP {resp.status_code}, {len(resp.text)} bytes)"

    def consultar(self, numero: int, ano: int) -> tuple[str, dict, str, str]:
        """Filtra o processo na tela do setor. Retorna (action, campos, nome_checkbox, chave)."""
        r = self._get(PAGINA_SETOR)
        action, campos = self._form(r)
        campos.update(
            txtNumeroProcesso=f"{numero:06d}",
            txtAnoProcesso=str(ano),
            oculto="C",
        )
        r = self._post(action, campos)
        chave = f"{numero:06d}{ano}"
        doc = lxml_html.fromstring(r.text)
        nomes = doc.xpath(f"//input[@type='checkbox'][@value='{chave}']/@name")
        if not nomes:
            raise LookupError(f"processo {numero:06d}/{ano} não está na listagem do setor")
        action, campos = self._form(r)
        return action, campos, nomes[0], chave

    def distribuir_propria(self, numero: int, ano: int, dry_run: bool = False) -> None:
        """Consultar -> Distribuição (Própria) -> Iniciar Análise."""
        action, campos, checkbox, chave = self.consultar(numero, ano)
        print(f"  consultado: {checkbox}={chave}")
        if dry_run:
            print("  dry-run: parando antes da distribuição")
            return
        extras = {
            checkbox: chave,
            "txtNumeroProcessoAba": chave[:6],
            "txtAnoProcessoAba": chave[6:],
        }
        r = self._post(action, {**campos, **extras, "oculto": "DM"})
        print(f"  DM: {self._mensagem(r)}")
        action, campos = self._form(r)
        r = self._post(action, {**campos, **extras, "oculto": "IA"})
        print(f"  IA: {self._mensagem(r)}")

    def _upload_pdf(self, pdf: str) -> str:
        """Sobe o PDF pelo popup de upload. Retorna o nome do arquivo no servidor."""
        r = self._get(BASE + "Upload/upload.asp?modo=PDFDigitalizado&NomeCampoDestino=txtNomeArquivo1")
        doc = lxml_html.fromstring(r.text)
        form = doc.forms[0]
        action = urljoin(r.url, form.get("action"))
        campos = dict(form.form_values())
        campos.pop("UploadFormName1", None)  # vai como arquivo, não como campo
        campos.pop("realupload", None)
        with open(pdf, "rb") as fh:
            resp = self.s.post(
                action,
                data=campos,
                files={"UploadFormName1": (os.path.basename(pdf), fh, "application/pdf")},
                timeout=300,
            )
        resp.raise_for_status()
        resp.encoding = "windows-1252"
        m = re.search(r"FechaJanela\('([^']+)'\)", resp.text)
        if not m:
            raise RuntimeError(f"upload sem FechaJanela: {self._mensagem(resp)}")
        return m.group(1)

    def cadastrar_informacao_digitalizada(self, numero: int, ano: int, pdf: str,
                                          dry_run: bool = False) -> None:
        """Consultar processo -> upload do PDF -> Incluir informação (modelo InformacaoInstrutiva)."""
        r = self._get(PAGINA_DIGITALIZAR)
        action, campos = self._form(r)
        campos.update(
            txtNumeroProcesso=f"{numero:06d}",
            txtAnoProcesso=str(ano),
            oculto="C",
        )
        r = self._post(action, campos)
        if "txtTituloModelo" not in r.text:
            raise LookupError(f"consulta não abriu o cadastro: {self._mensagem(r)}")
        print("  consultado: cadastro disponível")
        if dry_run:
            print("  dry-run: parando antes do upload/inclusão")
            return
        nome_arquivo = self._upload_pdf(pdf)
        print(f"  upload: {nome_arquivo}")
        action, campos = self._form(r)
        campos.update(
            txtTituloModelo=MODELO_TITULO,
            txtResumo=MODELO_RESUMO,
            txtNomeArquivo1=nome_arquivo,
            oculto="I",
        )
        r = self._post(action, campos)
        # sucesso = servidor devolve o identificador da informação criada
        m = re.search(r'name="ocultoNomeArquivoPDF"[^>]*value="([^"]+)"', r.text)
        if not m:
            raise RuntimeError(f"inclusão não confirmada: {self._mensagem(r)}")
        print(f"  incluída: {m.group(1)} (pendente de assinatura no navegador)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Automação da Área Restrita do TCE")
    sub = parser.add_subparsers(dest="tarefa", required=True)

    p_dist = sub.add_parser("distribuir", help="distribuição própria + iniciar análise")
    p_dist.add_argument("processos", nargs="+", help="numero/ano, ex.: 12345/2024")
    p_dist.add_argument("--dry-run", action="store_true", help="só consulta; não distribui")

    p_info = sub.add_parser("informacao", help="cadastrar informação digitalizada (InformacaoInstrutiva)")
    p_info.add_argument("processos", nargs="+", help="numero/ano, ex.: 12345/2024")
    p_info.add_argument("--pdf", required=True, help="PDF a subir como arquivo digitalizado 1")
    p_info.add_argument("--dry-run", action="store_true", help="só consulta; não sobe nem inclui")

    args = parser.parse_args()
    if args.tarefa == "informacao" and not os.path.isfile(args.pdf):
        print(f"PDF não encontrado: {args.pdf}")
        return 1

    ar = AreaRestrita()
    falhas = 0
    for proc in args.processos:
        m = re.fullmatch(r"(\d{1,6})/(\d{4})", proc.strip())
        if not m:
            print(f"{proc}: formato inválido (esperado numero/ano)")
            falhas += 1
            continue
        numero, ano = int(m.group(1)), int(m.group(2))
        print(f"{numero:06d}/{ano}:")
        try:
            if args.tarefa == "distribuir":
                ar.distribuir_propria(numero, ano, dry_run=args.dry_run)
            else:
                ar.cadastrar_informacao_digitalizada(numero, ano, args.pdf, dry_run=args.dry_run)
        except Exception as e:  # segue para o próximo processo do lote
            print(f"  ERRO: {e}")
            falhas += 1
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
