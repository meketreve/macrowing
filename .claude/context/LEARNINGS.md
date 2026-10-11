---
updated: 2026-10-03
tier: 2
---

# Aprendizados

<!-- TETO: 100 linhas fora de blocos auto. Uma linha por fato, formato grepável: `- [AAAA-MM-DD] [tag] fato — consequência`.
     O que foi tentado ou decidido leva veredito depois da tag: [✓] testado e mantido, [✗] tentado e descartado (nunca apagar), [↻ AAAA-MM-DD] substituído pela entrada dessa data. -->

## Preferências do usuário

- [2026-10-03] [idioma] código, comentários, commits e UI em PT-BR — manter

## Pegadinhas (versão, API, CI)

- [2026-10-03] [git] árvore em CRLF, blobs em LF, sem `.gitattributes` — `git status` mostra ~145 `M` falsos; usar `git diff --ignore-cr-at-eol` antes de concluir que há mudança
- [2026-10-03] [plataforma] só roda de verdade no Windows (`ctypes.windll`, `pywin32`, `keyboard`, hiddenimports `_win32` no spec) — no Linux dá no máximo `compileall`
- [2026-10-03] [hotkeys] dois backends de input: `keyboard` para hotkeys/pânico, `pynput` para gravar/reproduzir — bug de tecla pode estar em qualquer um; nomes de tecla diferem entre as libs
- [2026-10-03] [qt-thread] `MacroPlayer` roda em `threading.Thread` e chama `on_started/on_stopped` direto, que alteram labels/tray — mexer em widget fora da thread Qt; ao mexer aí, passar por `pyqtSignal`
- [2026-10-03] [admin] jogos/apps elevados ignoram input de processo não-admin — por isso `uac_admin=True` no spec; `request_admin()` em `main.py` está comentado de propósito
- [2026-10-03] [contagem] arquivos de tooling BMAD (`_bmad/`, `.agent/`, `.claude/commands/`) são ~95% do `git ls-files` — não usar a contagem para julgar o tamanho do app (~25 arquivos)

## Erros a não repetir

- [2026-10-03] [gravação] gravação duplicava e a 1ª ação herdava o tempo da contagem regressiva (corrigido em a593c4a: 1ª ação com `delay_before = 0`) — não regredir em `recorder.py`/`macro_recorder.py`

## Decisões e o porquê

- [2026-10-03] [contexto] [✓] tier 2, não 3 — o auto apontou 3 só pela contagem inflada pelo BMAD; app pequeno, sem monorepo/time
