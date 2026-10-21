## Texto do prompt

```text
Você lê a resposta de um órgão público a uma notificação do TCE/RN para desconto em folha
de pagamento de uma multa ou débito. Extraia SOMENTE o que o texto afirma sobre o valor do desconto:
- valor total descontado/implantado (ou a implantar) em folha;
- se é parcelado, cada parcela com competência (mês/ano) quando o texto informar;
- o trecho literal (uma frase, copiada exatamente) de onde tirou o valor.
Não invente valores nem competências. Se o texto não informa o valor do desconto em folha
(ex.: só acusa recebimento, ou nega vínculo), responda encontrou=false e deixe o resto vazio.
Valores em reais no formato numérico (R$2.477,35 → 2477.35).
O processo pode ter mais de um responsável e a resposta pode tratar de outra pessoa. Informe em
`beneficiario` o nome de quem sofre o desconto, como escrito no texto. Só responda encontrou=true
se o desconto incide sobre {responsavel}. Se o texto tratar de várias pessoas, o valor total e as
parcelas são SÓ os de {responsavel}; ignore os valores das demais.

Texto:
"""{texto}"""
```

## Schema de saída

```python
class ParcelaExtraida(BaseModel):
    numero: int = Field(description="Número sequencial da parcela, começando em 1")
    mes: Optional[int] = Field(None, description="Mês de competência (1-12), se informado")
    ano: Optional[int] = Field(None, description="Ano de competência, se informado")
    valor: Optional[float] = Field(None, description="Valor da parcela em reais")


class RespostaDescontoFolha(BaseModel):
    encontrou: bool = Field(
        description="True só se o texto informa o valor efetivamente descontado/implantado em folha"
    )
    valor_total: Optional[float] = Field(
        None, description="Valor total descontado ou a descontar, em reais (ex.: 2477.35)"
    )
    parcelado: bool = Field(False, description="True se o desconto é em parcelas mensais")
    parcelas: list[ParcelaExtraida] = Field(
        default_factory=list, description="Parcelas, quando parcelado; vazio quando valor único"
    )
    trecho: str = Field(
        "", description="Cópia literal do trecho do texto que informa o valor (uma frase)"
    )
    beneficiario: Optional[str] = Field(
        None, description="Nome da pessoa em cujos vencimentos/proventos incide o desconto"
    )
```