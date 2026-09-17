---
name: ar-baixa-entregue-pode-ser-devolucao
description: "No retorno dos Correios, a baixa \"01 - Entregue\" pode ser a devolução do objeto ao próprio TCE; só a imagem do AR distingue citação válida de frustrada"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3e1d34c4-ef4f-47a2-9338-1fcda2ab1b97
  modified: 2026-08-24T14:43:04.964Z
---

`Cit_ItensArquivoRetorno` guarda uma linha por movimento do mesmo `NumeroObjeto`. Uma citação frustrada pode terminar com uma linha `MotivoDevolucao = 0` (baixa "01 – Entregue ao Destinatário") que na verdade é **a entrega do envelope devolvido ao remetente**. Só essa última linha é consolidada em `Cit_ArquivoItensGuiaPostagem` (`idMotivoBaixa = 1`) e vira `Cit_Citacoes.DataInicioContagem` — e daí a `DataInicioContagem`/`DataFinalResposta` dos `Exe_Debito`. O sistema passa a exibir prazo escoado contra quem nunca foi citado.

`NomeRecebedor` e `RGRecebedor` vêm vazios **tanto na entrega real quanto na devolução**, então não servem para distinguir. O que distingue é a **imagem digitalizada do AR**: entrega real traz assinatura, data e nº de documento; devolução traz carimbo "AO REMETENTE", campos em branco e quadrículas de motivo marcadas ("Mudou-se", "Não Procurado").

**Como checar**: `SELECT NumeroObjeto, DataEntregaAR, MotivoDevolucao FROM Cit_ItensArquivoRetorno WHERE RTRIM(NumeroObjeto) = :obj ORDER BY DataEntregaAR`. Mais de uma linha, com motivos ≠ 0 antes de um motivo 0, é sinal forte de devolução — confirme lendo o PDF do AR (é imagem: use a ferramenta Read, não `extract_text_from_pdf`).

Visto em 005090/2018 (citação 002614/2025, objeto AR330869456TE): motivos 71 → 26 → 0. Ver [[cit-citacoes-authoritative-source]] e [[processo-005090-2018-citacao-frustrada]].
