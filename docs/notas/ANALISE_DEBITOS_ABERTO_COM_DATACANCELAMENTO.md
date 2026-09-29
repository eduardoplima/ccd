# Débitos em aberto com DataCancelamento preenchida: análise da CCD

**Data:** 28/09/2026
**Origem:** demanda da TI. O sistema encontrou débitos com `CodigoStatusDivida = 1` (Em Aberto) e `DataCancelamento` preenchida:

```sql
SELECT top 100 '//// Iddebito: '+CAST(iddebito as VARCHAR(10)), p.numero_processo, p.ano_processo, d.DataCancelamento, d.ObservacaoCancelamento
FROM exe_debito d (NOLOCK)
INNER JOIN processos p (NOLOCK) ON p.idprocesso = d.IdProcessoOrigem
WHERE codigostatusdivida = '1' AND DataCancelamento IS NOT NULL
ORDER BY DataCancelamento
```

Encaminhamento pedido pela TI:
- débito **em aberto**: a TI remove os dados de cancelamento (`DataCancelamento`, `UsuarioCancelamento`, `ObservacaoCancelamento`);
- débito **cancelado**: a TI conclui o cancelamento (altera o `CodigoStatusDivida`).

**Método:** consultas de leitura em `Exe_Debito` (inclusive a cadeia `IdDebitoAnterior`), `Exe_DebitoPessoa`, `PGE_Processo` e leitura das peças dos processos de origem e de execução.

---

## 1. Resultado

| IdDébito | Processo (origem → execução) | Responsável | Tipo / valor original | Situação real | Ação |
|---|---|---|---|---|---|
| 2607 | 007309/2002 → 000297/2015 | Espólio de Aluízio Elói Rodrigues | multa, R$ 2.050,00 | Multa inscrita em dívida ativa pela PGE. A execução foi arquivada (art. 209, V, RI) por despacho do Cons. Gilberto Jales em 06/04/2022. | **Em aberto**: remover dados de cancelamento |
| 266 | 010797/2007 → 000727/2015 | Elizeu Jalmir de Macedo | ressarcimento, R$ 356.610,77 | Execução em curso (setor PROC_EXSOB). O credor não deu retorno sobre o ressarcimento (despacho DAE de 23/11/2018). | **Em aberto**: remover dados de cancelamento |
| 164 | 002907/1993 → 000789/2015 | Djalma Gorgônio de Medeiros | ressarcimento, R$ 167,97 | Execução sobrestada (art. 44 da Res. 013/2015, despacho do relator de 09/08/2017). Continua pendente junto ao credor. | **Em aberto**: remover dados de cancelamento |
| 165 | 002907/1993 → 000789/2015 | Djalma Gorgônio de Medeiros | multa, R$ 3.500,00 | Multa inscrita na PGE (despacho DAE de 26/11/2018). Execução sobrestada. | **Em aberto**: remover dados de cancelamento |
| 166 | 002907/1993 → 000789/2015 | Djalma Gorgônio de Medeiros | multa percentual (100%), R$ 167,97 | Mesma situação da 165. | **Em aberto**: remover dados de cancelamento |
| 455 | 002002/2004 → 001879/2015 | Maria da Conceição Fernandes de Oliveira | multa, R$ 300,00 | Inscrita em dívida ativa (despacho DAE de 22/03/2019). A execução foi arquivada em 2023 por causa da inscrição. O débito pago foi a 456, de Isaura Amélia Rosado Maia. | **Em aberto**: remover dados de cancelamento |
| 3509 | 011853/2002 → 003609/2015 | José Marcílio Pessoa | multa, R$ 8.166,80 (saldo da 3507, paga parcialmente) | Inscrita em dívida ativa. A execução foi arquivada por despacho do Cons. Gilberto Jales em 07/04/2022. | **Em aberto**: remover dados de cancelamento |
| 3617 | 011849/2002 (sem processo de execução) | **nenhum** (sem registro em `Exe_DebitoPessoa`) | multa, R$ 300,00 | A Decisão nº 2.736/2016-TC reconheceu a prescrição da pretensão executória das multas do Acórdão 219/2007. O registro também não tem responsável e foi "cancelado" 1 minuto depois de incluído. | **Cancelar**: Cancelada por prescrição (cód. 6) |
| 15322 | 008002/2002 → 007425/2019 | Josemar França | ressarcimento, R$ 24.880,20 | O Acórdão 149/2026-TC, item "a", reconheceu o exaurimento quanto ao ressarcimento, *"mantendo-se as dívidas em aberto até sua eventual desconstituição e/ou baixa dos respectivos cadastros por decisão judicial"*. Só as multas prescreveram (15321 e 15323 já estão com cód. 6). | **Em aberto**: remover dados de cancelamento. A observação "Decisão no Acórdão 149/2026" foi gravada por engano. |
| 15324 | 008002/2002 → 007425/2019 | Josemar França | ressarcimento, R$ 46.240,04 | A CCD já cancelou em 23/09/2026 (cód. 15, "Ressarcimento cadastrado em lugar de obrigação de fazer"). | **Nada a fazer**: já sai da consulta |
| 15325 | 008002/2002 → 007425/2019 | Josemar França | ressarcimento, R$ 584.107,57 | Idem 15324. | **Nada a fazer**: já sai da consulta |
| 26997 | 005294/2010 → 005275/2019 | José Renato Teixeira de Souza | multa, R$ 9.265,48 (débito vigente da cadeia 10851 → … → 26408 → 26997) | O despacho decisório do Cons. Paulo Roberto (DOE 19/12/2025) reconheceu a prescrição **só das multas de Geraldo Menezes da Silva** (10848 e 10850, já com cód. 6). Os parcelamentos suspenderam a prescrição da multa de José Renato, que está inscrita em dívida ativa (CDA nº 00000711012400, de 11/01/2024). | **Em aberto**: remover dados de cancelamento (gravados por engano em 19/01/2026) |
| 28084 | 200165/2023 → 002732/2025 | Manoel dos Santos Bernardo | multa, R$ 20.585,16 | Há certidão de cancelamento de 09/01/2026 (evento 53), por "Erro de Cadastro", com a observação "será cadastrada novamente como multa cominatória". A multa foi recadastrada como débito 29029 (tipo 5, R$ 20.585,16). | **Cancelar**: Cancelada por Erro de Cadastro (cód. 15), como já certificado |

**Totais (13 débitos):**
- **9 em aberto** (remover dados de cancelamento): 2607, 266, 164, 165, 166, 455, 3509, 15322, 26997;
- **2 a cancelar**: 3617 (cód. 6, prescrição) e 28084 (cód. 15, erro de cadastro);
- **2 já cancelados**: 15324 e 15325 (cód. 15, desde 23/09/2026).

---

## 2. Causa provável

- **Lote de 2015** (2607, 266, 164–166, 455, 3509, 3617): a `DataCancelamento` cai no mesmo minuto em que o processo de execução foi instaurado ou em que o débito foi recadastrado. Exemplos: a 266 foi "cancelada" às 09:03 de 16/01/2015 e a 2650 (multa de 10% do mesmo processo) foi criada às 09:04; a 3509 foi criada logo após a baixa parcial da 3507. É um artefato do sistema antigo, não um cancelamento de fato. Nenhum desses débitos tem certidão de cancelamento nos autos.
- **2026** (15322, 26997, 28084): o cancelamento foi iniciado na tela, mas não foi concluído. A data e a observação foram gravadas, e o status continuou "Em Aberto".

---

## 3. Achado fora da lista

- **3618**: processo 011849/2002, João Epaminondas de Araújo Neto, multa de R$ 6.150,00. Continua Em Aberto e sem `DataCancelamento`, embora a Decisão nº 2.736/2016-TC tenha reconhecido a prescrição das multas e mandado dar baixa na responsabilidade. O processo foi arquivado em 16/11/2017. Deve ser **cancelado por prescrição (cód. 6)**, junto com a 3617.
- A consulta da TI não pega casos como esse, em que a decisão de cancelamento existe mas o débito não recebeu nenhuma marca de cancelamento. Uma varredura de débitos Em Aberto em processos arquivados com decisão de prescrição cobriria esses casos.

---

## 4. Fontes

| Processo | Evento | Peça |
|---|---|---|
| 000297/2015 | 40 / 44 | Parecer MPC nº 446/2022-PG e despacho GCGIL (06/04/2022): arquivamento após inscrição em dívida ativa |
| 003609/2015 | 29 / 33 | Parecer MPC nº 426/2022-PG e despacho GCGIL (07/04/2022): idem |
| 000727/2015 | 38 | Despacho DAE (23/11/2018): ressarcimento sem resposta, multa inscrita |
| 000789/2015 | 38 / 41 | Despacho do relator (09/08/2017): sobrestamento; despacho DAE (26/11/2018): multa inscrita |
| 001879/2015 | 30 / 31 / 45 / 52 | Baixa e quitação da 456 (Isaura); despacho de inscrição em dívida ativa de Maria da Conceição (22/03/2019); arquivamento pelo GCPRO (2023) |
| 011849/2002 | 16 / 28 | Decisão nº 2.736/2016-TC (prescrição das multas); arquivamento (16/11/2017) |
| 007425/2019 | 64 / 75 | Acórdão nº 149/2026-TC; informação CCD "Prescrição e Arquivamento" (multas canceladas, ressarcimento mantido) |
| 005275/2019 | 117 / 121 / 127 | Parecer MPC; despacho decisório GCPRO (DOE nº 3923, 19/12/2025); informação CCD (só as multas de Geraldo Menezes canceladas) |
| 002732/2025 | 53 | Certidão de cancelamento da dívida 28.084 (09/01/2026) |
