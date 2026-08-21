# POP-CCD-010 — Reabertura de parcelamento

| Campo | Valor |
|---|---|
| **Código** | POP-CCD-010 |
| **Versão** | 0.1 (minuta) |
| **Data de emissão** | 20/08/2026 |
| **Elaborado por** | CCD |
| **Aprovado por** | _pendente de aprovação_ |
| **Próxima revisão** | 08/2027 |

> **MINUTA PARA VALIDAÇÃO.** Não há fluxo de reabertura documentado em norma nem em manual anterior — a reabertura é ato de gestão suportado pelo sistema. As etapas da seção 7 foram propostas a partir do modelo de dados e dos efeitos observados; devem ser validadas pelo coordenador antes da aprovação.

## 1. Objetivo

Disciplinar a reabertura de parcelamento de multa quando o parcelamento anterior foi encerrado por inadimplência e o responsável requer nova oportunidade de pagamento parcelado, garantindo registro rastreável (autor, data e justificativa) e a integridade da cadeia de débitos.

## 2. Escopo

Processos de execução com parcelamento **encerrado por inadimplência** cujo responsável formula novo pedido de parcelamento, antes do êxito de outra modalidade de execução ([protesto](protesto), [desconto em folha](desconto-em-folha), [dívida ativa](divida-ativa)).

## 3. Referências normativas

- Res. nº 013/2015-TCE, art. 20 — parcelamento (requerimento no Portal do Responsável; deferimento pelo pagamento da 1ª parcela; vencimento antecipado do saldo na falta de parcela); art. 21 — certidão de quitação; art. 38 — alimentação do CGAD com as informações de parcelamentos.
- Regimento Interno, art. 337, §§ 1º e 2º — valor mínimo e número de parcelas.
- **A reabertura não tem previsão normativa expressa** — é ato de gestão registrado no sistema; recomenda-se deliberação do coordenador em cada caso.

## 4. Definições e siglas

- **Reabertura**: cancelamento do débito vinculado ao parcelamento encerrado e criação de novo débito/parcelamento sobre o saldo atualizado, com justificativa registrada.
- **Cadeia de débitos**: versões sucessivas do mesmo crédito encadeadas por `IdDebitoAnterior`; **a situação vigente é a da folha da cadeia (nó sem filho), não a da raiz**.
- **Situação do parcelamento** (`Exe_Parcelamento.SituacaoParcelamento`, domínio do dicionário de dados): 1 – Aguardando Pagamento 1ª Parcela · 2 – Ativo · 3 – Encerrado por inadimplência · 4 – Quitado · 5 – Indeferido · 6 – Encerrado por Quitação do valor Integral.

## 5. Responsabilidades

- **Responsável (devedor)**: requerer o novo parcelamento.
- **Servidor da CCD**: verificar condições, registrar a reabertura com justificativa, atualizar marcadores, CADINQ e CGAD.
- **Coordenador da CCD**: deliberar sobre o pedido (marcador "Deliberação do Coordenador").

## 6. Recursos e sistemas

- Área Restrita — gestão de dívidas e parcelamentos; Portal do Responsável (requerimento).
- Sistema de execução: `Exe_Parcelamento` (campos `JustificativaReabertura`, `DataReabertura`), `Exe_Debito` (campos `Reaberto`, `DataReabertura`, `JustificativaReabertura`, `UsuarioReabertura`), `Exe_ParcelamentoParametros` (parâmetros vigentes: nº máximo de parcelas, valor mínimo).

## 7. Descrição das atividades (fluxo proposto)

1. **Receber o requerimento** do responsável (novo pedido de parcelamento sobre dívida com parcelamento anterior encerrado).
2. **Verificar as condições**:
   1. Parcelamento anterior com situação **3 – Encerrado por inadimplência** (não reabrir parcelamento ativo ou quitado);
   2. Saldo devedor atualizado da dívida (débito vigente = folha da cadeia);
   3. Prescrição — o período do parcelamento anterior suspendeu a prescrição; conferir o prazo remanescente;
   4. Estágio das demais modalidades (processo já protestado ou inscrito em dívida ativa exige providências próprias antes da reabertura).
3. **Submeter à deliberação do coordenador** com o histórico do parcelamento anterior (parcelas pagas, data do encerramento).
4. **Registrar a reabertura no sistema**, preenchendo a **justificativa** (obrigatória para rastreabilidade — o sistema grava autor e data): o débito anterior é cancelado com o status próprio ("Cancelada por Reabertura de Parcelamento") e um **novo débito/parcelamento** é criado sobre o saldo atualizado, observados os parâmetros vigentes (`Exe_ParcelamentoParametros`).
5. **Confirmar o deferimento** pelo pagamento da 1ª parcela do novo parcelamento (art. 20, § 2º, por analogia).
6. **Atualizar os controles**: marcador **"Parcelamento em Curso"** ([POP-CCD-009](parcelamento)); [CADINQ](cadinq) refletindo a nova dívida; **CGAD** alimentado com o novo parcelamento (art. 38).

## 8. Registros

- `Exe_Debito`: débito anterior cancelado por reabertura (status "Cancelada por Reabertura de Parcelamento"), com `Reaberto`, `DataReabertura`, `JustificativaReabertura` e `UsuarioReabertura` preenchidos; novo débito criado como filho na cadeia.
- `Exe_Parcelamento`: novo parcelamento com `JustificativaReabertura`/`DataReabertura`.
- Deliberação do coordenador nos autos; CGAD atualizado.

## 9. Pontos de controle e exceções

- **Efeito contábil**: o débito cancelado por reabertura sai da base ativa da carteira (o crédito segue vivo apenas no novo nó). Reabertura **não é perdão de dívida** — o saldo migra integralmente para o novo débito; conferir que o valor do novo parcelamento corresponde ao saldo atualizado.
- **Cadeia**: nunca ler a situação da dívida pela raiz da cadeia; a vigente é a folha. Evitar duplo registro (há histórico de forks na cadeia por duplo clique).
- **Divergência de domínio conhecida**: rótulos de `SituacaoParcelamento` usados no alerta da webapp diferem do dicionário de dados; **prevalece o domínio do dicionário** (seção 4) até a criação da tabela de domínio no sistema.
- Não há limite normativo de reaberturas por dívida — na dúvida sobre pedidos sucessivos com inadimplência reiterada, submeter ao coordenador com o histórico completo.

## 10. Histórico de revisões

| Versão | Data | Alteração |
|---|---|---|
| 0.1 | 20/08/2026 | Minuta inicial — fluxo proposto a partir do modelo de dados; pendente de validação do coordenador. |
