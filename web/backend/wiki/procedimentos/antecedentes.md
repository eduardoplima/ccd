# POP-CCD-007 — Antecedentes

| Campo | Valor |
|---|---|
| **Código** | POP-CCD-007 |
| **Versão** | 1.0 |
| **Data de emissão** | 20/08/2026 |
| **Elaborado por** | CCD |
| **Aprovado por** | _pendente de aprovação_ |
| **Próxima revisão** | 08/2027 |

## 1. Objetivo

Atender às solicitações dos relatores de informação sobre os antecedentes de responsáveis (outros processos e dívidas vinculadas), do levantamento à entrega da informação assinada no gabinete solicitante.

## 2. Escopo

Processos na CCD com o marcador "Antecedentes".

## 3. Referências normativas

- Res. nº 042/2024-TCE, art. 32, V — atividades inerentes à área de competência da CCD.
- Res. nº 013/2015-TCE (dívidas e execuções consultadas no levantamento).

## 4. Definições e siglas

- **Trânsito em julgado**: condenações definitivas consultadas por CPF do responsável.
- **Gabinetes** (siglas de providência): GAANA (Ana), GCAED (Antônio Ed), GCCTH (Carlos), GCGEO (George), GCGIL (Gilberto), GAMAR (Marco), GCPRO (Paulo), GCREN (Renato).
- **Web PKI / A3**: assinatura digital com certificado em token.

## 5. Responsabilidades

- **Servidor da CCD**: gerar as informações, revisar (gate de qualidade), distribuir, cadastrar, assinar e tramitar.
- **Gabinete solicitante**: origem do pedido e destinatário da informação (padrão: GAANA).

## 6. Recursos e sistemas

- Pipeline automatizado do repositório da CCD (`gerar_antecedentes`: descoberta por marcador → despacho-fonte → extração dos responsáveis por LLM → débitos transitados em julgado por CPF → docx/PDF).
- Área Restrita: distribuição, cadastro de informação digitalizada, tramitação.
- Assinatura A3 via Web PKI (navegador).

## 7. Descrição das atividades

1. **Gerar**: rodar a geração com `--dry-run` para listar os candidatos (marcador "Antecedentes" na CCD); depois gerar as informações — uma por processo, em pasta datada dedicada.
2. **Gate de revisão** (obrigatório — os documentos vão ao gabinete de um Conselheiro): conferir responsável extraído, tabela de condenações e ausência de código cru **antes** de subir na Área Restrita.
3. **Distribuir** os processos para o usuário — **sempre antes de cadastrar** (o cadastro de informação digitalizada só abre para processo distribuído).
4. **Cadastrar** as informações digitalizadas em lote a partir da pasta gerada.
5. **Assinar** com token A3 (Web PKI), em lotes de até 20; verificação: o processo sai da lista de pendentes.
6. **Tramitar** à DIP com a providência **"ENVIO A \<gabinete\>"** (padrão "ENVIO A GAANA"); verificação: os processos saem da listagem da CCD.

Regra transversal: **cada ação irreversível (cadastro, assinatura, tramitação) tem `--dry-run` conferido antes da execução real**.

## 8. Registros

- Informações de antecedentes (PDF) cadastradas e assinadas nos processos.
- Tramitação registrada com a providência do gabinete.
- Pasta datada com os documentos gerados (`saidas/automacao/antecedentes/`).

## 9. Pontos de controle e exceções

> **Lacuna:** o cadastro de decisões consolidado ainda não existe — o levantamento usa as consultas disponíveis (trânsitos em julgado por CPF, dívidas cadastradas).

Armadilhas conhecidas (checar no gate de revisão):

- **Despacho-fonte errado**: o pipeline pega a informação mais recente, que às vezes é um Termo de Apensamento e não a solicitação de antecedentes. Sintoma: responsável extraído é um servidor do TCE. Correção: localizar a solicitação real e regenerar.
- **Homônimos**: nomes iguais com CPFs diferentes misturam débitos; conferir que o CPF do responsável bate com o do processo.
- **Processos de CONTAS**: os combos de relatório de auditoria são obrigatórios no cadastro; sem preenchê-los (com "N"), a inclusão falha silenciosamente.
- Alertas JS de data/numérico na Área Restrita são falso-positivos; confiar nas verificações reais (identificador retornado, item que sai da lista).
- Antecedentes **adiciona** informação nova; não substitui informação anterior.

## 10. Histórico de revisões

| Versão | Data | Alteração |
|---|---|---|
| 1.0 | 20/08/2026 | Versão inicial — formato POP (ISO 10013:2021), incorporando o ciclo completo na Área Restrita. |
