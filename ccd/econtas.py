"""Sessão autenticada e ações no e-Contas (https://processos.tce.rn.gov.br).

Sucessor da Área Restrita ASP (ccd.area_restrita) para consultar, tramitar e
cadastrar informação. Fluxo de login (SSO do TCE, mapeado do bundle Angular):
  1. GET  tceauth  /api/servicos  -> ClientId do operador interno (tipo 1)
  2. POST tceauth  /v2/token      -> access_token (grant_type=password, username=CPF)
  3. GET  tceadmin2 /api/v3/operador/auth/informacoes/login -> dados do operador
Demais chamadas levam o access_token cru no header Authorization (sem "Bearer").
Credenciais em ECONTAS_USER (CPF) / ECONTAS_PASS no .env; fallback AR_USER/AR_PASS.

Assinatura de informações NÃO está aqui: o e-Contas assina com certificado A3 via
extensão Web PKI no navegador (/api/AssinaturaDigital/Preparar+ConcluirAssinatura),
impossível por requests puro — segue em scripts/automacao/assinar_informacoes.py.
CLI em scripts/automacao/econtas.py.
"""

from __future__ import annotations

import json
import os
from typing import Any

import requests
import urllib3

from ccd.area_restrita import GABINETES, parse_processo  # noqa: F401  (reexport p/ compat)
from ccd.config import load_env

BASE = "https://processos.tce.rn.gov.br"
AUTH = "https://tceauth.tce.rn.gov.br"
RECURSOS = "https://tceadmin2.tce.rn.gov.br"
COMMON = "https://tce-commonapi.tce.rn.gov.br"
SISTEMA = "e-Contas"
TIPO_OPERADOR_INTERNO = 1


def _unwrap(payload: Any) -> Any:
    """Respostas das APIs do TCE ora vêm cruas, ora embrulhadas em {status, obj, message}."""
    if isinstance(payload, dict) and "obj" in payload:
        return payload["obj"]
    return payload


class EContas:
    """Sessão autenticada no e-Contas (token SSO no header Authorization)."""

    def __init__(self, setor: str = "CCD") -> None:
        load_env()
        urllib3.disable_warnings()
        self.s = requests.Session()
        self.s.verify = False  # TLS interceptado pelo proxy corporativo
        self.setor = setor
        user = os.environ.get("ECONTAS_USER") or os.environ["AR_USER"]
        senha = os.environ.get("ECONTAS_PASS") or os.environ["AR_PASS"]
        client_id = next(
            sv["ClientId"]
            for sv in _unwrap(self._json(self.s.get(f"{AUTH}/api/servicos", timeout=60)))
            if sv["idTipoOperadorServico"] == TIPO_OPERADOR_INTERNO
        )
        tok = self._json(
            self.s.post(
                f"{AUTH}/v2/token",
                data={
                    "grant_type": "password",
                    "username": user,
                    "password": senha,
                    "client_id": client_id,
                    "sistema": SISTEMA,
                },
                timeout=60,
            )
        )
        self.s.headers["Authorization"] = tok["access_token"]
        self.operador = _unwrap(
            self._json(self.s.get(f"{RECURSOS}/api/v3/operador/auth/informacoes/login", timeout=60))
        )

    @staticmethod
    def _json(r: requests.Response) -> Any:
        if not r.ok:
            raise RuntimeError(f"HTTP {r.status_code} em {r.url}: {r.text[:300]}")
        return r.json()

    def setores(self) -> list[Any]:
        """Setores do operador logado (GetAllSetorByToken)."""
        return _unwrap(self._json(self.s.get(f"{BASE}/api/Setor/GetAllSetorByToken", timeout=60)))

    def consultar(self, numero: int, ano: int) -> dict:
        """Processo por número/ano; retorna o dict do processo (com idProcesso e setorAtual)."""
        r = self.s.get(
            f"{BASE}/api/Processo",
            params={"numeroProcesso": numero, "anoProcesso": ano},
            timeout=60,
        )
        dados = _unwrap(self._json(r))
        if isinstance(dados, list):
            if not dados:
                raise LookupError(f"processo {numero:06d}/{ano} não encontrado no e-Contas")
            dados = dados[0]
        if not isinstance(dados, dict):
            raise RuntimeError(f"resposta inesperada de /api/Processo: {str(dados)[:200]}")
        return dados

    def tramitar(self, processos: list[tuple[int, int]], destino: str,
                 dry_run: bool = False) -> None:
        """Tramita cada processo ao setor `destino` via /api/tramitacao/tramitarAutomatico.

        Payload observado no bundle: {idProcesso, numeroProcesso, anoProcesso,
        setorAtual, setorDestino}. Sem campo de providência — a tramitação
        automática do e-Contas não o expõe (diferente do ASP).
        """
        for numero, ano in processos:
            proc = self.consultar(numero, ano)
            body = {
                "idProcesso": proc.get("idProcesso"),
                "numeroProcesso": numero,
                "anoProcesso": ano,
                "setorAtual": proc.get("setorAtual", self.setor),
                "setorDestino": destino,
            }
            url = f"{BASE}/api/tramitacao/tramitarAutomatico?setorDestino={destino}"
            print(f"  {numero:06d}/{ano}: setorAtual={body['setorAtual']!r} "
                  f"idProcesso={body['idProcesso']}")
            if dry_run:
                print(f"  [dry-run] POST {url} NÃO enviado: {json.dumps(body, ensure_ascii=False)}")
                continue
            resp = self._json(self.s.post(url, json=body, timeout=120))
            print(f"  tramitado: {str(resp)[:200]}")

    def cadastrar_informacao_digitalizada(self, numero: int, ano: int, pdf: str,
                                          resumo: str = "Informação instrutiva....",
                                          dry_run: bool = False) -> None:
        """Cadastra informação digitalizada via POST multipart /api/Informacao/formfile.

        # ponytail: nomes dos campos do multipart inferidos do bundle (recurso
        # Informacao serializado em FormData); confirmar via DevTools na primeira
        # execução real e ajustar aqui — o servidor responde 400 se divergirem.
        """
        proc = self.consultar(numero, ano)
        campos = {
            "idProcesso": str(proc.get("idProcesso", "")),
            "numeroProcesso": str(numero),
            "anoProcesso": str(ano),
            "resumo": resumo,
            "setor": self.setor,
        }
        url = f"{BASE}/api/Informacao/formfile"
        if dry_run:
            print(f"  [dry-run] POST {url} NÃO enviado: campos={campos} arquivo={pdf}")
            return
        with open(pdf, "rb") as fh:
            resp = self._json(
                self.s.post(
                    url,
                    data=campos,
                    files={"file": (os.path.basename(pdf), fh, "application/pdf")},
                    timeout=300,
                )
            )
        print(f"  incluída: {str(resp)[:200]} (pendente de assinatura no navegador)")
