---
updated: 2026-10-14
tier: 2
---

# Status — tier 2+

<!-- TETO: 60 linhas FORA do bloco auto (o bloco é do script e não conta). Resumir "Concluído" quando crescer. -->

## Estado atual

**Port para Linux feito em 2026-10-14 (não commitado).** Backend de hotkeys plugável (`pynput` no Linux/X11 sem root, `keyboard` no Windows), autostart por SO, `run.sh`, deps e `.spec` multiplataforma.
Validado nesta sessão (X11): `MainWindow` sobe, bindings de pânico/macro, matching de hotkeys, autostart `.desktop` e fallback sem X. **Falta** rodar gravar → executar → ESC de ponta a ponta.
A árvore CRLF sumiu: `git status` estava limpo antes deste trabalho.

## Próxima fase

Testar no Linux/X11: abrir o app, conferir gravar → executar → ESC e o autostart pelo checkbox de Configurações.
→ verify: `python -m compileall -q src main.py` sai 0 e `./run.sh` abre a janela; gravação e parada por ESC funcionam.
Depois: commitar o port (sugestão: `feat: port para Linux (backend pynput, autostart, run.sh)`).

## Pendências e bloqueios

- Comportamento no **Windows** não foi re-testado após a refatoração de hotkeys (backend `keyboard` preservado)
- **Wayland**: pynput não captura input global → gravação/hotkeys limitadas; só X11 é suportado
- `MacroPlayer.on_error` não é ligado em `main_window.py` → erros de execução somem em silêncio
- Callbacks do player/pânico rodam fora da thread Qt e mexem em widgets (ver LEARNINGS [qt-thread])
- Sem testes nem lint; `_bmad-output/` vazio (BMAD instalado, nunca usado para planejamento)

## Concluído (recente)

- 2026-10-14 port para Linux: `hotkey_backend.py` (pynput/keyboard), `autostart.py`, `run.sh`, deps/`.spec` condicionais
- Árvore CRLF normalizada (desde 2026-10-03) → `git status` limpo
- 2026-04-20 code review: refator de tipagem, easing map, `stop()` sem corrida no `on_stopped`
- 2026-01-20 correção de gravação duplicada e delay da 1ª ação

## Bruto do git (auto — não editar)

<!-- auto:start -->
data: 2026-10-14

```
ea81159 chore: contexto do projeto e AGENTS.md
cd66909 update e code review
e6ad917 update
a593c4a corrigido duplicidade na gravação
ca19f99 Update README.md
f7b9aff feat: Initial release - MacroWing v1.0.0
--- status ---
 M .claude/context/LEARNINGS.md
 M .claude/context/MAP.md
 M .claude/context/STATUS.md
 M README.md
 M macrowing.spec
 M main.py
 M requirements.txt
 M src/core/hotkey_manager.py
 M src/gui/macro_recorder.py
 M src/gui/main_window.py
... +5
```
<!-- auto:end -->
