"""
Gravador de macros - captura eventos de teclado e mouse.
"""
import time
import threading
from typing import Callable, Optional
from pynput import keyboard, mouse

from .macro import Macro, MacroAction, ActionType, MouseButton


class MacroRecorder:
    """Grava eventos de teclado e mouse para criar macros."""
    
    def __init__(self):
        self._recording = False
        self._actions: list[MacroAction] = []
        self._start_time: float = 0
        self._last_action_time: float = 0
        
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        
        # Configurações
        self.record_mouse_movement = False
        self.record_key_release = True
        self.min_movement_distance = 10  # Pixels mínimos para registrar movimento
        
        # Callbacks
        self.on_action_recorded: Optional[Callable[[MacroAction], None]] = None
        self.on_recording_started: Optional[Callable[[], None]] = None
        self.on_recording_stopped: Optional[Callable[[list[MacroAction]], None]] = None
        
        # Estado do mouse para filtrar movimentos
        self._last_mouse_pos = (0, 0)
    
    @property
    def is_recording(self) -> bool:
        return self._recording
    
    def start(self) -> None:
        """Inicia a gravação."""
        if self._recording:
            return
        
        self._recording = True
        self._actions = []
        self._start_time = time.time() * 1000  # Em ms
        self._last_action_time = self._start_time
        
        # Inicia listeners
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll,
            on_move=self._on_mouse_move if self.record_mouse_movement else None
        )
        
        self._keyboard_listener.start()
        self._mouse_listener.start()
        
        if self.on_recording_started:
            self.on_recording_started()
    
    def stop(self) -> list[MacroAction]:
        """Para a gravação e retorna as ações gravadas."""
        if not self._recording:
            return []
        
        self._recording = False
        
        # Para listeners
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        
        actions = self._actions.copy()
        
        if self.on_recording_stopped:
            self.on_recording_stopped(actions)
        
        return actions
    
    def create_macro(self, name: str = "Macro Gravada") -> Macro:
        """Cria uma macro com as ações gravadas."""
        macro = Macro(name=name)
        macro.actions = self._actions.copy()
        return macro
    
    def _add_action(self, action: MacroAction) -> None:
        """Adiciona uma ação à lista."""
        current_time = time.time() * 1000
        
        # Primeira ação não tem delay (ignorar tempo da contagem regressiva)
        if len(self._actions) == 0:
            action.delay_before = 0
        else:
            action.delay_before = current_time - self._last_action_time
        
        self._last_action_time = current_time
        
        self._actions.append(action)
        
        if self.on_action_recorded:
            self.on_action_recorded(action)
    
    def _key_to_str(self, key) -> str:
        """Converte uma tecla para string."""
        try:
            # Tecla normal (letra, número)
            return key.char if key.char else str(key)
        except AttributeError:
            # Tecla especial (ctrl, alt, etc)
            return str(key).replace("Key.", "")
    
    def _on_key_press(self, key) -> None:
        """Callback quando uma tecla é pressionada."""
        if not self._recording:
            return
        
        key_str = self._key_to_str(key)
        action = MacroAction(
            action_type=ActionType.KEY_PRESS,
            data={"key": key_str}
        )
        self._add_action(action)
    
    def _on_key_release(self, key) -> None:
        """Callback quando uma tecla é solta."""
        if not self._recording or not self.record_key_release:
            return
        
        key_str = self._key_to_str(key)
        action = MacroAction(
            action_type=ActionType.KEY_RELEASE,
            data={"key": key_str}
        )
        self._add_action(action)
    
    def _on_mouse_click(self, x: int, y: int, button, pressed: bool) -> None:
        """Callback quando um botão do mouse é clicado."""
        if not self._recording:
            return
        
        button_str = str(button).replace("Button.", "")
        
        if pressed:
            action = MacroAction(
                action_type=ActionType.MOUSE_CLICK,
                data={"x": x, "y": y, "button": button_str}
            )
        else:
            action = MacroAction(
                action_type=ActionType.MOUSE_RELEASE,
                data={"x": x, "y": y, "button": button_str}
            )
        
        self._add_action(action)
    
    def _on_mouse_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """Callback quando o scroll do mouse é usado."""
        if not self._recording:
            return
        
        action = MacroAction(
            action_type=ActionType.MOUSE_SCROLL,
            data={"x": x, "y": y, "dx": dx, "dy": dy}
        )
        self._add_action(action)
    
    def _on_mouse_move(self, x: int, y: int) -> None:
        """Callback quando o mouse é movido."""
        if not self._recording:
            return
        
        # Filtra movimentos muito pequenos
        last_x, last_y = self._last_mouse_pos
        distance = ((x - last_x) ** 2 + (y - last_y) ** 2) ** 0.5
        
        if distance < self.min_movement_distance:
            return
        
        self._last_mouse_pos = (x, y)
        
        action = MacroAction(
            action_type=ActionType.MOUSE_MOVE,
            data={"x": x, "y": y}
        )
        self._add_action(action)
