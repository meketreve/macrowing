"""
Funções utilitárias para o MacroWing.
"""
import os
import sys
from pathlib import Path


def get_data_dir() -> Path:
    """Retorna o diretório de dados da aplicação."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".config"
    
    data_dir = base / "MacroWing"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_macros_file() -> Path:
    """Retorna o caminho do arquivo de macros."""
    return get_data_dir() / "macros.json"


def get_settings_file() -> Path:
    """Retorna o caminho do arquivo de configurações."""
    return get_data_dir() / "settings.json"


def format_hotkey(keys: list[str]) -> str:
    """
    Formata uma lista de teclas em uma string de hotkey.
    Ex: ['ctrl', 'shift', '1'] -> 'Ctrl+Shift+1'
    """
    formatted = []
    for key in keys:
        key_lower = key.lower()
        if key_lower in ('ctrl', 'control', 'ctrl_l', 'ctrl_r'):
            formatted.append('Ctrl')
        elif key_lower in ('alt', 'alt_l', 'alt_r'):
            formatted.append('Alt')
        elif key_lower in ('shift', 'shift_l', 'shift_r'):
            formatted.append('Shift')
        elif key_lower in ('win', 'super', 'cmd', 'super_l', 'super_r'):
            formatted.append('Win')
        else:
            formatted.append(key.upper() if len(key) == 1 else key.capitalize())
    return '+'.join(formatted)


def parse_hotkey(hotkey_str: str) -> list[str]:
    """
    Converte uma string de hotkey em lista de teclas.
    Ex: 'Ctrl+Shift+1' -> ['ctrl', 'shift', '1']
    """
    if not hotkey_str:
        return []
    
    parts = hotkey_str.split('+')
    result = []
    for part in parts:
        part_clean = part.strip().lower()
        if part_clean:
            result.append(part_clean)
    return result


def key_to_display(key: str) -> str:
    """Converte uma tecla para exibição amigável."""
    display_map = {
        'space': 'Espaço',
        'enter': 'Enter',
        'return': 'Enter',
        'tab': 'Tab',
        'escape': 'Esc',
        'esc': 'Esc',
        'backspace': '⌫',
        'delete': 'Del',
        'up': '↑',
        'down': '↓',
        'left': '←',
        'right': '→',
        'home': 'Home',
        'end': 'End',
        'page_up': 'PgUp',
        'page_down': 'PgDn',
        'insert': 'Ins',
        'caps_lock': 'CapsLock',
        'num_lock': 'NumLock',
        'scroll_lock': 'ScrLock',
        'print_screen': 'PrtSc',
        'pause': 'Pause',
    }
    
    key_lower = key.lower()
    if key_lower in display_map:
        return display_map[key_lower]
    elif key_lower.startswith('f') and key_lower[1:].isdigit():
        return key.upper()
    elif len(key) == 1:
        return key.upper()
    return key.capitalize()


def is_modifier_key(key: str) -> bool:
    """Verifica se a tecla é um modificador."""
    modifiers = {
        'ctrl', 'control', 'ctrl_l', 'ctrl_r',
        'alt', 'alt_l', 'alt_r', 'alt_gr',
        'shift', 'shift_l', 'shift_r',
        'win', 'super', 'cmd', 'super_l', 'super_r', 'meta'
    }
    return key.lower() in modifiers


def ms_to_display(ms: float) -> str:
    """Converte milissegundos para exibição amigável."""
    if ms < 1000:
        return f"{int(ms)}ms"
    elif ms < 60000:
        seconds = ms / 1000
        return f"{seconds:.1f}s"
    else:
        minutes = ms / 60000
        return f"{minutes:.1f}min"
