---
name: nereu-presidente-ipern
description: Nereu Batista Linhares é presidente do IPERN; citações de 5 dias ao IPERN contam como dele na análise planilha_nereu
metadata: 
  node_type: memory
  type: project
  originSessionId: 73526d54-64a4-4271-897d-b65629111654
---

Na análise de débitos do Nereu (`scripts/analise/planilha_nereu.ipynb`), o **Nereu Batista
Linhares (CPF 13006444434) é presidente do IPERN** — então citações de 5 dias endereçadas ao
**IPERN** são consideradas citações a ele.

**Por quê:** muitas citações de cumprimento/pagamento nos processos dele são emitidas em nome do
IPERN (a pessoa jurídica), não do CPF.

**Como aplicar:** o IPERN tem mais de um cadastro em `GenPessoa` (ex.: CNPJ `08242034000102` e
`08242034000285`) — casar pela **raiz do CNPJ `08242034`** (`LEFT(Documento,8)`), não por um CNPJ
único. A coluna `destinatario_citacao` da aba Processos mostra se a citação foi a 'Nereu' ou
'IPERN'; `diag_citacao` explica os processos sem citação 5d (sem citação / só outro prazo /
C05 para terceiro). Cuidado: presidentes do IPERN citados pelo **CPF próprio** (ex.: José Marlício
Diógenes de Paiva, CPF 00352691468) NÃO entram automaticamente — são tratados como terceiros.
Ver [[cit-citacoes-authoritative-source]].
