# Números institucionais do CGAD — resposta ao "Subjetivo / Quanto?" (Justificativa, p. 13)

Levantamento de 2026-07-22, bases `processo` (10.24.0.77) e `BdDIP`, consultas
somente-leitura. Scripts one-off da sessão; a query de decisões/ano é a mesma do
`HANDOFF.md` ("Como reconferir cobertura").

## Números obtidos

| Ano | Decisões colegiadas | Com obrig./recom. cadastrada | Sujeitas a cadastro¹ |
|---|---:|---:|---:|
| 2020 | 1.637 | 1 | — |
| 2021 | 4.204 | 3 | — |
| 2022 | 4.769 | 4 | — |
| 2023 | 3.657 | 435 | — |
| 2024 | 3.718 | 605 | **757** |
| 2025 | 3.282 | 644 | **752** |
| 2026 (até jul.) | 1.655 | 370 | 410 |

¹ União de: item detectado pelo NER (obrigação, recomendação, multa ou
ressarcimento) ∪ já cadastrado nas tabelas finais (`BdDIP.dbo.Obrigacao` /
`Recomendacao`, `Cancelado IS NULL OR = 0`). Só é confiável para 2024–2026
(cobertura NER de 84–98%).

- **Média de decisões 2023–2025**: ≈ 3.552/ano.
- **Estoque atual do CGAD**: 1.712 obrigações + 1.172 recomendações vigentes = **2.884 itens**.
- **Taxa**: ~1 em cada 5 decisões (20–23%) exige cadastramento no CGAD.

## Caveats

- 1.812 decisões sem `DataSessao` ficam fora da conta anual — os números são **piso**.
- O quase-zero de 2020–2022 reflete que o registro sistemático no CGAD é recente
  (backfill em curso), não ausência de obrigações nesses anos.
- Proxies que **não** funcionaram para os itens 2 e 3 da crítica: as tabelas
  staging não têm nenhum par `DataReserva`/`DataRevisao` preenchido (amostra
  zero) e os únicos operadores registrados (`admin`, `eduardo`, `antonietta`)
  são da webapp nova, não a equipe histórica.

## Pendente — pedir à secretaria/setor responsável pelo CGAD

1. **Tempo médio de cadastramento manual** por decisão (ou por item);
2. **Nº de servidores** envolvidos no cadastramento.

## Texto para a Justificativa

**Versão segura (só dados do banco — usável já):**

> No TCE/RN, o Tribunal profere cerca de 3,5 mil decisões colegiadas por ano
> (média de 3.552 no triênio 2023–2025, conforme a base de dados processual).
> Dessas, entre 600 e 750 por ano — aproximadamente uma em cada cinco — contêm
> obrigações, recomendações, multas ou ressarcimentos que exigem cadastramento
> individualizado e acompanhamento no CGAD (757 decisões em 2024 e 752 em
> 2025). O estoque de itens atualmente acompanhados soma 2.884 registros
> vigentes, entre obrigações e recomendações.

**Versão completa (preencher quando o setor responder):**

> Considerando as cerca de 750 decisões anuais que exigem cadastramento no
> CGAD e um tempo médio de **[Y]** minutos por decisão, o cadastramento manual
> consome aproximadamente **[750 × Y ÷ 60]** horas de trabalho por ano,
> executadas por uma equipe de **[N]** servidores.
