---
name: area-restrita-tramitar-flow
description: "Área Restrita tramitação funciona via oculto M→I; processo enviado some da listagem (sinal de sucesso, não \"aguardando envio\")"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 75f9c09c-3db6-44c8-8881-e0e172bc7e1f
  modified: 2026-08-18T14:21:46.488Z
---

`scripts/automacao/area_restrita.py` comando `tramitar` (validado em produção, jul/2026):
tramita cada processo do setor atual para outro. Fluxo por processo:
1. `consultar` (oculto=`C`) filtra e devolve o checkbox da linha.
2. POST `oculto='M'` ("Tramitar Processo(s)") com o checkbox marcado → abre a seção
   "Enviar Processos" (campos `txtSetorDestino`, `txtFaseProcessualN`, `ProcessoN`).
3. Setar `txtSetorDestino` (ex.: `DIP`) e `txtFaseProcessual1` (providência, texto livre,
   ex.: `ENVIO A GAANA`), POST `oculto='I'` ("Enviar Processos") → **efetiva** o envio.

Códigos de ação vêm do frame `<BASE>/botoesNOVO.asp?...&pagina=ProcessonoSetor`
(botões `parametros(valoraux, aux, ...)`, aux = form1.oculto). Frame fica na RAIZ do site,
não em SISTEMAS/Processo.

**Sinal de sucesso (importante):** depois de enviado, o processo **sai da listagem do setor
e perde o checkbox** (aparece sem caixa de seleção). Isso é sucesso — NÃO é "aguardando
envio". A mensagem "Operação realizada com sucesso" é genérica (aparece até no passo M),
então não serve como confirmação. Ver [[read-db-lags-area-restrita]] para verificar estado.

**Flakiness do passo M (observado 21/07/2026):** o eco do form de envio é intermitente —
num lote de 80, o servidor ecoou só os 31 primeiros `checkProcessoN`; lotes de 1–3
voltaram sem `txtSetorDestino` nenhum; minutos depois os mesmos processos ecoaram normal.
Não é validação contra a página renderizada (pág. 1 não continha os processos e mesmo
assim ecoou) nem estado por processo/relator/marcador (hipóteses testadas e descartadas).
Mitigação que funcionou: **chunks de ≤25 + sessão nova (`AreaRestrita()`) por tentativa +
retry com espera**. `tramitar` é seguro p/ retry: valida o eco ANTES do oculto=I e
pós-verifica a saída da listagem (houve caso de oculto=I "sucesso" sem tramitar de fato —
o retry pegou). Exceções persistentes (10+ recusas): processo **distribuído** a alguém
(013166/2017) e 003709/2022 (causa não identificada) — ver [[nereu-ms-envio-progresso]].

**Distribuído bloqueia tramitar (confirmado 18/08/2026, 001322/2014):** processo
distribuído com informação pendente de assinatura não é ecoado no passo M (erro "form de
envio não veio com todos os processos"). **Assinar/publicar a informação encerra a
distribuição na hora** — o mesmo `tramitar` passou logo em seguida, sem retry. Ordem
correta: distribuir → informacao → assinar → tramitar (como no runbook
[[enviar-antecedentes-gaana]]).
