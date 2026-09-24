---
name: cit-certidao-situacao-21-ambigua
description: Cit_Certidao.IdComunicacaoTipoSituacao=21 não distingue "resposta tempestiva" de "não apresentação de resposta" — ler a situação no PDF da certidão
metadata:
  type: project
---

`Cit_Certidao.IdComunicacaoTipoSituacao` vale **21** tanto na certidão de "Não apresentação de resposta até o fim do prazo" (001324/2024, IdCertidao 87623) quanto nas de "Apresentação de resposta tempestiva" (001323/2024 87740; 001325/2024 87622). O comentário do script `processos/informacoes/001324_2024/gerar_informacao.py` ("situação 21 = não apresentação") está errado.

`Cit_Citacoes.Data_Resposta` também não é confiável: ficou NULL no 001325/2024 apesar da defesa juntada e certificada tempestiva.

**Why:** validar tempestividade/revelia pelo código do banco dá falso positivo.

**How to apply:** ler o PDF da certidão (`ccd.pdf.extract_text_from_pdf` + `ccd.processo.get_info_file_path`) e checar as linhas "Inicio do prazo", "Final do prazo" e "Situação encontrada" (o texto sai com ligadura: "tempes va"). Padrão em `processos/informacoes/001323_2024/gerar_informacao.py`. Ver [[cit-citacoes-authoritative-source]].
