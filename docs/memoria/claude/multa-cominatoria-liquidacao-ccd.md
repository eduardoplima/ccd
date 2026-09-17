---
name: multa-cominatoria-liquidacao-ccd
description: "Como a CCD liquida multa diária (cominatória) — início da mora, contagem de dias, teto anual (Portaria 007/2026 = R$ 21.493,07), cadastro tipo 5; caso 101053/2022 (MACAUPREV)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 715ea4a7-59ce-4f5b-b4a1-0f84266f654c
  modified: 2026-09-02T17:25:07.007Z
---

**Prática da CCD para liquidar multa diária do art. 110 da LCE 464/2012** (ref.: 101327/2021 Evento 28, 002166/2024, 101026/2019):
- Mora começa no dia seguinte ao fim do prazo certificado pela DE (não do trânsito). Liquida-se "até a data" do cadastro; a mora continua e pode ser complementada (art. 110, § único).
- Nº de diárias no sistema = `(fim − ini).days` (exclui um extremo): 09/09/2025→11/02/2026 = 155 dias; 25/11/2022→22/05/2023 = 178.
- Teto = % do art. 323, II, do RI sobre o valor da Portaria anual: **2026 = Portaria nº 007/2026-GP/TCE, R$ 21.493,07** (alínea "f" → 50% = R$ 10.746,54); 2025 = Portaria 05/2025, R$ 20.585,16; 2021 = R$ 16.054,81.
- Cadastro: `Exe_Debito` tipo 5 + `Exe_Debito_MultaCominatoria` (ValorMultaCominatoria, CcTotal, LimiteValor, ini/fim), `setorDebito` CCD. Depois: citação 5 dias (art. 117) e retorno ao Relator para fixar a multa do art. 107, II, "f".

**Caso 101053/2022 (APO MACAUPREV, Decisão 328/2025, relator Marco Antônio)** — na CCD desde 28/08/2026 com marcador "EXECUÇÃO - Instaurar processo". Obrigação de fazer (item "c": juntar documentos da Res. 08/2012) descumprida: citação 001475/2026 recebida tacitamente 14/05/2026, prazo até 12/08/2026, certidão DE 13/08/2026 (Evento 120) sem resposta. Mora desde **13/08/2026**, R$ 50/dia. Multa R$ 1.100 = débito 28240 (aberto, citação 001476/2026 vencida 21/05/2026). Gerador: `processos/101053_2022/gerar_informacao.py` (usa o débito tipo 5 se cadastrado; senão apura até hoje). Pendências: cadastrar o débito (responsável = gestor ATUAL do MACAUPREV, não João Batista, que é "à época"); `BdDIP.Obrigacao` 831/832 têm DataCumprimento 06-07/2025 (errado, anterior ao trânsito) — a obrigação aparece como cumprida no CGAD.

**Why:** valores e convenções não estão documentados em lugar nenhum; extraídos de liquidações anteriores da CCD.
**How to apply:** ao liquidar cominatória nova, copiar `processos/101053_2022/gerar_informacao.py` ou `002166_2024`; conferir a Portaria do ano na informação mais recente da CCD que a cite. Ver [[multa-cominatoria-tabela-propria]], [[portaria-valor-maximo-multa]].
