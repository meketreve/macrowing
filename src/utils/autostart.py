"""
Inicialização automática com o sistema.

- Linux: cria/remove ``~/.config/autostart/macrowing.desktop``.
- Windows: cria/remove um valor em
  ``HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run``.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "MacroWing"
_WIN_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _project_root() -> Path:
    """Diretório raiz do projeto (onde está o main.py)."""
    return Path(__file__).resolve().parents[2]


def _launch_command() -> str:
    """Comando usado para iniciar o app com o sistema."""
    return f'"{sys.executable}" "{_project_root() / "main.py"}"'


# --- Linux -----------------------------------------------------------------

def _autostart_file() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "autostart" / "macrowing.desktop"


def _desktop_entry() -> str:
    return (
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={APP_NAME}\n"
        "Comment=Gerenciador de macros para teclado e mouse\n"
        f"Exec={_launch_command()}\n"
        "Terminal=false\n"
        "X-GNOME-Autostart-enabled=true\n"
    )


def _set_linux(enabled: bool) -> bool:
    path = _autostart_file()
    if enabled:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_desktop_entry(), encoding="utf-8")
    elif path.exists():
        path.unlink()
    return True


def _get_linux() -> bool:
    return _autostart_file().exists()


# --- Windows ---------------------------------------------------------------

def _set_windows(enabled: bool) -> bool:
    import winreg

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, _WIN_RUN_KEY, 0, winreg.KEY_SET_VALUE
    ) as key:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _launch_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
    return True


def _get_windows() -> bool:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _WIN_RUN_KEY) as key:
            winreg.QueryValueEx(key, APP_NAME)
        return True
    except OSError:
        return False


# --- API pública -----------------------------------------------------------

def is_autostart_enabled() -> bool:
    """Informa se o app está configurado para iniciar com o sistema."""
    try:
        if sys.platform == "win32":
            return _get_windows()
        return _get_linux()
    except Exception:
        return False


def set_autostart(enabled: bool) -> bool:
    """
    Configura (ou remove) a inicialização automática.

    Retorna True em caso de sucesso.
    """
    try:
        if sys.platform == "win32":
            return _set_windows(enabled)
        return _set_linux(enabled)
    except Exception as exc:
        print(f"Erro ao configurar autostart: {exc}")
        return False