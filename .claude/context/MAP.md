---
updated: 2026-10-14
tier: 2
---

# Mapa do projeto

<!-- TETO: 60 linhas FORA do bloco auto (o bloco é do script e não conta). O `git log` guarda o resto. -->

## Comandos

App desktop **Windows e Linux/X11** (Python 3.10+, PyQt6). Sem testes, sem lint/format configurado, sem CI.
- Instalar: `pip install -r requirements.txt` (PyQt6, pynput; `keyboard`/`pywin32` só no Windows — não há venv no repo)
- Rodar: `python main.py` (Windows, ou `run.bat`); `./run.sh` (Linux)
- Build: `pip install pyinstaller && pyinstaller --clean macrowing.spec` → `dist/MacroWing` (Linux) / `dist/MacroWing.exe` (Windows; `uac_admin=True` só lá)
- Checagem mínima sem testes: `python -m compileall -q src main.py`

<!-- auto:start -->
gerado em: 2026-10-14

primeiro nível:

```
_bmad
CHANGELOG.md
LICENSE
macrowing.spec
main.py
README.md
requirements.txt
run.bat
run.sh
src
```
<!-- auto:end -->

## Onde fica cada coisa

- `main.py` — entry: QApplication + `MainWindow`; `request_admin()` existe mas está comentado (e só age no Windows)
- `src/core/macro.py` — modelo: `Macro`, `MacroAction`, `ActionType`, `MouseButton` (to_dict/from_dict)
- `src/core/recorder.py` — `MacroRecorder`: listeners pynput (teclado+mouse) → lista de `MacroAction` com `delay_before`
- `src/core/player.py` — `MacroPlayer` (thread daemon, loops, pause, callbacks `on_*`) + `SmoothMouseMover`/`EasingType` (movimento suave)
- `src/core/hotkey_manager.py` — hotkeys globais e tecla de pânico; delega ao backend da plataforma (`_bindings` id → hotkey)
- `src/core/hotkey_backend.py` — backends de hotkey: `KeyboardBackend` (Windows, lib `keyboard`), `PynputBackend` (Linux/X11, sem root), `NullBackend` (fallback) e `GlobalHotkey` (hotkey avulsa)
- `src/core/storage.py` — `MacroStorage`: JSON + backup `.json.bak`, import/export
- `src/utils/helpers.py` — caminhos de dados: `%APPDATA%/MacroWing/{macros,settings}.json` (`$XDG_CONFIG_HOME/MacroWing` fora do Windows)
- `src/utils/autostart.py` — início automático: `~/.config/autostart/macrowing.desktop` (Linux) / `HKCU\...\Run` (Windows)
- `src/gui/main_window.py` — orquestra tudo: liga sinais, carrega settings, `_register_hotkeys`, `_EASING_MAP`
- `src/gui/macro_recorder.py` — diálogo de gravação com contagem regressiva → sinal `recording_finished`
- `src/gui/macro_editor.py` / `macro_list.py` — editor de ações e lista (sinais `*_requested`, `macro_saved`)
- `src/gui/settings_dialog.py` — configurações (sinal `settings_changed(dict)`); `styles.py` — tema dark (`COLORS`); `tray_icon.py` — bandeja
- `_bmad/`, `.agent/`, `.claude/commands/` — framework BMAD (~460 arquivos de tooling, não é código do app); `_bmad-output/` vazio
- `build/`, `dist/` — saída do PyInstaller (gitignored)

## Pontos de entrada e fluxos principais

- Gravar: `MainWindow` → `macro_recorder` (countdown) → `MacroRecorder.start/stop` → `recording_finished(Macro)` → `_on_recording_finished` → `MacroStorage.save_macro` → `_register_hotkeys`
- Executar: duplo clique / hotkey (`HotkeyManager.bind`) / "Testar" no editor → `MainWindow._play_macro` → `MacroPlayer.play` (thread) → `_execute_action` (pynput Controller)
- Parar: tecla de pânico (default `escape`) → `HotkeyManager` panic callback → `MainWindow._stop_playback` → `MacroPlayer.stop`
- Settings: `settings_dialog` → `settings_changed` → `MainWindow._on_settings_changed` → grava `settings.json`, aplica panic key/easing
