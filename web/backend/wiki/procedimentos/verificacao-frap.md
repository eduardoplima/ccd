# POP-CCD-011 — Verificação de transferência ao FRAP

| Campo | Valor |
|---|---|
| **Código** | POP-CCD-011 |
| **Versão** | 1.0 |
| **Data de emissão** | 20/08/2026 |
| **Elaborado por** | CCD |
| **Aprovado por** | _pendente de aprovação_ |
| **Próxima revisão** | 08/2027 |

## 1. Objetivo

Conciliar os descontos em folha efetuados pelos órgãos pagadores com os repasses efetivamente creditados ao FRAP, comprovando o recolhimento das multas executadas por desconto em folha.

## 2. Escopo

Processos de execução com desconto em folha implementado ([POP-CCD-004](desconto-em-folha)), no ciclo de marcadores **Implementar → Verificar transferência FRAP (5953) → Fim**.

## 3. Referências normativas

- Res. nº 013/2015-TCE, art. 25, § 1º, I — desconto com crédito ao FRAP; art. 25, §§ 3º e 4º — o órgão deve comprovar o desconto e o crédito ao FRAP em **15 dias**.

## 4. Definições e siglas

- **FRAP**: Fundo de Reaparelhamento do TCE/RN.
- **Quadro de descontos**: descontos registrados na folha do órgão (SIAI Pessoal, rubrica TCE/FRAP).
- **Quadro de repasses**: créditos no extrato bancário do FRAP (por CPF do depositante) ou baixas de parcela registradas no controle de desconto em folha (`FRAPDescontoFolhaParcela`).

## 5. Responsabilidades

- **Servidor da CCD**: levantar os quadros, confrontar os totais, elaborar a informação de conciliação e registrar o resultado.
- **Órgão pagador**: comprovar desconto e repasse (art. 25, §§ 3º e 4º).

## 6. Recursos e sistemas

- SIAI Pessoal (folha dos órgãos — quadro de descontos).
- Módulo FRAP da webapp da CCD / extrato bancário do FRAP (quadro de repasses).
- Rastreio automatizado no repositório da CCD (`rastreio_verificar_frap` + geração das informações de conciliação por processo).
- Área Restrita (marcador 5953, informações).

## 7. Descrição das atividades

1. Identificar os processos com desconto em folha implementado e sem conciliação (rastreio; aplicar o marcador **"Verificar transferência FRAP" (5953)**).
2. Para cada processo, levantar:
   1. **Quadro de descontos em folha** — SIAI Pessoal, rubrica TCE/FRAP, por competência;
   2. **Quadro de repasses** — extrato do FRAP por CPF do depositante ou baixas em `FRAPDescontoFolhaParcela`.
3. **Confrontar os totais** dos dois quadros.
4. Elaborar a **informação de conciliação** nos autos: "Trata-se de…" com processo, assunto, responsáveis e valor atualizado da multa; os dois quadros com o confronto; ou parágrafo explicativo da **ausência de registros**, quando nada foi localizado.
5. Conforme o resultado:
   - **Conciliado e dívida quitada** → seguir o [POP-CCD-012 — Baixa e saldo residual](baixa-saldo-residual);
   - **Desconto cessado sem quitação** ou **repasse não localizado** → notificar o órgão (via DE) pela comprovação do art. 25, §§ 3º e 4º, e manter o acompanhamento;
   - **Desconto em curso** → manter no acompanhamento até a quitação.
6. Ao concluir, retirar o marcador 5953 e registrar o desfecho.

## 8. Registros

- Informação de conciliação (com os quadros) cadastrada nos autos.
- Marcador 5953 aplicado/retirado conforme o estágio.
- Registro da conciliação no histórico do débito (`Exe_HistoricoDebito`), quando aplicável.

## 9. Pontos de controle e exceções

- O desconto pode ser feito **em pares de processos** com uma única transferência ao FRAP cobrindo os dois — conciliar o par junto, não cada processo isolado.
- O campo de CPF do depositante no extrato pode vir vazio na grande maioria dos lançamentos — usar as vias alternativas (documento da OB, `FRAPDescontoFolhaParcela`).
- O pagamento por desconto em folha **não** aparece nos retornos de boleto — a conciliação é a única comprovação.
- Descontos cessados há meses sem quitação do débito indicam pendência a investigar junto ao órgão.

## 10. Histórico de revisões

| Versão | Data | Alteração |
|---|---|---|
| 1.0 | 20/08/2026 | Versão inicial — POP novo (ISO 10013:2021), a partir do rastreio e das informações de conciliação em uso. |
