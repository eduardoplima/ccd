"""Candidatos a desconto em folha — recorte de ABRIL/2026.

Candidato = pessoa fisica que
  (1) tem debito ainda devido em processo.dbo.Exe_Debito
      (CodigoStatusDivida 1=Em Aberto / 3=Pago parcialmente);
  (2) aparece na folha de 04/2026 (contracheque como servidor OU pensionista); e
  (3) NAO tem rubrica de desconto (Tipo='2') com descricao TCE / FRAP /
      Tribunal de Contas nesse mes.
"""
import time
import pandas as pd
from sqlalchemy import text
from ccd.db import get_connection

ANO, MES = 2026, 4

# etapa 1 -- devedores PF (nome + qtd de debitos ainda devidos)
eng_proc = get_connection("processo")
df_dev = pd.read_sql(text("""
    SELECT gp.Documento AS cpf, MAX(gp.Nome) AS nome,
           COUNT(DISTINCT ed.IdDebito) AS qtd_debitos
    FROM processo.dbo.Exe_Debito ed
    JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = ed.IdDebito
    JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
    WHERE ed.CodigoStatusDivida IN (1, 3)
      AND LEN(gp.Documento) = 11 AND gp.Documento NOT LIKE '%[^0-9]%'
    GROUP BY gp.Documento
"""), eng_proc)
print(f"etapa 1: {len(df_dev)} devedores PF", flush=True)

# etapa 2 -- cruzamento com a folha do mes (temp tables na mesma conexao)
eng = get_connection("BdSIAIPessoal")
t0 = time.time()
with eng.connect() as conn:
    conn.exec_driver_sql("CREATE TABLE #dev (cpf varchar(11) COLLATE DATABASE_DEFAULT PRIMARY KEY)")
    cpfs = df_dev["cpf"].tolist()
    for i in range(0, len(cpfs), 500):
        vals = ",".join(f"('{c}')" for c in cpfs[i:i + 500])
        conn.exec_driver_sql(f"INSERT INTO #dev (cpf) VALUES {vals}")

    # folhas do mes (poucas centenas) -> torna o join no contracheque seletivo
    conn.exec_driver_sql(f"""
        SELECT IdFolhaPagamento INTO #fp FROM dbo.SiaiDp_FolhaPagamento
        WHERE CAST(Ano AS INT) = {ANO} AND CAST(Mes AS INT) = {MES}
    """)
    conn.exec_driver_sql("CREATE CLUSTERED INDEX ix ON #fp (IdFolhaPagamento)")

    # contracheques do mes das pessoas devedoras (servidor OU pensionista)
    conn.exec_driver_sql("""
        SELECT cc.IdContraCheque, cp.CPF
        INTO #cc
        FROM dbo.Comum_Pessoa cp
        JOIN #dev d ON d.cpf = cp.CPF
        JOIN dbo.SiaiDp_Funcionario f ON f.IdPessoa = cp.IdPessoa
        JOIN dbo.SiaiDp_ContraCheque cc ON cc.IdFuncionario = f.IdFuncionario
        JOIN #fp fp ON fp.IdFolhaPagamento = cc.IdFolhaPagamento
        UNION
        SELECT cc.IdContraCheque, cp.CPF
        FROM dbo.Comum_Pessoa cp
        JOIN #dev d ON d.cpf = cp.CPF
        JOIN dbo.SiaiDp_Pensionista pen ON pen.IdPessoa = cp.IdPessoa
        JOIN dbo.SiaiDp_ContraCheque cc ON cc.IdPensionista = pen.IdPensionista
        JOIN #fp fp ON fp.IdFolhaPagamento = cc.IdFolhaPagamento
    """)
    conn.exec_driver_sql("CREATE CLUSTERED INDEX ix ON #cc (IdContraCheque)")

    resumo = conn.execute(text("""
        SELECT
          (SELECT COUNT(DISTINCT CPF) FROM #cc) AS na_folha,
          (SELECT COUNT(DISTINCT cc.CPF) FROM #cc cc
             JOIN dbo.SiaiDp_ContraChequeItem cci ON cci.IdContraCheque = cc.IdContraCheque
             JOIN dbo.SiaiDp_Rubrica r ON r.IdRubrica = cci.IdRubrica
             WHERE r.Tipo='2' AND (UPPER(r.Descricao) LIKE '%TCE%'
               OR UPPER(r.Descricao) LIKE '%TRIBUNAL DE CONTAS%'
               OR UPPER(r.Descricao) LIKE '%FRAP%')) AS com_rubrica_tce
    """)).fetchone()
    print(f"   na folha 04/2026: {resumo[0]} | ja com rubrica TCE/FRAP: {resumo[1]}", flush=True)

    df_cand = pd.read_sql(text("""
        WITH na_folha AS (SELECT DISTINCT CPF FROM #cc),
        com_tce AS (
            SELECT DISTINCT cc.CPF
            FROM #cc cc
            JOIN dbo.SiaiDp_ContraChequeItem cci ON cci.IdContraCheque = cc.IdContraCheque
            JOIN dbo.SiaiDp_Rubrica r ON r.IdRubrica = cci.IdRubrica
            WHERE r.Tipo = '2'
              AND (UPPER(r.Descricao) LIKE '%TCE%'
                   OR UPPER(r.Descricao) LIKE '%TRIBUNAL DE CONTAS%'
                   OR UPPER(r.Descricao) LIKE '%FRAP%')
        )
        SELECT CPF AS cpf FROM na_folha
        WHERE CPF NOT IN (SELECT CPF FROM com_tce)
    """), conn)
print(f"etapa 2: {time.time() - t0:.1f}s", flush=True)

# saida -- somente os candidatos
cand = df_cand.merge(df_dev, on="cpf", how="left").sort_values("nome")
print(f"\n==> CANDIDATOS (na folha 04/2026 e SEM rubrica TCE/FRAP): {len(cand)}\n", flush=True)
print(cand.to_string(index=False), flush=True)

out = "scripts/analise/docs/candidatos_desconto_folha_042026.xlsx"
cand.to_excel(out, index=False)
print(f"\n-> {out}", flush=True)
