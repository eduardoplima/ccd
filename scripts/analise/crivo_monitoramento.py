"""Crivo de monitoramento: triagem CCD vs. Unidade Técnica.

Para cada processo da lista, lê as peças decisórias e pareceres do MPjTC,
classifica cada obrigação em CCD / UNIDADE_TECNICA / DAP / DUVIDA via LLM,
e grava um JSON por processo + uma planilha consolidada.
"""
from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path
from typing import Literal

import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from ccd.notebook import setup
from ccd.processo import get_informacoes_processo

_ASSUNTO_APR_PT = "APURAÇÃO DE RESPONSABILIDADE - PORTAL DA TRANSPARÊNCIA 2019."

PROCESSOS_PARA_TRIAR: list[dict] = [
    {"processo": "009050/2018", "tipo": "REP", "assunto": "DESCUMPRIMENTO DA LEI N.º 13.303/2016", "interessado": "CENTRAIS DE ABASTECIMENTO DO RN S/A"},
    {"processo": "000454/2026", "tipo": "MON", "assunto": "MONITORAMENTO REFERENTE AO PROCESSO 7226/2019-TC", "interessado": "CÂMARA MUNICIPAL DE CAIÇARA DO NORTE"},
    {"processo": "000455/2026", "tipo": "MON", "assunto": "MONITORAMENTO REFERENTE AO PROCESSO 1831/2020-TC", "interessado": "PREFEITURA MUNICIPAL DE SERRA DE SÃO BENTO"},
    {"processo": "012886/2016", "tipo": "MON", "assunto": "MONITORAMENTO DO PROCESSO Nº 7485/2002-TC", "interessado": "PREF.MUN.PASSAGEM"},
    {
        "processo": "000699/2022",
        "tipo": "AUD",
        "assunto": "AUDITORIA DE CONFORMIDADE NAS CONTAS ANUAIS DE GESTÃO DA SECRETARIA DE ESTADO DO TRABALHO, DA HABITAÇÃO E DA ASSISTÊNCIA SOCIAL - SETHAS (ID 16/2021).",
        "interessado": "SECRETARIA DE ESTADO DO TRABALHO, DA HABITAÇÃO E DA ASSISTÊNCIA SOCIAL",
    },
    {"processo": "001311/2020", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "PREFEITURA MUNICIPAL DE SANTO ANTÔNIO"},
    {"processo": "000741/2020", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "CÂMARA MUNICIPAL DE JAPI"},
    {"processo": "004076/2021", "tipo": "MON", "assunto": "MONITORAMENTO", "interessado": "COMPANHIA DE SERVIÇOS URBANOS DE NATAL"},
    {"processo": "000137/2026", "tipo": "MON", "assunto": "MONITORAMENTO REFERENTE AO PROCESSO 001823/2020-TC", "interessado": "PREFEITURA MUNICIPAL DE SÃO PEDRO"},
    {"processo": "006940/2019", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "PREFEITURA MUNICIPAL DE CAMPO REDONDO"},
    {"processo": "003442/2025", "tipo": "MON", "assunto": "MONITORAMENTO REFERENTE AO PROCESSO 907/2020-TC", "interessado": "PREFEITURA MUNICIPAL DE PATU"},
    {"processo": "001834/2024", "tipo": "MON", "assunto": "MONITORAMENTO REF. AO PROCESSO 7098/2019-TC", "interessado": "PREFEITURA MUNICIPAL DE FERNANDO PEDROSA"},
    {"processo": "001886/2020", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "CÂMARA MUNICIPAL DE SÃO RAFAEL"},
    {"processo": "000898/2020", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "PREFEITURA MUNICIPAL DE MESSIAS TARGINO"},
    {"processo": "000908/2020", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "PREFEITURA MUNICIPAL DE PASSA E FICA"},
    {"processo": "000733/2020", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "PREFEITURA MUNICIPAL DE MAXARANGUAPE"},
    {"processo": "001305/2020", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "PREFEITURA MUNICIPAL DE RIO DO FOGO"},
    {"processo": "002056/2020", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "CÂMARA MUNICIPAL DE SERRA DE SÃO BENTO"},
    {"processo": "000912/2020", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "PREFEITURA MUNICIPAL DE PAU DOS FERROS"},
    {"processo": "000726/2020", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "PREFEITURA MUNICIPAL DE LUIS GOMES"},
    {"processo": "006683/2019", "tipo": "APR", "assunto": "APURAÇÃO DE RESPONSABILIDADE REFERENTE AO PORTAL DA TRANSPARÊNCIA 2019.", "interessado": "CÂMARA MUNICIPAL DE ALEXANDRIA"},
    {"processo": "000932/2020", "tipo": "APR", "assunto": _ASSUNTO_APR_PT, "interessado": "CÂMARA MUNICIPAL DE MESSIAS TARGINO"},
    {"processo": "002365/2023", "tipo": "MON", "assunto": "MONITORAMENTO REFERENTE AO PROCESSO 2927/2018-TC", "interessado": "PREFEITURA MUNICIPAL DE TAIPU"},
]

SETORES_EXATOS: frozenset[str] = frozenset({"DAI", "DAD", "DAM", "DCD", "DCC"})
SETORES_PREFIXO: tuple[str, ...] = ("GAB", "PROC")

SYSTEM_PROMPT = """Você é um agente que tria deliberações do TCE/RN para definir qual unidade monitorará o cumprimento de cada obrigação fixada.

# Saídas possíveis (por obrigação)
- CCD — Coordenadoria de Controle de Decisões monitora diretamente.
- UNIDADE_TECNICA — Volta à unidade técnica de origem para relatório adicional.
- DAP — Ato de pessoal sujeito a registro.
- DUVIDA — Sinais insuficientes ou contraditórios.

# Critério central
O cumprimento pode ser comprovado por simples juntada de prova documental pelo responsável?
- Sim → CCD
- Não, exige nova atividade técnica de fiscalização → UNIDADE_TECNICA

# Sinais
CCD: obrigação discreta, responsável e prazo definidos; verificação do tipo "fez/não fez", "pagou", "publicou"; comprovação por publicação, certidão, comprovante, ato administrativo; correção formal de cláusula ou ato.

UNIDADE_TECNICA: a decisão fixa prazo para reapresentação de relatório pela unidade técnica; exige inspeção in loco, releitura técnica complexa, avaliação de efetividade; trata de implementação de sistema, plano de ação ou política pública; envolve múltiplos órgãos ou frentes ("implicações mais amplas").

DAP: ato de admissão, aposentadoria, pensão por morte ou benefício previdenciário sujeito a registro.

# Cumulatividade
Para classificar como UNIDADE_TECNICA, precisa coexistir: (1) implicações mais amplas, E (2) demanda de relatório adicional pela unidade técnica de origem. Se só um, é CCD.

# Honestidade
- Texto ambíguo → DUVIDA, nunca chute.
- Cite literalmente o trecho que fundamenta a classificação, e no campo `fonte` informe o nome do arquivo de origem (o material vem com marcadores `=== Arquivo: <nome>.pdf (setor: <setor>) ===` antes de cada peça).
- Use confiança BAIXA quando a classificação depender de inferência ampla.
- Se não há obrigação a monitorar no material apresentado, devolva lista vazia em `obrigacoes` e explique em `observacao`.
- Responda em pt-BR.
"""


class Obrigacao(BaseModel):
    trecho: str = Field(description="Citação literal do trecho da deliberação que fixa a obrigação.")
    fonte: str = Field(description="Nome do arquivo PDF que contém o trecho.")
    classificacao: Literal["CCD", "UNIDADE_TECNICA", "DAP", "DUVIDA"]
    confianca: Literal["ALTA", "MEDIA", "BAIXA"]
    sinais: list[str] = Field(description="Lista curta dos sinais do crivo que justificam a classificação.")
    justificativa: str = Field(description="1-2 frases ligando os sinais ao critério central.")


class RelatorioCrivo(BaseModel):
    processo: str
    tipo: str
    assunto: str = ""
    interessado: str
    obrigacoes: list[Obrigacao]
    observacao: str = ""


def _setor_passa_filtro(setor: str) -> bool:
    s = (setor or "").strip().upper()
    if s in SETORES_EXATOS:
        return True
    return any(s.startswith(p) for p in SETORES_PREFIXO)


def selecionar_pdfs(processo: str, engine, aplicar_filtro_setor: bool = True) -> pd.DataFrame:
    """Lê as informações do processo. Por padrão filtra pelos setores de peças
    decisórias / MPjTC; com `aplicar_filtro_setor=False`, devolve todas as peças.
    """
    df = get_informacoes_processo(processo, engine)
    if df.empty:
        return df
    if aplicar_filtro_setor:
        df = df[df["setor"].apply(_setor_passa_filtro)]
    return df.loc[:, ["arquivo", "setor", "texto"]].reset_index(drop=True)


def consolidar_texto(df: pd.DataFrame) -> str:
    blocos: list[str] = []
    for _, row in df.iterrows():
        cabecalho = f"\n\n=== Arquivo: {row['arquivo']} (setor: {row['setor'].strip()}) ===\n\n"
        blocos.append(cabecalho + (row["texto"] or ""))
    return "".join(blocos).strip()


def triar_processo(info: dict, engine, llm, aplicar_filtro_setor: bool = True) -> RelatorioCrivo:
    processo = info["processo"]
    df_pdfs = selecionar_pdfs(processo, engine, aplicar_filtro_setor=aplicar_filtro_setor)
    if df_pdfs.empty:
        msg_vazia = (
            "Nenhuma peça decisória/parecer encontrada nos setores filtrados."
            if aplicar_filtro_setor
            else "Processo sem peças disponíveis."
        )
        return RelatorioCrivo(
            processo=processo,
            tipo=info["tipo"],
            interessado=info["interessado"],
            obrigacoes=[],
            observacao=msg_vazia,
        )

    texto = consolidar_texto(df_pdfs)
    descricao_material = (
        "peças decisórias e pareceres do MPjTC"
        if aplicar_filtro_setor
        else "TODAS as peças do processo (filtro de setor desligado)"
    )
    user_message = (
        f"Processo: {processo}\n"
        f"Tipo: {info['tipo']}\n"
        f"Interessado: {info['interessado']}\n\n"
        f"Material para análise ({descricao_material}):\n\n{texto}"
    )

    structured = llm.with_structured_output(schema=RelatorioCrivo)
    relatorio: RelatorioCrivo = structured.invoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_message)]
    )
    relatorio.processo = processo
    relatorio.tipo = info["tipo"]
    relatorio.assunto = info.get("assunto", "")
    relatorio.interessado = info["interessado"]
    return relatorio


# Sinal histórico do override APR -> UNIDADE_TECNICA (revogado). Continua
# reconhecido para que rotinas de manutenção saibam identificar obrigações que
# foram afetadas pelo override antigo.
REGRA_APR_SINAL = "Regra fixa: APR (Portal da Transparência) vai para a unidade técnica."


def _assunto_eh_portal_transparencia(assunto: str) -> bool:
    return "portal da transparência" in (assunto or "").lower()


def destino_processo(relatorio: RelatorioCrivo) -> str:
    """Decide a unidade que recebe o processo como um todo.

    Regras (na ordem):
    1. Se o `assunto` menciona "portal da transparência", vai para a CCD.
    2. Se alguma obrigação foi classificada como CCD, vai para a CCD.
    3. Senão, se houver obrigação UNIDADE_TECNICA, vai para a unidade técnica.
    4. Senão, se houver DAP, vai para DAP. Senão, vazio.
    """
    if _assunto_eh_portal_transparencia(relatorio.assunto):
        return "CCD"
    classes = {o.classificacao for o in relatorio.obrigacoes}
    if "CCD" in classes:
        return "CCD"
    if "UNIDADE_TECNICA" in classes:
        return "UNIDADE_TECNICA"
    if "DAP" in classes:
        return "DAP"
    return ""


def _safe_name(processo: str) -> str:
    return processo.replace("/", "_")


def salvar_json(relatorio: RelatorioCrivo, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{_safe_name(relatorio.processo)}.json"
    payload = json.loads(relatorio.model_dump_json())
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def consolidar_xlsx(relatorios: list[RelatorioCrivo], out_dir: Path) -> Path:
    linhas: list[dict] = []
    for r in relatorios:
        destino = destino_processo(r)
        if not r.obrigacoes:
            linhas.append({
                "processo": r.processo,
                "tipo": r.tipo,
                "assunto": r.assunto,
                "interessado": r.interessado,
                "destino_processo": destino,
                "trecho": "",
                "fonte": "",
                "classificacao": "",
                "confianca": "",
                "sinais": "",
                "justificativa": "",
                "observacao": r.observacao,
            })
            continue
        for o in r.obrigacoes:
            linhas.append({
                "processo": r.processo,
                "tipo": r.tipo,
                "assunto": r.assunto,
                "interessado": r.interessado,
                "destino_processo": destino,
                "trecho": o.trecho,
                "fonte": o.fonte,
                "classificacao": o.classificacao,
                "confianca": o.confianca,
                "sinais": "; ".join(o.sinais),
                "justificativa": o.justificativa,
                "observacao": r.observacao,
            })

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "crivo.xlsx"
    pd.DataFrame(linhas).to_excel(path, index=False)
    return path


def main(out_dir: Path, processos_filtro: list[str] | None, aplicar_filtro_setor: bool = True) -> None:
    alvo = PROCESSOS_PARA_TRIAR
    if processos_filtro:
        wanted = set(processos_filtro)
        alvo = [p for p in PROCESSOS_PARA_TRIAR if p["processo"] in wanted]
        faltando = wanted - {p["processo"] for p in alvo}
        if faltando:
            print(f"Aviso: processos ignorados (não estão na lista): {sorted(faltando)}")
    if not alvo:
        print("Nenhum processo a triar.")
        return

    ctx = setup()
    for info in alvo:
        processo = info["processo"]
        print(f"[{processo}] triando...")
        try:
            r = triar_processo(info, ctx.engine, ctx.llm, aplicar_filtro_setor=aplicar_filtro_setor)
        except Exception as exc:
            print(f"[{processo}] FALHOU: {exc}")
            traceback.print_exc()
            r = RelatorioCrivo(
                processo=processo,
                tipo=info["tipo"],
                interessado=info["interessado"],
                obrigacoes=[],
                observacao=f"Erro durante a triagem: {exc!r}",
            )
        path_json = salvar_json(r, out_dir)
        print(f"[{processo}] {len(r.obrigacoes)} obrigacao(oes) -> {path_json}")

    # Reconstrói o xlsx a partir de TODOS os JSONs em disco — assim rodadas
    # parciais (com --processos) não apagam o que já estava consolidado.
    todos = [
        RelatorioCrivo.model_validate_json(p.read_text(encoding="utf-8"))
        for p in sorted(out_dir.glob("*.json"))
    ]
    path_xlsx = consolidar_xlsx(todos, out_dir)
    print(f"Planilha consolidada ({len(todos)} processos) -> {path_xlsx}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="crivo_monitoramento", description=__doc__)
    parser.add_argument(
        "--out-dir",
        default="saidas/analise/crivo_monitoramento",
        help="Diretório onde JSONs por processo e o crivo.xlsx serão gravados.",
    )
    parser.add_argument(
        "--processos",
        nargs="+",
        help="Subset opcional da lista hardcoded (ex.: --processos 000454/2026 001311/2020).",
    )
    parser.add_argument(
        "--sem-filtro-setor",
        action="store_true",
        help="Desliga o filtro de setores (DAI/DAD/DAM/DCD/DCC/GAB*/PROC*). Use para "
        "processos sem peças decisórias nesses setores (ex.: MON novos).",
    )
    args = parser.parse_args()
    main(Path(args.out_dir), args.processos, aplicar_filtro_setor=not args.sem_filtro_setor)
