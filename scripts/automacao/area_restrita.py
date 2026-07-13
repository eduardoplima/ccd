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
from pathlib import Path
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
# Administrativo > Informações > Substituir Informação
PAGINA_SUBSTITUIR = (
    BASE + "SISTEMAS/Informacoes/SubstituirInformacao.asp"
    "?tcenet_Sistema=Administrativo&tcenet_Modulo=Informacoes"
)
MOTIVO_INFORMACAO_INCOMPLETA = "4"  # cmbMotivoExclusao
MODELO_TITULO = "InformacaoInstrutiva"
MODELO_RESUMO = "Informação instrutiva...."
# pasta de saidas/nereu_ms -> sigla do gabinete (tabela Setor); providência = "ENVIO A <sigla>"
GABINETES = {
    "ana": "GAANA",
    "antonio_ed": "GCAED",
    "carlos": "GCCTH",
    "george": "GCGEO",
    "gilberto": "GCGIL",
    "marco": "GAMAR",
    "paulo": "GCPRO",
    "renato": "GCREN",
}


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

    def _consultar_substituicao(self, numero: int, ano: int) -> tuple[str, dict, list[dict]]:
        """Consulta a tela Substituir Informação. Retorna (action, campos, linhas),
        cada linha = {id, ordem, resumo, data, autor} de uma informação substituível."""
        r = self._get(PAGINA_SUBSTITUIR)
        action, campos = self._form(r)
        campos.update(
            txtNumeroProcesso=f"{numero:06d}",
            txtAnoProcesso=str(ano),
            oculto="C",
        )
        r = self._post(action, campos)
        doc = lxml_html.fromstring(r.text)
        linhas = []
        for rd in doc.xpath("//input[@name='rdInformacaoSubstituida']"):
            tr = rd.xpath("ancestor::tr[1]")
            celulas = [" ".join(t.strip() for t in td.xpath(".//text()") if t.strip())
                       for td in tr[0].xpath("./td")] if tr else []
            # células: [radio, ?, ordem, setor, resumo, data digitação, autor, data assinatura, ...]
            linhas.append({
                "id": rd.get("value") or "",
                "ordem": int(celulas[2]) if len(celulas) > 2 and celulas[2].isdigit() else 0,
                "resumo": celulas[4] if len(celulas) > 4 else "",
                "data": celulas[5].split()[0] if len(celulas) > 5 and celulas[5] else "",
                "autor": celulas[6] if len(celulas) > 6 else "",
            })
        if not linhas:
            raise LookupError(f"consulta não listou informações: {self._mensagem(r)}")
        action, campos = self._form(r)
        return action, campos, linhas

    def substituir_informacao(self, numero: int, ano: int, autor_substituida: str,
                              resumo_substituta: str = "Informação instrutiva",
                              dry_run: bool = False) -> None:
        """Substitui a informação de `autor_substituida` (a mais recente dele) pela
        'Informação instrutiva' mais recente, com motivo 'Informação incompleta'."""
        action, campos, linhas = self._consultar_substituicao(numero, ano)
        alvo = autor_substituida.casefold()
        substituidas = [ln for ln in linhas if alvo in ln["autor"].casefold()]
        if not substituidas:
            raise LookupError(
                f"nenhuma informação de {autor_substituida!r} entre: "
                + "; ".join(f"{ln['ordem']}={ln['autor']}" for ln in linhas)
            )
        substituida = max(substituidas, key=lambda ln: ln["ordem"])
        chave = resumo_substituta.casefold()
        substitutas = [ln for ln in linhas if ln["resumo"].casefold().startswith(chave)]
        if not substitutas:
            raise LookupError(
                f"nenhuma informação com resumo {resumo_substituta!r} entre: "
                + "; ".join(f"{ln['ordem']}={ln['resumo'][:30]}" for ln in linhas)
            )
        substituta = max(substitutas, key=lambda ln: ln["ordem"])
        if substituta["id"] == substituida["id"]:
            raise RuntimeError("substituída e substituta são a mesma informação")
        print(f"  substituída: ordem {substituida['ordem']} {substituida['autor']} "
              f"({substituida['data']}) {substituida['resumo'][:50]!r}")
        print(f"  substituta:  ordem {substituta['ordem']} {substituta['autor']} "
              f"({substituta['data']}) {substituta['resumo'][:50]!r}")
        if dry_run:
            print("  dry-run: substituição NÃO enviada")
            return
        campos.update(
            rdInformacaoSubstituida=substituida["id"],
            rdInformacaoSubstituta=substituta["id"],
            cmbMotivoExclusao=MOTIVO_INFORMACAO_INCOMPLETA,
            txtMotivoOutros="",
            oculto="I",
        )
        r = self._post(action, campos)
        print(f"  incluída substituição: {self._mensagem(r)}")
        # verificação: a substituída não deve mais aparecer como substituível
        _, _, depois = self._consultar_substituicao(numero, ano)
        if any(ln["id"] == substituida["id"] for ln in depois):
            raise RuntimeError("informação substituída ainda aparece como substituível")
        print("  verificado: informação substituída saiu da lista")

    def tramitar(self, processos: list[tuple[int, int]], destino: str, providencia: str,
                 dry_run: bool = False) -> None:
        """Tramita os `processos` em UM lote: 'Tramitar Processo(s)' (oculto=M) com a
        seleção montada direto no POST (checkProcesso1..N + quantidadeChk — a listagem
        pagina de 30 em 30, mas o servidor só lê esses campos), depois 'Enviar
        Processos' (oculto=I) com destino e providência por processo."""
        chaves = [f"{numero:06d}{ano}" for numero, ano in processos]
        r = self._get(PAGINA_SETOR)
        action, campos = self._form(r)
        selecao = {f"checkProcesso{i}": ch for i, ch in enumerate(chaves, start=1)}
        selecao["quantidadeChk"] = str(len(chaves))
        # 'Tramitar Processo(s)' abre a seção 'Enviar Processos'. Não commita.
        r = self._post(action, {**campos, **selecao, "oculto": "M"})
        action2, campos2 = self._form(r)
        ecoados = {v: m.group(1) for k, v in campos2.items()
                   if (m := re.fullmatch(r"Processo(\d+)", k))}
        faltando = sorted(set(chaves) - set(ecoados))
        if "txtSetorDestino" not in campos2 or faltando:
            raise RuntimeError(
                f"form de envio não veio com todos os processos (faltam {faltando}): "
                f"{self._mensagem(r)}"
            )
        for chave in chaves:
            i = ecoados[chave]
            if f"txtFaseProcessual{i}" not in campos2:
                raise RuntimeError(f"form sem txtFaseProcessual{i}")
            campos2[f"txtFaseProcessual{i}"] = providencia
            print(f"  Processo{i}={chave} prov={providencia!r}")
        campos2["txtSetorDestino"] = destino
        if dry_run:
            print(f"  [dry-run] setaria txtSetorDestino={destino!r}; oculto=I NÃO enviado")
            return
        # 'Enviar Processos' (oculto=I) confirma a tramitação do lote
        r = self._post(action2, {**campos2, "oculto": "I"})
        print(f"lote enviado (destino={destino}): {self._mensagem(r)}")
        # verificação real: quem tramitou some da listagem do setor (consulta filtrada)
        ainda = []
        for numero, ano in processos:
            try:
                self.consultar(numero, ano)
                ainda.append(f"{numero:06d}/{ano}")
            except LookupError:
                pass  # fora da listagem = tramitado
        if ainda:
            raise RuntimeError(f"ainda na listagem do setor (NÃO tramitados?): {ainda}")
        print(f"verificado: {len(chaves)} processo(s) fora da listagem do setor")


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

    p_lote = sub.add_parser(
        "informacao-lote",
        help="cadastra informação digitalizada de cada PDF NNNNNN_YYYY.pdf de uma pasta",
    )
    p_lote.add_argument("--pasta", required=True, help="pasta com PDFs NNNNNN_YYYY.pdf (recursivo)")
    p_lote.add_argument("--dry-run", action="store_true", help="só consulta; não sobe nem inclui")

    p_subst = sub.add_parser(
        "substituir",
        help='substituir a informação de um autor pela "Informação instrutiva" mais recente',
    )
    p_subst.add_argument("processos", nargs="+", help="numero/ano, ex.: 12345/2024")
    p_subst.add_argument("--autor", default="Luzenildo",
                         help="autor da informação a substituir (default: Luzenildo)")
    p_subst.add_argument("--dry-run", action="store_true", help="só mostra o par; não substitui")

    p_tram = sub.add_parser("tramitar", help="tramitar processos EM LOTE do setor atual para o destino")
    p_tram.add_argument("processos", nargs="+", help="numero/ano, ex.: 12345/2024")
    p_tram.add_argument("--destino", default="DIP", help="setor destino (default: DIP)")
    p_tram.add_argument("--relator", choices=sorted(GABINETES),
                        help='usa providência "ENVIO A <gabinete do relator>"')
    p_tram.add_argument("--providencia", help='providência explícita, ex.: "ENVIO A GAANA"')
    p_tram.add_argument("--dry-run", action="store_true", help="vai até o form; não confirma")

    args = parser.parse_args()

    if args.tarefa == "substituir":
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
                ar.substituir_informacao(numero, ano, args.autor, dry_run=args.dry_run)
            except Exception as e:  # segue para o próximo do lote
                print(f"  ERRO: {e}")
                falhas += 1
        return 1 if falhas else 0

    if args.tarefa == "tramitar":
        providencia = args.providencia or (
            args.relator and f"ENVIO A {GABINETES[args.relator]}"
        )
        if not providencia:
            print("informe --relator ou --providencia")
            return 1
        procs: list[tuple[int, int]] = []
        for proc in args.processos:
            m = re.fullmatch(r"(\d{1,6})/(\d{4})", proc.strip())
            if not m:
                print(f"{proc}: formato inválido (esperado numero/ano)")
                return 1
            procs.append((int(m.group(1)), int(m.group(2))))
        ar = AreaRestrita()
        try:
            ar.tramitar(procs, args.destino, providencia, dry_run=args.dry_run)
        except Exception as e:
            print(f"ERRO: {e}")
            return 1
        return 0

    if args.tarefa == "informacao-lote":
        pasta = Path(args.pasta)
        if not pasta.is_dir():
            print(f"pasta não encontrada: {pasta}")
            return 1
        alvos: list[tuple[int, int, Path]] = []
        for pdf in sorted(pasta.rglob("*.pdf")):
            m = re.fullmatch(r"(\d{1,6})_(\d{4})", pdf.stem)
            if not m:
                print(f"  ignorado (nome fora do padrão NNNNNN_YYYY): {pdf.name}")
                continue
            alvos.append((int(m.group(1)), int(m.group(2)), pdf))
        if not alvos:
            print(f"nenhum PDF NNNNNN_YYYY.pdf em {pasta}")
            return 1
        ar = AreaRestrita()
        falhas = 0
        for numero, ano, pdf in alvos:
            print(f"{numero:06d}/{ano}: ({pdf.relative_to(pasta)})")
            try:
                ar.cadastrar_informacao_digitalizada(numero, ano, str(pdf), dry_run=args.dry_run)
            except Exception as e:  # segue para o próximo do lote
                print(f"  ERRO: {e}")
                falhas += 1
        return 1 if falhas else 0

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
