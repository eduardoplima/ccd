# Reunião TCE/RN (CCD) × SEAD/SEARH — Desconto em folha

**Objetivo:** alinhar a efetivação dos descontos em folha de débitos do TCE e melhorar a planilha de consignações trocada entre os órgãos.

## Onde estamos (números)
- **43 processos** do gestor de referência foram encaminhados para desconto em folha (**24 em 2025 + 18 em 2026** + 1 sem data).
- **42 de 43** têm **notificação da DAE à SEARH** ("Promover o desconto em folha"), emitidas em **out/2024**.
- Apenas **10** estão **confirmados descontando e com repasse ao TCE** (jan–mai/2025, via SIAIDP + FRAP).
- **33 sem confirmação** de desconto/repasse (a verificação interna só vai até mai/2025).
- **28** têm uma nota **antiga** de "impossibilidade – ADI 0808846-43.2020" (jul/2023), **anterior** e **superada** pela notificação de out/2024.
- À parte: **5 CPFs** que a SEAD desconta e o TCE **não tinha em seu controle** (origem a esclarecer).

## Pedido 1 — Ajustes na planilha de consignações
Para permitir conciliação automática, incluir/padronizar colunas:
1. **Nº do processo TCE** (numero/ano) em coluna própria (hoje só no campo de observação).
2. **Nome do servidor**.
3. **CPF padronizado** (11 dígitos, com zeros à esquerda).
4. **Valor já descontado acumulado** + **parcelas pagas / total** + **saldo devedor**.
5. **Situação da consignação** (ativa / suspensa / encerrada / indeferida) **+ motivo**.
6. **Datas**: início do desconto e competência da parcela.
7. **Identificador do repasse ao TCE** (conta / nº da OB / documento).
8. **Extrato mensal completo por competência** + **ID estável** por consignação.
9. Corrigir **linhas sem CPF/identificação**.

## Pedido 2 — Outras solicitações
1. **Confirmar a implantação dos 42 já notificados** (lista anexa): está descontando? desde quando? se não, **por quê**?
2. **ADI 0808846-43.2020**: confirmar que não bloqueia mais a operacionalização (notificação é posterior).
3. **Relatório de margem consignável** + critério de prioridade quando a margem não cobre tudo.
4. **Repasse ao TCE**: conta destino (700000-6) e layout/documento, para fechar a conciliação.
5. **Fluxo e prazo (SLA)** entre notificação da DAE e implantação na folha + **ponto focal** (SEI).
6. **Conciliação periódica**: TCE envia mensalmente processo + CPF + valor esperado; SEARH devolve status + valor descontado + dado do repasse.
7. **Origem das consignações dos 5 CPFs** não controlados pelo TCE.

## Anexos
- `notificacoes_nereu_datas.xlsx` — 43 processos × data de notificação à SEARH.
- `estado_nereu_desconto_folha.xlsx` — panorama (situação no banco, folha, FRAP) + aba "Notificação SEAD".
