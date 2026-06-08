"""Entry-point da CLI `frap`."""

from __future__ import annotations

import calendar
from datetime import date
from pathlib import Path

import click
import pandas as pd
from sqlalchemy import text

from frap.ccd import scan_notificacoes as ccd_scan_mod
from frap.config import (
    ANOS_SIGEF,
    BANCO_DIP,
    BANCO_PROCESSO,
    BANCO_SIAIPESSOAL,
    ID_ORGAO_SUPERIOR_ESTADO,
    banco_sigef,
    build_engine,
    cnpjs_estado_rn,
)
from frap.extratos import ingest
from frap.matching import descontofolha as match_descontofolha_mod
from frap.matching import guia as match_guia_mod
from frap.matching import inferencia_orgao as inferencia_orgao_mod
from frap.matching import ob as match_ob_mod
from frap.matching import pessoa as match_pessoa_mod
from frap.matching import relatorio as relatorio_mod
from frap.persistencia import descontofolha as persistencia_descontofolha
from frap.persistencia import descontos_extras as persistencia_descontos_extras
from frap.persistencia import extrato as persistencia_extrato
from frap.persistencia import matches as persistencia_matches
from frap.persistencia import metrica_pessoa as persistencia_metrica_pessoa
from frap.persistencia import planilha_monitoramento as planilha_mod
from frap.processo import repos as processo_repos
from frap.siaipessoal import repos as siaipessoal_repos
from frap.sigef import repos as sigef_repos


@click.group()
def cli() -> None:
    """Conciliação das contas FRAP do TCE/RN."""


@cli.command("parse-extratos")
@click.option(
    "--pasta",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path("docs/extratos_frap"),
    show_default=True,
    help="Pasta com subpastas por conta (cada uma contendo MMYYYY.txt).",
)
@click.option(
    "--out",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/interim"),
    show_default=True,
    help="Diretório destino do parquet canônico.",
)
def parse_extratos_cmd(pasta: Path, out: Path) -> None:
    """Lê extratos MMYYYY.txt e gera extrato_canonico.parquet."""
    df = ingest.ingest_pasta(pasta)
    if df.empty:
        click.echo(f"Nenhum extrato encontrado em {pasta}", err=True)
        raise SystemExit(1)
    out.mkdir(parents=True, exist_ok=True)
    destino = out / "extrato_canonico.parquet"
    df.to_parquet(destino, index=False)
    click.echo(f"{len(df)} lancamentos x {df['conta'].nunique()} contas -> {destino}")


@cli.command("conciliar-ob")
@click.option(
    "--ano", type=int, required=True, help="Ano do extrato (e do banco SIGEF correspondente)."
)
@click.option(
    "--mes", type=click.IntRange(1, 12), default=None, help="Mês (1-12); padrão = ano todo."
)
@click.option(
    "--extrato",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("data/interim/extrato_canonico.parquet"),
    show_default=True,
)
@click.option(
    "--out",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/processed"),
    show_default=True,
)
def conciliar_ob_cmd(ano: int, mes: int | None, extrato: Path, out: Path) -> None:
    """Cruza créditos OB_RECEBIDA do extrato com OBs do SIGEF (credor=FRAP)."""
    df_extrato = pd.read_parquet(extrato)
    inicio, fim = _intervalo(ano, mes)
    df_extrato = df_extrato[
        (df_extrato["doc_data"] >= pd.Timestamp(inicio))
        & (df_extrato["doc_data"] <= pd.Timestamp(fim))
    ]

    if ano in ANOS_SIGEF:
        engine = build_engine(banco_sigef(ano))
        df_sigef = sigef_repos.ob_para_frap_periodo(engine, inicio, fim)
    else:
        df_sigef = pd.DataFrame()

    resultado = match_ob_mod.match_ob(df_extrato, df_sigef, ano)

    out.mkdir(parents=True, exist_ok=True)
    sufixo = f"{ano}" if mes is None else f"{ano}-{mes:02d}"
    destino = out / f"match_ob_{sufixo}.parquet"
    resultado.to_parquet(destino, index=False)

    contagem = resultado["status_match"].value_counts().to_dict()
    click.echo(f"{len(resultado)} linhas -> {destino}")
    click.echo(f"  status: {contagem}")


def _intervalo(ano: int, mes: int | None) -> tuple[date, date]:
    if mes is None:
        return date(ano, 1, 1), date(ano, 12, 31)
    ultimo = calendar.monthrange(ano, mes)[1]
    return date(ano, mes, 1), date(ano, mes, ultimo)


@cli.command("conciliar-pessoa")
@click.option("--ano", type=int, required=True)
@click.option("--mes", type=click.IntRange(1, 12), default=None)
@click.option(
    "--extrato",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("data/interim/extrato_canonico.parquet"),
    show_default=True,
)
@click.option(
    "--out",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/processed"),
    show_default=True,
)
def conciliar_pessoa_cmd(ano: int, mes: int | None, extrato: Path, out: Path) -> None:
    """Cruza créditos com cpfcnpj_depositante contra Exe_Debito via GenPessoa."""
    df_extrato = pd.read_parquet(extrato)
    inicio, fim = _intervalo(ano, mes)
    janela = (df_extrato["dt_movimento"] >= pd.Timestamp(inicio)) & (
        df_extrato["dt_movimento"] <= pd.Timestamp(fim)
    )
    df_extrato = df_extrato[janela]

    docs = (
        df_extrato.loc[df_extrato["cpfcnpj_depositante"].notna(), "cpfcnpj_depositante"]
        .astype(str)
        .unique()
        .tolist()
    )
    if not docs:
        df_debitos = pd.DataFrame()
    else:
        engine = build_engine(BANCO_PROCESSO)
        df_debitos = processo_repos.debitos_por_pessoas(engine, docs, anos=(ano,))

    resultado = match_pessoa_mod.match_pessoa(df_extrato, df_debitos)

    out.mkdir(parents=True, exist_ok=True)
    sufixo = f"{ano}" if mes is None else f"{ano}-{mes:02d}"
    destino = out / f"match_pessoa_{sufixo}.parquet"
    resultado.to_parquet(destino, index=False)

    contagem = resultado["status_match"].value_counts().to_dict()
    click.echo(f"{len(resultado)} linhas -> {destino}")
    click.echo(f"  status: {contagem}")


@cli.command("conciliar-guia")
@click.option("--ano", type=int, required=True)
@click.option("--mes", type=click.IntRange(1, 12), default=None)
@click.option(
    "--extrato",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("data/interim/extrato_canonico.parquet"),
    show_default=True,
)
@click.option(
    "--out",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/processed"),
    show_default=True,
)
def conciliar_guia_cmd(ano: int, mes: int | None, extrato: Path, out: Path) -> None:
    """Cruza créditos GUIA_RECEBIMENTO com Exe_Retorno_Boleto via CodigoBarras (parcelamentos)."""
    df_extrato = pd.read_parquet(extrato)
    inicio, fim = _intervalo(ano, mes)
    janela = (df_extrato["dt_movimento"] >= pd.Timestamp(inicio)) & (
        df_extrato["dt_movimento"] <= pd.Timestamp(fim)
    )
    df_extrato = df_extrato[janela]

    engine = build_engine(BANCO_PROCESSO)
    df_rb = processo_repos.boletos_pagos(engine, inicio, fim)

    resultado = match_guia_mod.match_guia(df_extrato, df_rb)

    out.mkdir(parents=True, exist_ok=True)
    sufixo = f"{ano}" if mes is None else f"{ano}-{mes:02d}"
    destino = out / f"match_guia_{sufixo}.parquet"
    resultado.to_parquet(destino, index=False)

    contagem = resultado["status_match"].value_counts().to_dict() if not resultado.empty else {}
    click.echo(f"{len(resultado)} linhas -> {destino}")
    click.echo(f"  status: {contagem}")


@cli.command("relatorio")
@click.option("--ano", type=int, required=True)
@click.option("--mes", type=click.IntRange(1, 12), required=True)
@click.option(
    "--extrato",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("data/interim/extrato_canonico.parquet"),
    show_default=True,
)
@click.option(
    "--processed",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/processed"),
    show_default=True,
    help="Pasta onde os match_*_{ano}-{mes}.parquet foram salvos pelos comandos conciliar-*.",
)
@click.option(
    "--out",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/processed"),
    show_default=True,
)
def relatorio_cmd(ano: int, mes: int, extrato: Path, processed: Path, out: Path) -> None:
    """Gera relatorio_{ano}-{mes}.xlsx consolidando os 3 matchers."""
    sufixo = f"{ano}-{mes:02d}"
    df_extrato = pd.read_parquet(extrato)
    inicio, fim = _intervalo(ano, mes)
    janela = (df_extrato["dt_movimento"] >= pd.Timestamp(inicio)) & (
        df_extrato["dt_movimento"] <= pd.Timestamp(fim)
    )
    df_extrato = df_extrato[janela]

    matches_ob = _ler_se_existe(processed / f"match_ob_{sufixo}.parquet")
    matches_pessoa = _ler_se_existe(processed / f"match_pessoa_{sufixo}.parquet")
    matches_guia = _ler_se_existe(processed / f"match_guia_{sufixo}.parquet")

    out.mkdir(parents=True, exist_ok=True)
    destino = out / f"relatorio_{sufixo}.xlsx"
    relatorio_mod.relatorio_mensal(matches_ob, matches_pessoa, matches_guia, df_extrato, destino)
    click.echo(f"Relatorio gerado em {destino}")


def _ler_se_existe(caminho: Path) -> pd.DataFrame:
    return pd.read_parquet(caminho) if caminho.exists() else pd.DataFrame()


@cli.command("publicar-extrato")
@click.option(
    "--extrato",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("data/interim/extrato_canonico.parquet"),
    show_default=True,
)
@click.option(
    "--pasta-origem",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path("docs/extratos_frap"),
    show_default=True,
    help="Pasta com os .txt MMAAAA — usada para calcular o HashSha256.",
)
def publicar_extrato_cmd(extrato: Path, pasta_origem: Path) -> None:
    """Publica o extrato canônico em FRAPExtratoArquivo + FRAPLancamento (BdDIP)."""
    df = pd.read_parquet(extrato)
    engine = build_engine(BANCO_DIP)
    resultado = persistencia_extrato.publica_extrato(engine, df, pasta_origem=pasta_origem)
    click.echo(f"{len(resultado)} arquivos publicados:")
    for (conta, periodo), id_arquivo in sorted(resultado.items()):
        click.echo(f"  {conta} {periodo} -> IdArquivo={id_arquivo}")


@cli.command("publicar-match-ob")
@click.option("--ano", type=int, required=True)
@click.option("--mes", type=click.IntRange(1, 12), required=True)
@click.option("--conta", type=str, required=True, help="'700000-6' ou '600000-2'.")
@click.option(
    "--processed",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/processed"),
    show_default=True,
)
def publicar_match_ob_cmd(ano: int, mes: int, conta: str, processed: Path) -> None:
    """Publica match_ob_{ano}-{mes}.parquet em FRAPMatchOB (BdDIP)."""
    sufixo = f"{ano}-{mes:02d}"
    caminho = processed / f"match_ob_{sufixo}.parquet"
    if not caminho.exists():
        raise click.ClickException(f"Arquivo nao encontrado: {caminho}")
    df = pd.read_parquet(caminho)
    periodo = f"{mes:02d}{ano}"
    engine = build_engine(BANCO_DIP)
    n = persistencia_matches.publica_match_ob(engine, df, conta, periodo, ano)
    click.echo(f"{n} linhas publicadas em FRAPMatchOB ({conta} {periodo}).")


@cli.command("publicar-match-pessoa")
@click.option("--ano", type=int, required=True)
@click.option("--mes", type=click.IntRange(1, 12), required=True)
@click.option("--conta", type=str, required=True)
@click.option(
    "--processed",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/processed"),
    show_default=True,
)
def publicar_match_pessoa_cmd(ano: int, mes: int, conta: str, processed: Path) -> None:
    """Publica match_pessoa_{ano}-{mes}.parquet em FRAPMatchPessoa (BdDIP)."""
    sufixo = f"{ano}-{mes:02d}"
    caminho = processed / f"match_pessoa_{sufixo}.parquet"
    if not caminho.exists():
        raise click.ClickException(f"Arquivo nao encontrado: {caminho}")
    df = pd.read_parquet(caminho)
    periodo = f"{mes:02d}{ano}"
    engine = build_engine(BANCO_DIP)
    n = persistencia_matches.publica_match_pessoa(engine, df, conta, periodo)
    click.echo(f"{n} linhas publicadas em FRAPMatchPessoa ({conta} {periodo}).")


@cli.command("publicar-match-guia")
@click.option("--ano", type=int, required=True)
@click.option("--mes", type=click.IntRange(1, 12), required=True)
@click.option("--conta", type=str, required=True)
@click.option(
    "--processed",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/processed"),
    show_default=True,
)
def publicar_match_guia_cmd(ano: int, mes: int, conta: str, processed: Path) -> None:
    """Publica match_guia_{ano}-{mes}.parquet em FRAPMatchGuia (BdDIP)."""
    sufixo = f"{ano}-{mes:02d}"
    caminho = processed / f"match_guia_{sufixo}.parquet"
    if not caminho.exists():
        raise click.ClickException(f"Arquivo nao encontrado: {caminho}")
    df = pd.read_parquet(caminho)
    periodo = f"{mes:02d}{ano}"
    engine = build_engine(BANCO_DIP)
    n = persistencia_matches.publica_match_guia(engine, df, conta, periodo)
    click.echo(f"{n} linhas publicadas em FRAPMatchGuia ({conta} {periodo}).")


@cli.command("parse-descontos-folha")
@click.option(
    "--out",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/interim"),
    show_default=True,
)
def parse_descontos_folha_cmd(out: Path) -> None:
    """Lê Exe_DescontoFolha + parcelas do banco `processo` e gera parquet."""
    engine = build_engine(BANCO_PROCESSO)
    df = processo_repos.descontos_folha_cadastrados(engine)
    out.mkdir(parents=True, exist_ok=True)
    destino = out / "descontos_folha.parquet"
    df.to_parquet(destino, index=False)
    click.echo(
        f"{df['IdDescontoFolha'].nunique()} descontos x "
        f"{df['IdParcela'].notna().sum()} parcelas -> {destino}"
    )


@cli.command("publicar-desconto-folha")
@click.option(
    "--cadastro",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("data/interim/descontos_folha.parquet"),
    show_default=True,
)
def publicar_desconto_folha_cmd(cadastro: Path) -> None:
    """Popula FRAPDescontoFolha + FRAPDescontoFolhaParcela."""
    df = pd.read_parquet(cadastro)
    engine = build_engine(BANCO_DIP)
    mapa = persistencia_descontofolha.publica_desconto_folha(engine, df)
    click.echo(f"{len(mapa)} descontos publicados.")


@cli.command("conciliar-desconto-folha")
@click.option("--ano", type=int, required=True)
@click.option("--mes", type=click.IntRange(1, 12), required=True)
@click.option(
    "--out",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/processed"),
    show_default=True,
)
def conciliar_desconto_folha_cmd(ano: int, mes: int, out: Path) -> None:
    """Concilia parcelas com contracheque (BdSIAIPessoal) + crédito FRAP."""
    eng_dip = build_engine(BANCO_DIP)
    # Carrega parcelas do mês a partir do BdDIP
    sql_parcelas = text("""
        SELECT
            P.IdFRAPDescontoFolhaParcela, P.MesReferencia, P.AnoReferencia,
            P.ValorEsperado, P.DataVencimento AS DataVencimentoParcela,
            P.SituacaoParcela, P.TipoDeBaixa, P.DataPagamentoParcela,
            DF.CpfCnpj, DF.IdOrgaoNotificado
        FROM dbo.FRAPDescontoFolhaParcela P
        JOIN dbo.FRAPDescontoFolha DF ON DF.IdFRAPDescontoFolha = P.IdFRAPDescontoFolha
        WHERE P.MesReferencia = :mes AND P.AnoReferencia = :ano
          AND DF.Ativo = 1
    """)
    with eng_dip.connect() as c:
        parcelas = pd.read_sql(sql_parcelas, c, params={"mes": mes, "ano": ano})
    if parcelas.empty:
        click.echo(f"Sem parcelas em {ano}-{mes:02d} no FRAPDescontoFolhaParcela.")
        return

    # Lança SIAIPessoal
    cpfs = parcelas["CpfCnpj"].dropna().astype(str).str.zfill(11).unique().tolist()
    eng_sip = build_engine(BANCO_SIAIPESSOAL)
    contra = siaipessoal_repos.contracheque_descontos_tce(eng_sip, cpfs, mes, ano)

    # Lançamentos FRAP do mês (categoria OB_RECEBIDA ou TRANSFERENCIA — prefeituras
    # municipais costumam repassar via TED/PIX, que cai em TRANSFERENCIA). Janela
    # ampla pra cobrir D+45.
    sql_frap = text("""
        SELECT L.IdLancamento, L.DtMovimento, L.Valor,
               cat.Codigo AS Categoria, L.CpfCnpjDepositante,
               L.Historico, L.Descricao
        FROM dbo.FRAPLancamento L
        JOIN dbo.FRAPCategoria cat ON cat.IdCategoria = L.IdCategoria
        WHERE cat.Codigo IN ('OB_RECEBIDA', 'TRANSFERENCIA')
          AND L.ValorDC = 'C'
          AND L.DtMovimento BETWEEN
              DATEFROMPARTS(:ano, :mes, 1) AND DATEADD(DAY, 45, EOMONTH(DATEFROMPARTS(:ano, :mes, 1)))
    """)
    with eng_dip.connect() as c:
        lanc = pd.read_sql(sql_frap, c, params={"mes": mes, "ano": ano})

    # Nível B': monta orgaos_por_lancamento combinando duas fontes —
    #   1) CNPJ depositante ∈ CNPJS_ESTADO_RN  → expande p/ órgãos com IdOrgaoSuperior=272.
    #   2) Inferência fuzzy de Historico/Descricao (PREF MUN, ESTADO DO RIO GRANDE...).
    orgaos_por_lancamento: dict[int, set[int]] = {}
    if not lanc.empty:
        indice_orgaos = inferencia_orgao_mod.carregar_indice_orgaos(eng_dip)
        # (2) inferência por descrição
        orgaos_por_lancamento = inferencia_orgao_mod.construir_mapa_lancamentos(
            lanc.to_dict(orient="records"), indice_orgaos
        )
        orgaos_por_lancamento = inferencia_orgao_mod.expandir_estado_rn(
            orgaos_por_lancamento, indice_orgaos, ID_ORGAO_SUPERIOR_ESTADO
        )
        # (1) depositante = Estado-RN: marca como "todos os subordinados a 272"
        cnpjs_estado = set(cnpjs_estado_rn())
        if cnpjs_estado:
            subordinados = {
                o.id_orgao for o in indice_orgaos if o.id_orgao_superior == ID_ORGAO_SUPERIOR_ESTADO
            }
            for r in lanc.itertuples():
                cnpj_dep = str(getattr(r, "CpfCnpjDepositante", "") or "")
                if cnpj_dep in cnpjs_estado:
                    id_l = int(r.IdLancamento)
                    orgaos_por_lancamento.setdefault(id_l, set()).update(subordinados)

    resultado = match_descontofolha_mod.match_desconto_folha(
        parcelas,
        contra,
        lanc,
        orgaos_por_lancamento=orgaos_por_lancamento,
    )

    out.mkdir(parents=True, exist_ok=True)
    sufixo = f"{ano}-{mes:02d}"
    destino = out / f"match_desconto_folha_{sufixo}.parquet"
    resultado.to_parquet(destino, index=False)

    contagem = resultado["status_match"].value_counts().to_dict()
    click.echo(f"{len(resultado)} parcelas -> {destino}")
    click.echo(f"  status: {contagem}")


@cli.command("publicar-match-desconto-folha")
@click.option("--ano", type=int, required=True)
@click.option("--mes", type=click.IntRange(1, 12), required=True)
@click.option(
    "--processed",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/processed"),
    show_default=True,
)
def publicar_match_desconto_folha_cmd(ano: int, mes: int, processed: Path) -> None:
    """Popula FRAPMatchDescontoFolha do mês/ano."""
    sufixo = f"{ano}-{mes:02d}"
    caminho = processed / f"match_desconto_folha_{sufixo}.parquet"
    if not caminho.exists():
        # conciliar-desconto-folha não gera parquet quando não há parcelas no mês.
        click.echo(f"Sem match a publicar para {sufixo} (parquet ausente).")
        return
    df = pd.read_parquet(caminho)
    engine = build_engine(BANCO_DIP)
    # Resolve mapa de status DESCONTO_FOLHA
    with engine.connect() as c:
        rows = c.execute(
            text(
                "SELECT Codigo, IdStatusMatch FROM dbo.FRAPStatusMatch WHERE Matcher = 'DESCONTO_FOLHA'"
            )
        ).fetchall()
    mapa_status = {r[0]: int(r[1]) for r in rows}
    n = persistencia_descontofolha.publica_match_desconto_folha(engine, df, mes, ano, mapa_status)
    click.echo(f"{n} linhas publicadas em FRAPMatchDescontoFolha ({ano}-{mes:02d}).")


@cli.command("importar-monitoramento")
@click.option(
    "--arquivo",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("docs/desconto_folha/monitoramento_desconto_folha.xlsx"),
    show_default=True,
)
@click.option("--apenas-orgao", is_flag=True, help="Só atualiza IdOrgaoNotificado dos legacy.")
@click.option("--criar-cadastros", is_flag=True, help="Cria cadastros faltantes (Origem='M').")
@click.option("--incluir-nereu", is_flag=True, help="Importa aba dedicada do Nereu + pré-match.")
@click.option(
    "--id-usuario",
    type=int,
    default=None,
    help="IdUsuario p/ FRAPMatchDescontoFolha.IdUsuarioConcilia (obrigatório com --incluir-nereu).",
)
@click.option("--dry-run", is_flag=True, help="Imprime o que faria sem persistir.")
def importar_monitoramento_cmd(
    arquivo: Path,
    apenas_orgao: bool,
    criar_cadastros: bool,
    incluir_nereu: bool,
    id_usuario: int | None,
    dry_run: bool,
) -> None:
    """Importa planilha de monitoramento para FRAPDescontoFolha + matches manuais."""
    engine = build_engine(BANCO_DIP)
    res = planilha_mod.importar_planilha(
        engine,
        arquivo,
        apenas_orgao=apenas_orgao,
        criar_cadastros=criar_cadastros,
        incluir_nereu=incluir_nereu,
        id_usuario=id_usuario,
        dry_run=dry_run,
    )
    prefixo = "[dry-run] " if dry_run else ""
    click.echo(f"{prefixo}{res.resumo()}")
    for err in res.erros[:20]:
        click.echo(f"  erro: {err}", err=True)
    if len(res.erros) > 20:
        click.echo(f"  ... +{len(res.erros) - 20} erros", err=True)


@cli.command("popular-descontos-siai")
@click.option("--dry-run", is_flag=True, help="Imprime contagens sem persistir.")
def popular_descontos_siai_cmd(dry_run: bool) -> None:
    """Popula FRAPDescontoFolha Origem='S' a partir da view SIAI (rubrica TCE/FRAP)."""
    engine = build_engine(BANCO_DIP)
    res = persistencia_descontos_extras.popular_descontos_siai(engine, dry_run=dry_run)
    prefixo = "[dry-run] " if dry_run else ""
    click.echo(f"{prefixo}{res.resumo()}")
    for err in res.erros[:20]:
        click.echo(f"  erro: {err}", err=True)


@cli.command("popular-descontos-ccd")
@click.option("--dry-run", is_flag=True, help="Imprime contagens sem persistir.")
def popular_descontos_ccd_cmd(dry_run: bool) -> None:
    """Popula FRAPDescontoFolha Origem='C' a partir de FRAPNotificacaoDescontoFolha."""
    engine = build_engine(BANCO_DIP)
    res = persistencia_descontos_extras.popular_descontos_ccd(engine, dry_run=dry_run)
    prefixo = "[dry-run] " if dry_run else ""
    click.echo(f"{prefixo}{res.resumo()}")
    for err in res.erros[:20]:
        click.echo(f"  erro: {err}", err=True)


@cli.command("scan-notificacoes-ccd")
@click.option(
    "--processo",
    default=None,
    help="Filtra um processo único no formato NUM/ANO (ex: 003636/2017).",
)
@click.option("--dry-run", is_flag=True, help="Imprime contagens sem persistir.")
def scan_notificacoes_ccd_cmd(processo: str | None, dry_run: bool) -> None:
    """Escaneia PDFs CCD de notificação para desconto em folha e persiste em FRAP."""
    engine = build_engine(BANCO_DIP)
    processo_filtro: tuple[str, str] | None = None
    if processo:
        if "/" not in processo:
            raise click.BadParameter("Use NUM/ANO, ex: 003636/2017.")
        num, ano = processo.split("/", 1)
        processo_filtro = (num.zfill(6), ano)
    res = ccd_scan_mod.scan_notificacoes_ccd(
        engine, processo_filtro=processo_filtro, dry_run=dry_run
    )
    prefixo = "[dry-run] " if dry_run else ""
    click.echo(f"{prefixo}{res.resumo()}")
    for err in res.erros[:20]:
        click.echo(f"  erro: {err}", err=True)
    if len(res.erros) > 20:
        click.echo(f"  ... +{len(res.erros) - 20} erros", err=True)


@cli.command("recalcular-metricas-pessoa")
@click.option(
    "--cpf",
    "cpf",
    type=str,
    default=None,
    help="Recalcula apenas esse CPF/CNPJ (já normalizado, sem pontuação).",
)
@click.option("--dry-run", is_flag=True, help="Conta CPFs candidatos sem rodar o MERGE.")
def recalcular_metricas_pessoa_cmd(cpf: str | None, dry_run: bool) -> None:
    """Recalcula dbo.FRAPMetricaPessoa (ValorAtualizadoTotal + contagens notificados)."""
    engine = build_engine(BANCO_DIP)
    res = persistencia_metrica_pessoa.recalcular_metricas_pessoa(
        engine, only_cpf=cpf, dry_run=dry_run
    )
    prefixo = "[dry-run] " if dry_run else ""
    click.echo(f"{prefixo}{res.resumo()}")


@cli.command("inferir-orgaos-lancamentos")
@click.option(
    "--id-lancamento",
    "id_lancamento",
    type=int,
    default=None,
    help="Reinferi apenas esse lançamento.",
)
@click.option("--dry-run", is_flag=True, help="Conta matches sem persistir.")
def inferir_orgaos_lancamentos_cmd(id_lancamento: int | None, dry_run: bool) -> None:
    """Recalcula dbo.FRAPLancamentoOrgao via regex + alias + LLM (Azure OpenAI).

    LLM é parte do pipeline obrigatório; só é pulado se Azure não estiver
    configurado (AZURE_OPENAI_API_KEY/ENDPOINT ausentes), com warning visível.
    Cobre todos os FRAPLancamento das contas FRAP (sem filtro de ValorDC).
    """
    from frap.persistencia import inferencia_orgaos_lancamento as persistencia

    engine = build_engine(BANCO_DIP)
    res = persistencia.recalcular(
        engine,
        only_id_lancamento=id_lancamento,
        dry_run=dry_run,
    )
    prefixo = "[dry-run] " if dry_run else ""
    click.echo(f"{prefixo}{res.resumo()}")
    if not res.llm_disponivel and res.qtd_sem_match > 0:
        click.echo(
            "WARNING: LLM indisponível — configure AZURE_OPENAI_API_KEY/ENDPOINT "
            "para cobrir os sem_match.",
            err=True,
        )
    if res.amostras_sem_match:
        click.echo("Amostras sem match (regex+LLM):")
        for a in res.amostras_sem_match:
            click.echo(
                f"  [{a['id_lancamento']}] hist={a['historico']!r} desc={a['descricao']!r}"
            )


if __name__ == "__main__":
    cli()
