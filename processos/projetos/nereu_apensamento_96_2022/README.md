# Despacho do Evento 63 do 000096/2022 (GCAED, 11/11/2026) — reunião das execuções do Nereu abrangidas pela APR 003474/2021

O Relator acolheu **parcialmente** a proposta da CCD (Ev. 60): reúne ao 96/2022 só as execuções de multa do
Nereu cujo **originário está no Evento 103 da APR 003474/2021** e **sem atos efetivos de cobrança**
(desconto em folha implantado / remessa ao MPC), por *bis in idem* com a APR (Ac. 162/2022-TC). O
arquivamento vai ao colegiado após manifestação da DIP e parecer do MPC.

| Item | Quem | O quê | Estado (12/11/2026) |
|---|---|---|---|
| a | assessoria GCAED | apensar as 78 da Tabela 1 ao 96/2022 | pendente no gabinete (96/2022 ainda no GCAED) |
| b | DIP | juntar cópia do despacho na APR + certidão dos 19 originários da Tabela 2 | **certidão gerada** com o despacho apensado (`apr_3474_2021/certidao_003474_2021.pdf`), não juntada — APR está na DAP |
| c | DIP | revisar o levantamento pelo Ev. 103 e reunir remanescentes | **feito**: único remanescente 003380/2024 (apontado na informação; está no GCAED) |
| d | DIP | manifestar-se sobre o arquivamento | **informação gerada**, favorável (`000096_2022/`), não cadastrada |
| e | DIP | encaminhar ao MPC | pendente: quando o 96/2022 chegar à CCD → ciclo e-Contas, tramitar DIP "ENVIO AO MPC" |

## Rodar
```
.venv/Scripts/python.exe processos/projetos/nereu_apensamento_96_2022/levantamento.py      # xlsx + json + md
.venv/Scripts/python.exe processos/projetos/nereu_apensamento_96_2022/gerar_documentos.py  # certidão + informação
```

## Levantamento (12/11/2026)
- 469 originários no Ev. 103; 477 execuções do Nereu (178 GCAED; 96 GCAED com originário na APR).
- Tabela 1 (78) e Tabela 2 (19) conferidas: existem, relator GCAED, origem = banco; nenhuma com
  `Exe_DescontoFolha`/`PGE_Processo`; 33 protestadas, 52 suspensas (MS 0807247-93).
- Remanescente (c): **003380/2024** (origem 101636/2019; GCAED; suspenso; R$ 9.829,92).
- Divergências: originários **não localizados** no Ev. 103 — 009621/2016 (Tab. 1 → 001385/2022),
  014245/2016 (Tab. 2 → 000104/2022), 014175/2016 (Tab. 2 → 000106/2022).
- Fora do despacho: 79 execuções GCAED sem originário na APR; 131 de outros relatores com originário na APR.

## Próximo ciclo (quando o usuário mandar)
1. Conferir `setor_atual` do 96/2022 = CCD e os 78 com `IdProcessoApensador` = 96/2022.
2. Skill `enviar-informacao`: distribuir → cadastrar `000096_2022/informacao_000096_2022.pdf` com anexo
   `levantamento_96_2022.xlsx` → assinar → publicar → tramitar DIP, movimentação "ENVIO AO MPC".
3. Item b: decidir a juntada na APR (DAP tramita à DIP, ou DAP junta `apr_3474_2021/certidao_003474_2021.pdf`, que já traz a cópia do despacho)).
