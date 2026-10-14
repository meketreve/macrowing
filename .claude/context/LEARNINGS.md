---
updated: 2026-10-14
tier: 2
---

# Aprendizados

<!-- TETO: 100 linhas fora de blocos auto. Uma linha por fato, formato grepável: `- [AAAA-MM-DD] [tag] fato — consequência`.
     O que foi tentado ou decidido leva veredito depois da tag: [✓] testado e mantido, [✗] tentado e descartado (nunca apagar), [↻ AAAA-MM-DD] substituído pela entrada dessa data. -->

## Preferências do usuário

- [2026-10-03] [idioma] código, comentários, commits e UI em PT-BR — manter

## Pegadinhas (versão, API, CI)

- [2026-10-03] [git] [↻ 2026-10-14] árvore em CRLF, blobs em LF, sem `.gitattributes` — `git status` mostrava ~145 `M` falsos; hoje a árvore está limpa (usar `git diff --ignore-cr-at-eol` se reaparecer)
- [2026-10-03] [plataforma] [↻ 2026-10-14] era Windows-only — o port de 2026-10-14 fez rodar no Linux/X11 (ver entradas [linux]/[wayland])
- [2026-10-14] [linux] roda no Linux/X11 pelo pynput, **sem root**; `pywin32`/`keyboard` viraram deps `; sys_platform == "win32"` e o `.spec` usa hiddenimports `_xorg` (`uac_admin` só no Windows)
- [2026-10-14] [wayland] pynput não captura input global nem injeta fora do XWayland — Wayland fica degradado; só X11 é suportado (documentado no README)
- [2026-10-03] [hotkeys] [↻ 2026-10-14] backends agora plugáveis em `hotkey_backend.py`: `keyboard` (Windows) e `pynput` (Linux/X11); a API do `HotkeyManager` não mudou
- [2026-10-14] [pynput] `Key.esc` (não `Key.escape`) e nomes de tecla diferem das strings do app — normalizar em `hotkey_backend.parse_hotkey` antes de casar
- [2026-10-14] [teste] casamento de hotkeys dá para testar sem X: chamar `PynputBackend._on_press/_on_release` com `Key`/`KeyCode` direto — não injetar input real no desktop do usuário [✓]
- [2026-10-03] [qt-thread] `MacroPlayer` roda em `threading.Thread` e chama `on_started/on_stopped` direto, que alteram labels/tray — mexer em widget fora da thread Qt; ao mexer aí, passar por `pyqtSignal`
- [2026-10-03] [admin] jogos/apps elevados ignoram input de processo não-admin — por isso `uac_admin=True` no spec; `request_admin()` em `main.py` está comentado de propósito
- [2026-10-03] [contagem] arquivos de tooling BMAD (`_bmad/`, `.agent/`, `.claude/commands/`) são ~95% do `git ls-files` — não usar a contagem para julgar o tamanho do app (~25 arquivos)

## Erros a não repetir

- [2026-10-03] [gravação] gravação duplicava e a 1ª ação herdava o tempo da contagem regressiva (corrigido em a593c4a: 1ª ação com `delay_before = 0`) — não regredir em `recorder.py`/`macro_recorder.py`

## Decisões e o porquê

- [2026-10-03] [contexto] [✓] tier 2, não 3 — o auto apontou 3 só pela contagem inflada pelo BMAD; app pequeno, sem monorepo/time
- [2026-10-14] [linux] [✓] hotkeys no Linux via pynput (sem root, X11) e manter `keyboard` no Windows — evita exigir sudo e não regride o Windows
- [2026-10-14] [linux] [✓] entrega via código-fonte (`run.sh`) e autostart implementado por SO — sem binário Linux nesta etapa
