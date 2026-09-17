---
name: arrecadacao-multa-vs-pge
description: "Split arrecadação em \"multa\" (Exe_*) vs \"repasse da PGE\" (PGE_Pagamento) vem do banco processo, não do FRAP"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 45b5fd01-fa88-4b7e-bd4e-7cdc39cadd13
---

Para separar arrecadação por **origem** (multa vs repasse da PGE), use o banco **processo**, não o FRAP (`FRAPLancamento` só categoriza por forma de pagamento — OB SIGEF / boleto / TED-PIX — e não distingue origem).

- **Multa (pagamento direto pelo jurisdicionado)**: `Exe_Retorno_Boleto` (DataPagamento, ValorPago) — confirmação bancária de boletos pagos. Tabelas irmãs `Exe_DebitoBoleto` (à vista) e `Exe_ParcelaBoleto` (parceladas) dão totais quase idênticos; o retorno é a fonte autoritativa de pagamento confirmado.
- **Repasse da PGE (recuperação em dívida ativa)**: `PGE_Pagamento` (DataPagamento, ValorPrincipal + Multa + Juros). Some os três para o valor repassado.

Ordem de grandeza 2026 (jan–mai): multa ≈ R$ 326,6 mil; PGE ≈ R$ 449,8 mil. O caixa do FRAP no mesmo período (≈ R$ 938,8 mil) é uma lente diferente (créditos na conta do fundo), não soma direta dessas duas.

Usado no deck `scripts/apresentacao/apresentacao_presidente_mat.html` (slide Contexto). Desconto em folha por mês vem da lógica de [[frap-tables-in-bddip]] via `match_desconto_folha_standalone.py`.
