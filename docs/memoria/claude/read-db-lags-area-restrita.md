---
name: read-db-lags-area-restrita
description: "O banco MSSQL processo (10.24.0.77) que consulto está defasado vs a Área Restrita ao vivo; para tramitação/recebimento recentes, a Área Restrita é autoritativa"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 75f9c09c-3db6-44c8-8881-e0e172bc7e1f
---

O banco `processo` que consulto (10.24.0.77, ver [[mssql-plain-ip-not-named-instance]]) **lag
em relação à Área Restrita ao vivo** para escritas recentes. Numa tramitação (jul/2026) os 4
processos foram enviados e recebidos na DIP na Área Restrita, mas `Processos.setor_atual`
ainda mostrava `CCD` e `Itens_Lote`/`Lotes` não tinha o lote novo — horas depois.

**Regra:** para confirmar tramitação/recebimento/setor recém-alterado, a **Área Restrita é a
fonte autoritativa**, não este banco. Não conclua "falhou" só porque o banco não refletiu
ainda. (Casa com [[deploy-host-var-disk-tight]]? não — isto é só sobre o replica do processo.)

**Why:** me levou a diagnosticar erroneamente uma tramitação bem-sucedida como "não commitou /
aguardando envio", e a ficar cutucando produção à toa.
**How to apply:** ao validar ação na Área Restrita, cheque o efeito na própria Área Restrita
(ou peça ao usuário); trate o banco como eventualmente-consistente para escritas do dia.
