"""Detecção de candidatos a benefício (SisBenefícios) nos bancos processo/BdDIP.

Insert-only: cada sub-rotina insere candidatos novos (Status='RASCUNHO') com
`WHERE NOT EXISTS (ChaveOrigem ativa)` e NUNCA atualiza linha existente — um
candidato editado/validado/descartado na tela não é tocado pelo job. O índice
único filtrado UX_CCDBeneficio_ChaveOrigem garante contra corrida.

IDs de domínio do BdBeneficio pré-preenchidos:
  Tipo 1=Sanção (subtipo 1=Multa) · Tipo 2=Restituição (subtipo 4=Débito imputado)
  Caracterização 2=QUANT. FINANCEIRO · Situação-efetivação 1=Efetivo, 2=Potencial
  Situação 1=Não Efetivado, 2=Efetivado Parcial, 3=Efetivado Total
  Área temática 13=Finanças e Contas Públicas (palpite, editável na tela)

O cron chama sem id_frap_job (sem linha em FRAPJob — IdUsuario é NOT NULL);
o endpoint manual passa um. Mesmo padrão de task_verificar_siai_folha.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.jobs.tasks import _session_factory, _set_done, _set_failed, _set_running

_NAO_EXISTE = (
    "NOT EXISTS (SELECT 1 FROM dbo.CCDBeneficio b WHERE b.ChaveOrigem = {chave} AND b.Ativo = 1)"
)

# ---------------------------------------------------------------------------
# DEBITO — benefício POTENCIAL: débito transitado em julgado ainda em cobrança.
# Grão = cadeia (Exe_Debito.IdDebitoAnterior encadeia versões): identidade é a
# RAIZ (valor imputado na decisão), situação vigente é a FOLHA — reparcelamento
# não duplica. CTE espelha scripts/analise/carteira_ipsas.py.
# CodigoTipoDebito: 1=Ressarcimento, 3=Remanejamento -> tipo 2/subtipo 4;
# 2/4/5=Multa -> tipo 1/subtipo 1.
# ---------------------------------------------------------------------------
_SQL_DEBITO = f"""
WITH cadeia AS (
    SELECT r.IdDebito AS id_raiz, r.IdDebito AS id_no, 0 AS nivel
      FROM processo.dbo.Exe_Debito r
     WHERE r.IdDebitoAnterior IS NULL
    UNION ALL
    SELECT c.id_raiz, f.IdDebito, c.nivel + 1
      FROM cadeia c
      JOIN processo.dbo.Exe_Debito f ON f.IdDebitoAnterior = c.id_no
),
folhas AS (
    SELECT c.id_raiz, e.IdDebito, e.CodigoStatusDivida, e.dataBaixa,
           ROW_NUMBER() OVER (PARTITION BY c.id_raiz
                              ORDER BY c.nivel DESC, e.datainclusao DESC, e.IdDebito DESC) AS rn
      FROM cadeia c
      JOIN processo.dbo.Exe_Debito e ON e.IdDebito = c.id_no
     WHERE NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_Debito g
                        WHERE g.IdDebitoAnterior = e.IdDebito)
),
transito AS (
    SELECT c.id_raiz, MIN(e.dataTransito) AS data_transito
      FROM cadeia c
      JOIN processo.dbo.Exe_Debito e ON e.IdDebito = c.id_no
     GROUP BY c.id_raiz
)
INSERT INTO dbo.CCDBeneficio
    (Origem, ChaveOrigem, IdDebitoExecucao, DescricaoPropostaBeneficio,
     ValorQuantidade, IdBeneficioSituacaoEfetivacao, IdBeneficioSituacao,
     IdCaracterizacaoBeneficio, IdAreaTematica, IdTipoBeneficio, IdSubTipoBeneficio,
     NumeroProcessoDecisao, AnoProcessoDecisao, CpfCnpj, NomePessoa, DataOcorrencia)
SELECT 'DEBITO',
       CONCAT('DEBITO:', r.IdDebito),
       r.IdDebito,
       LEFT(CONCAT(
           CASE WHEN r.CodigoTipoDebito IN (2, 4, 5) THEN 'Multa aplicada' ELSE 'Débito imputado' END,
           ' — processo ', ISNULL(CONCAT(p.numero_processo, '/', p.ano_processo), 's/ processo'),
           CASE WHEN gp.Nome IS NOT NULL THEN CONCAT(', ', gp.Nome) ELSE '' END,
           ' (trânsito em julgado; aguarda cumprimento)'), 500),
       r.valorOriginalDebito,
       2,  -- Potencial
       1,  -- Não Efetivado
       2,  -- Quantitativo financeiro
       13, -- Finanças e Contas Públicas
       CASE WHEN r.CodigoTipoDebito IN (2, 4, 5) THEN 1 ELSE 2 END,
       CASE WHEN r.CodigoTipoDebito IN (2, 4, 5) THEN 1 ELSE 4 END,
       p.numero_processo, TRY_CAST(p.ano_processo AS SMALLINT),
       LEFT(REPLACE(REPLACE(REPLACE(REPLACE(gp.Documento, '.', ''), '-', ''), '/', ''), ' ', ''), 14),
       gp.Nome,
       CAST(t.data_transito AS DATE)
FROM processo.dbo.Exe_Debito r
JOIN transito t ON t.id_raiz = r.IdDebito
JOIN folhas f ON f.id_raiz = r.IdDebito AND f.rn = 1
LEFT JOIN processo.dbo.Processos p ON p.IdProcesso = r.IdProcessoOrigem
OUTER APPLY (SELECT TOP 1 gp2.Nome, gp2.Documento
               FROM processo.dbo.Exe_DebitoPessoa edp
               JOIN processo.dbo.GenPessoa gp2 ON gp2.IdPessoa = edp.IDPessoa
              WHERE edp.IDDebito = r.IdDebito
              ORDER BY gp2.IdPessoa) gp
WHERE r.IdDebitoAnterior IS NULL
  AND t.data_transito IS NOT NULL
  AND f.dataBaixa IS NULL
  AND r.DataCancelamento IS NULL
  AND {_NAO_EXISTE.format(chave="CONCAT('DEBITO:', r.IdDebito)")}
OPTION (MAXRECURSION 100)
"""

# ---------------------------------------------------------------------------
# BOLETO — benefício EFETIVO: multa recolhida por guia bancária.
# Cadeia de joins de web/tools/frap/frap/processo/repos.py.
# ---------------------------------------------------------------------------
_SQL_BOLETO = f"""
INSERT INTO dbo.CCDBeneficio
    (Origem, ChaveOrigem, IdDebitoExecucao, DescricaoPropostaBeneficio,
     ValorQuantidade, IdBeneficioSituacaoEfetivacao, IdBeneficioSituacao,
     IdCaracterizacaoBeneficio, IdAreaTematica, IdTipoBeneficio, IdSubTipoBeneficio,
     NumeroProcessoDecisao, AnoProcessoDecisao, CpfCnpj, NomePessoa, DataOcorrencia)
SELECT 'BOLETO',
       CONCAT('BOLETO:', rb.IdRetornoBoleto),
       ed.IdDebito,
       LEFT(CONCAT('Recolhimento por boleto — processo ',
           ISNULL(CONCAT(p.numero_processo, '/', p.ano_processo), 's/ processo'),
           CASE WHEN gp.Nome IS NOT NULL THEN CONCAT(', ', gp.Nome) ELSE '' END), 500),
       rb.ValorPago,
       1,  -- Efetivo
       3,  -- Efetivado Total (do evento de recolhimento)
       2, 13,
       CASE WHEN ed.CodigoTipoDebito IN (2, 4, 5) THEN 1 ELSE 2 END,
       CASE WHEN ed.CodigoTipoDebito IN (2, 4, 5) THEN 1 ELSE 4 END,
       p.numero_processo, TRY_CAST(p.ano_processo AS SMALLINT),
       LEFT(REPLACE(REPLACE(REPLACE(REPLACE(gp.Documento, '.', ''), '-', ''), '/', ''), ' ', ''), 14),
       gp.Nome,
       CAST(rb.DataPagamento AS DATE)
FROM processo.dbo.Exe_Retorno_Boleto rb
JOIN processo.dbo.Exe_DebitoBoleto db ON db.IdBoleto = rb.IdBoleto
JOIN processo.dbo.Exe_Debito ed ON ed.IdDebito = db.IdDebito
LEFT JOIN processo.dbo.Processos p ON p.IdProcesso = ed.IdProcessoOrigem
OUTER APPLY (SELECT TOP 1 gp2.Nome, gp2.Documento
               FROM processo.dbo.Exe_DebitoPessoa edp
               JOIN processo.dbo.GenPessoa gp2 ON gp2.IdPessoa = edp.IDPessoa
              WHERE edp.IDDebito = ed.IdDebito
              ORDER BY gp2.IdPessoa) gp
WHERE rb.DataPagamento IS NOT NULL
  AND rb.DataPagamento >= :inicio
  AND {_NAO_EXISTE.format(chave="CONCAT('BOLETO:', rb.IdRetornoBoleto)")}
"""

# ---------------------------------------------------------------------------
# PGE — benefício EFETIVO: repasse de valor arrecadado pela dívida ativa.
# ---------------------------------------------------------------------------
_SQL_PGE = f"""
INSERT INTO dbo.CCDBeneficio
    (Origem, ChaveOrigem, IdDebitoExecucao, DescricaoPropostaBeneficio,
     ValorQuantidade, IdBeneficioSituacaoEfetivacao, IdBeneficioSituacao,
     IdCaracterizacaoBeneficio, IdAreaTematica, IdTipoBeneficio, IdSubTipoBeneficio,
     NumeroProcessoDecisao, AnoProcessoDecisao, DataOcorrencia)
SELECT 'PGE',
       CONCAT('PGE:', pg.IdPagamentoPGE),
       pp.IdDebitoExecucao,
       LEFT(CONCAT('Repasse PGE (dívida ativa, CDA ', LTRIM(RTRIM(ISNULL(pp.NumeroCDA, '?'))),
           ') — execução ', LTRIM(RTRIM(ISNULL(pp.NumeroProcessoExecucao, '?'))), '/',
           LTRIM(RTRIM(ISNULL(pp.AnoProcessoExecucao, '?')))), 500),
       COALESCE(pg.ValorPrincipal, 0) + COALESCE(pg.Multa, 0) + COALESCE(pg.Juros, 0),
       1, 3, 2, 13,
       1, 1,  -- repasses PGE são de multa (conferido em conciliacao_competencia_caixa.py)
       LTRIM(RTRIM(pp.NumeroProcessoExecucao)), TRY_CAST(pp.AnoProcessoExecucao AS SMALLINT),
       pg.DataPagamento
FROM processo.dbo.PGE_Pagamento pg
JOIN processo.dbo.PGE_Processo pp ON pp.IdProcessoPGE = pg.IdProcessoPGE
WHERE pg.DataPagamento IS NOT NULL
  AND pg.DataPagamento >= :inicio
  AND {_NAO_EXISTE.format(chave="CONCAT('PGE:', pg.IdPagamentoPGE)")}
"""

# ---------------------------------------------------------------------------
# PROPOSTA — propostas de benefício já cadastradas pelas UTCEs no BdBeneficio,
# APROVADAS no workflow do SisBenefícios (IdStatusBeneficio=7). A CCD gerencia
# o fluxo proposta -> potencial -> efetivo; a cópia entra pré-classificada com
# os campos que a UTCE preencheu e estágio Potencial sugerido (editável).
# ---------------------------------------------------------------------------
_SQL_PROPOSTA = f"""
INSERT INTO dbo.CCDBeneficio
    (Origem, ChaveOrigem, DescricaoPropostaBeneficio, MemoriaCalculoPropostaBeneficio,
     ValorQuantidade, JustificativaPropostaBeneficio, IdBeneficioSituacaoEfetivacao,
     IdBeneficioSituacao, IdAreaTematica, IdCaracterizacaoBeneficio, IdUnidadeDeMedida,
     IdTipoBeneficio, IdSubTipoBeneficio, NumeroProcessoDecisao, AnoProcessoDecisao,
     IdProcessoDecisao, DescricaoMotivo)
SELECT 'PROPOSTA',
       CONCAT('PROPOSTA:', p.IdPropostaBeneficio),
       p.DescricaoPropostaBeneficio,
       p.MemoriaCalculoPropostaBeneficio,
       p.ValorQuantidade,
       p.JustificativaPropostaBeneficio,
       2,  -- Potencial (próximo estágio do fluxo; a CCD ajusta na tela)
       1,  -- Não Efetivado
       p.IdAreaTematica,
       p.IdCaracterizacaoBeneficio,
       p.IdUnidadeDeMedida,
       p.IdTipoBeneficio,
       p.IdSubTipoBeneficio,
       p.NumeroProcessoDecisao,
       p.AnoProcessoDecisao,
       p.IdProcessoDecisao,
       p.DescricaoMotivo
FROM BdBeneficio.dbo.Beneficio_PropostaBeneficio p
WHERE p.IdStatusBeneficio = 7  -- Aprovado
  AND {_NAO_EXISTE.format(chave="CONCAT('PROPOSTA:', p.IdPropostaBeneficio)")}
"""

# Origens ativas na v1. FOLHA (parcela SIAI, grão por competência a referendar
# pela SECEX) e DIVIDA_ATIVA (inscrição de CDA não é benefício autônomo pelo
# Manual — é etapa de cobrança; o efetivo é o repasse PGE) ficaram fora por
# decisão de 01/09/2026; o CHECK da tabela e o Literal dos schemas mantêm os
# valores para uma eventual reativação.
_ORIGENS: dict[str, tuple[str, dict[str, Any]]] = {
    "PROPOSTA": (_SQL_PROPOSTA, {}),
    "DEBITO": (_SQL_DEBITO, {}),
    "BOLETO": (_SQL_BOLETO, {"inicio": "2021-01-01"}),
    "PGE": (_SQL_PGE, {"inicio": "2021-01-01"}),
}


def detectar_origem(session: Session, origem: str) -> int:
    sql, params = _ORIGENS[origem]
    return int(session.execute(text(sql), params).rowcount or 0)


async def task_detectar_beneficios(
    ctx: dict[str, Any],
    id_frap_job: int | None = None,
    origens: list[str] | None = None,
) -> str:
    """Varre as fontes e insere candidatos novos em CCDBeneficio (insert-only).

    `origens` restringe a rodada (depuração/backfill); default = todas.
    """
    factory = _session_factory()
    if id_frap_job is not None:
        _set_running(factory, id_frap_job)
    try:
        alvo = [o for o in (origens or list(_ORIGENS)) if o in _ORIGENS]
        linhas: list[str] = []
        with factory() as s:
            for origem in alvo:
                n = detectar_origem(s, origem)
                s.commit()
                linhas.append(f"{origem}: {n} candidatos novos")
        resultado = "\n".join(linhas)
        if id_frap_job is not None:
            _set_done(factory, id_frap_job, resultado)
        return resultado
    except Exception as exc:
        if id_frap_job is not None:
            _set_failed(factory, id_frap_job, repr(exc))
        raise
