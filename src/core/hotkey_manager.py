"""
Gerenciador de hotkeys globais.
"""
import threading
from typing import Callable
from dataclasses import dataclass

from .hotkey_backend import HotkeyBackend, create_backend


@dataclass
class HotkeyBinding:
    """Representa uma associação de hotkey."""
    hotkey: str
    callback: Callable
    description: str = ""
    active: bool = True


class HotkeyManager:
    """Gerencia hotkeys globais usando o backend da plataforma."""
    
    def __init__(self):
        self._bindings: dict[str, HotkeyBinding] = {}
        self._active = False
        self._panic_key: str | None = "escape"
        self._on_panic: Callable[[], None] | None = None
        
        # Backend de hotkeys (keyboard no Windows, pynput no Linux/X11)
        self._backend: HotkeyBackend = create_backend()
        
        # Lock para thread safety
        self._lock = threading.Lock()
    
    @property
    def is_active(self) -> bool:
        return self._active
    
    @property
    def panic_key(self) -> str | None:
        return self._panic_key
    
    @panic_key.setter
    def panic_key(self, value: str | None) -> None:
        """Define a tecla de pânico (para todas as macros)."""
        # Remove binding anterior
        if self._panic_key and f"__panic_{self._panic_key}" in self._bindings:
            self.unbind(f"__panic_{self._panic_key}")
        
        self._panic_key = value
        
        # Registra novo binding se estiver ativo
        if self._active and value and self._on_panic:
            self.bind(
                f"__panic_{value}",
                value,
                self._on_panic,
                "Parar todas as macros"
            )
    
    def set_panic_callback(self, callback: Callable[[], None]) -> None:
        """Define o callback para a tecla de pânico."""
        self._on_panic = callback
        
        # Registra se já estiver ativo
        if self._active and self._panic_key:
            self.bind(
                f"__panic_{self._panic_key}",
                self._panic_key,
                callback,
                "Parar todas as macros"
            )
    
    def bind(self, id: str, hotkey: str, callback: Callable, 
             description: str = "") -> bool:
        """
        Registra uma hotkey.
        
        Args:
            id: Identificador único para esta binding
            hotkey: Combinação de teclas (ex: "ctrl+shift+1")
            callback: Função a ser chamada
            description: Descrição da ação
        
        Returns:
            True se registrado com sucesso
        """
        with self._lock:
            # Remove binding anterior se existir
            if id in self._bindings:
                self._unbind_internal(id)
            
            try:
                # Normaliza o hotkey
                hotkey_normalized = hotkey.lower().replace(" ", "")
                
                # Registra no backend
                self._backend.add(
                    hotkey_normalized,
                    callback,
                    suppress=False,
                )
                
                # Salva binding
                self._bindings[id] = HotkeyBinding(
                    hotkey=hotkey_normalized,
                    callback=callback,
                    description=description,
                    active=True
                )
                
                return True
            
            except Exception as e:
                print(f"Erro ao registrar hotkey '{hotkey}': {e}")
                return False
    
    def unbind(self, id: str) -> bool:
        """Remove uma hotkey pelo ID."""
        with self._lock:
            return self._unbind_internal(id)
    
    def _unbind_internal(self, id: str) -> bool:
        """Remove uma hotkey (sem lock)."""
        if id not in self._bindings:
            return False
        
        binding = self._bindings[id]
        
        try:
            self._backend.remove(binding.hotkey)
        except Exception:
            pass
        
        del self._bindings[id]
        return True
    
    def unbind_all(self) -> None:
        """Remove todas as hotkeys."""
        with self._lock:
            for id in list(self._bindings.keys()):
                self._unbind_internal(id)
    
    def start(self) -> None:
        """Ativa o gerenciador de hotkeys."""
        if self._active:
            return
        
        self._active = True
        
        # Registra tecla de pânico
        if self._panic_key and self._on_panic:
            self.bind(
                f"__panic_{self._panic_key}",
                self._panic_key,
                self._on_panic,
                "Parar todas as macros"
            )
    
    def stop(self) -> None:
        """Desativa o gerenciador de hotkeys."""
        if not self._active:
            return
        
        self._active = False
        self.unbind_all()
        self._backend.stop()
    
    def enable_binding(self, id: str) -> bool:
        """Ativa uma binding específica."""
        with self._lock:
            if id not in self._bindings:
                return False
            
            binding = self._bindings[id]
            if binding.active:
                return True
            
            try:
                self._backend.add(binding.hotkey, binding.callback, suppress=False)
                binding.active = True
                return True
            except Exception:
                return False
    
    def disable_binding(self, id: str) -> bool:
        """Desativa temporariamente uma binding."""
        with self._lock:
            if id not in self._bindings:
                return False
            
            binding = self._bindings[id]
            if not binding.active:
                return True
            
            try:
                self._backend.remove(binding.hotkey)
                binding.active = False
                return True
            except Exception:
                return False
    
    def get_bindings(self) -> list[tuple[str, HotkeyBinding]]:
        """Retorna todas as bindings registradas."""
        with self._lock:
            return list(self._bindings.items())
    
    def is_hotkey_available(self, hotkey: str) -> bool:
        """Verifica se uma hotkey está disponível."""
        hotkey_normalized = hotkey.lower().replace(" ", "")
        
        with self._lock:
            for binding in self._bindings.values():
                if binding.hotkey == hotkey_normalized:
                    return False
        return True
