"""
Modelo de dados para macros e ações.
"""
from dataclasses import dataclass, field
from typing import Literal, Any
from enum import Enum
import uuid
import time


class ActionType(Enum):
    """Tipos de ações suportadas."""
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    MOUSE_CLICK = "mouse_click"
    MOUSE_RELEASE = "mouse_release"
    MOUSE_MOVE = "mouse_move"
    MOUSE_SCROLL = "mouse_scroll"
    DELAY = "delay"


class MouseButton(Enum):
    """Botões do mouse."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


@dataclass
class MacroAction:
    """Representa uma única ação dentro de uma macro."""
    action_type: ActionType
    data: dict[str, Any] = field(default_factory=dict)
    delay_before: float = 0.0  # Delay em ms antes desta ação
    
    def to_dict(self) -> dict:
        """Converte para dicionário para serialização."""
        return {
            "action_type": self.action_type.value,
            "data": self.data,
            "delay_before": self.delay_before
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MacroAction":
        """Cria uma ação a partir de um dicionário."""
        return cls(
            action_type=ActionType(data["action_type"]),
            data=data.get("data", {}),
            delay_before=data.get("delay_before", 0.0)
        )
    
    def get_description(self) -> str:
        """Retorna uma descrição legível da ação."""
        if self.action_type == ActionType.KEY_PRESS:
            return f"⌨️ Pressionar tecla: {self.data.get('key', '?')}"
        elif self.action_type == ActionType.KEY_RELEASE:
            return f"⌨️ Soltar tecla: {self.data.get('key', '?')}"
        elif self.action_type == ActionType.MOUSE_CLICK:
            btn = self.data.get('button', 'left')
            x, y = self.data.get('x', 0), self.data.get('y', 0)
            return f"🖱️ Clique {btn} em ({x}, {y})"
        elif self.action_type == ActionType.MOUSE_RELEASE:
            btn = self.data.get('button', 'left')
            return f"🖱️ Soltar botão {btn}"
        elif self.action_type == ActionType.MOUSE_MOVE:
            x, y = self.data.get('x', 0), self.data.get('y', 0)
            return f"🖱️ Mover para ({x}, {y})"
        elif self.action_type == ActionType.MOUSE_SCROLL:
            dx, dy = self.data.get('dx', 0), self.data.get('dy', 0)
            return f"🖱️ Scroll ({dx}, {dy})"
        elif self.action_type == ActionType.DELAY:
            ms = self.data.get('ms', 0)
            return f"⏱️ Aguardar {ms}ms"
        return "❓ Ação desconhecida"


@dataclass
class Macro:
    """Representa uma macro completa."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Nova Macro"
    hotkey: str = ""  # Ex: "ctrl+shift+1"
    actions: list[MacroAction] = field(default_factory=list)
    loop_count: int = 1  # 0 = infinito
    loop_delay: float = 0.0  # Delay entre loops em ms
    enabled: bool = True
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        """Converte para dicionário para serialização."""
        return {
            "id": self.id,
            "name": self.name,
            "hotkey": self.hotkey,
            "actions": [a.to_dict() for a in self.actions],
            "loop_count": self.loop_count,
            "loop_delay": self.loop_delay,
            "enabled": self.enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Macro":
        """Cria uma macro a partir de um dicionário."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Nova Macro"),
            hotkey=data.get("hotkey", ""),
            actions=[MacroAction.from_dict(a) for a in data.get("actions", [])],
            loop_count=data.get("loop_count", 1),
            loop_delay=data.get("loop_delay", 0.0),
            enabled=data.get("enabled", True),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time())
        )
    
    def add_action(self, action: MacroAction) -> None:
        """Adiciona uma ação à macro."""
        self.actions.append(action)
        self.updated_at = time.time()
    
    def remove_action(self, index: int) -> None:
        """Remove uma ação pelo índice."""
        if 0 <= index < len(self.actions):
            del self.actions[index]
            self.updated_at = time.time()
    
    def move_action(self, from_index: int, to_index: int) -> None:
        """Move uma ação de uma posição para outra."""
        if 0 <= from_index < len(self.actions) and 0 <= to_index < len(self.actions):
            action = self.actions.pop(from_index)
            self.actions.insert(to_index, action)
            self.updated_at = time.time()
    
    def get_total_duration(self) -> float:
        """Calcula a duração total estimada da macro em ms."""
        total = 0.0
        for action in self.actions:
            total += action.delay_before
            if action.action_type == ActionType.DELAY:
                total += action.data.get('ms', 0)
        return total
    
    def duplicate(self) -> "Macro":
        """Cria uma cópia da macro com novo ID."""
        new_macro = Macro.from_dict(self.to_dict())
        new_macro.id = str(uuid.uuid4())
        new_macro.name = f"{self.name} (cópia)"
        new_macro.created_at = time.time()
        new_macro.updated_at = time.time()
        return new_macro
