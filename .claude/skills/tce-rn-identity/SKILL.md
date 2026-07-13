---
name: tce-rn-identity
description: Aplica a identidade visual oficial do TCE/RN (Tribunal de Contas do Estado do Rio Grande do Norte) em tabelas, gráficos, imagens e documentos jurídicos. Use esta skill SEMPRE que Luiz Henrique pedir para criar tabelas, gráficos, planilhas, apresentações, ou qualquer elemento visual destinado a relatórios técnicos, denúncias, notas de auditoria, ou documentos da DCP/CFP. Também deve ser usada ao criar documentos HTML, PPTX, DOCX, XLSX ou qualquer artefato visual relacionado ao trabalho no TCE/RN.
---

# TCE/RN — Identidade Visual Oficial

## Visão Geral

Esta skill garante que todos os elementos visuais criados para o trabalho no TCE/RN sigam a paleta de cores e o padrão institucional do Tribunal de Contas do Estado do Rio Grande do Norte.

---

## Paleta de Cores Oficial

### Cores Primárias

| Nome | HEX | RGB | Uso |
|------|-----|-----|-----|
| Verde Institucional | `#2E5B3C` | rgb(46, 91, 60) | Cabeçalhos, barras de título, bordas principais |
| Verde Escuro | `#1A3D28` | rgb(26, 61, 40) | Fundo de cabeçalhos, elementos de destaque |
| Verde Médio | `#3D7A52` | rgb(61, 122, 82) | Linhas alternadas de tabela, subtítulos |
| Verde Claro | `#6B9F7E` | rgb(107, 159, 126) | Bordas secundárias, elementos de suporte |

### Cores Secundárias

| Nome | HEX | RGB | Uso |
|------|-----|-----|-----|
| Dourado/Amarelo Institucional | `#C8A84B` | rgb(200, 168, 75) | Destaques, alertas, elementos decorativos, estrela do brasão |
| Dourado Escuro | `#A07830` | rgb(160, 120, 48) | Bordas douradas, ênfase secundária |
| Branco | `#FFFFFF` | rgb(255, 255, 255) | Texto sobre fundos escuros, células de dados |

### Cores Neutras

| Nome | HEX | RGB | Uso |
|------|-----|-----|-----|
| Cinza Escuro | `#333333` | rgb(51, 51, 51) | Texto principal de corpo |
| Cinza Médio | `#666666` | rgb(102, 102, 102) | Texto secundário, legendas |
| Cinza Claro | `#F2F2F2` | rgb(242, 242, 242) | Fundo alternado de linhas de tabela |
| Cinza Borda | `#CCCCCC` | rgb(204, 204, 204) | Bordas de tabela, divisores |

---

## Regras de Aplicação

### Tabelas

- **Cabeçalho**: Fundo `#2E5B3C` (Verde Institucional), texto `#FFFFFF` (Branco), negrito
- **Linhas alternadas**: Fundo `#F2F2F2` (Cinza Claro) para linhas ímpares, `#FFFFFF` para pares
- **Bordas**: `#CCCCCC` (Cinza Borda) para linhas internas; `#2E5B3C` para borda externa
- **Linha de totais/rodapé**: Fundo `#1A3D28` (Verde Escuro), texto `#FFFFFF`, negrito
- **Destaques de alerta**: Fundo `#C8A84B` (Dourado) com texto escuro `#333333`
- **Texto do corpo**: `#333333` (Cinza Escuro)
- **Fonte recomendada**: Arial ou Calibri, tamanho 10-11pt para corpo, 11-12pt para cabeçalho

### Gráficos

- **Série principal**: `#2E5B3C` (Verde Institucional)
- **Série secundária**: `#C8A84B` (Dourado)
- **Série terciária**: `#6B9F7E` (Verde Claro)
- **Série quaternária**: `#A07830` (Dourado Escuro)
- **Fundo do gráfico**: `#FFFFFF` (Branco)
- **Título do gráfico**: `#1A3D28` (Verde Escuro), negrito
- **Eixos e legendas**: `#333333` (Cinza Escuro)
- **Linhas de grade**: `#CCCCCC` (Cinza Borda), suave

### Cabeçalhos de Documentos

Ao criar cabeçalhos para documentos oficiais, incluir:
1. Brasão/logo do TCE/RN à esquerda (arquivo disponível em `assets/tce-rn-header.png`)
2. Texto institucional: **TRIBUNAL DE CONTAS DO ESTADO** / **RIO GRANDE DO NORTE**
3. Subunidade: Diretoria de Controle de Pessoal e Previdência – DCP / Coordenadoria de Fiscalização de Pessoal – CFP
4. Fundo branco, texto em verde institucional `#2E5B3C` para o título principal
5. Linha divisória inferior em `#C8A84B` (Dourado)

---

## Exemplos de Uso

### HTML / Artefatos Web

```css
/* Variáveis CSS para identidade TCE/RN */
:root {
  --tce-verde-principal: #2E5B3C;
  --tce-verde-escuro: #1A3D28;
  --tce-verde-medio: #3D7A52;
  --tce-verde-claro: #6B9F7E;
  --tce-dourado: #C8A84B;
  --tce-dourado-escuro: #A07830;
  --tce-cinza-texto: #333333;
  --tce-cinza-claro: #F2F2F2;
  --tce-branco: #FFFFFF;
}

/* Estilo de tabela padrão */
.tce-tabela thead {
  background-color: var(--tce-verde-principal);
  color: var(--tce-branco);
  font-weight: bold;
}

.tce-tabela tr:nth-child(even) {
  background-color: var(--tce-cinza-claro);
}

.tce-tabela tr:last-child {
  background-color: var(--tce-verde-escuro);
  color: var(--tce-branco);
  font-weight: bold;
}

.tce-tabela .destaque {
  background-color: var(--tce-dourado);
  color: var(--tce-cinza-texto);
}
```

### Python (para XLSX/PPTX/DOCX)

```python
# Cores TCE/RN para uso com openpyxl, python-pptx ou python-docx
TCE_COLORS = {
    "verde_principal": "2E5B3C",
    "verde_escuro":    "1A3D28",
    "verde_medio":     "3D7A52",
    "verde_claro":     "6B9F7E",
    "dourado":         "C8A84B",
    "dourado_escuro":  "A07830",
    "branco":          "FFFFFF",
    "cinza_texto":     "333333",
    "cinza_claro":     "F2F2F2",
    "cinza_borda":     "CCCCCC",
}

# Exemplo de cabeçalho de tabela em XLSX (openpyxl)
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

header_fill  = PatternFill("solid", fgColor=TCE_COLORS["verde_principal"])
header_font  = Font(color=TCE_COLORS["branco"], bold=True, name="Calibri", size=11)
total_fill   = PatternFill("solid", fgColor=TCE_COLORS["verde_escuro"])
total_font   = Font(color=TCE_COLORS["branco"], bold=True, name="Calibri", size=11)
alt_fill     = PatternFill("solid", fgColor=TCE_COLORS["cinza_claro"])
destaque_fill = PatternFill("solid", fgColor=TCE_COLORS["dourado"])
borda_thin   = Border(
    left=Side(style="thin", color=TCE_COLORS["cinza_borda"]),
    right=Side(style="thin", color=TCE_COLORS["cinza_borda"]),
    top=Side(style="thin", color=TCE_COLORS["cinza_borda"]),
    bottom=Side(style="thin", color=TCE_COLORS["cinza_borda"])
)
```

---

## Checklist de Conformidade Visual

Antes de entregar qualquer elemento visual, verificar:

- [ ] Cabeçalho de tabela em verde institucional `#2E5B3C`
- [ ] Texto de cabeçalho em branco e negrito
- [ ] Linhas alternadas com cinza claro `#F2F2F2`
- [ ] Linha de totais em verde escuro `#1A3D28`
- [ ] Bordas em cinza `#CCCCCC`
- [ ] Texto do corpo em cinza escuro `#333333`
- [ ] Destaques (irregularidades, alertas) em dourado `#C8A84B`
- [ ] Fontes: Arial, Calibri ou Times New Roman (documentos jurídicos)
- [ ] Gráficos com paleta de cores na sequência: Verde → Dourado → Verde Claro → Dourado Escuro

---

## Contexto de Uso

Esta identidade visual é aplicada em documentos produzidos pela **DCP – Diretoria de Controle de Pessoal e Previdência** e pela **CFP – Coordenadoria de Fiscalização de Pessoal** do **TCE/RN**, incluindo:

- Relatórios técnicos de auditoria
- Notas de fiscalização
- Processos de denúncia sobre irregularidades em pessoal
- Análises de despesa com pessoal (Lei de Responsabilidade Fiscal)
- Planilhas de apuração de limites constitucionais
- Apresentações para julgamento de processos
