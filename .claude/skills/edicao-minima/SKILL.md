---
name: edicao-minima
description: Regras obrigatórias ao alterar arquivos existentes neste repositório — especialmente documentos gerados (.docx) e scripts de informações/despachos. Use SEMPRE antes de editar qualquer arquivo já existente, regenerar um documento, ou quando o usuário pedir uma alteração pontual ("mude só isso", "somente altere", "mantenha o texto").
---

# Edição mínima com preservação de versão

Duas regras invioláveis ao alterar qualquer coisa neste projeto:

## 1. Só mexa nos pontos especificamente pedidos

- Altere **exatamente** o que o usuário pediu — nada de "aproveitar" para reescrever, renumerar, remover ou "melhorar" trechos vizinhos.
- Se uma alteração pedida parecer exigir mudanças em outros pontos (numeração, referências cruzadas, pontuação de item final), **pergunte ou avise antes** — não decida sozinho.
- Conteúdo removido/alterado em turnos anteriores por decisão minha (não pedida) deve ser tratado como erro: restaurar exige confirmação do usuário, nunca reintroduzir silenciosamente.
- Atenção especial a documentos que o usuário edita à mão (Word): regenerar um `.docx` a partir do script **sobrescreve as edições manuais dele**. Antes de regenerar, confirme que o script reflete a última versão desejada.

## 2. Sempre preserve a versão anterior em outro arquivo

- Antes de sobrescrever um arquivo gerado (`.docx`, `.xlsx`, `.pdf`), copie a versão atual para um arquivo de backup com timestamp: `<nome>_YYYYmmdd_HHMMSS.<ext>` na mesma pasta.
- Em scripts geradores, o padrão é embutir o backup antes do `doc.save(OUT)` (exemplo em `scripts/processos/000068_2024/gerar_informacao.py`):

```python
out_path = Path(OUT)
if out_path.exists():
    bak = out_path.with_name(f"{out_path.stem}_{datetime.now():%Y%m%d_%H%M%S}{out_path.suffix}")
    shutil.copy2(out_path, bak)  # copy2, não rename: funciona com o arquivo aberto no Word
doc.save(OUT)
```

- Novo script gerador de documento? Incluir esse bloco desde a primeira versão.
- Se o arquivo de saída estiver aberto no Word (lockfile `~$...` na pasta), o `save` falha com `PermissionError` — avise o usuário para fechar o arquivo; **nunca** mate o processo do Word.

## 3. O texto dos documentos é jurídico — nunca use termos técnicos de TI

Nos textos das informações, despachos e demais peças geradas, **nunca** mencionar nomes de views, tabelas, bases de dados ou scripts utilizados na apuração (ex.: `vwDespesaPagamento`, `BdDIP`, `Exe_Debito`, nomes de arquivos `.py`/`.sql`).

- Referir-se às fontes por sua denominação institucional: "dados oficiais do SIAI (Anexo 14)", "sistemas informatizados desta Corte", "registros do sistema de processos", "consulta aos dados prestados pelos jurisdicionados".
- Termos técnicos ficam no código, nos comentários do script e nos arquivos `.sql` de documentação — nunca no texto da peça.
- Ao revisar texto existente, se encontrar termo técnico de TI, apontar ao usuário (não corrigir por conta própria — regra 1).
