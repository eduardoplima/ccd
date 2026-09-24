# Processos do Nereu com débitos pagos e conciliados

Levantamento em 31/07/2026. Recorte: débitos em que NEREU BATISTA LINHARES
(CPF ***.064.444-**) figura em `Exe_DebitoPessoa`, com `IdDebitoAnterior IS NULL`.

Todos os casos abaixo têm registro em `Exe_HistoricoDebito` com a narrativa
"Desconto em folha efetuado em <mês>/2025 ... Transferência para o FRAP
verificada (Documento <doc do extrato>)".

## Débitos com status de pagamento

| id_debito | processo (execução) | setor_atual | relator (origem) | situação | valor atualizado | desconto |
|---|---|---|---|---|---|---|
| 22596 | 003269/2023 | DIP_SOBR | ANTONIO GILBERTO DE OLIVEIRA JALES | Pago Integralmente | 1.263,83 | jan/2025 |
| 22554 | 003661/2022 | CCD | CARLOS THOMPSON COSTA FERNANDES | Pago Integralmente | 1.319,75 | jan/2025 |
| 22595 | 001391/2023 | CCD | CARLOS THOMPSON COSTA FERNANDES | Pago parcialmente | 1.285,31 | fev/2025 |
| 22484 | 003666/2022 | CCD | CARLOS THOMPSON COSTA FERNANDES | Pago parcialmente | 1.329,35 | mar/2025 |
| 23466 | 001417/2023 | CCD | CARLOS THOMPSON COSTA FERNANDES | Pago parcialmente | 1.270,54 | abr/2025 |
| 22452 | 001420/2023 | CCD | ANTONIO GILBERTO DE OLIVEIRA JALES | Pago parcialmente | 1.308,37 | abr/2025 |
| 23056 | 000100/2023 | CCD | CARLOS THOMPSON COSTA FERNANDES | Pago parcialmente | 1.292,04 | mai/2025 |
| 22859 | 000106/2023 | CCD | CARLOS THOMPSON COSTA FERNANDES | Pago parcialmente | 1.319,44 | mai/2025 |

## Divergências — pago e conciliado, mas ainda "Em Aberto"

Mesmo histórico de desconto + conciliação no FRAP, sem a baixa refletida no
status da dívida:

| id_debito | processo (execução) | setor_atual | relator (origem) | situação | desconto |
|---|---|---|---|---|---|
| 23057 | 000099/2023 | CCD | CARLOS THOMPSON COSTA FERNANDES | **Em Aberto** | mar/2025 (par de 003666/2022) |
| 23478 | 001418/2023 | CCD | CARLOS THOMPSON COSTA FERNANDES | **Em Aberto** | fev/2025 (par de 001391/2023) |

## Observações

- **Relator** é o do processo de **origem**. Na execução todos figuram como
  CARLOS THOMPSON COSTA FERNANDES (relator da CCD), o que não distingue nada.
- Os descontos foram feitos **em pares** de processos, com uma única
  transferência ao FRAP cobrindo dois: 003269/2023+003661/2022,
  001391/2023+001418/2023, 003666/2022+000099/2023, 001417/2023+001420/2023,
  000100/2023+000106/2023.
- O pagamento **não** está em `Exe_DebitoBoleto.DataPagamento` nem em
  `Exe_Retorno_Boleto` (ambos vazios), e **não** há vínculo por `IdDebito` em
  `FRAPMatchGuia` / `FRAPMatchPessoa` / `FRAPDescontoFolha`. A conciliação foi
  registrada manualmente no histórico do débito (usuário ***.662.102-**, mai/2026).
- O panorama geral dos débitos do Nereu: 422 Em Aberto, 193 Suspenso, 85
  cancelados, 2 Pago Integralmente, 6 Pago parcialmente.

## Consulta

```sql
SELECT DISTINCT e.IdDebito,
  CONCAT(RTRIM(pe.numero_processo),'/',RTRIM(pe.ano_processo)) execucao,
  RTRIM(pe.setor_atual) setor_atual, ro.nome relator_origem,
  esd.DescricaoStatusDivida situacao,
  processo.dbo.fn_Exe_RetornaValorAtualizado(e.IdDebito) valor_atual
FROM processo.dbo.Exe_Debito e
JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
LEFT JOIN processo.dbo.Exe_StatusDivida esd ON esd.CodigoStatusDivida = e.CodigoStatusDivida
LEFT JOIN processo.dbo.Processos pe ON pe.IdProcesso = e.IdProcessoExecucao
LEFT JOIN processo.dbo.Processos po ON po.IdProcesso = e.IdProcessoOrigem
LEFT JOIN processo.dbo.Relator ro ON ro.codigo = po.codigo_relator
WHERE gp.Documento = :cpf AND e.IdDebitoAnterior IS NULL
  AND esd.DescricaoStatusDivida LIKE 'Pago%'
```

Os conciliados "ocultos" (status Em Aberto) só aparecem por
`Exe_HistoricoDebito.Justificativa LIKE '%FRAP%'` — vale rodar essa varredura
antes de tratar qualquer débito do Nereu como pendente.
