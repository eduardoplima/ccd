#!/usr/bin/env python3
"""Scraper para páginas de processos do TCE/RN (Área Restrita).

Autentica com HTTP Basic Auth via AR_USER / AR_PASS (do .env),
acessa páginas de processos do menu Administrativo > Processo.

Origens disponíveis:
  - setor     : Processos no Setor   (ProcessonoSetor.asp, default)
  - eletronicos : Meus Processos Eletrônicos (MeusProcessos.asp?qsEletronico=S)

Uso:
    # Processos no Setor (default)
    python scripts/scraper_tce_processos_setor.py
    python scripts/scraper_tce_processos_setor.py --csv saida.csv

    # Meus Processos Eletrônicos
    python scripts/scraper_tce_processos_setor.py --eletronicos
    python scripts/scraper_tce_processos_setor.py -e --csv meus_eletronicos.csv

    # Limitar registros
    python scripts/scraper_tce_processos_setor.py -e --max 100
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests

from ccd.area_restrita import BASE, AreaRestrita

# ── config ──────────────────────────────────────────────────────────────
BASE_URL = BASE.rstrip("/")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded",
}

# Colunas comuns
COLUMNS = [
    "processo",
    "acao",
    "origem",
    "relator",
    "tipo",
    "assunto",
    "data_recebimento",
    "distribuido_em",
    "distribuido_para",
    "processos_juntados",
    "ultima_informacao_por",
]

# ── helpers ──────────────────────────────────────────────────────────────


def _criar_sessao() -> requests.Session:
    """Sessão já autenticada (login/env centralizados em ccd.area_restrita)."""
    sess = AreaRestrita().s
    sess.headers.update(HEADERS)
    return sess


def _extrair_tabela(html: str, section_id: str = "tbproc01") -> list[dict[str, Any]]:
    """Extrai linhas de dados de uma seção tbproc*.

    Pode estar dentro de <table id="tbproc*"> ou em comentários HTML
    (<!-- id="tbproc*" -->) com dados soltos. Varre todo o HTML
    procurando <tr> com checkProcesso.
    As páginas são carregadas via POST com NumeroPagina e o resultado
    vem completo — esta função extrai todas as linhas visíveis.
    """
    registros: list[dict[str, Any]] = []

    # Cada linha de dados tem checkProcessoN (N=1,2,3...), sem "Todos"
    raw_segments = html.split("</tr>")
    for seg in raw_segments:
        if "checkProcesso" not in seg or "checkProcessoTodos" in seg:
            continue
        if not re.search(r"\d{6}/\d{4}", seg):
            continue
        rec = _parse_linha(seg)
        if rec.get("processo"):
            registros.append(rec)

    return registros


def _txt(td: str) -> str:
    t = re.sub(r"<[^>]+>", " ", td)
    t = re.sub(r"\s+", " ", t).strip()
    t = t.replace("&nbsp;", "").strip()
    return t


def _parse_linha(row_html: str) -> dict[str, Any]:
    """Extrai campos de uma linha <tr> da tabela.

    Funciona tanto para ProcessonoSetor.asp quanto MeusProcessos.asp.
    As colunas de dados começam em posições diferentes conforme a página,
    então usamos um parser por padrão de conteúdo.
    """
    rec: dict[str, Any] = {}
    tds = re.findall(r"<td[^>]*>(.*?)</td>", row_html, re.DOTALL)

    for td in tds:
        txt = _txt(td)
        if not txt:
            continue

        # Processo: 000000/0000 (primeiro que aparecer)
        m_proc = re.search(r"(\d{6}/\d{4})", txt)
        if m_proc and not rec.get("processo"):
            rec["processo"] = m_proc.group(1)
            continue

        # Ação/Origem: começa com 6 dígitos e "/" (ex: "227167/2014 - SESAP")
        # ou formato "000000/1993 - NOME"
        if re.match(r"\d{5,6}/\d{4}", txt) and not rec.get("acao"):
            rec["acao"] = txt
            rec["origem"] = txt
            continue

        # Relator: nome de conselheiro conhecido ou contém "("
        if (("(" in txt and re.search(r"[A-ZÇÀ-Ú]{3,}", txt)) or
                any(n in txt.upper() for n in [
                    "CAVALCANTI", "JÚNIOR", "JUNIOR", "CONS.",
                    "GOMES", "FERNANDES", "ALVES", "DIAS",
                    "SOARES", "MONTENEGRO", "SANTANA", "JALES",
                    "CHAVES", "COSTA", "POTIGUAR",
                ])) and not rec.get("relator"):
            rec["relator"] = txt
            continue

        # Interessado: contém "PREF.", "MUNICÍPIO", "SECRETARIA", "FUNDAÇÃO"
        lower = txt.lower()
        if any(k in lower for k in ["pref.", "município", "municipal",
                                    "fundação", "secretaria", "estado",
                                    "governo", "departamento"]) and not rec.get("interessado"):
            rec["interessado"] = txt
            continue

        # Câmara: dígito solto "1", "2", ou "Pleno"
        m_cam = re.match(r"^(\d|Pleno)$", txt, re.IGNORECASE)
        if m_cam and not rec.get("camara"):
            rec["camara"] = m_cam.group(1)
            continue

        # Tipo: 2-6 letras maiúsculas (PCM, TC, APO, TC-P, etc.)
        m_tipo = re.match(r"^[A-ZÇÀ-Ú]{2,6}$", txt)
        if m_tipo and not rec.get("tipo"):
            rec["tipo"] = m_tipo.group(0)
            continue

        # Assunto: texto longo (>20 chars) que não é relator nem ação
        if (len(txt) > 20 and not rec.get("assunto")
                and (not rec.get("relator") or txt != rec.get("relator"))):
            rec["assunto"] = txt
            continue

        # Datas: dd/mm/aaaa
        m_dt = re.search(r"(\d{2}/\d{2}/\d{4})", txt)
        if m_dt:
            dt = m_dt.group(1)
            # Data de recebimento (primeira data encontrada)
            if not rec.get("data_recebimento"):
                rec["data_recebimento"] = dt
                continue
            # Distribuído em (segunda data)
            elif not rec.get("distribuido_em"):
                rec["distribuido_em"] = dt
                continue

        # Distribuído para: contém "-->"
        if "-->" in txt:
            rec["distribuido_para"] = txt.replace("-->", "").strip()
            continue

        # Última informação por: texto curto com nome de pessoa (CPF-like)
        if re.match(r"^[A-Za-zÀ-ú\s]{5,}$", txt) and \
           not rec.get("ultima_informacao_por") and \
           rec.get("relator") != txt and \
           rec.get("interessado") != txt:
            # É um nome de pessoa
            rec["ultima_informacao_por"] = txt
            continue

    return rec


def _extrair_paginacao(html: str) -> tuple[int, int]:
    """Extrai total de registros e total de páginas."""
    m = re.search(r"Registros\s*:\s*\d+\s*a\s*\d+\s*de\s*(\d+)", html, re.IGNORECASE)
    total = int(m.group(1)) if m else 0
    m2 = re.search(r"P[aá]gina\s*(\d+)\s*de\s*(\d+)", html, re.IGNORECASE)
    paginas = int(m2.group(2)) if m2 else 1
    return total, paginas


# ── origens ──────────────────────────────────────────────────────────────

ORIGENS: dict[str, dict[str, Any]] = {
    "setor": {
        "url": "/SISTEMAS/PROCESSO/ProcessonoSetor.asp"
               "?tcenet_Sistema=Administrativo&tcenet_Modulo=Processo&qsEletronico=N",
        "descricao": "Processos no Setor",
    },
    "eletronicos": {
        "url": "/SISTEMAS/PROCESSO/MeusProcessos.asp"
               "?tcenet_Sistema=Administrativo&tcenet_Modulo=Processo&qsSetor=CCD"
               "&qsEletronico=S&seletivo=0&qsTipoConsulta=",
        "qsSetor": "CCD",
        "descricao": "Meus Processos Eletrônicos",
    },
}


def _payload_base(pagina: int = 1, limite: int = 5000) -> dict[str, str]:
    return {
        "NumeroPagina": str(pagina),
        "txtQuantProc": str(limite),
        "oculto": "",
        "OcultoEletronico": "",  # página decide o padrão
        "txtNumeroProcesso": "",
        "txtAnoProcesso": "",
        "optMesReferencia": "",
        "txtAnoReferencia": "",
        "txtCodigoPessoa": "",
        "txtInteressado": "",
        "txtAssunto": "",
        "optNatureza": "",
        "optCamara": "",
        "txtCodigoOrgaoOrigem": "",
        "txtUltimaTramitacao": "",
        "txtCodigoTipoProcesso": "",
        "optInformacao": "1",
        "cmbDecisaoParecerPrevio": "0",
        "cmbCodigoRelator": "",
        "cmbCodigoProcurador": "",
        "cmbMarcadorFiltro": "",
        "txtDataInicio": "",
        "txtDataFim": "",
        "txtDataRecebidoInicio": "",
        "txtDataRecebidoFim": "",
        "txtResponsavelInformacao": "",
        "txtRevisorBusca": "",
        "txtDividaAtiva": "",
        "txtAnaliseVinculo": "",
        "txtDescontoFolha": "",
        "txtProtestado": "",
        "txtMulta": "",
        "txtObrigacoes": "",
        "txtRessarcimento": "",
        "txtObito": "",
        "txtPessoaInteressada": "",
        "txtClassificacaoDocumental": "",
        "PossuiPendenciaAto": "",
        "MenuProcessoPrioritario": "",
        "MenuProcessoEstrela": "",
        "MenuProcessosemEstrela": "",
        "MenuProcessoEmJulgado": "",
        "MenuProcessoNaoEmJulgado": "",
        "optOrdenacaoPagina": "5",  # Tipo do Processo, Data Recebimento
    }


def buscar_processos(
    sess: requests.Session,
    origem: str = "setor",
    limite: int = 5000,
    pagina_inicial: int = 1,
) -> list[dict[str, Any]]:
    """Faz POST na página de origem e coleta todos os registros."""
    config = ORIGENS.get(origem)
    if not config:
        sys.exit(f"Origem desconhecida: {origem}. Opções: {list(ORIGENS.keys())}")

    url = urljoin(BASE_URL, config["url"])

    todos: list[dict[str, Any]] = []
    pagina = pagina_inicial

    while len(todos) < limite:
        payload = _payload_base(pagina, limite)
        if config.get("qsSetor"):
            payload["qsSetor"] = config["qsSetor"]

        resp = sess.post(url, data=payload)
        resp.raise_for_status()

        html = resp.text
        if not html.strip():
            break

        # Extrai todas as linhas de dados do HTML da página
        registros = _extrair_tabela(html, "tbproc01")
        if not registros:
            break

        # Deduplica por número de processo
        vistos = {r["processo"] for r in todos}
        novos = 0
        for r in registros:
            if r["processo"] not in vistos:
                todos.append(r)
                vistos.add(r["processo"])
                novos += 1

        # Se nenhum novo registro foi adicionado, avançamos
        # além do fim — encerra
        if novos == 0:
            break

        # Verifica se há link "Próxima" para continuar paginando
        if "Próxima" not in html and "Proxima" not in html:
            break

        pagina += 1
        if len(todos) >= limite:
            break

    return todos[:limite]


# ── CLI ──────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scraper de Processos do TCE/RN (Área Restrita)"
    )
    parser.add_argument(
        "--eletronicos", "-e",
        action="store_true",
        help="Busca Meus Processos Eletrônicos em vez de Processos no Setor",
    )
    parser.add_argument(
        "--csv", metavar="ARQUIVO",
        help="Salva resultado como CSV no caminho informado",
    )
    parser.add_argument(
        "--json", metavar="ARQUIVO",
        help="Salva resultado como JSON no caminho informado",
    )
    parser.add_argument(
        "--max", type=int, default=5000,
        help="Máximo de registros (default: 5000)",
    )
    parser.add_argument(
        "--pagina", type=int, default=1,
        help="Página inicial (default: 1)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Exibe progresso no stderr",
    )
    args = parser.parse_args()

    origem = "eletronicos" if args.eletronicos else "setor"
    descricao = ORIGENS[origem]["descricao"]

    sess = _criar_sessao()

    if args.verbose:
        print(f"🔐 Autenticado. Buscando {descricao} (até {args.max})...",
              file=sys.stderr)

    dados = buscar_processos(
        sess, origem=origem,
        limite=args.max, pagina_inicial=args.pagina,
    )

    if args.verbose:
        print(f"📊 {len(dados)} registros encontrados.", file=sys.stderr)

    if not dados:
        print("Nenhum registro encontrado.")
        return

    if args.csv:
        path = Path(args.csv)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(dados)
        print(f"✅ CSV salvo em: {path.resolve()}")
        return

    if args.json:
        path = Path(args.json)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ JSON salvo em: {path.resolve()}")
        return

    _print_tabela(dados, descricao)


def _print_tabela(dados: list[dict[str, Any]], titulo: str = "") -> None:
    cols = [
        ("processo", 16),
        ("relator", 30),
        ("interessado", 28),
        ("data_recebimento", 14),
        ("tipo", 8),
        ("acao", 28),
    ]
    header = "  ".join(h.ljust(w) for h, w in [("Processo", 16), ("Relator", 30),
                                                 ("Interessado", 28), ("Dt.Receb.", 14),
                                                 ("Tipo", 8), ("Ação/Origem", 28)])

    if titulo:
        print(f"\n📋 {titulo}")
    print("  " + "─" * len(header))
    print("  " + header)
    print("  " + "─" * len(header))
    for rec in dados:
        linha = "  ".join(
            rec.get(campo, "")[:larg].ljust(larg)
            for campo, larg in cols
        )
        print(linha)
    print("  " + "─" * len(header))
    print(f"  Total: {len(dados)} registros\n")


if __name__ == "__main__":
    main()