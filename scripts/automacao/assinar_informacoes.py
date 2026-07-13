"""Assinatura semi-automática de informações pendentes (Lacuna Web PKI).

A assinatura A3 exige a extensão Web PKI + token com PIN — impossível por HTTP puro.
Este script dirige o Chrome real (Playwright, channel="chrome") na página
Administrativo > Informações > Assinar e Publicar Minhas Informações: marca as
pendências pedidas, seleciona o certificado e dispara `prepararAssinatura(...)`
(o mesmo JS que o botão "Assinar" do frame de botões chama). O PIN do token é
digitado pelo usuário no diálogo nativo do Web PKI; o sucesso é verificado pela
própria lista de pendentes (quem assinou sai da lista).

A Web Store é bloqueada por política corporativa, então a extensão (copiada do
perfil Default do Chrome para ~/.ccd_webpki_ext; manifest tem `key`, o ID oficial
se mantém) é carregada por --load-extension no Chromium do Playwright — o Chrome
estável >=137 ignora essa flag. O host nativo da Lacuna foi espelhado em
HKCU\\SOFTWARE\\Chromium e HKCU\\SOFTWARE\\Google\\Chrome for Testing.

Uso:
    python -m scripts.automacao.assinar_informacoes --dry-run
    python -m scripts.automacao.assinar_informacoes 002681/2022 002683/2022 [--cert EDUARDO]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from ccd.config import load_env

BASE = "https://novaarearestrita.tce.rn.gov.br/"
# Administrativo > Informações > Assinar e Publicar Minhas Informações (processo eletrônico)
PAGINA_ASSINAR = (
    BASE + "SISTEMAS/Informacoes/AssinarInformacoesPendentes.asp"
    "?tcenet_Sistema=Administrativo&tcenet_Modulo=Informacoes"
)
PERFIL = Path.home() / ".ccd_chrome_assinatura"
WEBPKI_EXT = Path.home() / ".ccd_webpki_ext"  # cópia de Default/Extensions/dcngea.../2.17.5_0
WEBPKI_EXT_ID = "dcngeagmmhegagicpcmpinaoklddcgon"  # ID oficial (manifest tem `key`)
LOTE_MAX = 20  # limite da própria página (contaproc)

# a página referencia parent.botoes.* (frame de botões); standalone, parent === window
STUB_BOTOES = """
window.botoes = {
    MostraBotao: function () {},
    EscondeBotao: function () {},
    CancelaAcaoBotoes: function () {},
    location: { replace: function () {} },
    document: { getElementById: function () { return { innerHTML: '', innerText: '', value: '' }; } },
};
"""


def _contexto(pw):
    """Contexto persistente no Chromium do Playwright com a extensão Web PKI."""
    if not (WEBPKI_EXT / "manifest.json").is_file():
        raise RuntimeError(f"extensão Web PKI não encontrada em {WEBPKI_EXT}")
    return pw.chromium.launch_persistent_context(
        str(PERFIL),
        headless=False,
        no_viewport=True,
        ignore_https_errors=True,  # TLS interceptado pelo proxy corporativo
        args=[
            f"--disable-extensions-except={WEBPKI_EXT}",
            f"--load-extension={WEBPKI_EXT}",
        ],
        http_credentials={
            "username": os.environ["AR_USER"],
            "password": os.environ["AR_PASS"],
        },
    )


def _pendencias(page) -> list[dict]:
    """Checkboxes checkProcessoN: value=CCD_NNNNNN_YYYY_SSSS.doc, title=resumo."""
    itens = []
    for chk in page.locator("input[type=checkbox][name^=checkProcesso]").all():
        name = chk.get_attribute("name") or ""
        if name == "checkProcessoTramTodos":  # "marcar todos"
            continue
        value = chk.get_attribute("value") or ""
        m = re.match(r"CCD_(\d{6})_(\d{4})_", value)
        proc = f"{m.group(1)}/{m.group(2)}" if m else ""
        itens.append({
            "chk": chk,
            "proc": proc,
            "arquivo": value,
            "resumo": chk.get_attribute("title") or "",
        })
    return itens


def _certificados(page, timeout_s: int = 60) -> list[str]:
    """Espera o Web PKI preencher #certificateSelect e retorna os textos das opções."""
    try:
        page.wait_for_function(
            "document.querySelectorAll('#certificateSelect option').length > 0",
            timeout=timeout_s * 1000,
        )
    except Exception:
        raise RuntimeError(
            "certificados não carregaram — extensão Web PKI instalada neste perfil? "
            "(rode --setup) Token conectado?"
        )
    return page.locator("#certificateSelect option").all_inner_texts()


def _confiar_site(ctx, thumbprint: str, texto_opcao: str) -> None:
    """Grava o 'confiar no site' da extensão Web PKI (senão ela pede 'permitir' por
    documento). Mesmas chaves que setSiteTrust em event-page.js; sync E local porque
    a extensão usa sync com fallback."""
    dominio = "novaarearestrita.tce.rn.gov.br"
    partes = [p.strip() for p in texto_opcao.split(":")]
    pg = ctx.new_page()
    try:
        pg.goto(f"chrome-extension://{WEBPKI_EXT_ID}/popup.html")
        pg.evaluate(
            """([dominio, thumb, subject, issuer]) => {
                const req = {
                    ['trust:' + dominio + ':' + thumb]: true,
                    ['certSubject:' + thumb]: subject,
                    ['certIssuer:' + thumb]: issuer,
                };
                return Promise.all([
                    chrome.storage.sync.set(req),
                    chrome.storage.local.set(req),
                ]);
            }""",
            [dominio, thumbprint, partes[3] if len(partes) > 3 else texto_opcao, partes[-1]],
        )
        print(f"  confiar no site gravado ({dominio})")
    finally:
        pg.close()


def _selecionar_certificado(page, cert: str) -> tuple[str, str]:
    """Seleciona o certificado no combo; retorna (texto, thumbprint)."""
    opcoes = page.locator("#certificateSelect option").all_inner_texts()
    if cert:
        alvo = [o for o in opcoes if cert.casefold() in o.casefold()]
        if not alvo:
            raise RuntimeError(f"nenhum certificado contém {cert!r}: {opcoes}")
    elif len(opcoes) == 1:
        alvo = opcoes
    else:
        raise RuntimeError(f"{len(opcoes)} certificados; escolha com --cert: {opcoes}")
    sel = page.locator("#certificateSelect")
    sel.select_option(label=alvo[0])
    thumb = sel.evaluate("s => s.value")
    return alvo[0].strip(), thumb


def _assinar_lote(page, lote: list[dict], timeout_s: int) -> None:
    """Marca o lote e dispara a assinatura (mesmo JS do botão 'Assinar' do frame)."""
    for it in lote:
        it["chk"].check()
    arquivos = page.evaluate("document.form1.nomeArquivoAssinar.value")
    if not arquivos:
        raise RuntimeError("nomeArquivoAssinar vazio após marcar — AtoLinha não rodou?")
    print(f"  marcados: {len(lote)} ({arquivos.count(';') + 1} arquivo(s) no form)")
    print(f"  >>> DIGITE O PIN do token no diálogo Web PKI (até {timeout_s}s) <<<")
    with page.expect_navigation(timeout=timeout_s * 1000):  # form1.submit() após a última assinatura
        page.evaluate(
            "prepararAssinatura(document.form1.nomeArquivoAssinar.value + ';',"
            " 'LacunaRetornoAjaxAssinaturaInformacao.asp', 'S')"
        )
    print("  lote submetido")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("processos", nargs="*", help="numero/ano a assinar (ex.: 2681/2022)")
    ap.add_argument("--dry-run", action="store_true", help="só lista pendências e certificados")
    ap.add_argument("--cert", default="", help="substring do certificado a usar (nome/CPF)")
    ap.add_argument("--timeout", type=int, default=300, help="segundos de espera pelo PIN/assinatura")
    args = ap.parse_args()

    load_env()
    from playwright.sync_api import sync_playwright

    alvos: list[str] = []
    for p in args.processos:
        m = re.fullmatch(r"(\d{1,6})/(\d{4})", p.strip())
        if not m:
            print(f"{p}: formato inválido (esperado numero/ano)")
            return 1
        alvos.append(f"{int(m.group(1)):06d}/{m.group(2)}")

    with sync_playwright() as pw:
        ctx = _contexto(pw)
        ctx.add_init_script(STUB_BOTOES)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.on("dialog", lambda d: (print(f"  [dialog] {d.message}"), d.accept()))
        page.goto(BASE + "telaPrincipalMenu.asp", wait_until="domcontentloaded")  # ASPSESSIONID
        page.goto(PAGINA_ASSINAR, wait_until="domcontentloaded")
        certs = _certificados(page)
        pend = _pendencias(page)
        print(f"Certificados: {certs}")
        print(f"Pendências: {len(pend)}")
        for it in pend:
            print(f"  [{it['proc']}] {it['arquivo']}  | {it['resumo'][:80]}")

        if args.dry_run:
            if len(certs) == 1 or args.cert:  # aproveita para gravar o "confiar no site"
                texto, thumb = _selecionar_certificado(page, args.cert)
                _confiar_site(ctx, thumb, texto)
            print("dry-run: nada foi marcado/assinado.")
            ctx.close()
            return 0
        if not alvos:
            print("informe os processos a assinar (dry-run para listar).")
            ctx.close()
            return 1

        sem_pendencia = set(alvos) - {it["proc"] for it in pend}
        if sem_pendencia:
            print(f"ERRO: sem pendência para: {', '.join(sorted(sem_pendencia))}")
            ctx.close()
            return 1

        # lotes de até 20 (limite da página); a navegação pós-submit invalida os
        # locators, então cada lote relê a lista a partir da página recarregada
        fila = list(alvos)
        n_lote = 0
        while fila:
            if n_lote:
                page.goto(PAGINA_ASSINAR, wait_until="domcontentloaded")
                _certificados(page)
                pend = _pendencias(page)
            nome_cert, thumb = _selecionar_certificado(page, args.cert)
            if n_lote == 0:
                _confiar_site(ctx, thumb, nome_cert)
            lote_alvos, fila = fila[:LOTE_MAX], fila[LOTE_MAX:]
            lote = [it for it in pend if it["proc"] in lote_alvos]
            n_lote += 1
            print(f"Lote {n_lote} (cert {nome_cert}): {[it['proc'] for it in lote]}")
            _assinar_lote(page, lote, args.timeout)

        # verificação real: quem assinou sai da lista de pendentes
        page.goto(PAGINA_ASSINAR, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")
        restantes = {it["proc"] for it in _pendencias(page)}
        ok = sorted(set(alvos) - restantes)
        falhas = sorted(set(alvos) & restantes)
        print(f"Assinadas (saíram da lista): {len(ok)} -> {ok}")
        if falhas:
            print(f"AINDA PENDENTES: {falhas}")
        ctx.close()
        return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
