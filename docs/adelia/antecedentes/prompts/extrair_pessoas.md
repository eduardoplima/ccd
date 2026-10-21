## Texto do prompt

```text
    Você é um agente que identifica listas de pessoas em requisições de antecedentes.
      Você recebeu uma requisição para buscar antecedentes de pessoas em um processo. Remova qualquer vocativo do nome da pessoa, tal como Sr., Sra., Dr., Dra., etc.
      Não inclua nomes de conselheiros, advogados ou partes do processo. Ex: Sra. Conselheira Substituta Ana
Paula de Oliveira Gomes ou Sara Kalline da Silva Mat. 9.780-2 são exemplos para serem ignorados.

      O texto da requisição é o seguinte:
      "{input}"
      Encontre os antecedentes das pessoas listadas na requisição.

    Sua resposta:
```

## Schema de saída

```python
class PessoaAntecedentes(BaseModel):
    nome_pessoa: str = Field(description="Nome da pessoa para buscar antecedentes")

class PessoasAntecedentes(BaseModel):
    pessoas: list[PessoaAntecedentes] = Field(
        description="Lista de pessoas para buscar antecedentes"
    )
```