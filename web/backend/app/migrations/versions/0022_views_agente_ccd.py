"""Views de leitura para o agente de IA de outro setor (produção de informações da CCD).

Cinco views em BdDIP, todas com nomes de 3 partes para o banco `processo`:

- `vwCCDDebito`            uma linha por CADEIA de débito (raiz = identidade, folha = situação)
- `vwCCDDebitoResponsavel` ponte débito × pessoa (grão pessoa, CPF/CNPJ só dígitos)
- `vwCCDDeterminacao`      obrigações + recomendações com `Status = 'approved'` no CGAD
- `vwCCDFrapLancamento`    extrato FRAP no grão lançamento × vínculo (4 matchers)
- `vwCCDFrapDescontoFolha` parcelas do desconto em folha × contracheque × lançamento

Armadilhas encapsuladas (todas verificadas no banco; ver docs/memoria/claude):
- `Exe_Debito.IdDebitoAnterior` encadeia versões PARA A FRENTE: o vigente é a FOLHA
  (nó sem filho), `IdDebitoAnterior IS NULL` é o original. 1.602 cadeias têm raiz ≠ folha.
- `Exe_Debito.ValorAPagar/Correcao*/Juros*` estão NULL em 99,9% dos abertos — não expor.
- `Exe_Debito.Status_PGE` é bit e vem vazio; dívida ativa vive em `PGE_Processo`.
- `vw_ia_votos_acordaos_decisoes` devolve >1 linha por chave — OUTER APPLY TOP 1.
- `Processo_TransitoJulgado` não tem IdProcesso: junção por numero+ano com RTRIM.
- Varredura completa de `vwCCDDebito` ≈ 30 s (UDF de valor atualizado); filtrada por
  processo/CPF < 1 s. FOR XML por linha custava 120 s — por isso só nas raízes multi-pessoa.
- `FRAPMatchDescontoFolha.IdLancamentoFRAP` (não `IdLancamento`).
- `FRAPDescontoFolhaParcela` repete a mesma parcela em planos-tranche — `rn_duplicata`.
- Lookups de texto (`Exe_StatusDivida`, `Exe_StatusProtesto`, `PGE_StatusProcesso`) vêm
  com acentos corrompidos via pymssql — rótulos fixos por código nas views.
- Servidor SQL Server 2016: sem STRING_AGG (FOR XML PATH), sem OPTION(MAXRECURSION) em view.

Revision ID: 0022_views_agente_ccd
Revises: 0021_origem_proposta
Create Date: 2026-09-14
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0022_views_agente_ccd"
down_revision: str | Sequence[str] | None = "0021_origem_proposta"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_DOC = "REPLACE(REPLACE(REPLACE(REPLACE({col}, '.', ''), '-', ''), '/', ''), ' ', '')"

_CADEIA = """
cadeia AS (
    SELECT r.IdDebito AS id_raiz, r.IdDebito AS id_no, 0 AS nivel
      FROM processo.dbo.Exe_Debito r
     WHERE r.IdDebitoAnterior IS NULL
    UNION ALL
    SELECT c.id_raiz, f.IdDebito, c.nivel + 1
      FROM cadeia c
      JOIN processo.dbo.Exe_Debito f ON f.IdDebitoAnterior = c.id_no
)"""

VW_DEBITO = f"""
CREATE OR ALTER VIEW dbo.vwCCDDebito AS
WITH {_CADEIA},
folhas AS (
    SELECT c.id_raiz, c.id_no,
           ROW_NUMBER() OVER (PARTITION BY c.id_raiz
                              ORDER BY c.nivel DESC, e.datainclusao DESC, e.IdDebito DESC) AS rn
      FROM cadeia c
      JOIN processo.dbo.Exe_Debito e ON e.IdDebito = c.id_no
     WHERE NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_Debito g
                        WHERE g.IdDebitoAnterior = e.IdDebito)
),
agregado AS (
    SELECT c.id_raiz,
           COUNT(*)                      AS nos_na_cadeia,
           SUM(COALESCE(e.ValorPago, 0)) AS valor_recuperado,
           MIN(e.dataTransito)           AS data_transito,
           MAX(CASE WHEN e.StatusProtesto IS NOT NULL AND e.StatusProtesto <> 0
                    THEN 1 ELSE 0 END)   AS protestado
      FROM cadeia c
      JOIN processo.dbo.Exe_Debito e ON e.IdDebito = c.id_no
     GROUP BY c.id_raiz
),
-- Vínculos que podem apontar para qualquer nó da cadeia (parcelamento em 972 filhos,
-- PGE em 117): ranqueados por raiz em conjunto. Um OUTER APPLY correlacionado sobre a
-- CTE recursiva reexecutava a recursão por linha (190 s na varredura completa).
mc AS (
    SELECT c.id_raiz, m.ValorMultaCominatoria, m.CcTotalMultaCominatoria, m.LimiteValor,
           m.DataInicioImputacaoMultaCominatoria, m.DataFinalImputacaoMultaCominatoria,
           ROW_NUMBER() OVER (PARTITION BY c.id_raiz ORDER BY m.IdDebitoMultaCominatoria DESC) AS rn
      FROM cadeia c
      JOIN processo.dbo.Exe_Debito_MultaCominatoria m ON m.IdDebito = c.id_no
),
pge AS (
    SELECT c.id_raiz, pp.IdProcessoPGE, pp.NumeroCDA, pp.IdStatusProcessoPGE, pp.HomologadoPGE,
           pp.DataEnvioInscricaoDividaPGE, pp.ValorAtualizadoPGE, pp.ValorPagoPGE,
           ROW_NUMBER() OVER (PARTITION BY c.id_raiz ORDER BY pp.IdProcessoPGE DESC) AS rn
      FROM cadeia c
      JOIN processo.dbo.PGE_Processo pp ON pp.IdDebitoExecucao = c.id_no
),
parc AS (
    SELECT c.id_raiz, ep.IdParcelamento, ep.SituacaoParcelamento,
           ROW_NUMBER() OVER (PARTITION BY c.id_raiz ORDER BY ep.IdParcelamento DESC) AS rn
      FROM cadeia c
      JOIN processo.dbo.Exe_Parcelamento ep ON ep.IdDebito = c.id_no
),
resp1 AS (
    -- 98% das raízes têm uma só pessoa: sai direto, sem FOR XML (que custava 120 s na varredura)
    SELECT dp.IDDebito, COUNT(*) AS n,
           MIN(RTRIM(gp.Nome)) AS nome, MIN({_DOC.format(col="gp.Documento")}) AS documento
      FROM processo.dbo.Exe_DebitoPessoa dp
      JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = dp.IDPessoa
     GROUP BY dp.IDDebito
),
parcelas AS (
    SELECT x.IdParcelamento, COUNT(*) AS numero_parcelas,
           SUM(CASE WHEN x.SituacaoParcela = '2' THEN 1 ELSE 0 END) AS parcelas_pagas
      FROM processo.dbo.Exe_Parcela x
     GROUP BY x.IdParcelamento
)
SELECT
    r.IdDebito                                  AS id_debito,
    f.IdDebito                                  AS id_debito_vigente,
    a.nos_na_cadeia                             AS nos_na_cadeia,
    r.CodigoTipoDebito                          AS cod_tipo,
    CASE r.CodigoTipoDebito
         WHEN 1 THEN N'Ressarcimento' WHEN 2 THEN N'Multa' WHEN 3 THEN N'Remanejamento'
         WHEN 4 THEN N'Multa Percentual' WHEN 5 THEN N'Multa Cominatória' END AS tipo,
    CASE WHEN r.CodigoTipoDebito IN (2, 4, 5) THEN N'multa' ELSE N'ressarcimento' END AS natureza,
    f.CodigoStatusDivida                        AS cod_status,
    CASE f.CodigoStatusDivida
         WHEN 1  THEN N'Em Aberto'
         WHEN 2  THEN N'Pago Integralmente'
         WHEN 3  THEN N'Pago parcialmente'
         WHEN 4  THEN N'Cancelada por extinção'
         WHEN 5  THEN N'Cancelada por Alteração'
         WHEN 6  THEN N'Cancelada por prescrição'
         WHEN 7  THEN N'Cancelada por decisão do relator'
         WHEN 8  THEN N'Parcelado'
         WHEN 9  THEN N'Pago Aguardando Compensação'
         WHEN 10 THEN N'Cancelada por Perdão de Dívida'
         WHEN 13 THEN N'Cancelada por Reabertura de Parcelamento'
         WHEN 14 THEN N'Cancelada por Reabertura de Dívida Paga Parcialmente'
         WHEN 15 THEN N'Cancelada por Erro de Cadastro'
         WHEN 16 THEN N'Cancelada por Decisão em novo Acórdão'
         WHEN 17 THEN N'Cancelada por Óbito do Gestor'
         WHEN 18 THEN N'Cancelada por Unificação da Dívida'
         WHEN 19 THEN N'Cancelada por Decisão Judicial'
         WHEN 20 THEN N'Suspenso'
         WHEN 21 THEN N'Cancelado por duplicidade' END AS status,
    CAST(CASE WHEN sd.StatusCancelamento = 1 OR f.DataCancelamento IS NOT NULL
              THEN 1 ELSE 0 END AS bit)         AS cancelado,
    r.valorOriginalDebito                       AS valor_imputado,
    a.valor_recuperado                          AS valor_recuperado,
    f.valorOriginalDebito                       AS saldo_registrado,
    -- ponytail: UDF escalar do sistema, avaliada por linha devolvida; remover se pesar
    processo.dbo.fn_Exe_RetornaValorAtualizado(f.IdDebito) AS valor_atualizado,
    r.dataDecisao                               AS data_decisao,
    r.dataAto                                   AS data_ato,
    -- ponytail: só dataTransito do débito; o fallback por Processo_TransitoJulgado
    -- recuperava 6 de 1.891 cadeias sem data e o legado do antecedentes também não o usa
    a.data_transito                             AS data_transito,
    f.dataBaixa                                 AS data_baixa,
    f.DataCancelamento                          AS data_cancelamento,
    RTRIM(r.setorDebito)                        AS setor_debito,
    po.IdProcesso                               AS id_processo_origem,
    RTRIM(po.numero_processo) + '/' + RTRIM(po.ano_processo) AS processo_origem,
    RTRIM(po.setor_atual)                       AS setor_origem,
    RTRIM(rel.nome)                             AS relator_origem,
    RTRIM(po.assunto)                           AS assunto_origem,
    pe.IdProcesso                               AS id_processo_execucao,
    RTRIM(pe.numero_processo) + '/' + RTRIM(pe.ano_processo) AS processo_execucao,
    RTRIM(pe.setor_atual)                       AS setor_execucao,
    CAST(COALESCE(rm.responsaveis, r1.nome + ' (' + COALESCE(r1.documento, '') + ')')
         AS nvarchar(4000))                     AS responsaveis,
    CAST(a.protestado AS bit)                   AS protestado,
    f.StatusProtesto                            AS protesto_cod,
    CASE f.StatusProtesto
         WHEN 1  THEN N'Incluída em lote de remessa'
         WHEN 2  THEN N'Enviada a Protesto'
         WHEN 3  THEN N'Protestada'
         WHEN 4  THEN N'Paga'
         WHEN 5  THEN N'Solicitação de Desistência'
         WHEN 6  THEN N'Solicitação de Cancelamento (Após o Protesto)'
         WHEN 7  THEN N'Solicitação de Autorização de Cancelamento (Dívida Paga ou Parcelada)'
         WHEN 8  THEN N'Cancelada antes do Protesto'
         WHEN 9  THEN N'Cancelada após o Protesto'
         WHEN 10 THEN N'Cancelada por Pagamento'
         WHEN 11 THEN N'Sustada por Ordem Judicial'
         WHEN 12 THEN N'Devolvida por Irregularidade' END AS protesto_status,
    mc.ValorMultaCominatoria                    AS mc_valor_dia,
    mc.CcTotalMultaCominatoria                  AS mc_total,
    mc.LimiteValor                              AS mc_teto,
    mc.DataInicioImputacaoMultaCominatoria      AS mc_data_inicio,
    mc.DataFinalImputacaoMultaCominatoria       AS mc_data_fim,
    CASE WHEN mc.ValorMultaCominatoria > 0
         THEN CAST(ROUND(mc.CcTotalMultaCominatoria / mc.ValorMultaCominatoria, 0) AS int) END AS mc_dias,
    pge.IdProcessoPGE                           AS pge_id,
    RTRIM(pge.NumeroCDA)                        AS pge_numero_cda,
    pge.IdStatusProcessoPGE                     AS pge_status_cod,
    CASE pge.IdStatusProcessoPGE
         WHEN 1 THEN N'Inscrito em Dívida Ativa' WHEN 2 THEN N'Negociado'
         WHEN 3 THEN N'Quitado' WHEN 4 THEN N'Exigibilidade Suspensa'
         WHEN 5 THEN N'Cancelado' WHEN 6 THEN N'Pagamento em Atraso'
         WHEN 7 THEN N'Remissão' WHEN 8 THEN N'Prescrito' END AS pge_status,
    pge.HomologadoPGE                           AS pge_homologado,
    pge.DataEnvioInscricaoDividaPGE             AS pge_data_envio,
    pge.ValorAtualizadoPGE                      AS pge_valor_atualizado,
    pge.ValorPagoPGE                            AS pge_valor_pago,
    parc.IdParcelamento                         AS parc_id,
    RTRIM(parc.SituacaoParcelamento)            AS parc_situacao_cod,
    CASE RTRIM(parc.SituacaoParcelamento)
         WHEN '1' THEN N'Aguardando início' WHEN '2' THEN N'Em curso'
         WHEN '3' THEN N'Cancelado' WHEN '4' THEN N'Quitado'
         WHEN '5' THEN N'Cancelado por inadimplência' WHEN '6' THEN N'Indefinida' END AS parc_situacao,
    CAST(CASE WHEN RTRIM(parc.SituacaoParcelamento) IN ('1', '2') AND f.DataCancelamento IS NULL
              THEN 1 ELSE 0 END AS bit)         AS parc_ativo,
    pc.numero_parcelas                          AS parc_numero_parcelas,
    pc.parcelas_pagas                           AS parc_parcelas_pagas
FROM processo.dbo.Exe_Debito r
JOIN agregado a ON a.id_raiz = r.IdDebito
JOIN folhas fl  ON fl.id_raiz = r.IdDebito AND fl.rn = 1
JOIN processo.dbo.Exe_Debito f ON f.IdDebito = fl.id_no
LEFT JOIN processo.dbo.Exe_StatusDivida sd ON sd.CodigoStatusDivida = f.CodigoStatusDivida
LEFT JOIN processo.dbo.Processos po ON po.IdProcesso = COALESCE(r.IdProcessoOrigem, f.IdProcessoOrigem)
LEFT JOIN processo.dbo.Processos pe ON pe.IdProcesso = COALESCE(r.IdProcessoExecucao, f.IdProcessoExecucao)
LEFT JOIN processo.dbo.Relator rel ON rel.codigo = po.codigo_relator
LEFT JOIN mc   ON mc.id_raiz = r.IdDebito AND mc.rn = 1
LEFT JOIN pge  ON pge.id_raiz = r.IdDebito AND pge.rn = 1
LEFT JOIN parc ON parc.id_raiz = r.IdDebito AND parc.rn = 1
LEFT JOIN parcelas pc ON pc.IdParcelamento = parc.IdParcelamento
LEFT JOIN resp1 r1 ON r1.IDDebito = r.IdDebito
LEFT JOIN (
    -- FOR XML só para as ~500 raízes com mais de uma pessoa (num CASE por linha o
    -- otimizador avaliava a subconsulta para todas as 17 mil). Responsáveis da RAIZ:
    -- os filhos replicam a pessoa; só 1 cadeia em 17 mil tem pessoa exclusiva de filho.
    SELECT mu.IDDebito, STUFF((
        SELECT '; ' + x.nome + ' (' + COALESCE(x.documento, '') + ')'
        FROM (SELECT DISTINCT RTRIM(gp.Nome) AS nome,
                     {_DOC.format(col="gp.Documento")} AS documento
              FROM processo.dbo.Exe_DebitoPessoa dp
              JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = dp.IDPessoa
              WHERE dp.IDDebito = mu.IDDebito) x
        ORDER BY x.nome
        FOR XML PATH(''), TYPE
    ).value('.', 'NVARCHAR(MAX)'), 1, 2, '') AS responsaveis
    FROM resp1 mu
    WHERE mu.n > 1
) rm ON rm.IDDebito = r.IdDebito
WHERE r.IdDebitoAnterior IS NULL
"""

VW_DEBITO_RESPONSAVEL = f"""
CREATE OR ALTER VIEW dbo.vwCCDDebitoResponsavel AS
WITH {_CADEIA}
SELECT DISTINCT
    c.id_raiz            AS id_debito,
    gp.IdPessoa          AS id_pessoa,
    RTRIM(gp.Nome)       AS nome,
    LOWER(RTRIM(gp.Nome)) AS nome_busca,
    d.documento          AS documento,
    CASE LEN(d.documento) WHEN 11 THEN 'CPF' WHEN 14 THEN 'CNPJ' END AS tipo_pessoa
FROM cadeia c
JOIN processo.dbo.Exe_DebitoPessoa dp ON dp.IDDebito = c.id_no
JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = dp.IDPessoa
CROSS APPLY (SELECT {_DOC.format(col="gp.Documento")} AS documento) d
"""

VW_DETERMINACAO = f"""
CREATE OR ALTER VIEW dbo.vwCCDDeterminacao AS
WITH curadas AS (
    SELECT
        'obrigacao'                       AS tipo,
        s.IdObrigacaoStaging              AS id_staging,
        s.IdNerObrigacao                  AS id_ner,
        s.IdObrigacao                     AS id_final,
        s.IdProcesso, s.IdComposicaoPauta, s.IdVotoPauta,
        s.DescricaoObrigacao              AS descricao,
        s.Prazo                           AS prazo_texto,
        s.DataCumprimento                 AS data_cumprimento,
        NULLIF(s.OrgaoResponsavel, 'Desconhecido')                AS orgao_responsavel,
        s.IdOrgaoResponsavel              AS id_orgao_responsavel,
        NULLIF(s.NomeResponsavelMultaCominatoria, 'Desconhecido') AS nome_responsavel,
        s.IdPessoaMultaCominatoria        AS id_pessoa_responsavel,
        {_DOC.format(col="s.DocumentoResponsavelMultaCominatoria")} AS documento_responsavel,
        s.TemMultaCominatoria             AS tem_multa_cominatoria,
        s.ValorMultaCominatoria           AS valor_multa_cominatoria,
        s.DeFazer                         AS de_fazer,
        CAST(0 AS bit)                    AS cancelado,
        s.Revisor                         AS revisor,
        s.DataRevisao                     AS data_revisao,
        s.ObservacoesRevisao              AS observacoes_revisao
    FROM dbo.ObrigacaoStaging s
    WHERE s.Status = 'approved'

    UNION ALL

    SELECT
        'recomendacao',
        r.IdRecomendacaoStaging,
        r.IdNerRecomendacao,
        r.IdRecomendacao,
        r.IdProcesso, r.IdComposicaoPauta, r.IdVotoPauta,
        r.DescricaoRecomendacao,
        r.PrazoCumprimentoRecomendacao,
        r.DataCumprimentoRecomendacao,
        NULLIF(r.OrgaoResponsavel, 'Desconhecido'),
        r.IdOrgaoResponsavel,
        NULLIF(r.NomeResponsavel, 'Desconhecido'),
        r.IdPessoaResponsavel,
        CAST(NULL AS varchar(20)),
        CAST(0 AS bit),
        CAST(NULL AS float),
        CAST(NULL AS bit),
        COALESCE(r.Cancelado, 0),
        r.Revisor,
        r.DataRevisao,
        r.ObservacoesRevisao
    FROM dbo.RecomendacaoStaging r
    WHERE r.Status = 'approved'
)
SELECT
    c.tipo, c.id_staging, c.id_ner, c.id_final,
    c.IdProcesso                                                AS id_processo,
    RTRIM(p.numero_processo) + '/' + RTRIM(p.ano_processo)      AS processo,
    RTRIM(p.setor_atual)                                        AS setor_atual,
    RTRIM(p.assunto)                                            AS assunto,
    RTRIM(p.interessado)                                        AS interessado,
    RTRIM(rel.nome)                                             AS relator,
    c.IdComposicaoPauta                                         AS id_composicao_pauta,
    c.IdVotoPauta                                               AS id_voto_pauta,
    v.acordao                                                   AS acordao,
    v.DataSessao                                                AS data_sessao,
    tj.data_transito                                            AS data_transito,
    CAST(CASE WHEN cgr.IdProcessoOriginario IS NULL THEN 0 ELSE 1 END AS bit) AS tem_cgr,
    c.descricao, c.prazo_texto, c.data_cumprimento,
    c.orgao_responsavel, c.id_orgao_responsavel,
    c.nome_responsavel, c.id_pessoa_responsavel, c.documento_responsavel,
    c.tem_multa_cominatoria, c.valor_multa_cominatoria, c.de_fazer, c.cancelado,
    c.revisor, c.data_revisao, c.observacoes_revisao
FROM curadas c
JOIN processo.dbo.Processos p ON p.IdProcesso = c.IdProcesso
LEFT JOIN processo.dbo.Relator rel ON rel.codigo = p.codigo_relator
OUTER APPLY (
    -- a view devolve >1 linha por chave: TOP 1 evita inflar a contagem
    SELECT TOP 1 vw.DataSessao,
           CONCAT(RTRIM(vw.numeroResultado), '/', RTRIM(vw.anoResultado)) AS acordao
    FROM processo.dbo.vw_ia_votos_acordaos_decisoes vw
    WHERE vw.IdProcesso = c.IdProcesso
      AND vw.IdComposicaoPauta = c.IdComposicaoPauta
      AND vw.idVotoPauta = c.IdVotoPauta
    ORDER BY vw.DataSessao DESC
) v
OUTER APPLY (
    -- trânsito POSTERIOR à decisão que fixou a determinação (é dele que corre o prazo)
    SELECT TOP 1 t.datatransito AS data_transito
    FROM processo.dbo.Processo_TransitoJulgado t
    WHERE RTRIM(t.numero_processo) = RTRIM(p.numero_processo)
      AND RTRIM(t.ano_processo) = RTRIM(p.ano_processo)
      AND (t.inativo = 0 OR t.inativo IS NULL)
      AND (v.DataSessao IS NULL OR t.datatransito >= v.DataSessao)
    ORDER BY t.datatransito ASC
) tj
OUTER APPLY (
    SELECT TOP 1 og.IdProcessoOriginario
    FROM processo.dbo.Obg_Obrigacao og
    WHERE og.IdProcessoOriginario = c.IdProcesso
) cgr
"""

_SUCESSO = "'EXATO', 'EXATO_POR_ORDEM', 'EXATO_PESSOA_VALOR', 'EXATO_LOTE', 'OK_TUDO', 'MATCH_MANUAL', 'REPASSE_VIA_ORGAO'"

VW_FRAP_LANCAMENTO = f"""
CREATE OR ALTER VIEW dbo.vwCCDFrapLancamento AS
WITH vinc AS (
    SELECT m.IdLancamento, 'GUIA' AS matcher, m.IdStatusMatch,
           m.IdDebito, m.IdBoleto, m.IdProcessoExecucao AS IdProcesso,
           m.CpfCnpj, m.NomePessoa, m.ValorPago AS valor, m.DataPagamento AS data_pagamento,
           CAST(NULL AS smallint) AS ob_ano_sigef, CAST(NULL AS varchar(20)) AS ob_numero,
           CAST(NULL AS nvarchar(200)) AS ob_credor, CAST(NULL AS int) AS ob_unidade_gestora,
           CAST(NULL AS bigint) AS df_id_plano, CAST(NULL AS int) AS df_numero_parcela,
           CAST(NULL AS int) AS df_competencia, CAST(NULL AS numeric(18, 2)) AS df_valor_contracheque,
           CAST(NULL AS bit) AS df_is_manual
    FROM dbo.FRAPMatchGuia m
    WHERE m.IdLancamento IS NOT NULL

    UNION ALL

    SELECT m.IdLancamento, 'PESSOA', m.IdStatusMatch,
           m.IdDebito, NULL, m.IdProcessoExecucao,
           m.CpfCnpj, m.NomePessoa, m.ValorPago, NULL,
           NULL, NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL
    FROM dbo.FRAPMatchPessoa m

    UNION ALL

    SELECT m.IdLancamento, 'OB', m.IdStatusMatch,
           NULL, NULL, NULL,
           m.CdCredor, m.NmCredor, m.ValorOB, m.DataPagamento,
           m.AnoSigef, m.NuOrdemBancaria, m.NmCredor, m.CdUnidadeGestora,
           NULL, NULL, NULL, NULL, NULL
    FROM dbo.FRAPMatchOB m
    WHERE m.IdLancamento IS NOT NULL

    UNION ALL

    SELECT m.IdLancamentoFRAP, 'DESCONTO_FOLHA', m.IdStatusMatch,
           df.IdDebito, NULL, df.IdProcesso,
           df.CpfCnpj, df.NomePessoa, p.ValorEsperado, p.DataPagamentoParcela,
           NULL, NULL, NULL, NULL,
           df.IdFRAPDescontoFolha, p.NumeroParcela,
           p.AnoReferencia * 100 + p.MesReferencia, m.ValorContracheque, m.IsManual
    FROM dbo.FRAPMatchDescontoFolha m
    JOIN dbo.FRAPDescontoFolhaParcela p ON p.IdFRAPDescontoFolhaParcela = m.IdFRAPDescontoFolhaParcela
    JOIN dbo.FRAPDescontoFolha df ON df.IdFRAPDescontoFolha = p.IdFRAPDescontoFolha
    WHERE m.IdLancamentoFRAP IS NOT NULL
)
SELECT
    l.IdLancamento                          AS id_lancamento,
    ct.Conta                                AS conta,
    l.Periodo                               AS periodo,
    RIGHT(l.Periodo, 4) + LEFT(l.Periodo, 2) AS competencia,
    l.DtMovimento                           AS dt_movimento,
    l.Historico                             AS historico,
    l.Documento                             AS documento,
    l.DocData                               AS doc_data,
    l.Valor                                 AS valor,
    l.ValorDC                               AS valor_dc,
    l.Descricao                             AS descricao,
    l.IdCategoria                           AS cod_categoria,
    cat.Codigo                              AS categoria,
    CAST(CASE WHEN l.ValorDC = 'C' AND l.IdCategoria IN (1, 2, 3, 9) THEN 1 ELSE 0 END AS bit) AS arrecadacao,
    l.CpfCnpjDepositante                    AS cpf_cnpj_depositante,
    CASE WHEN l.CpfCnpjDepositante IS NOT NULL THEN RIGHT(l.CpfCnpjDepositante, 11) END AS cpf_depositante,
    l.CpfCnpjAmbiguo                        AS cpf_cnpj_ambiguo,
    v.matcher                               AS matcher,
    st.Codigo                               AS status_match,
    CAST(CASE WHEN st.Codigo IN ({_SUCESSO}) THEN 1 ELSE 0 END AS bit) AS conciliado,
    v.IdDebito                              AS id_debito,
    v.IdBoleto                              AS id_boleto,
    v.IdProcesso                            AS id_processo,
    v.CpfCnpj                               AS cpf_cnpj_vinculo,
    v.NomePessoa                            AS nome_vinculo,
    v.valor                                 AS valor_vinculo,
    v.data_pagamento                        AS data_pagamento_vinculo,
    v.ob_ano_sigef, v.ob_numero, v.ob_credor, v.ob_unidade_gestora,
    v.df_id_plano, v.df_numero_parcela, v.df_competencia, v.df_valor_contracheque, v.df_is_manual
FROM dbo.FRAPLancamento l
JOIN dbo.FRAPConta ct ON ct.IdConta = l.IdConta
JOIN dbo.FRAPCategoria cat ON cat.IdCategoria = l.IdCategoria
LEFT JOIN vinc v ON v.IdLancamento = l.IdLancamento
LEFT JOIN dbo.FRAPStatusMatch st ON st.IdStatusMatch = v.IdStatusMatch
"""

VW_FRAP_DESCONTO_FOLHA = f"""
CREATE OR ALTER VIEW dbo.vwCCDFrapDescontoFolha AS
SELECT
    df.IdFRAPDescontoFolha                  AS id_plano,
    df.Origem                               AS origem,
    df.IdProcesso                           AS id_processo,
    RTRIM(pr.numero_processo) + '/' + RTRIM(pr.ano_processo) AS processo,
    df.IdDebito                             AS id_debito,
    df.IdParcelamento                       AS id_parcelamento,
    df.CpfCnpj                              AS cpf_cnpj,
    df.NomePessoa                           AS nome_pessoa,
    df.IdOrgaoNotificado                    AS id_orgao,
    df.NomeOrgaoNotificado                  AS nome_orgao,
    df.QtdParcelasPlanejadas                AS qtd_parcelas_planejadas,
    df.ValorTotalEsperado                   AS valor_total_esperado,
    RTRIM(df.SituacaoParcelamento)          AS situacao_parcelamento,
    df.Ativo                                AS plano_ativo,
    p.IdFRAPDescontoFolhaParcela            AS id_parcela,
    p.NumeroParcela                         AS numero_parcela,
    p.AnoReferencia * 100 + p.MesReferencia AS competencia,
    p.ValorEsperado                         AS valor_esperado,
    p.DataVencimento                        AS data_vencimento,
    p.DataPagamentoParcela                  AS data_pagamento_parcela,
    RTRIM(p.SituacaoParcela)                AS situacao_parcela,
    -- a mesma parcela aparece em planos-tranche sobrepostos: somar só rn_duplicata = 1
    ROW_NUMBER() OVER (PARTITION BY df.CpfCnpj, p.AnoReferencia, p.MesReferencia, p.ValorEsperado
                       ORDER BY p.IdFRAPDescontoFolhaParcela) AS rn_duplicata,
    st.Codigo                               AS status_match,
    CAST(CASE WHEN st.Codigo IN ({_SUCESSO}) THEN 1 ELSE 0 END AS bit) AS conciliado,
    m.ValorContracheque                     AS valor_contracheque,
    m.IsManual                              AS is_manual,
    m.Observacao                            AS observacao,
    m.IdLancamentoFRAP                      AS id_lancamento,
    l.DtMovimento                           AS lanc_dt_movimento,
    l.Valor                                 AS lanc_valor,
    l.Historico                             AS lanc_historico
FROM dbo.FRAPDescontoFolha df
JOIN dbo.FRAPDescontoFolhaParcela p ON p.IdFRAPDescontoFolha = df.IdFRAPDescontoFolha
LEFT JOIN processo.dbo.Processos pr ON pr.IdProcesso = df.IdProcesso
OUTER APPLY (
    SELECT TOP 1 x.IdStatusMatch, x.ValorContracheque, x.IsManual, x.Observacao, x.IdLancamentoFRAP
    FROM dbo.FRAPMatchDescontoFolha x
    WHERE x.IdFRAPDescontoFolhaParcela = p.IdFRAPDescontoFolhaParcela
    ORDER BY x.IsManual DESC, x.DataCalculo DESC
) m
LEFT JOIN dbo.FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
LEFT JOIN dbo.FRAPLancamento l ON l.IdLancamento = m.IdLancamentoFRAP
"""

VIEWS = {
    "vwCCDDebito": VW_DEBITO,
    "vwCCDDebitoResponsavel": VW_DEBITO_RESPONSAVEL,
    "vwCCDDeterminacao": VW_DETERMINACAO,
    "vwCCDFrapLancamento": VW_FRAP_LANCAMENTO,
    "vwCCDFrapDescontoFolha": VW_FRAP_DESCONTO_FOLHA,
}


def upgrade() -> None:
    for ddl in VIEWS.values():
        op.execute(ddl)


def downgrade() -> None:
    for name in VIEWS:
        op.execute(f"IF OBJECT_ID('dbo.{name}', 'V') IS NOT NULL DROP VIEW dbo.{name};")
