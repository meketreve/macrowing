---
updated: 2026-10-03
tier: 2
---

# Status — tier 2+

<!-- TETO: 60 linhas FORA do bloco auto (o bloco é do script e não conta). Resumir "Concluído" quando crescer. -->

## Estado atual

v1.0.0 lançada em 2026-01-17 (`dist/MacroWing.exe`; o CHANGELOG diz 2025-01-17, provável erro de digitação). Projeto parado desde 2026-04-20 (último commit "update e code review": tipagem `X | None`, `_EASING_MAP`, player com movimento suave e `on_error`).
Árvore de trabalho "suja": os ~145 `M` do `git status` são só fim de linha (CRLF na árvore, LF no repo) — `git diff --ignore-cr-at-eol` sai vazio. Não há mudança real pendente.

## Próxima fase

Sem tarefa definida. Ao retomar: decidir o CRLF (ver pendências), depois `python main.py` no Windows e conferir gravar → executar → ESC.
→ verify: `git diff --ignore-cr-at-eol --stat` vazio e `python -m compileall -q src main.py` sai 0.

## Pendências e bloqueios

- Normalizar fim de linha (`.gitattributes` ou `core.autocrlf`) — decisão do usuário
- `MacroPlayer.on_error` não é ligado em `main_window.py` → erros de execução somem em silêncio
- Callbacks do player/pânico rodam fora da thread Qt e mexem em widgets (ver LEARNINGS [qt-thread])
- Sem testes nem lint; `_bmad-output/` vazio (BMAD instalado, nunca usado para planejamento)

## Concluído (recente)

- 2026-04-20 code review: refator de tipagem, easing map, `stop()` sem corrida no `on_stopped`
- 2026-01-20 correção de gravação duplicada e delay da 1ª ação

## Bruto do git (auto — não editar)

<!-- auto:start -->
data: 2026-10-03

```
cd66909 update e code review
e6ad917 update
a593c4a corrigido duplicidade na gravação
ca19f99 Update README.md
f7b9aff feat: Initial release - MacroWing v1.0.0
--- status ---
 M .gitignore
 M CHANGELOG.md
 M LICENSE
 M README.md
 M _bmad/bmb/module-help.csv
 M _bmad/bmb/workflows/agent/steps-c/step-01-brainstorm.md
 M _bmad/bmb/workflows/agent/steps-c/step-02-discovery.md
 M _bmad/bmb/workflows/agent/steps-c/step-03-type-metadata.md
 M _bmad/bmb/workflows/agent/steps-c/step-04-persona.md
 M _bmad/bmb/workflows/agent/steps-c/step-05-commands-menu.md
... +136
```
<!-- auto:end -->
