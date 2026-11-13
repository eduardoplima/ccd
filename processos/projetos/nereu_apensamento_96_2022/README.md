# Despacho do Evento 63 do 000096/2022 (GCAED, 11/11/2026) — reunião das execuções do Nereu abrangidas pela APR 003474/2021

O Relator acolheu **parcialmente** a proposta da CCD (Ev. 60): reúne ao 96/2022 só as execuções de multa do
Nereu cujo **originário está no Evento 103 da APR 003474/2021** e **sem atos efetivos de cobrança**
(desconto em folha implantado / remessa ao MPC), por *bis in idem* com a APR (Ac. 162/2022-TC). O
arquivamento vai ao colegiado após manifestação da DIP e parecer do MPC.

| Item | Quem | O quê | Estado (13/11/2026) |
|---|---|---|---|
| a | assessoria GCAED | apensar as 78 da Tabela 1 ao 96/2022 | pendente: 96/2022 já está na **CCD** (13/11) sem os apensos — conferir `IdProcessoApensador` |
| b | DIP | juntar cópia do despacho na APR + certidão dos 19 originários da Tabela 2 | **certidão gerada** com o despacho apensado (`apr_3474_2021/certidao_003474_2021.pdf`), não juntada — APR está na DAP |
| c | DIP | revisar o levantamento pelo Ev. 103 e reunir remanescentes | **feito**: único remanescente 003380/2024 (apontado na informação; está no GCAED) |
| d | DIP | manifestar-se sobre o arquivamento | **informação gerada** (13/11, levantamento corrigido), favorável, com fluxograma (`000096_2022/`), não cadastrada |
| e | DIP | encaminhar ao MPC | pendente: 96/2022 na CCD → ciclo e-Contas, tramitar DIP "ENVIO AO MPC" |

## Rodar
```
.venv/Scripts/python.exe processos/projetos/nereu_apensamento_96_2022/levantamento.py      # xlsx + json + md
.venv/Scripts/python.exe processos/projetos/nereu_apensamento_96_2022/gerar_documentos.py  # certidão + informação
```

## Levantamento (13/11/2026)
- 489 originários no Ev. 103; 477 execuções do Nereu (178 GCAED; 99 GCAED com originário na APR).
  A planilha do Ev. 103 escreve alguns números sem zeros à esquerda (`9621/2016`) ou com sete dígitos
  (`0003499 / 2017`): o parser lê a linha inteira e normaliza para 6 dígitos — a versão de 12/11 (469) perdia 20
  originários e apontava 3 falsas "divergências" (parágrafo e Quadro 2 removidos da informação e da certidão).
- Tabela 1 (78) e Tabela 2 (19) conferidas: existem, relator GCAED, origem = banco; nenhuma com
  `Exe_DescontoFolha`/`PGE_Processo`; 33 protestadas, 52 suspensas (MS 0807247-93).
- Remanescente (c): **003380/2024** (origem 101636/2019; GCAED; suspenso; R$ 9.829,92).
- Fora do despacho: 79 execuções GCAED sem originário na APR; 135 de outros relatores com originário na APR.
- `levantamento.py` aborta se algum originário das Tabelas ficar fora do Ev. 103 (seria divergência real).

## Próximo ciclo (quando o usuário mandar)
1. Conferir `setor_atual` do 96/2022 = CCD e os 78 com `IdProcessoApensador` = 96/2022.
2. Skill `enviar-informacao`: distribuir → cadastrar `000096_2022/informacao_000096_2022.pdf` com anexo
   `levantamento_96_2022.xlsx` → assinar → publicar → tramitar DIP, movimentação "ENVIO AO MPC".
3. Item b: decidir a juntada na APR (DAP tramita à DIP, ou DAP junta `apr_3474_2021/certidao_003474_2021.pdf`, que já traz a cópia do despacho)).
