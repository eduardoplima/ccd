"""Match de parcelas de desconto folha contra contracheque (Nível A) e crédito FRAP (Nível B).

Regra:
  - **Nível A**: para cada parcela esperada (CpfCnpj, MesReferencia, AnoReferencia,
    ValorEsperado), achar item no contracheque do mesmo CPF/mês/ano com rubrica TCE
    cuja `Valor` bate (tolerância de meio centavo).
  - **Nível B**: agrupar parcelas confirmadas (com item de contracheque) por
    (mes, ano) e procurar `FRAPLancamento` com categoria=OB_RECEBIDA cujo
    `valor` ≈ soma do lote, dentro da janela `[primeiro_dia_mes_ref,
    ultimo_dia_mes_ref + janela_dias]`. A janela começa no início do mês para
    capturar prepagamentos (órgão deposita no decorrer do mês, antes de a folha
    fechar). Reusa a estratégia closest-first / dpag-consumida do matcher de guia.

Status de saída (1 linha por parcela):
  - OK_TUDO              — Nível A casa + Nível B casa + parcela já baixada (Exe_Parcela.SituacaoParcela='2')
  - DESCONTADA_SEM_REPASSE — Nível A casa, Nível B falha
  - REPASSADA_SEM_DESCONTO — Nível A falha (sem item) mas há FRAPLancamento "candidato" com sobra do lote
  - REPASSE_VIA_ORGAO    — Nível C: parcela NAO_DESCONTADA casada com lançamento via inferência de órgão depositante
  - PARCELA_AGUARDANDO    — vencimento futuro (DataVencimento > hoje)
  - NAO_DESCONTADA        — passou o mês esperado, sem item no contracheque
  - BAIXADA_SEM_RASTRO    — parcela com `TipoDeBaixa=2` (Manual) e `DataPagamentoParcela` mas A e B falham
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum

import pandas as pd


class StatusDescontoFolha(StrEnum):
    OK_TUDO = "OK_TUDO"
    DESCONTADA_SEM_REPASSE = "DESCONTADA_SEM_REPASSE"
    REPASSADA_SEM_DESCONTO = "REPASSADA_SEM_DESCONTO"
    REPASSE_VIA_ORGAO = "REPASSE_VIA_ORGAO"
    PARCELA_AGUARDANDO = "PARCELA_AGUARDANDO"
    NAO_DESCONTADA = "NAO_DESCONTADA"
    BAIXADA_SEM_RASTRO = "BAIXADA_SEM_RASTRO"


_TOL = 0.005


def match_desconto_folha(
    parcelas_df: pd.DataFrame,
    contracheques_df: pd.DataFrame,
    lancamentos_frap_df: pd.DataFrame,
    janela_dias: int = 31,
    hoje: date | None = None,
    *,
    orgaos_por_lancamento: dict[int, set[int]] | None = None,
) -> pd.DataFrame:
    """Concilia parcelas com contracheque e crédito FRAP.

    `parcelas_df` precisa ter: CpfCnpj, MesReferencia, AnoReferencia, ValorEsperado,
                               DataVencimentoParcela, SituacaoParcela, TipoDeBaixa,
                               DataPagamentoParcela, IdFRAPDescontoFolhaParcela (chave),
                               IdOrgaoNotificado (opcional, para Nível B').
    `contracheques_df` precisa ter: CPF, MesReferencia, AnoReferencia, Valor,
                                    IdContraChequeItem, IdRubrica.
    `lancamentos_frap_df` precisa ter: IdLancamento, DtMovimento, Valor, Categoria.

    **Nível B' (opcional)**: `orgaos_por_lancamento` é um mapa pré-computado
    `IdLancamento -> set[IdOrgao]` que diz, para cada lançamento, quais órgãos
    podem ser pagadores reais. Construído tipicamente combinando:

      - CNPJ do depositante ∈ lista de CNPJs do Estado-RN → expande para os órgãos
        com IdOrgaoSuperior = 272.
      - Inferência fuzzy de `Historico`/`Descricao` (ver `inferencia_orgao.py`):
        "PREF MUN ALTO RODRIGUES" → IdOrgao da Prefeitura; "ESTADO DO RIO GRANDE"
        → órgãos subordinados ao Estado.

    Para parcelas com status NAO_DESCONTADA cujo IdOrgaoNotificado aparece em
    `orgaos_por_lancamento[idLancamento]`, tenta match individual por valor +
    janela `[primeiro_dia_mes_ref, ultimo_dia_mes_ref + janela_dias]`. Sucesso →
    REPASSE_VIA_ORGAO.

    Retorna 1 linha por parcela com colunas: IdFRAPDescontoFolhaParcela,
    IdContraChequeItem, IdRubrica, ValorContracheque, IdLancamentoFRAP, status_match.
    """
    hoje = hoje or date.today()
    parcelas = parcelas_df.copy()
    if parcelas.empty:
        return pd.DataFrame(
            columns=[
                "IdFRAPDescontoFolhaParcela",
                "IdContraChequeItem",
                "IdRubrica",
                "ValorContracheque",
                "IdLancamentoFRAP",
                "status_match",
            ]
        )

    # ---------- Nível A: parcela × contracheque ----------
    contra = contracheques_df.copy()
    if not contra.empty:
        contra["CPF"] = contra["CPF"].astype(str).str.zfill(11)
        contra["valor_cent"] = (contra["Valor"].astype(float) * 100).round().astype("Int64")
        # Deduplicar (servidor pode ter mesmo item em folhas distintas no mesmo mês —
        # complementar/13º/extra). Fica com o IdContraChequeItem de menor id.
        contra = contra.sort_values("IdContraChequeItem").drop_duplicates(
            subset=["CPF", "MesReferencia", "AnoReferencia", "valor_cent"], keep="first"
        )

    parcelas["CpfCnpj"] = parcelas["CpfCnpj"].astype(str).str.zfill(11)
    parcelas["valor_cent"] = (parcelas["ValorEsperado"].astype(float) * 100).round().astype("Int64")

    if not contra.empty:
        merged_a = parcelas.merge(
            contra[
                [
                    "CPF",
                    "MesReferencia",
                    "AnoReferencia",
                    "valor_cent",
                    "IdContraChequeItem",
                    "IdRubrica",
                    "Valor",
                ]
            ].rename(columns={"Valor": "ValorContracheque"}),
            how="left",
            left_on=["CpfCnpj", "MesReferencia", "AnoReferencia", "valor_cent"],
            right_on=["CPF", "MesReferencia", "AnoReferencia", "valor_cent"],
        )
        merged_a = merged_a.drop(columns=["CPF"], errors="ignore")
    else:
        merged_a = parcelas.copy()
        merged_a["IdContraChequeItem"] = pd.NA
        merged_a["IdRubrica"] = pd.NA
        merged_a["ValorContracheque"] = pd.NA

    merged_a["__casou_contracheque"] = merged_a["IdContraChequeItem"].notna()

    # ---------- Nível B: lote (mes, ano) × FRAPLancamento ----------
    fr = lancamentos_frap_df.copy() if lancamentos_frap_df is not None else pd.DataFrame()
    if not fr.empty:
        cat_col = (
            "Categoria"
            if "Categoria" in fr.columns
            else ("categoria" if "categoria" in fr.columns else None)
        )
        if cat_col is not None:
            fr = fr[fr[cat_col].astype(str).isin(("OB_RECEBIDA", "TRANSFERENCIA"))].copy()
        dt_col = "DtMovimento" if "DtMovimento" in fr.columns else "dt_movimento"
        fr["DtMovimento"] = pd.to_datetime(fr[dt_col]).dt.normalize()
        valor_col = "Valor" if "Valor" in fr.columns else "valor"
        fr["Valor"] = pd.to_numeric(fr[valor_col], errors="coerce")

    confirmadas = merged_a[merged_a["__casou_contracheque"]].copy()
    lote_para_lanc: dict[tuple[int, int], int | None] = {}
    if not confirmadas.empty and not fr.empty:
        somas = confirmadas.groupby(["MesReferencia", "AnoReferencia"])["ValorContracheque"].sum()
        lanc_consumido: set = set()
        for (mes, ano), soma in somas.items():
            soma = float(soma)
            primeiro_dia = pd.Timestamp(date(int(ano), int(mes), 1))
            ultimo_dia = primeiro_dia + pd.offsets.MonthEnd(0)
            limite = ultimo_dia + pd.Timedelta(days=janela_dias)
            cand = fr[
                (fr["DtMovimento"] >= primeiro_dia)
                & (fr["DtMovimento"] <= limite)
                & ((fr["Valor"] - soma).abs() < _TOL)
                & (~fr["IdLancamento"].isin(lanc_consumido))
            ].sort_values("DtMovimento")
            escolhido = int(cand.iloc[0]["IdLancamento"]) if not cand.empty else None
            if escolhido is not None:
                lanc_consumido.add(escolhido)
            lote_para_lanc[(int(mes), int(ano))] = escolhido

    def _lanc_para_parcela(row):
        if not row["__casou_contracheque"]:
            return None
        return lote_para_lanc.get((int(row["MesReferencia"]), int(row["AnoReferencia"])))

    merged_a["IdLancamentoFRAP"] = merged_a.apply(_lanc_para_parcela, axis=1)

    # ---------- Status final ----------
    def _status(row) -> str:
        casou_cc = bool(row["__casou_contracheque"])
        casou_fr = pd.notna(row["IdLancamentoFRAP"])
        venc = pd.to_datetime(row.get("DataVencimentoParcela"), errors="coerce")
        sit = str(row.get("SituacaoParcela") or "").strip()
        tipo_baixa = row.get("TipoDeBaixa")

        if casou_cc and casou_fr:
            return StatusDescontoFolha.OK_TUDO.value
        if casou_cc and not casou_fr:
            return StatusDescontoFolha.DESCONTADA_SEM_REPASSE.value
        if not casou_cc and casou_fr:
            return StatusDescontoFolha.REPASSADA_SEM_DESCONTO.value
        # nenhum dos dois casou
        if pd.notna(venc) and venc.date() > hoje:
            return StatusDescontoFolha.PARCELA_AGUARDANDO.value
        if sit == "2" and pd.notna(row.get("DataPagamentoParcela")) and tipo_baixa == 2:
            return StatusDescontoFolha.BAIXADA_SEM_RASTRO.value
        return StatusDescontoFolha.NAO_DESCONTADA.value

    merged_a["status_match"] = merged_a.apply(_status, axis=1)

    # ---------- Nível B' (opcional, aditivo) ----------
    # Cobre dois cenários onde Nível B (soma do lote) falha mas existe crédito
    # individual por órgão:
    #   - NAO_DESCONTADA: parcela sem contracheque, prefeitura pagou direto.
    #   - DESCONTADA_SEM_REPASSE: parcela com contracheque, mas a soma da folha do
    #     mês não bate com um único FRAPLancamento (típico quando múltiplas
    #     prefeituras repassam separadamente, cada uma pelo valor exato da parcela).
    # Match individual por (valor exato + órgão inferido + janela).
    if (
        orgaos_por_lancamento
        and "IdOrgaoNotificado" in merged_a.columns
        and not fr.empty
        and "IdLancamentoFRAP" in merged_a.columns
    ):
        fr_b_linha = fr.copy()
        fr_b_linha["valor_cent"] = (fr_b_linha["Valor"].astype(float) * 100).round().astype("Int64")
        # adiciona coluna com set de orgãos inferidos
        fr_b_linha["__orgaos_inf"] = fr_b_linha["IdLancamento"].map(
            lambda i: orgaos_por_lancamento.get(int(i), set())
        )
        # só lançamentos com inferência não-vazia
        fr_b_linha = fr_b_linha[fr_b_linha["__orgaos_inf"].map(bool)].copy()
        if not fr_b_linha.empty:
            # Evita reuso de lançamentos já consumidos pelo Nível B (soma do lote).
            consumidos: set[int] = {
                int(v) for v in merged_a["IdLancamentoFRAP"].dropna().tolist()
            }
            alvos = (
                StatusDescontoFolha.NAO_DESCONTADA.value,
                StatusDescontoFolha.DESCONTADA_SEM_REPASSE.value,
            )
            for idx, row in merged_a.iterrows():
                status_atual = str(row["status_match"])
                if status_atual not in alvos:
                    continue
                id_org = row.get("IdOrgaoNotificado")
                if id_org is None or pd.isna(id_org):
                    continue
                id_org_int = int(id_org)
                mes_p = int(row["MesReferencia"])
                ano_p = int(row["AnoReferencia"])
                primeiro_dia = pd.Timestamp(date(ano_p, mes_p, 1))
                ultimo_dia = primeiro_dia + pd.offsets.MonthEnd(0)
                limite = ultimo_dia + pd.Timedelta(days=janela_dias)
                valor_cent = int(row["valor_cent"])
                cand = fr_b_linha[
                    (fr_b_linha["DtMovimento"] >= primeiro_dia)
                    & (fr_b_linha["DtMovimento"] <= limite)
                    & (fr_b_linha["valor_cent"] == valor_cent)
                    & (~fr_b_linha["IdLancamento"].isin(consumidos))
                    & (fr_b_linha["__orgaos_inf"].map(lambda s: id_org_int in s))
                ].sort_values("DtMovimento")
                if cand.empty:
                    continue
                escolhido = int(cand.iloc[0]["IdLancamento"])
                consumidos.add(escolhido)
                merged_a.at[idx, "IdLancamentoFRAP"] = escolhido
                # Se já tinha contracheque (DESCONTADA_SEM_REPASSE), agora vira OK_TUDO;
                # senão, marca como REPASSE_VIA_ORGAO (parcela sem contracheque).
                if status_atual == StatusDescontoFolha.DESCONTADA_SEM_REPASSE.value:
                    merged_a.at[idx, "status_match"] = StatusDescontoFolha.OK_TUDO.value
                else:
                    merged_a.at[idx, "status_match"] = StatusDescontoFolha.REPASSE_VIA_ORGAO.value

    cols = [
        "IdFRAPDescontoFolhaParcela",
        "IdContraChequeItem",
        "IdRubrica",
        "ValorContracheque",
        "IdLancamentoFRAP",
        "status_match",
    ]
    return merged_a[cols].copy()
