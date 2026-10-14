"""
Backends de hotkeys globais, selecionados por plataforma.

- Windows: biblioteca ``keyboard`` (comportamento original).
- Linux/X11: ``pynput`` — não exige root e funciona no X11. No Wayland a
  captura global de input não é possível via pynput.

Também expõe ``GlobalHotkey``, um utilitário para registrar uma hotkey
avulsa (ex.: F10 para parar a gravação).
"""
from __future__ import annotations

import sys
import threading
from typing import Callable, Optional

_IS_WINDOWS = sys.platform == "win32"

# Aliases -> nome canônico de modificador.
_MODIFIER_ALIASES = {
    "ctrl": "ctrl",
    "control": "ctrl",
    "ctrl_l": "ctrl",
    "ctrl_r": "ctrl",
    "alt": "alt",
    "alt_l": "alt",
    "alt_r": "alt",
    "alt_gr": "alt_gr",
    "shift": "shift",
    "shift_l": "shift",
    "shift_r": "shift",
    "win": "cmd",
    "super": "cmd",
    "super_l": "cmd",
    "super_r": "cmd",
    "cmd": "cmd",
    "cmd_l": "cmd",
    "cmd_r": "cmd",
    "meta": "cmd",
}

_MODIFIER_NAMES = {"ctrl", "alt", "shift", "cmd", "alt_gr"}

# Aliases -> nome canônico de tecla "principal".
_MAIN_ALIASES = {
    "escape": "esc",
    "return": "enter",
    "del": "delete",
    "pgup": "page_up",
    "pageup": "page_up",
    "pgdn": "page_down",
    "pagedown": "page_down",
    "printscreen": "print_screen",
    "prtsc": "print_screen",
    "capslock": "caps_lock",
    "numlock": "num_lock",
    "scrolllock": "scroll_lock",
}


def _is_modifier(token: str) -> bool:
    """Verifica se um token de hotkey é um modificador."""
    return _MODIFIER_ALIASES.get(token) in _MODIFIER_NAMES


def _normalize_main(token: str) -> str:
    """Normaliza o nome de uma tecla principal."""
    token = token.lower()
    return _MAIN_ALIASES.get(token, token)


def parse_hotkey(hotkey: str) -> tuple[set[str], Optional[str]]:
    """
    Separa uma hotkey em (modificadores, tecla principal).

    Ex.: ``"ctrl+shift+1"`` -> ``({"ctrl", "shift"}, "1")``.
    """
    tokens = [t for t in hotkey.lower().replace(" ", "").split("+") if t]
    modifiers: set[str] = set()
    main: Optional[str] = None

    for token in tokens:
        if _is_modifier(token):
            modifiers.add(_MODIFIER_ALIASES[token])
        else:
            main = _normalize_main(token)

    return modifiers, main


class HotkeyBackend:
    """Interface comum dos backends de hotkey global."""

    def add(self, hotkey: str, callback: Callable, suppress: bool = False) -> None:
        """Registra uma hotkey. Levanta exceção se não for possível."""
        raise NotImplementedError

    def remove(self, hotkey: str) -> bool:
        """Remove uma hotkey. Retorna True se existia."""
        raise NotImplementedError

    def stop(self) -> None:
        """Encerra recursos do backend."""


class KeyboardBackend(HotkeyBackend):
    """Backend baseado na biblioteca ``keyboard`` (Windows)."""

    def __init__(self) -> None:
        import keyboard  # import tardio: só existe/instala no Windows

        self._keyboard = keyboard

    def add(self, hotkey: str, callback: Callable, suppress: bool = False) -> None:
        self._keyboard.add_hotkey(hotkey, callback, suppress=suppress)

    def remove(self, hotkey: str) -> bool:
        try:
            self._keyboard.remove_hotkey(hotkey)
            return True
        except (KeyError, ValueError):
            return False


class PynputBackend(HotkeyBackend):
    """
    Backend baseado em ``pynput`` (Linux/X11).

    Mantém um único ``Listener`` de teclado e faz o casamento das hotkeys
    (modificadores + tecla principal) manualmente, permitindo registrar e
    remover combinações em tempo de execução.
    """

    def __init__(self) -> None:
        from pynput import keyboard

        self._keyboard = keyboard
        self._listener: Optional["keyboard.Listener"] = None
        self._listener_failed = False
        self._hotkeys: dict[str, tuple[set[str], str, Callable]] = {}
        self._pressed_mods: set[str] = set()
        self._fired: set[str] = set()
        self._lock = threading.RLock()

    def add(self, hotkey: str, callback: Callable, suppress: bool = False) -> None:
        modifiers, main = parse_hotkey(hotkey)
        if main is None:
            raise ValueError(f"Hotkey '{hotkey}' não possui tecla principal")

        with self._lock:
            self._hotkeys[hotkey] = (modifiers, main, callback)
            self._ensure_listener()

    def remove(self, hotkey: str) -> bool:
        with self._lock:
            return self._hotkeys.pop(hotkey, None) is not None

    def stop(self) -> None:
        with self._lock:
            if self._listener is not None:
                self._listener.stop()
                self._listener = None
            self._hotkeys.clear()
            self._pressed_mods.clear()
            self._fired.clear()

    def _ensure_listener(self) -> None:
        if self._listener is not None or self._listener_failed:
            return
        try:
            self._listener = self._keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
            )
            self._listener.daemon = True
            self._listener.start()
        except Exception as exc:
            self._listener = None
            self._listener_failed = True
            print(
                f"Aviso: captura global de teclado indisponível ({exc}). "
                "Hotkeys não funcionarão (Wayland?)."
            )

    def _identity(self, key) -> Optional[str]:
        """Converte uma tecla pynput no token canônico usado nas hotkeys."""
        if isinstance(key, self._keyboard.Key):
            name = key.name
            return _MODIFIER_ALIASES.get(name, name)

        char = getattr(key, "char", None)
        if char:
            return char.lower()
        return None

    def _on_press(self, key) -> None:
        ident = self._identity(key)
        if ident is None:
            return

        to_fire: list[Callable] = []
        with self._lock:
            if ident in _MODIFIER_NAMES:
                self._pressed_mods.add(ident)
                return

            for hotkey, (modifiers, main, callback) in self._hotkeys.items():
                if main != ident or hotkey in self._fired:
                    continue
                if modifiers <= self._pressed_mods:
                    self._fired.add(hotkey)
                    to_fire.append(callback)

        # Roda fora do listener para não bloquear a captura de eventos.
        for callback in to_fire:
            threading.Thread(
                target=self._invoke, args=(callback,), daemon=True
            ).start()

    def _on_release(self, key) -> None:
        ident = self._identity(key)
        if ident is None:
            return

        with self._lock:
            if ident in _MODIFIER_NAMES:
                self._pressed_mods.discard(ident)
            else:
                for hotkey, (_mods, main, _cb) in self._hotkeys.items():
                    if main == ident:
                        self._fired.discard(hotkey)

    @staticmethod
    def _invoke(callback: Callable) -> None:
        try:
            callback()
        except Exception as exc:  # nunca deixar exceção matar o listener
            print(f"Erro no callback da hotkey: {exc}")


class NullBackend(HotkeyBackend):
    """Backend inerte, usado quando nenhum backend real está disponível."""

    def add(self, hotkey: str, callback: Callable, suppress: bool = False) -> None:
        print(f"Aviso: hotkeys globais indisponíveis; '{hotkey}' ignorada.")

    def remove(self, hotkey: str) -> bool:
        return False


def create_backend() -> HotkeyBackend:
    """Cria o backend adequado à plataforma atual."""
    try:
        if _IS_WINDOWS:
            return KeyboardBackend()
        return PynputBackend()
    except Exception as exc:
        print(f"Aviso: não foi possível iniciar o backend de hotkeys ({exc}).")
        print("Hotkeys globais ficarão desativadas.")
        return NullBackend()


class GlobalHotkey:
    """Registra uma hotkey global avulsa, de forma cross-platform."""

    def __init__(self) -> None:
        self._backend = create_backend()

    def register(self, hotkey: str, callback: Callable, suppress: bool = False) -> bool:
        try:
            self._backend.add(hotkey, callback, suppress=suppress)
            return True
        except Exception as exc:
            print(f"Erro ao registrar hotkey '{hotkey}': {exc}")
            return False

    def unregister(self, hotkey: str) -> bool:
        try:
            return self._backend.remove(hotkey)
        except Exception:
            return False

    def close(self) -> None:
        self._backend.stop()