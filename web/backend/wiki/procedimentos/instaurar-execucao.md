# POP-CCD-002 — Instaurar processo de execução

| Campo | Valor |
|---|---|
| **Código** | POP-CCD-002 |
| **Versão** | 1.0 |
| **Data de emissão** | 20/08/2026 |
| **Elaborado por** | CCD |
| **Aprovado por** | _pendente de aprovação_ |
| **Próxima revisão** | 08/2027 |

## 1. Objetivo

Criar um processo de execução para executar as decisões condenatórias (multas e ressarcimentos) de um acórdão dos Conselheiros, com o encaminhamento adequado do processo original e do processo de execução.

## 2. Escopo

Processos na CCD com o marcador "Instaurar Processo de Execução", cuja decisão autorize a execução.

## 3. Referências normativas

- LC Estadual nº 464/2012 (Lei Orgânica do TCE/RN), título VI — execução das decisões.
- Res. nº 013/2015-TCE, Capítulo III (Execução), em especial art. 25 (modalidades de execução) e art. 14 (prazo de manifestação do responsável).
- Res. nº 042/2024-TCE, art. 32, III — cobrança executiva como competência da CCD.

## 4. Definições e siglas

- **CADINQ**: Certidão de Inscrição no Cadastro Informativo de Créditos não Quitados (ver [POP-CCD-003](cadinq)).
- **Citação de 5 dias**: citação para pagamento no prazo de 5 dias, requisito reconhecido pelo sistema.
- **DE**: Diretoria de Expediente (fornece os números de processo e expede notificações).

## 5. Responsabilidades

- **Servidor da CCD**: verificar requisitos, instaurar a execução, gerar e assinar o CADINQ, encaminhar.
- **Relator / departamento responsável**: sanar a ausência de autorização para execução (devolução).
- **DE**: fornecer os números para abertura de processos.

## 6. Recursos e sistemas

Área Restrita — *Administrativo / Acompanhamento de Decisões / Instaurar Processo de Execução*.

## 7. Descrição das atividades

### 7.1 Verificação dos requisitos

1. **Autorização para execução** — quando não há, devolver ao relator ou departamento responsável.
2. **Certidão atestando o trânsito em julgado** emitida.
3. **Citação de 5 dias** realizada (ver exceção na seção 9).
4. **Cadastro correto dos valores** (multas/ressarcimentos), conferidos contra o acórdão.
5. **Cadastro correto do responsável.**
6. Avaliar: **"está perto de prescrever?"**

### 7.2 Instauração

1. Solicitar à DE os possíveis números para abrir processos (pedir alguns números e ter para o trabalho da semana).
2. Inserir o número do processo de execução e referenciar o processo original.
3. Redigir o despacho no campo próprio — é o último parágrafo da certidão (automática), informando o destino do processo. O despacho criado é inserido automaticamente no processo original.
4. Referenciar o Relator.
5. Selecionar os documentos herdados (eventos) do processo original — selecionar todos.
6. Clicar em **"novo processo"** e assinar.
7. Gerar o [CADINQ](cadinq) no processo de execução e assinar o CADINQ.
8. Assinar o documento e instaurar por definitivo.

### 7.3 Encaminhamento do processo original

- **Apenas obrigações de pagar**: encaminhar à relatoria para autorização de arquivamento.
- **Outras obrigações de fazer ou não fazer**: a própria DIP/CCD faz o cadastro e os controles das obrigações (arquivo, monitoramento ou outras providências, conforme a decisão).

### 7.4 Encaminhamento do processo de execução

1. Verificar se o [CADINQ](cadinq) está atualizado.
2. **Apenas ressarcimento**, ou **ressarcimento com multa percentual**: seguir o [POP-CCD-006 — Dívida ativa](divida-ativa).
3. **Multas**: identificar a modalidade de execução, conforme determinação do Relator no acórdão/despacho:
   - [POP-CCD-004 — Desconto em folha](desconto-em-folha) — verificar o vínculo do responsável;
   - [POP-CCD-005 — Protesto](protesto) — marcador "Protesto Eletrônico - Revisar antes de enviar";
   - [POP-CCD-006 — Dívida ativa](divida-ativa).
4. Após protesto e/ou envio para desconto em folha, enviar o processo que possui ressarcimento ao MP de Contas para encaminhamento à PGE/PGM.

## 8. Registros

- Processo de execução instaurado na Área Restrita, com despacho e documentos herdados.
- CADINQ gerado e assinado no processo de execução.
- Despacho inserido automaticamente no processo original.

## 9. Pontos de controle e exceções

> **Limitação do sistema:** existem outras formas de ciência além da citação de 5 dias, mas o sistema só reconhece esta. Processos com outras menções não podem ser instaurados diretamente — abrir chamado manual para corrigir.

> **Melhoria pendente:** automatizar a inclusão dos documentos herdados (hoje é manual).

## 10. Histórico de revisões

| Versão | Data | Alteração |
|---|---|---|
| 1.0 | 20/08/2026 | Versão inicial — conversão ao formato POP (ISO 10013:2021), consolidando instauração e encaminhamentos. |
