---
name: docxtpl-get-docx-descarta-render
description: docxtpl — get_docx() após render() recarrega o template e descarta o render; usar doc.docx direto para pós-processar
metadata: 
  node_type: memory
  type: reference
  originSessionId: 14cb1774-2e32-429b-909a-9c2c7d64a9ab
---

Na versão do docxtpl do `.venv` deste repo, `DocxTemplate.get_docx()` chama `init_docx(reload=True)`: se `is_rendered`, **recria o Document a partir do template**, jogando fora o conteúdo renderizado (o save seguinte grava o template cru, sem erro). Para pós-processar o documento renderizado (ex.: zebrar tabela em `gerar_info_nereu_ms._estilizar_tabela`), acessar `doc.docx` diretamente entre `render()` e `save()`.
