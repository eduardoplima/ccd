"""Consultas (somente leitura) ao banco `processo` usadas pelo desconto em folha.

Armadilhas confirmadas no banco, todas tratadas aqui:
- `vw_ata_informacao.IdProcesso` é NULL → juntar por número/ano.
- `Pro_ProcessoEvento.IdTipo` é sempre 0 → tipo do evento pelo nome da informação.
- `Exe_Debito` não tem IdPessoa → `Exe_DebitoPessoa`; o débito vigente é a
  folha da cadeia `IdDebitoAnterior`.
- A notificação pode estar só em `Cit_Certidao` (Classe 'NOT') + PDFs; o AR nem
  sempre é rastreável.
- `numero_processo`/`ano_processo`/`sigla_origem` são CHAR com padding → RTRIM.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_PROCESSO_RE = re.compile(r"^\s*(\d{1,6})\s*/\s*(\d{4})\s*$")


def parse_processo(texto: str) -> tuple[int, int] | None:
    m = _PROCESSO_RE.match(texto or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


_SQL_PROCESSO = """
SELECT IdProcesso, RTRIM(numero_processo) AS numero, RTRIM(ano_processo) AS ano,
       RTRIM(codigo_tipo_processo) AS tipo, data_registro, idprocessoorigemexecucao AS id_origem,
       IdProcessoApensador
FROM dbo.Processos
WHERE {filtro}
"""


def resolver_processo(session: Session, texto: str) -> Optional[dict[str, Any]]:
    par = parse_processo(texto)
    if par is None:
        return None
    row = (
        session.execute(
            text(
                _SQL_PROCESSO.format(
                    filtro="TRY_CAST(numero_processo AS INT) = :num "
                    "AND TRY_CAST(ano_processo AS INT) = :ano"
                )
            ),
            {"num": par[0], "ano": par[1]},
        )
        .mappings()
        .first()
    )
    return dict(row) if row else None


def processo_por_id(session: Session, id_processo: int) -> Optional[dict[str, Any]]:
    row = (
        session.execute(text(_SQL_PROCESSO.format(filtro="IdProcesso = :id")), {"id": id_processo})
        .mappings()
        .first()
    )
    return dict(row) if row else None


def debitos_do_processo(session: Session, id_processo: int) -> list[dict[str, Any]]:
    """Débitos do processo com o responsável: vigentes = sem filho vivo na cadeia
    IdDebitoAnterior (a folha pode ter sido cancelada); cancelados vêm por último."""
    rows = session.execute(
        text(
            """
            SELECT d.IdDebito AS id_debito, d.valorOriginalDebito AS valor_original,
                   RTRIM(td.Descricao) AS tipo, RTRIM(sd.DescricaoStatusDivida) AS status,
                   d.DataCancelamento AS data_cancelamento,
                   dp.IDPessoa AS id_pessoa, gp.Nome AS nome_pessoa, gp.Documento AS documento
            FROM dbo.Exe_Debito d
            LEFT JOIN dbo.Exe_TipoDebito td ON td.CodigoTipoDebito = d.CodigoTipoDebito
            LEFT JOIN dbo.Exe_StatusDivida sd ON sd.CodigoStatusDivida = d.CodigoStatusDivida
            LEFT JOIN dbo.Exe_DebitoPessoa dp ON dp.IDDebito = d.IdDebito
            LEFT JOIN dbo.GenPessoa gp ON gp.IdPessoa = dp.IDPessoa
            WHERE (d.IdProcessoExecucao = :id OR d.IdProcessoOrigem = :id)
              AND NOT EXISTS (SELECT 1 FROM dbo.Exe_Debito f
                              WHERE f.IdDebitoAnterior = d.IdDebito AND f.DataCancelamento IS NULL)
            ORDER BY d.DataCancelamento, d.IdDebito
            """
        ),
        {"id": id_processo},
    ).mappings()
    return [dict(r) for r in rows]


def pessoa(session: Session, id_pessoa: int) -> Optional[dict[str, Any]]:
    row = (
        session.execute(
            text(
                "SELECT IdPessoa AS id_pessoa, Nome AS nome, Documento AS documento "
                "FROM dbo.GenPessoa WHERE IdPessoa = :id"
            ),
            {"id": id_pessoa},
        )
        .mappings()
        .first()
    )
    return dict(row) if row else None


def orgao_notificado(session: Session, id_processo: int) -> Optional[str]:
    """Pessoa jurídica mais recente entre os responsáveis de despesa do processo."""
    row = session.execute(
        text(
            """
            SELECT TOP 1 gp.Nome
            FROM dbo.Pro_ProcessosResponsavelDespesa r
            JOIN dbo.GenPessoa gp ON gp.IdPessoa = r.IdPessoa
            WHERE r.IdProcesso = :id AND gp.TipoPessoa = 'J'
            ORDER BY r.DataInclusao DESC
            """
        ),
        {"id": id_processo},
    ).first()
    return str(row[0]).strip() if row else None


def informacoes(session: Session, numero: str, ano: str) -> list[dict[str, Any]]:
    """Informações do processo (por número/ano), com o nome do PDF no share."""
    rows = session.execute(
        text(
            """
            SELECT inf.idInformacao AS id_informacao, ppe.SequencialProcessoEvento AS evento,
                   RTRIM(inf.setor) AS setor, inf.ordem, inf.nome_informacao, inf.resumo,
                   inf.data_resumo,
                   CONCAT(RTRIM(inf.setor), '_', inf.numero_processo, '_', inf.ano_processo, '_',
                          RIGHT(CONCAT('0000', inf.ordem), 4), '.pdf') AS arquivo
            FROM dbo.vw_ata_informacao inf
            JOIN dbo.Pro_ProcessoEvento ppe ON ppe.IdInformacao = inf.idInformacao
            WHERE inf.numero_processo = :numero AND inf.ano_processo = :ano
            ORDER BY inf.ordem
            """
        ),
        {"numero": numero, "ano": ano},
    ).mappings()
    return [dict(r) for r in rows]


def notificacao(
    session: Session, *, numero: str, ano: str, id_processo: int, id_origem: int | None
) -> dict[str, Any]:
    """Número/data da notificação de desconto em folha e as chaves para achar o AR."""
    out: dict[str, Any] = {
        "numero": None,
        "data": None,
        "id_informacao": None,
        "id_citacao": None,
        "numero_postagem": None,
    }
    info = session.execute(
        text(
            """
            SELECT TOP 1 idInformacao, data_resumo FROM dbo.vw_ata_informacao
            WHERE numero_processo = :numero AND ano_processo = :ano
              AND (nome_informacao LIKE '%NOTIFICA%' OR resumo LIKE '%Notifica%')
              AND (nome_informacao LIKE '%FOLHA%' OR resumo LIKE '%folha%')
            ORDER BY data_resumo DESC
            """
        ),
        {"numero": numero, "ano": ano},
    ).first()
    if info:
        out["id_informacao"], out["data"] = int(info[0]), info[1]

    cert = session.execute(
        text(
            """
            SELECT TOP 1 NumeroCitacao, AnoCitacao, DataInclusao FROM dbo.Cit_Certidao
            WHERE Numero_processo = :numero AND Ano_processo = :ano AND Classe = 'NOT'
              AND inativo IS NULL
            ORDER BY DataInclusao DESC
            """
        ),
        {"numero": numero, "ano": ano},
    ).first()
    if cert:
        out["numero"] = f"{str(cert[0]).strip()}/{str(cert[1]).strip()}"
        out["data"] = out["data"] or cert[2]

    cit = session.execute(
        text(
            """
            SELECT TOP 1 Numero_Citacao, Ano_citacao, DataInicioContagem, DataInclusao,
                   NumeroPostagem, IdCitacao
            FROM dbo.Cit_Citacoes
            WHERE IdProcesso IN (:id, :id_origem) AND Tipo LIKE 'N%' AND DataExclusao IS NULL
            ORDER BY DataInclusao DESC
            """
        ),
        {"id": id_processo, "id_origem": id_origem or -1},
    ).first()
    if cit:
        out["numero"] = out["numero"] or f"{str(cit[0]).strip()}/{str(cit[1]).strip()}"
        out["data"] = out["data"] or cit[2] or cit[3]
        out["numero_postagem"] = (cit[4] or "").strip() or None
        out["id_citacao"] = cit[5]
    return out


def ar(
    session: Session,
    *,
    id_informacao: int | None,
    id_citacao: int | None,
    numero_postagem: str | None,
) -> dict[str, Any]:
    """AR da notificação: guia de postagem → arquivo de retorno. `None` quando não rastreável."""
    row = session.execute(
        text(
            """
            SELECT TOP 1 RTRIM(g.NumeroPostagem) AS postagem, g.DataRecebimento, ret.DataEntregaAR
            FROM dbo.Cit_ItensGuiaPostagem g
            LEFT JOIN dbo.Cit_ItensArquivoRetorno ret ON RTRIM(ret.NumeroObjeto) = RTRIM(g.NumeroPostagem)
            WHERE (g.IdInformacao = :idi) OR (g.IdCitacao = :idc)
               OR (RTRIM(g.NumeroPostagem) = :post)
            ORDER BY g.DataInclusao DESC
            """
        ),
        {"idi": id_informacao or -1, "idc": id_citacao or -1, "post": numero_postagem or ""},
    ).first()
    if row:
        return {"numero_postagem": row[0] or numero_postagem, "data": row[2] or row[1]}
    if numero_postagem:
        ret = session.execute(
            text(
                "SELECT TOP 1 DataEntregaAR FROM dbo.Cit_ItensArquivoRetorno "
                "WHERE RTRIM(NumeroObjeto) = :post ORDER BY DataEntregaAR DESC"
            ),
            {"post": numero_postagem},
        ).first()
        return {"numero_postagem": numero_postagem, "data": ret[0] if ret else None}
    return {"numero_postagem": None, "data": None}


def apensados(session: Session, id_processo: int) -> list[dict[str, Any]]:
    rows = session.execute(
        text(
            """
            SELECT IdProcesso AS id_processo, RTRIM(numero_processo) AS numero,
                   RTRIM(ano_processo) AS ano, data_registro
            FROM dbo.Processos WHERE IdProcessoApensador = :id
            ORDER BY data_registro DESC
            """
        ),
        {"id": id_processo},
    ).mappings()
    return [dict(r) for r in rows]


def evento_apensamento(
    infos_principal: list[dict[str, Any]], data_registro: datetime | None
) -> Optional[int]:
    """Evento do termo de apensamento mais próximo da data de registro do apensado.

    O principal pode ter mais de um termo (inclusive herdado da origem); o número
    do apenso só está no PDF, então a proximidade de datas é o critério.
    """
    termos = [
        i for i in infos_principal if "apensamento" in str(i.get("nome_informacao") or "").lower()
    ]
    if not termos:
        return None
    if data_registro is None:
        return int(termos[-1]["evento"])
    melhor = min(
        termos,
        key=lambda i: (
            abs((i["data_resumo"] - data_registro).total_seconds())
            if i.get("data_resumo")
            else float("inf")
        ),
    )
    return int(melhor["evento"])
