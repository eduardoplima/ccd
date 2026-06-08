"""Cliente da API Extratos do BB (OAuth2 + cert ICP-Brasil). Stub até credenciamento sair."""
from __future__ import annotations

# Interface plugável para fontes de extrato:
#   class ExtratoSource(Protocol):
#       def fetch(self, conta: str, periodo: str) -> Iterable[LinhaExtrato]: ...
#
# Implementações:
#   - ArquivoLocal: lê MMYYYY.txt em uma pasta (uso atual)
#   - ApiBBExtratos: chama https://api.bb.com.br/extratos/v1/...
#       headers = {Authorization: Bearer <token>, gw-dev-app-key: <key>}
#       cert = (BB_CERT_PATH, BB_CERT_PASSWORD)
#       requer .env preenchido com BB_CLIENT_ID / BB_CLIENT_SECRET / etc.
