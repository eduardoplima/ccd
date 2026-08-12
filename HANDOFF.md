# HANDOFF — CGAD extração de recomendações/obrigações

Contexto: destravar processos que não tinham recomendação/obrigação e rodar a
extração (NER + stage-2) para 2024–2026 com o modelo novo. Gerado em 2026-07-14,
para terminar amanhã.

---

## ✅ Já feito

1. **Fix do JOIN (commitado + pushed — commit `cceb0db`)**
   `LEFT JOIN processo.dbo.Orgaos` nos 4 SQLs do pipeline CGAD
   (`decisions_base.sql`, `decisions_full_text.sql`, `obligations_nonprocessed.sql`,
   `recommendations_nonprocessed.sql`). Antes, processos com `IdOrgaoEnvolvido = NULL`
   eram silenciosamente descartados por `INNER JOIN`. Foi a causa de 302645/2021
   não ter recomendação.

2. **Backfill de abril/2026 (destravados) — rodado, modelo gpt-5.4-nano**
   302645/2021 ganhou a recomendação (São Gonçalo do Amarante). No total: 97 NER,
   19 obrigações + 3 recomendações gravadas em `BdDIP`.

3. **Recomendações manuais do 8389/2014 — inseridas**
   `IdRecomendacao 989 e 990` (Súmula 28 / pesquisa de preços sem vínculo),
   ancoradas na decisão mais recente **70/2026** (`IdComposicaoPauta=124771,
   IdVotoPauta=46662`), órgão `115 = Câmara Municipal de Passagem`.
   ⚠️ Caveat: na tela de revisão o texto do acórdão que carrega é o dos embargos
   de 2026, não o acórdão de 2019 de onde vieram as recomendações (o de 2019 não
   está em `vw_ia_votos_acordaos_decisoes`). Degrada sem erro.
   Script: `handoff/insert_rec_8389.py`.

---

> **ATUALIZAÇÃO 2026-07-16**: Pendentes 1–3 concluídos.
> 1. Commits `70a8267` (NaN→None) e `76d802f` (deepseek) pushed; deploy automático disparado (deployment deepseek confirmado por ping antes).
> 2. Stage-1 completo: a task da sessão anterior tinha morrido; duas passadas idempotentes fecharam a cobertura. Resíduo sem NER (~1.090) é estrutural, não falha: 1.038 decisões já tinham obrigação/recomendação antigas (excluídas do driver pelo `NOT EXISTS`), 52 sem responsável de despesa (INNER JOIN `Pro_ProcessosResponsavelDespesa` as exclui).
> 3. Stage-2 rodado (deepseek): **Obrigações scanned=271 enqueued=249 skipped=21 failed=1; Recomendações scanned=88 enqueued=88 failed=0**. Rede oscilou muito; `run_etl_2024_2026.py` ganhou retry (10x, sessão nova) no stage-2. Logs: `handoff/etl_full_20260716*.log`.
>
> Segue pendente só o item 4 (backlog ≤2023 + DataSessao NULL).

## ✅ ~~PENDENTE 1~~ — Commitar 2 alterações de código (não commitadas)

`git status` mostra:
- `web/backend/app/cgad/tasks.py` — modelo de extração trocado para
  **`deepseek-v4-flash`** (era `gpt-5.4-nano`). Mantido `function_calling`.
- `web/tools/cgad/cgad/etl/pipeline.py` — helper **`_clean_str`** coage `NaN → None`
  em `orgao_responsavel` nos drafts de Obrigação/Recomendação. **Bug real exposto
  pelo fix do JOIN**: o worker de produção quebrava (`ValidationError`) em qualquer
  decisão sem órgão. Unit-check já feito.

**Ação:** revisar, `git add` os 2, commit (mensagens curtas, 1 linha, **sem**
`Co-Authored-By`, conforme CLAUDE.md) e `git push`.
⚠️ O push dispara **deploy automático** no host 10.24.0.197 → o worker passa a usar
deepseek + o fix de NaN. Confirme antes se o deployment `deepseek-v4-flash` existe
no recurso Azure (ping OK hoje via `AZURE_OPENAI_ENDPOINT`).

---

## 🔴 PENDENTE 2 — Stage-1 (NER) 2024–2026: verificar se terminou

Rodado localmente com **deepseek-v4-flash**, `overwrite=False` (idempotente,
re-startável). Quando você saiu estava ~90% (task de background podia ainda estar
rodando; ela **para sozinha** ao fim do stage-1 por causa do guard `STAGE1_ONLY=1`,
**não roda stage-2**).

Cobertura NER 2024–2026 no momento do handoff (parcial, subindo):

| Ano | decisões na view | com NER | sem NER |
|----|----:|----:|----:|
| 2024 | 3.718 | 3.000 | 718 |
| 2025 | 3.283 | 2.299 | 984 |
| 2026 | 1.632 | 1.124 | 508 |

(`RunId='deepseek-2024_2026'` = 5.393 NER criados nesta rodada.)

~5 decisões falharam por **blip de rede** (transiente). Uma 2ª passada do stage-1
(idempotente) pega as que faltam. Reconferir amanhã com a query em
**"Como reconferir cobertura"** abaixo — o número `sem NER` deve estar bem menor.

Se faltar, retomar stage-1 apenas:
```powershell
$env:PYTHONPATH="C:\Users\05911205424\Dev\ccd\web\tools\cgad"; $env:STAGE1_ONLY="1"
& "C:\Users\05911205424\Dev\ccd\web\.venv\Scripts\python.exe" `
  "C:\Users\05911205424\Dev\ccd\handoff\run_etl_2024_2026.py" *> stage1.log
```

---

## 🔴 PENDENTE 3 — Stage-2 (obrigação/recomendação) 2024–2026: NÃO rodado

Você pediu explicitamente para **não** rodar o stage-2 agora. É o que falta para as
recomendações/obrigações de 2024–2026 aparecerem na fila de revisão. O NER (stage-1)
sozinho não gera nada revisável.

Rodar quando quiser (roda stage-1 idempotente de novo + stage-2), **sem** o guard:
```powershell
$env:PYTHONPATH="C:\Users\05911205424\Dev\ccd\web\tools\cgad"; $env:STAGE1_ONLY=""
& "C:\Users\05911205424\Dev\ccd\web\.venv\Scripts\python.exe" `
  "C:\Users\05911205424\Dev\ccd\handoff\run_etl_2024_2026.py" *> stage2.log
```
Custa chamadas Azure (deepseek) e escreve em `BdDIP`. Idempotente: obrigações/
recomendações já gravadas são puladas pelo bridge `Processed*`.

> Alternativa "oficial": disparar pelo endpoint admin `/etl` (grava linha `Extracao`
> + feed de eventos + abort). Precisa do deploy dos commits do Pendente 1 no ar e do
> seu login admin. O script local **não** cria linha `Extracao` (writes idênticos,
> mas sem trilha de auditoria no app).

---

## ⚪ PENDENTE 4 — Backlog restante (fora do escopo de hoje)

- Anos **≤ 2023** sem NER: ~18 mil decisões (2020–2023 é o grosso).
- **1.803 decisões com `DataSessao` NULL**: invisíveis a rodadas por janela de data
  (`get_decisions_by_dates` filtra por data). Só via `process_numbers` ou ajuste do
  driver p/ incluir NULL. Vale investigar por que não têm data antes de processar.

---

## Como reconferir cobertura (roda quando quiser)
```powershell
& "C:\Users\05911205424\Dev\ccd\.venv\Scripts\python.exe" -c @'
import pandas as pd
from ccd.db import get_connection
eng=get_connection("processo")
q="""WITH dec AS (SELECT DISTINCT d.IdProcesso,d.IdComposicaoPauta,d.idVotoPauta,d.DataSessao
  FROM processo.dbo.vw_ia_votos_acordaos_decisoes d WHERE YEAR(d.DataSessao) IN (2024,2025,2026)),
ner AS (SELECT DISTINCT IdProcesso,IdComposicaoPauta,IdVotoPauta FROM BdDIP.dbo.NERDecisao)
SELECT YEAR(dec.DataSessao) ano, COUNT(*) total, COUNT(n.IdProcesso) com_ner,
  COUNT(*)-COUNT(n.IdProcesso) sem_ner
FROM dec LEFT JOIN ner n ON n.IdProcesso=dec.IdProcesso
  AND n.IdComposicaoPauta=dec.IdComposicaoPauta AND n.IdVotoPauta=dec.idVotoPauta
GROUP BY YEAR(dec.DataSessao) ORDER BY ano"""
print(pd.read_sql_query(q,eng).to_string(index=False))
'@
```

## Arquivos de apoio (nesta pasta `handoff/`)
- `run_etl_2024_2026.py` — stage-1 + stage-2, deepseek, 2024–2026, `overwrite=False`.
  Env `STAGE1_ONLY=1` para parar antes do stage-2. Resiliente a blip de rede
  (rollback + reconexão) e pula linhas com id nulo.
- `insert_rec_8389.py` — inserção manual das 2 recomendações do 8389/2014 (já rodado).

> Nota: `handoff/` não estava no repo antes — decida se versiona ou apaga depois.

---

# 📌 TAREFA 2026-07-29 — Processo 006457/2016-TC (CCD: prescrição + correção de nome no CGAD)

Contexto (levantado em 2026-07-28): execução do **Acórdão nº 1022/2010 – 1ª Câmara**
(origem 013947/2000, CM de Montanhas; o acórdão está no Evento 2, página 79 do PDF
= fl. física 137): ressarcimento R$ 2.260,00 + multa R$ 500,00 (multa paga e baixada
em 2012). O **Acórdão nº 135/2026 – 2ª Câmara** (relator Gilberto Jales) **transitou
em julgado em 03/06/2026** (certidão Evento 56, de 20/07/2026) e a DE mandou os autos
"à DIP para ciência e demais providências". O voto (Evento 45) decidiu:
nulidade por erro material no nome da responsável + **prescrição da pretensão
executória** (art. 115, LC 464/2012) + exclusão do nome errado dos cadastros +
arquivamento (art. 209, V, RITCE).

Estado do CGAD (conferido no banco): `Exe_Debito` **IdDebito 6815**, R$ 2.260,00,
**em aberto** e no nome **errado** — Maria de Fátima **Cordeiro da Silva** Medeiros
(CPF ***CPF-REMOVIDO***); a correta é Maria de Fátima **Américo de Lima** Medeiros
(CPF ***CPF-REMOVIDO***).

A fazer:
1. Registrar a decisão no CGAD e **dar baixa** do débito 6815 (motivo: prescrição
   da pretensão executória).
2. **Excluir o nome** da Sra. Maria de Fátima Cordeiro da Silva Medeiros dos
   cadastros do processo (substituição pela responsável correta, conforme voto).
3. **Emitir informação** certificando as anotações (padrão
   `processos/002264_2016/gerar_informacao.py`, skill `legislacao-ccd`) e devolver
   para arquivamento.

⚠️ **Antes de anotar**: o dispositivo do acórdão publicado (Evento 46) está errado —
itens a)–c) citam OUTRO caso (Acórdão 1155/2008, Proc. 2870/2002, Francisco Artur
de Souza); só d)–f) batem com o voto. Suscitar o erro material à Relatoria/SECSC
(na informação ou antes), em vez de executar de plano com base só no voto.

---

# 📌 ABRIR SEGUNDA 10/08/2026 — Desconto em folha (Nereu): 9 processos aguardando tramitação

Em **07/08/2026** as informações de desconto em folha do Sr. **Nereu Batista Linhares**
(CPF ***CPF-REMOVIDO***) foram geradas, cadastradas e **assinadas** na Área Restrita.
**Nada foi tramitado** — é o que fica para segunda.

Gerador: `processos/gerar_informacoes_nereu_desconto_folha.py`
(modelo `scripts/automacao/templates/desconto_folha.docx`; órgão notificado = SEAD;
valor = soma do `fn_Exe_RetornaValorAtualizado` dos débitos vigentes).
PDFs: `processos/nereu_desconto_folha/<NNNNNN_AAAA>/` e cópia do lote em
`saidas/automacao/nereu_desconto_folha_20260807/`.

| Processo | Informação (assinada) | Débito | Situação | Valor atualizado | Marcador |
|---|---|---|---|---|---|
| 000101/2022 | CCD_000101_2022_0070 | 27505 | Em Aberto | R$ 8.985,10 | DESCONTO EM FOLHA - Implementar Nereu |
| 000133/2022 | CCD_000133_2022_0058 | 29013 | Em Aberto | R$ 8.027,40 | DESCONTO EM FOLHA - Implementar Nereu |
| 000142/2023 | CCD_000142_2023_0071 | 27518 | Em Aberto | R$ 9.602,34 | NEREU - verificar data |
| 002062/2024 | CCD_002062_2024_0049 | 27109 | Em Aberto | R$ 13.677,08 | DESCONTO EM FOLHA - Implementar Nereu |
| 002564/2024 | CCD_002564_2024_0061 | 27187 | **Suspenso** | R$ 13.696,28 | (sem marcador) |
| 003023/2022 | CCD_003023_2022_0069 | 22973 | Em Aberto | R$ 1.548,22 | DESCONTO EM FOLHA - Implementar Nereu |
| 003064/2022 | CCD_003064_2022_0074 | 22928 | Em Aberto | R$ 1.492,35 | DESCONTO EM FOLHA - Implementar Nereu |
| 003078/2022 | CCD_003078_2022_0066 | 22445 | Em Aberto | R$ 1.548,22 | NEREU - verificar data |
| 003659/2022 | CCD_003659_2022_0078 | 22316 | Em Aberto | R$ 1.509,89 | DESCONTO EM FOLHA - Implementar Nereu |

Substituições já feitas (a informação de hoje substituiu a anterior da CCD):
**000101/2022** (a de 18/06/2026) e **002564/2024** (a de 15/07/2026).

**Retirado do lote**: 000130/2023 — desconto já implementado; diretório apagado e o
processo removido de `PROCESSOS` no gerador.

## A fazer segunda

1. **Decidir o destino/tramitação** dos 9 (nada foi tramitado). Se for o fluxo usual:
   `python -m scripts.automacao.area_restrita tramitar <procs> --destino <SETOR> --providencia "<...>" --dry-run`
   e depois sem `--dry-run`. Verificação: os processos saem da listagem do CCD.
2. **002564/2024**: o débito 27187 está **Suspenso** — conferir se cabe determinar o
   desconto antes de resolver a suspensão. Há ainda a informação antiga
   `CCD_002564_2024_0060`, cadastrada antes de 07/08 e não assinada; sumiu da fila de
   pendentes durante o lote — verificar o que houve com ela.
3. **000142/2023 e 003078/2022** estão no marcador "NEREU - verificar data" (não
   "Implementar"): confirmar se a determinação de desconto já vale para eles ou se
   falta a verificação de data.
4. Ajustar os marcadores depois da tramitação (os 6 "Implementar Nereu" continuam
   ativos, sem data de exclusão).

Pendências de terceiros na fila de assinatura (não tocar): 000237/2026, 000460/2026.
