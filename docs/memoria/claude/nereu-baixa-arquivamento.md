---
name: nereu-baixa-arquivamento
description: Lote nereu_baixa — 100/106/1391/2023 arquivamento ENVIADO (CCD→DIP, ENVIO A GCCTH, 01/09/2026)
metadata: 
  node_type: memory
  type: project
  originSessionId: 97cc01fd-03e0-46a0-a6ef-ce7dfbcabcf1
  modified: 2026-09-02T13:09:37.863Z
---

Trilha pós-baixa do lote [[nereu-desconto-folha-progresso]] (processos já pagos): em
000100/2023, 000106/2023 e 001391/2023 o Relator (GCCTH, título "Decisão.") acolheu a
informação de baixa e cancelou o saldo residual — débitos-filho 29059/29063/29062 constam
"Cancelada por decisão do relator"; certidão declaratória de quitação juntada aos autos.
Em 01/09/2026 geradas as informações de arquivamento (envio à DE, art. 26 da Res.
013/2015) com `processos/gerar_informacoes_nereu_arquivamento.py` → saídas em
`processos/nereu_arquivamento/`. Em **01/09/2026** o ciclo completo foi executado na Área
Restrita: distribuídos, informações cadastradas (CCD_000100_2023_0094 /
CCD_000106_2023_0099 / CCD_001391_2023_0096), assinadas (Web PKI) e **tramitadas CCD→DIP
com providência "ENVIO A GCCTH"** (saíram da listagem da CCD). Texto final revisado pelo
usuário: 3 parágrafos, sem CPF e sem "É a informação."; assert de 1 página no gerador.
**Lote 2 (redigido 01/09/2026)**: 001417/2023 (23466, padrão do lote 1: Decisão Ev. 112,
cancelamento 115, certidão 116) — **ENVIADO 02/09/2026** (CCD_001417_2023_0083, assinada,
tramitada CCD→DIP "ENVIO A GCCTH"); 003661/2022 (22554, ainda não cadastrado/tramitado,
variante quitado: Decisão Ev. 124 levantou sobrestamento — liminar STF na SS 5.749 —,
reconheceu inexigibilidade do resíduo e determinou exclusão do Cadastro + certidão +
retificação do motivo). **Pendência no 003661**: a certidão de cancelamento juntada
(Ev. 127) cita a dívida 29.062 — que é do 001391/2023 (R$ 30,13) — em vez da 29.049
(R$ 20,72), e o motivo do 29049 segue "Cancelada por Erro de Cadastro" no banco (item
c.iii da Decisão não refletido). Avaliação do usuário (01/09/2026): erro formal pequeno,
sem alterar a materialidade — não retificar, não voltar a apontar. Os demais do
lote de baixa aguardam decisão do Relator — basta acrescentar o IdDebito em `DEBITOS`.
