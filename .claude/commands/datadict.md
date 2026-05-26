Gera dicionário de dados em Markdown para um ou mais bancos MSSQL.

Uso: /datadict <banco1> [banco2 ...]

Se nenhum banco for informado, usa os bancos default definidos no script.

Execute o seguinte comando PowerShell no diretório do projeto:

```powershell
.\.venv\Scripts\python.exe -m scripts.analise.dicionario_dados --dbs $ARGUMENTS
```

Se `$ARGUMENTS` estiver vazio, omita o `--dbs` e rode com os defaults:

```powershell
.\.venv\Scripts\python.exe -m scripts.analise.dicionario_dados
```

Após a execução, informe quais bancos foram gerados, quantos objetos e colunas cada um tem, e o caminho do arquivo INDEX.md.
