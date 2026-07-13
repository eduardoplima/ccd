"""Sessão autenticada e ações na Área Restrita do TCE (novaarearestrita.tce.rn.gov.br).

Replica os POSTs que os botões do site fazem (frame botoesNOVO.asp apenas seta
form1.oculto e submete o form principal). Credenciais em AR_USER/AR_PASS no .env.
CLI em scripts/automacao/area_restrita.py.
"""

from __future__ import annotations

import os
import re
from urllib.parse import urljoin

import requests
import urllib3
from lxml import html as lxml_html

from ccd.config import load_env

BASE = "https://novaarearestrita.tce.rn.gov.br/"
# tile "Proc./ Doc. Eletrônico no Setor" da Mesa Eletrônica ({setor} = sigla ativa)
PAGINA_SETOR = (
    BASE + "SISTEMAS/Processo/ProcessonoSetor.asp"
    "?tcenet_Sistema=Administrativo&tcenet_Modulo=Processo"
    "&qsSetor={setor}&qsEletronico=S&seletivo=&qsTipoConsulta="
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


def parse_processo(texto: str) -> tuple[int, int]:
    """'12345/2024' -> (12345, 2024). Levanta ValueError se fora do formato."""
    m = re.fullmatch(r"(\d{1,6})/(\d{4})", texto.strip())
    if not m:
        raise ValueError(f"{texto}: formato inválido (esperado numero/ano)")
    return int(m.group(1)), int(m.group(2))


class AreaRestrita:
    """Sessão autenticada na Área Restrita (Basic Auth + cookie ASP)."""

    def __init__(self, setor: str = "CCD") -> None:
        load_env()
        urllib3.disable_warnings()
        self.s = requests.Session()
        self.s.auth = (os.environ["AR_USER"], os.environ["AR_PASS"])
        self.s.verify = False  # TLS interceptado pelo proxy corporativo
        self.setor = "CCD"  # setor default da sessão recém-aberta
        self._get(BASE + "telaPrincipalMenu.asp")  # estabelece ASPSESSIONID
        if setor != self.setor:
            self.trocar_setor(setor)

    def trocar_setor(self, sigla: str) -> None:
        """Troca o setor ativo da sessão (combo 'Selecione o setor' da tela
        principal — mesmo AJAX de CarregaOrgaoSetor.asp)."""
        import time
        self._get(BASE + f"CarregaOrgaoSetor.asp?qsSigla={sigla}&id={int(time.time() * 1000)}")
        self.setor = sigla

    def _pagina_setor(self) -> str:
        return PAGINA_SETOR.format(setor=self.setor)

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
        r = self._get(self._pagina_setor())
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
                              data_substituida: str | None = None,
                              dry_run: bool = False) -> None:
        """Substitui a informação de `autor_substituida` (a mais recente dele — ou,
        se `data_substituida` for dada, a daquela data, ex. '08/07/2026') pela
        'Informação instrutiva' mais recente, com motivo 'Informação incompleta'."""
        action, campos, linhas = self._consultar_substituicao(numero, ano)
        alvo = autor_substituida.casefold()
        substituidas = [ln for ln in linhas if alvo in ln["autor"].casefold()
                        and (data_substituida is None or ln["data"] == data_substituida)]
        if not substituidas:
            raise LookupError(
                f"nenhuma informação de {autor_substituida!r}"
                + (f" em {data_substituida}" if data_substituida else "")
                + " entre: "
                + "; ".join(f"{ln['ordem']}={ln['autor']} ({ln['data']})" for ln in linhas)
            )
        substituida = max(substituidas, key=lambda ln: ln["ordem"])
        chave = resumo_substituta.casefold()
        substitutas = [ln for ln in linhas if ln["resumo"].casefold().startswith(chave)
                       and ln["id"] != substituida["id"]]
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
        r = self._get(self._pagina_setor())
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
