"""
Reprodutor de macros - executa ações gravadas.
"""
import time
import math
import threading
from typing import Callable, Optional
from enum import Enum
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

from .macro import Macro, MacroAction, ActionType


class EasingType(Enum):
    """Tipos de curvas de easing para movimento suave."""
    LINEAR = "linear"
    EASE_IN = "ease_in"         # Começa devagar, acelera
    EASE_OUT = "ease_out"       # Começa rápido, desacelera (mais natural)
    EASE_IN_OUT = "ease_in_out" # Suave no início e fim
    EASE_OUT_QUAD = "ease_out_quad"   # Desaceleração quadrática
    EASE_OUT_CUBIC = "ease_out_cubic" # Desaceleração cúbica (ainda mais suave)
    EASE_OUT_EXPO = "ease_out_expo"   # Desaceleração exponencial


class SmoothMouseMover:
    """Algoritmo para movimento suave do mouse."""
    
    @staticmethod
    def ease_linear(t: float) -> float:
        """Movimento linear (sem easing)."""
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Começa devagar, acelera (quadrático)."""
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Começa rápido, desacelera (quadrático)."""
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Suave no início e fim (quadrático)."""
        if t < 0.5:
            return 2 * t * t
        return 1 - pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Começa rápido, desacelera (cúbico - mais suave)."""
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_out_expo(t: float) -> float:
        """Desaceleração exponencial (muito suave no final)."""
        return 1 if t == 1 else 1 - pow(2, -10 * t)
    
    @staticmethod
    def ease_out_back(t: float) -> float:
        """Ultrapassa levemente e volta (efeito de 'overshoot')."""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    @classmethod
    def get_easing_function(cls, easing_type: EasingType):
        """Retorna a função de easing correspondente."""
        easing_map = {
            EasingType.LINEAR: cls.ease_linear,
            EasingType.EASE_IN: cls.ease_in_quad,
            EasingType.EASE_OUT: cls.ease_out_quad,
            EasingType.EASE_IN_OUT: cls.ease_in_out_quad,
            EasingType.EASE_OUT_QUAD: cls.ease_out_quad,
            EasingType.EASE_OUT_CUBIC: cls.ease_out_cubic,
            EasingType.EASE_OUT_EXPO: cls.ease_out_expo,
        }
        return easing_map.get(easing_type, cls.ease_out_quad)
    
    @classmethod
    def calculate_points(cls, start_x: int, start_y: int, end_x: int, end_y: int,
                        duration_ms: float, easing: EasingType = EasingType.EASE_OUT_CUBIC,
                        steps_per_second: int = 120) -> list[tuple[int, int, float]]:
        """
        Calcula os pontos intermediários para movimento suave.
        
        Args:
            start_x, start_y: Posição inicial
            end_x, end_y: Posição final
            duration_ms: Duração do movimento em milissegundos
            easing: Tipo de curva de easing
            steps_per_second: Quantidade de passos por segundo (frames)
        
        Returns:
            Lista de tuplas (x, y, delay_ms) com posições e delays
        """
        # Calcula distância para ajustar duração automaticamente se necessário
        distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
        
        # Número de passos baseado na duração
        duration_sec = duration_ms / 1000
        total_steps = max(2, int(duration_sec * steps_per_second))
        
        # Delay entre cada passo
        delay_per_step = duration_ms / total_steps
        
        # Função de easing
        easing_func = cls.get_easing_function(easing)
        
        points = []
        for i in range(total_steps + 1):
            # Progresso de 0 a 1
            t = i / total_steps
            
            # Aplica easing
            eased_t = easing_func(t)
            
            # Interpola posição
            x = int(start_x + (end_x - start_x) * eased_t)
            y = int(start_y + (end_y - start_y) * eased_t)
            
            points.append((x, y, delay_per_step))
        
        return points
    
    @classmethod
    def calculate_duration_by_distance(cls, start_x: int, start_y: int, 
                                        end_x: int, end_y: int,
                                        speed: float = 1.0,
                                        min_duration_ms: float = 50,
                                        max_duration_ms: float = 1000) -> float:
        """
        Calcula a duração ideal baseada na distância.
        
        Args:
            start_x, start_y: Posição inicial
            end_x, end_y: Posição final
            speed: Multiplicador de velocidade (1.0 = normal, 2.0 = 2x mais rápido)
            min_duration_ms: Duração mínima
            max_duration_ms: Duração máxima
        
        Returns:
            Duração em milissegundos
        """
        distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
        
        # Fórmula: ~1ms por pixel, ajustado pela velocidade
        base_duration = distance * 0.8 / speed
        
        # Limita entre min e max
        return max(min_duration_ms, min(max_duration_ms, base_duration))


class MacroPlayer:
    """Reproduz macros executando as ações gravadas."""
    
    def __init__(self):
        self._keyboard = KeyboardController()
        self._mouse = MouseController()
        
        self._playing = False
        self._paused = False
        self._stop_requested = False
        self._current_thread: Optional[threading.Thread] = None
        self._current_macro: Optional[Macro] = None
        self._current_loop = 0
        
        # Configurações de movimento suave
        self.smooth_mouse_enabled = True
        self.smooth_mouse_easing = EasingType.EASE_OUT_CUBIC
        self.smooth_mouse_speed = 1.0  # 1.0 = normal, 2.0 = 2x mais rápido
        self.smooth_mouse_min_duration = 50   # ms
        self.smooth_mouse_max_duration = 800  # ms
        self.smooth_mouse_steps_per_second = 120  # FPS do movimento
        
        # Callbacks
        self.on_started: Optional[Callable[[Macro], None]] = None
        self.on_stopped: Optional[Callable[[Macro], None]] = None
        self.on_paused: Optional[Callable[[Macro], None]] = None
        self.on_resumed: Optional[Callable[[Macro], None]] = None
        self.on_action_executed: Optional[Callable[[MacroAction, int], None]] = None
        self.on_loop_completed: Optional[Callable[[int], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
    
    @property
    def is_playing(self) -> bool:
        return self._playing
    
    @property
    def is_paused(self) -> bool:
        return self._paused
    
    @property
    def current_macro(self) -> Optional[Macro]:
        return self._current_macro
    
    @property
    def current_loop(self) -> int:
        return self._current_loop
    
    def play(self, macro: Macro) -> None:
        """Inicia a reprodução de uma macro."""
        if self._playing:
            self.stop()
        
        self._playing = True
        self._paused = False
        self._stop_requested = False
        self._current_macro = macro
        self._current_loop = 0
        
        self._current_thread = threading.Thread(target=self._play_thread, daemon=True)
        self._current_thread.start()
        
        if self.on_started:
            self.on_started(macro)
    
    def stop(self) -> None:
        """Para a reprodução da macro."""
        self._stop_requested = True
        self._paused = False
        
        if self._current_thread and self._current_thread.is_alive():
            self._current_thread.join(timeout=1)
        
        if self._playing and self._current_macro:
            if self.on_stopped:
                self.on_stopped(self._current_macro)
        
        self._playing = False
        self._current_macro = None
        self._current_thread = None
    
    def pause(self) -> None:
        """Pausa a reprodução."""
        if self._playing and not self._paused:
            self._paused = True
            if self.on_paused and self._current_macro:
                self.on_paused(self._current_macro)
    
    def resume(self) -> None:
        """Retoma a reprodução."""
        if self._playing and self._paused:
            self._paused = False
            if self.on_resumed and self._current_macro:
                self.on_resumed(self._current_macro)
    
    def toggle_pause(self) -> None:
        """Alterna entre pausado e reproduzindo."""
        if self._paused:
            self.resume()
        else:
            self.pause()
    
    def _play_thread(self) -> None:
        """Thread que executa a macro."""
        if not self._current_macro:
            return
        
        macro = self._current_macro
        loop_count = macro.loop_count if macro.loop_count > 0 else float('inf')
        
        try:
            while self._current_loop < loop_count and not self._stop_requested:
                self._current_loop += 1
                
                # Executa todas as ações
                for i, action in enumerate(macro.actions):
                    if self._stop_requested:
                        break
                    
                    # Aguarda enquanto pausado
                    while self._paused and not self._stop_requested:
                        time.sleep(0.01)
                    
                    if self._stop_requested:
                        break
                    
                    # Delay antes da ação
                    if action.delay_before > 0:
                        self._sleep_ms(action.delay_before)
                    
                    if self._stop_requested:
                        break
                    
                    # Executa a ação
                    self._execute_action(action)
                    
                    if self.on_action_executed:
                        self.on_action_executed(action, i)
                
                if self.on_loop_completed and not self._stop_requested:
                    self.on_loop_completed(self._current_loop)
                
                # Delay entre loops
                if macro.loop_delay > 0 and self._current_loop < loop_count:
                    self._sleep_ms(macro.loop_delay)
        
        except Exception as e:
            if self.on_error:
                self.on_error(e)
        
        finally:
            self._playing = False
            if not self._stop_requested and self._current_macro:
                if self.on_stopped:
                    self.on_stopped(self._current_macro)
    
    def _sleep_ms(self, ms: float) -> None:
        """Dorme por um tempo em milissegundos, verificando stop."""
        end_time = time.time() + (ms / 1000)
        while time.time() < end_time and not self._stop_requested:
            if self._paused:
                while self._paused and not self._stop_requested:
                    time.sleep(0.01)
            time.sleep(0.001)
    
    def _execute_action(self, action: MacroAction) -> None:
        """Executa uma ação individual."""
        try:
            if action.action_type == ActionType.KEY_PRESS:
                self._key_press(action.data.get("key", ""))
            
            elif action.action_type == ActionType.KEY_RELEASE:
                self._key_release(action.data.get("key", ""))
            
            elif action.action_type == ActionType.MOUSE_CLICK:
                x = action.data.get("x", 0)
                y = action.data.get("y", 0)
                button = action.data.get("button", "left")
                self._mouse_click(x, y, button)
            
            elif action.action_type == ActionType.MOUSE_RELEASE:
                button = action.data.get("button", "left")
                self._mouse_release(button)
            
            elif action.action_type == ActionType.MOUSE_MOVE:
                x = action.data.get("x", 0)
                y = action.data.get("y", 0)
                self._mouse.position = (x, y)
            
            elif action.action_type == ActionType.MOUSE_SCROLL:
                dx = action.data.get("dx", 0)
                dy = action.data.get("dy", 0)
                self._mouse.scroll(dx, dy)
            
            elif action.action_type == ActionType.DELAY:
                ms = action.data.get("ms", 0)
                self._sleep_ms(ms)
        
        except Exception as e:
            print(f"Erro ao executar ação {action.action_type}: {e}")
    
    def _smooth_mouse_move(self, target_x: int, target_y: int) -> None:
        """
        Move o mouse suavemente até a posição de destino.
        
        Usa interpolação com curvas de easing para criar
        um movimento natural e fluido.
        """
        if not self.smooth_mouse_enabled:
            # Movimento instantâneo se desabilitado
            self._mouse.position = (target_x, target_y)
            return
        
        # Obtém posição atual
        start_x, start_y = self._mouse.position
        
        # Se já está na posição, não faz nada
        if start_x == target_x and start_y == target_y:
            return
        
        # Calcula duração baseada na distância
        duration = SmoothMouseMover.calculate_duration_by_distance(
            start_x, start_y, target_x, target_y,
            speed=self.smooth_mouse_speed,
            min_duration_ms=self.smooth_mouse_min_duration,
            max_duration_ms=self.smooth_mouse_max_duration
        )
        
        # Calcula os pontos intermediários
        points = SmoothMouseMover.calculate_points(
            start_x, start_y, target_x, target_y,
            duration_ms=duration,
            easing=self.smooth_mouse_easing,
            steps_per_second=self.smooth_mouse_steps_per_second
        )
        
        # Move o mouse por cada ponto
        for x, y, delay_ms in points:
            if self._stop_requested:
                break
            
            # Aguarda se pausado
            while self._paused and not self._stop_requested:
                time.sleep(0.01)
            
            if self._stop_requested:
                break
            
            # Move para a posição
            self._mouse.position = (x, y)
            
            # Delay entre passos
            if delay_ms > 0:
                time.sleep(delay_ms / 1000)
        
        # Garante que termina na posição exata
        if not self._stop_requested:
            self._mouse.position = (target_x, target_y)
    
    def _str_to_key(self, key_str: str):
        """Converte string para tecla pynput."""
        # Tenta teclas especiais
        try:
            return getattr(Key, key_str.lower())
        except AttributeError:
            pass
        
        # Se for um único caractere, retorna direto
        if len(key_str) == 1:
            return key_str
        
        return key_str
    
    def _key_press(self, key_str: str) -> None:
        """Pressiona uma tecla."""
        key = self._str_to_key(key_str)
        self._keyboard.press(key)
    
    def _key_release(self, key_str: str) -> None:
        """Solta uma tecla."""
        key = self._str_to_key(key_str)
        self._keyboard.release(key)
    
    def _str_to_button(self, button_str: str) -> Button:
        """Converte string para botão do mouse."""
        button_map = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle
        }
        return button_map.get(button_str.lower(), Button.left)
    
    def _mouse_click(self, x: int, y: int, button_str: str) -> None:
        """Clica em uma posição (movimento instantâneo)."""
        self._mouse.position = (x, y)
        button = self._str_to_button(button_str)
        self._mouse.press(button)
    
    def _mouse_click_at_current(self, button_str: str) -> None:
        """Clica na posição atual do mouse."""
        button = self._str_to_button(button_str)
        self._mouse.press(button)
    
    def _mouse_release(self, button_str: str) -> None:
        """Solta um botão do mouse."""
        button = self._str_to_button(button_str)
        self._mouse.release(button)
