"""Export do staging para o lote de importação do SisBenefícios.

Gera csv e json com os NOMES DE COLUNA de
BdBeneficio.dbo.Beneficio_PropostaBeneficio, 1:1 para o script importador do
outro setor. Duas colunas extras de correlação: IdInterno (IdCCDBeneficio) e
IdInternoBeneficioAnterior (vínculo efetivo->potencial, que o importador
resolve para IdBeneficioAnterior após inserir os potenciais do lote).
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, date, datetime
from decimal import Decimal
from io import StringIO
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ccd.beneficios.service import _where_lista
from app.config import get_settings

# staging -> nome no Beneficio_PropostaBeneficio (ordem do arquivo exportado)
_COLUNAS_EXPORT: list[tuple[str, str]] = [
    ("IdCCDBeneficio", "IdInterno"),
    ("IdCCDBeneficioPotencial", "IdInternoBeneficioAnterior"),
    ("DescricaoPropostaBeneficio", "DescricaoPropostaBeneficio"),
    ("MemoriaCalculoPropostaBeneficio", "MemoriaCalculoPropostaBeneficio"),
    ("ValorQuantidade", "ValorQuantidade"),
    ("JustificativaPropostaBeneficio", "JustificativaPropostaBeneficio"),
    ("IdBeneficioSituacaoEfetivacao", "IdBeneficioSituacaoEfetivacao"),
    ("IdAreaTematica", "IdAreaTematica"),
    ("IdCaracterizacaoBeneficio", "IdCaracterizacaoBeneficio"),
    ("IdUnidadeDeMedida", "IdUnidadeDeMedida"),
    ("IdBeneficioSituacao", "IdBeneficioSituacao"),
    ("IdTipoBeneficio", "IdTipoBeneficio"),
    ("IdSubTipoBeneficio", "IdSubTipoBeneficio"),
    ("NumeroProcessoDecisao", "NumeroProcessoDecisao"),
    ("AnoProcessoDecisao", "AnoProcessoDecisao"),
    ("IdProcessoDecisao", "IdProcessoDecisao"),
    ("DescricaoMotivo", "DescricaoMotivo"),
]

# IdStatusBeneficio do workflow do SisBenefícios: todo lote entra como 1=Cadastrado.
_ID_STATUS_CADASTRADO = 1


class ExportVazio(Exception):
    pass


def _selecionar(
    session: Session,
    *,
    q: str | None,
    origem: str | None,
    data_de: date | None,
    data_ate: date | None,
) -> list[dict[str, Any]]:
    where_sql, params = _where_lista(q, origem, data_de, data_ate)
    stmt = text(f"SELECT b.* FROM dbo.CCDBeneficio b {where_sql} ORDER BY b.IdCCDBeneficio")
    return [dict(r) for r in session.execute(stmt, params).mappings().all()]


def _linha_export(row: dict[str, Any], id_setor: int | None) -> dict[str, Any]:
    linha = {destino: row[origem] for origem, destino in _COLUNAS_EXPORT}
    linha["IdStatusBeneficio"] = _ID_STATUS_CADASTRADO
    linha["IdSetorUsuarioCadastro"] = id_setor
    # Origem PROPOSTA: o registro deriva de uma proposta real do BdBeneficio —
    # IdBeneficioAnterior recebe o id dela (ChaveOrigem = 'PROPOSTA:<id>') para
    # o importador vincular a conversão proposta -> potencial/efetivo.
    chave = row.get("ChaveOrigem") or ""
    linha["IdBeneficioAnterior"] = (
        int(chave.split(":", 1)[1]) if row.get("Origem") == "PROPOSTA" and ":" in chave else None
    )
    return linha


def _json_default(v: Any) -> Any:
    if isinstance(v, Decimal):
        return str(v)
    if isinstance(v, datetime):
        return v.isoformat()
    raise TypeError(f"não serializável: {type(v)}")


def _celula(v: Any) -> Any:
    if v is None:
        return ""
    return v if isinstance(v, (str, int, float)) else _json_default(v)


def _csv(linhas: list[dict[str, Any]]) -> bytes:
    # ponytail: ';' + BOM abre direto no Excel pt-BR; troque p/ ',' se o importador exigir.
    buf = StringIO()
    w = csv.DictWriter(buf, fieldnames=list(linhas[0]), delimiter=";", lineterminator="\n")
    w.writeheader()
    for linha in linhas:
        w.writerow({k: _celula(v) for k, v in linha.items()})
    return buf.getvalue().encode("utf-8-sig")


def exportar(
    session: Session,
    *,
    formato: str,
    q: str | None = None,
    origem: str | None = None,
    data_de: date | None = None,
    data_ate: date | None = None,
) -> tuple[str, bytes, str]:
    """Retorna (nome_arquivo, conteúdo, media_type) do recorte atual da lista."""
    rows = _selecionar(session, q=q, origem=origem, data_de=data_de, data_ate=data_ate)
    if not rows:
        raise ExportVazio
    lote = "beneficios-ccd-" + datetime.now(UTC).strftime("%Y%m%d-%H%M")
    id_setor = get_settings().beneficio_id_setor_ccd
    linhas = [_linha_export(r, id_setor) for r in rows]

    if formato == "json":
        payload = {
            "lote": lote,
            "geradoEm": datetime.now(UTC).isoformat(),
            "origem": "CCD/DIP - staging CCDBeneficio (BdDIP)",
            "itens": linhas,
        }
        conteudo = json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default).encode(
            "utf-8"
        )
        return f"{lote}.json", conteudo, "application/json"
    return f"{lote}.csv", _csv(linhas), "text/csv; charset=utf-8"
