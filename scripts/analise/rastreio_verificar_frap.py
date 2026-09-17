"""Rastreia os processos da CCD que precisam verificar valores depositados no FRAP.

Um processo entra no rastreio por dois sinais (união):
  - marcador  : marcador ativo da família "DESCONTO EM FOLHA" (ciclo
                Implementar -> Verificar transferência FRAP (5953) -> Fim/Finalizado);
  - notificacao: informação de notificação de desconto em folha seguida de
                resposta/AR vinda da Diretoria de Expediente (caso do 000068/2026,
                eventos 73/74 = retorno da SEAD, sem marcador nenhum).

Para cada processo cruza, pelo CPF do responsável pelo débito de multa vigente:
  - descontos reais    <- BdSIAIPessoal SiaiDp_ContraChequeItem (rubrica TCE/FRAP);
  - repasses ao FRAP   <- BdDIP.FRAPLancamento (OB_RECEBIDA/TRANSFERENCIA, crédito,
                          casado por CpfCnpjDepositante);
  - plano cadastrado   <- BdDIP.FRAPDescontoFolha(Parcela).

Saída:  saidas/analise/rastreio_verificar_frap.xlsx (abas resumo / descontos / repasses)
        + no console, a lista de processos que devem receber o marcador 5953.

Limites: contracheque cobre só folhas ingeridas no SIAI DP (folha municipal pode não
ter rastro); repasse via órgão sem CPF do responsável cai em "sem repasse identificado"
e pede conferência manual (o casamento fino existe em
scripts/docs/match_desconto_folha_standalone.py).
"""

import re

import pandas as pd

from ccd.config import REPO_ROOT
from ccd.db import get_connection, run_query_df

OUT = REPO_ROOT / "saidas" / "analise" / "rastreio_verificar_frap.xlsx"

# Família "DESCONTO EM FOLHA" em Pro_Marcador (IdSetor 762 = CCD):
# 5021 Implementar | 5022 Implementar Nereu | 5469 Acompanhamento Nereu
# 5684 ACOMPANHAMENTO | 5907 Finalizado | 5953 Verificar transferência FRAP
# 5963 sem resposta | 5967 sem resposta enviar para MPC | 6116 Despacho - Execução
# 6170-6174 Fim ago/set, out a dez, 2027, 2028..., julho
MARCADORES_FAMILIA = (5021, 5022, 5469, 5684, 5907, 5953, 5963, 5967, 6116,
                      6170, 6171, 6172, 6173, 6174)
MARCADOR_VERIFICAR_FRAP = 5953
MARCADORES_POS_VERIFICACAO = {5684, 5907, 6170, 6171, 6172, 6173, 6174}

# Sai do rastreio quem está suspenso/parado por outro motivo (subconjunto dos
# MARCADORES_PERMANENCIA de scripts/analise/instrucao_ccd.py, sem os de
# acompanhamento de desconto em folha) + 6139 Nereu - substituir informação
# (fluxo próprio das informações nereu_ms, não é verificação de FRAP).
MARCADORES_EXCLUSAO = (5032, 5846, 5591, 5966, 5020, 6127, 5790,
                       5593, 5712, 5797, 5040, 5041, 6139)

# Exe_TipoDebito: 2 Multa, 4 Multa Percentual, 5 Multa Cominatória
# (1 Ressarcimento não passa pelo FRAP)
TIPOS_MULTA = "(2, 4, 5)"

SQL_UNIVERSO = f"""
WITH marcados AS (
    SELECT mp.IdProcesso, m.IdMarcador, RTRIM(m.Descricao) AS marcador
    FROM Pro_MarcadorProcesso mp
    JOIN Pro_Marcador m ON m.IdMarcador = mp.IdMarcador
    WHERE mp.DataExclusao IS NULL
      AND m.IdMarcador IN {tuple(MARCADORES_FAMILIA)}
), notif AS (
    -- notificação de desconto em folha (à SEAD ou via mandado), não quotas/despachos
    SELECT numero_processo, ano_processo, MIN(data_resumo) AS dt_notif
    FROM vw_ata_informacao
    WHERE (nome_informacao LIKE :df OR resumo LIKE :df)
      AND (nome_informacao LIKE :notif OR resumo LIKE :notif)
    GROUP BY numero_processo, ano_processo
), resp AS (
    -- resposta posterior vinda da Diretoria de Expediente (nomes variam:
    -- Resposta à Comunicação, AR digitalizado, volume digitalizado)
    SELECT n.numero_processo, n.ano_processo, MAX(v.data_resumo) AS dt_resposta
    FROM notif n
    JOIN vw_ata_informacao v
      ON v.numero_processo = n.numero_processo AND v.ano_processo = n.ano_processo
    WHERE v.data_resumo > n.dt_notif
      AND LTRIM(RTRIM(v.setor)) IN ('DE', 'DE_MANDA', 'DE_EXP')
      AND (v.resumo LIKE '%resposta%' OR v.nome_informacao LIKE '%AR_Digitalizado%')
    GROUP BY n.numero_processo, n.ano_processo
), excluidos AS (
    SELECT DISTINCT mp.IdProcesso
    FROM Pro_MarcadorProcesso mp
    WHERE mp.DataExclusao IS NULL
      AND mp.IdMarcador IN {tuple(MARCADORES_EXCLUSAO)}
)
SELECT p.IdProcesso,
       RTRIM(p.numero_processo) + '/' + RTRIM(p.ano_processo) AS processo,
       mc.IdMarcador, mc.marcador, r.dt_resposta
FROM Processos p
LEFT JOIN marcados mc ON mc.IdProcesso = p.IdProcesso
LEFT JOIN resp r ON r.numero_processo = p.numero_processo
              AND r.ano_processo = p.ano_processo
WHERE RTRIM(p.setor_atual) = 'CCD' AND p.IdProcessoApensador IS NULL
  AND (mc.IdProcesso IS NOT NULL OR r.numero_processo IS NOT NULL)
  AND NOT EXISTS (SELECT 1 FROM excluidos e WHERE e.IdProcesso = p.IdProcesso)
"""

# Débito de multa vigente ligado ao processo pelos DOIS papéis, nunca COALESCE.
SQL_DEBITOS = f"""
SELECT pr.IdProcesso, d.IdDebito, d.CodigoTipoDebito,
       RTRIM(sd.DescricaoStatusDivida) AS situacao,
       processo.dbo.fn_Exe_RetornaValorAtualizado(d.IdDebito) AS valor_atual,
       RTRIM(gp.Nome) AS responsavel, gp.Documento AS documento
FROM Exe_Debito d
JOIN Exe_StatusDivida sd ON sd.CodigoStatusDivida = d.CodigoStatusDivida
JOIN Processos pr ON pr.IdProcesso IN (d.IdProcessoExecucao, d.IdProcessoOrigem)
JOIN Exe_DebitoPessoa dp ON dp.IDDebito = d.IdDebito
JOIN GenPessoa gp ON gp.IdPessoa = dp.IDPessoa
WHERE sd.StatusCancelamento IS NULL
  AND d.CodigoTipoDebito IN {TIPOS_MULTA}
  AND pr.IdProcesso IN ({{ids}})
"""

SQL_CONTRACHEQUE = """
SELECT P.CPF, CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT) AS Ano,
       CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT) AS Mes, CCI.Valor,
       MIN(R.Codigo) AS RubricaCodigo, COUNT(*) AS folhas
FROM dbo.SiaiDp_ContraChequeItem CCI
JOIN dbo.SiaiDp_Rubrica R ON R.IdRubrica = CCI.IdRubrica
JOIN dbo.SiaiDp_ContraCheque CC ON CC.IdContraCheque = CCI.IdContraCheque
LEFT JOIN dbo.SiaiDp_Funcionario FU ON FU.IdFuncionario = CC.IdFuncionario
LEFT JOIN dbo.Comum_Pessoa P ON P.IdPessoa = FU.IdPessoa
WHERE P.CPF IN ({cpfs}) AND R.Tipo = '2'
  AND (UPPER(R.Descricao) LIKE '%TCE%' OR UPPER(R.Descricao) LIKE '%TRIBUNAL DE CONTAS%'
       OR UPPER(R.Descricao) LIKE '%FRAP%')
GROUP BY P.CPF, CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT),
         CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT), CCI.Valor
"""

# CpfCnpjDepositante é NULL em ~98% dos lançamentos e, quando vem, pode ter
# zeros à esquerda — o RIGHT(,11) casa os CPFs preenchidos; o casamento fino
# extrato x parcela é o match_desconto_folha_standalone, não este rastreio.
SQL_REPASSES = """
SELECT RIGHT(L.CpfCnpjDepositante, 11) AS CPF, L.DtMovimento, L.Valor, L.Documento,
       cat.Codigo AS Categoria, c.Conta
FROM dbo.FRAPLancamento L
JOIN dbo.FRAPCategoria cat ON cat.IdCategoria = L.IdCategoria
JOIN dbo.FRAPConta c ON c.IdConta = L.IdConta
WHERE cat.Codigo IN ('OB_RECEBIDA', 'TRANSFERENCIA') AND L.ValorDC = 'C'
  AND RIGHT(L.CpfCnpjDepositante, 11) IN ({cpfs})
"""

SQL_PLANOS = """
SELECT DF.CpfCnpj AS CPF, COUNT(*) AS parcelas_cadastradas,
       SUM(CASE WHEN P.DataPagamentoParcela IS NOT NULL THEN 1 ELSE 0 END) AS parcelas_pagas
FROM dbo.FRAPDescontoFolha DF
JOIN dbo.FRAPDescontoFolhaParcela P ON P.IdFRAPDescontoFolha = DF.IdFRAPDescontoFolha
WHERE DF.Ativo = 1 AND DF.CpfCnpj IN ({cpfs})
GROUP BY DF.CpfCnpj
"""


def _cpf(doc: object) -> str | None:
    """Só dígitos; devolve CPF de 11 posições ou None (CNPJ/vazio)."""
    d = re.sub(r"\D", "", str(doc or ""))
    return d.zfill(11) if 0 < len(d) <= 11 else None


def _in_list(cpfs: set[str]) -> str:
    assert all(re.fullmatch(r"\d{11}", c) for c in cpfs)
    return ", ".join(f"'{c}'" for c in sorted(cpfs))


def acao(row: pd.Series) -> str:
    if row.IdMarcador == MARCADOR_VERIFICAR_FRAP:
        return "na fila 5953 - verificar transferência"
    if row.IdMarcador in MARCADORES_POS_VERIFICACAO:
        return "acompanhamento até o fim do plano"
    if pd.notna(row.IdMarcador):  # Implementar/sem resposta/Despacho: ciclo próprio
        return ("atualizar marcador (desconto no contracheque?)"
                if row.total_descontado > 0 else "aguardando implementação")
    # sem marcador nenhum da família — o caso do 000068/2026
    if row.total_descontado > 0 or pd.notna(row.dt_resposta):
        return "APLICAR MARCADOR 5953"
    return "aguardando implementação"


def main() -> None:
    eng = get_connection("processo")

    uni = run_query_df(SQL_UNIVERSO, eng, df="%desconto%folha%", notif="%notifica%")
    uni["sinal"] = uni.apply(
        lambda r: "+".join(
            s for s, ok in (("marcador", pd.notna(r.IdMarcador)),
                            ("notificacao", pd.notna(r.dt_resposta))) if ok),
        axis=1,
    )
    assert not uni.processo.duplicated().any(), "processo com mais de um marcador ativo da família"

    ids = ", ".join(str(i) for i in uni.IdProcesso)
    deb = run_query_df(SQL_DEBITOS.format(ids=ids), eng)
    deb["cpf"] = deb.documento.map(_cpf)

    cpfs = set(deb.cpf.dropna())
    engp = get_connection("BdSIAIPessoal")
    engd = get_connection("BdDIP")
    cc = run_query_df(SQL_CONTRACHEQUE.format(cpfs=_in_list(cpfs)), engp)
    rep = run_query_df(SQL_REPASSES.format(cpfs=_in_list(cpfs)), engd)
    planos = run_query_df(SQL_PLANOS.format(cpfs=_in_list(cpfs)), engd)

    por_proc = (
        deb.groupby("IdProcesso")
        .agg(
            responsaveis=("responsavel", lambda s: "; ".join(sorted(set(s)))),
            cpfs=("cpf", lambda s: sorted(set(s.dropna()))),
            debitos=("IdDebito", lambda s: ", ".join(map(str, sorted(set(s))))),
            valor_atualizado=("valor_atual", lambda s: round(float(s.sum()), 2)),
        )
        .reset_index()
    )
    resumo = uni.merge(por_proc, on="IdProcesso", how="left")
    resumo["cpfs"] = resumo.cpfs.apply(lambda v: v if isinstance(v, list) else [])

    cc_por_cpf = cc.groupby("CPF").Valor.agg(["sum", "count"]).astype(float)
    rep_por_cpf = rep.groupby("CPF").Valor.sum().astype(float)
    planos_por_cpf = planos.set_index("CPF").parcelas_cadastradas.astype(float)
    pagas_por_cpf = planos.set_index("CPF").parcelas_pagas.astype(float)

    def soma(serie: pd.Series, cpfs: list[str]) -> float:
        return round(float(serie.reindex(cpfs).dropna().sum()), 2)

    resumo["meses_descontados"] = resumo.cpfs.apply(
        lambda c: int(cc_por_cpf["count"].reindex(c).fillna(0).sum()))
    resumo["total_descontado"] = resumo.cpfs.apply(lambda c: soma(cc_por_cpf["sum"], c))
    resumo["total_repassado_frap"] = resumo.cpfs.apply(lambda c: soma(rep_por_cpf, c))
    resumo["parcelas_cadastradas"] = resumo.cpfs.apply(
        lambda c: int(planos_por_cpf.reindex(c).fillna(0).sum()))
    resumo["parcelas_pagas"] = resumo.cpfs.apply(
        lambda c: int(pagas_por_cpf.reindex(c).fillna(0).sum()))

    def status(r: pd.Series) -> str:
        if not r.cpfs:
            return "SEM_RESPONSAVEL_PF"
        if r.total_descontado > 0:
            tem_repasse = r.total_repassado_frap > 0 or r.parcelas_pagas > 0
            return ("DESCONTO_CONFIRMADO_COM_REPASSE" if tem_repasse
                    else "DESCONTO_SEM_REPASSE_IDENTIFICADO")
        return "SEM_DESCONTO_NO_CONTRACHEQUE"

    resumo["status"] = resumo.apply(status, axis=1)
    resumo["acao_sugerida"] = resumo.apply(acao, axis=1)
    resumo["cpfs"] = resumo.cpfs.apply(", ".join)
    resumo = resumo.sort_values(["acao_sugerida", "processo"]).drop(columns="IdProcesso")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cpf_proc = deb.dropna(subset=["cpf"]).groupby("cpf").IdProcesso.first()
    id_proc = uni.set_index("IdProcesso").processo
    for det in (cc, rep):
        det.insert(0, "processo", det.CPF.map(cpf_proc).map(id_proc))
    with pd.ExcelWriter(OUT, engine="openpyxl") as w:
        resumo.to_excel(w, sheet_name="resumo", index=False)
        cc.sort_values(["processo", "Ano", "Mes"]).to_excel(w, sheet_name="descontos", index=False)
        rep.sort_values(["processo", "DtMovimento"]).to_excel(w, sheet_name="repasses", index=False)

    assert (resumo.status != "").all() and resumo.status.notna().all()
    print(f"{OUT}: {len(resumo)} processos no rastreio")
    print(resumo.groupby(["status", "acao_sugerida"]).size().to_string(), "\n")
    marcar = resumo[resumo.acao_sugerida == "APLICAR MARCADOR 5953"]
    print(f"Aplicar marcador 5953 (DESCONTO EM FOLHA - Verificar transferência FRAP) "
          f"em {len(marcar)} processos:")
    cols = ["processo", "marcador", "sinal", "responsaveis", "status", "total_descontado"]
    print(marcar[cols].to_string(index=False))


if __name__ == "__main__":
    main()
