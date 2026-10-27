---
name: excluir-suspensao
description: Exclui a suspensão de débitos na Área Restrita (Administrativo / Acompanhamento de Decisões / Gerenciar Dívidas, aba "Dívidas Suspensas" → Manutenção → Observações → "Excluir Suspensão"), devolvendo-os a "Dívidas em Aberto". Use quando o usuário pedir para "remover/excluir a suspensão", "passar o débito de suspenso para em aberto" ou "retomar o débito" de um ou mais processos de execução — por padrão os de processos/projetos/nereu_debito_em_aberto_mpc/.
---

# Excluir suspensão de débito (Gerenciar Dívidas)

Uso: `/excluir-suspensao [<projeto> | <numero/ano> ...]`. Sem argumento, o projeto é `processos/projetos/nereu_debito_em_aberto_mpc/`.

Implementação: `AreaRestrita.excluir_suspensao` (`ccd/area_restrita.py`), CLI `excluir-suspensao`. Rodar da raiz com `PYTHONIOENCODING=utf-8`.

## Regras invioláveis

- **Dry-run de todo o lote antes da execução real.** Mostre ao usuário a suspensão encontrada de cada débito (id, início, motivo, processo judicial) e só rode a real depois do ok dele.
- O método só age se o débito estiver na aba **"Dívidas Suspensas"** e tiver **exatamente 1** suspensão cadastrada. Qualquer outra situação gera ERRO, e o processo é pulado. Não force.
- Observação default: **"Débito retomado por determinação do Relator."** (máx. 300 caracteres). Use outra só se o usuário pedir.
- Os alerts "Tamanho de data não permitido / Caracter inválido / numérico" são JS estático (falso positivo). O que vale é a linha "verificado".

## 1. Processos

Os processos são as subpastas `NNNNNN_AAAA/` do projeto, e o número/ano é o do **processo de execução**:

```
ls -d processos/projetos/nereu_debito_em_aberto_mpc/*_*/ | sed -E 's#.*/0*([0-9]+)_([0-9]{4})/#\1/\2#'
```

O débito vem do banco, como a folha vigente da cadeia (`Exe_Debito`, sem cancelamento e sem filho por `IdDebitoAnterior`). Com mais de um débito vigente, o CLI para e pede `--debito <IdDebito>` (aceito só com 1 processo).

## 2. Dry-run

```
.venv/Scripts/python.exe -m scripts.automacao.area_restrita excluir-suspensao <proc> [<proc> ...] \
    --observacao "Débito retomado por determinação do Relator." --dry-run
```

Confira cada linha `suspensão N: início …, motivo …, proc. judicial …`. No lote do Nereu, todas são de 24/07/2025, motivo 2 (decisão judicial liminar), MS 0807247-93.2025.8.20.0000.

## 3. Real

Mesmo comando, sem `--dry-run`. Para cada processo, o método envia `oculto=ES`, consulta de novo e só imprime `verificado: débito N em 'Dívidas em Aberto'` se a mudança aconteceu. Do contrário, imprime ERRO.

## 4. Depois

- O banco (`Exe_Debito.CodigoStatusDivida` 20 → 1) pode demorar a refletir a mudança; a Área Restrita é a fonte autoritativa.
- Próximo passo do lote: `/enviar-informacao` com a informação de `processos/projetos/<projeto>/<NNNNNN_AAAA>/`. Pergunte a providência (ex.: "ENVIO AO MPC").
- Atualize a memória do lote (`nereu-debito-em-aberto-mpc`) com a data e os processos feitos.
