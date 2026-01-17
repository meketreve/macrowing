"""
Ícone na bandeja do sistema.
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import pyqtSignal, QObject

from ..core.macro import Macro


def create_default_icon() -> QIcon:
    """Cria um ícone padrão para a bandeja."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Círculo de fundo
    painter.setBrush(QColor("#e94560"))
    painter.setPen(QColor("#e94560"))
    painter.drawEllipse(4, 4, 56, 56)
    
    # Letra M
    painter.setPen(QColor("#ffffff"))
    font = painter.font()
    font.setPixelSize(36)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), 0x0084, "M")  # AlignCenter
    
    painter.end()
    return QIcon(pixmap)


class TrayIcon(QObject):
    """Gerencia o ícone na bandeja do sistema."""
    
    # Sinais
    show_window_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    toggle_macro_requested = pyqtSignal(str)  # macro_id
    stop_all_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._tray = QSystemTrayIcon(parent)
        self._tray.setIcon(create_default_icon())
        self._tray.setToolTip("MacroWing - Gerenciador de Macros")
        
        self._menu = QMenu()
        self._macro_actions: dict[str, QAction] = {}
        
        self._setup_menu()
        
        self._tray.setContextMenu(self._menu)
        self._tray.activated.connect(self._on_activated)
    
    def _setup_menu(self) -> None:
        """Configura o menu de contexto."""
        # Mostrar janela
        show_action = self._menu.addAction("📋 Mostrar MacroWing")
        show_action.triggered.connect(lambda: self.show_window_requested.emit())
        
        self._menu.addSeparator()
        
        # Submenu de macros (será populado depois)
        self._macros_menu = self._menu.addMenu("🎮 Macros")
        
        self._menu.addSeparator()
        
        # Parar todas
        stop_action = self._menu.addAction("⏹️ Parar Todas")
        stop_action.triggered.connect(lambda: self.stop_all_requested.emit())
        
        self._menu.addSeparator()
        
        # Sair
        quit_action = self._menu.addAction("❌ Sair")
        quit_action.triggered.connect(lambda: self.quit_requested.emit())
    
    def update_macros(self, macros: list[Macro]) -> None:
        """Atualiza a lista de macros no menu."""
        self._macros_menu.clear()
        self._macro_actions.clear()
        
        if not macros:
            no_macros = self._macros_menu.addAction("(nenhuma macro)")
            no_macros.setEnabled(False)
            return
        
        for macro in macros:
            if macro.enabled:
                status = "🟢"
            else:
                status = "🔴"
            
            hotkey_str = f" [{macro.hotkey}]" if macro.hotkey else ""
            action_text = f"{status} {macro.name}{hotkey_str}"
            
            action = self._macros_menu.addAction(action_text)
            action.setCheckable(True)
            action.setChecked(macro.enabled)
            action.triggered.connect(
                lambda checked, m_id=macro.id: self.toggle_macro_requested.emit(m_id)
            )
            
            self._macro_actions[macro.id] = action
    
    def show(self) -> None:
        """Mostra o ícone na bandeja."""
        self._tray.show()
    
    def hide(self) -> None:
        """Esconde o ícone da bandeja."""
        self._tray.hide()
    
    def show_message(self, title: str, message: str, 
                     icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
                     duration_ms: int = 3000) -> None:
        """Exibe uma notificação na bandeja."""
        self._tray.showMessage(title, message, icon, duration_ms)
    
    def set_recording(self, recording: bool) -> None:
        """Atualiza o ícone para indicar gravação."""
        if recording:
            self._tray.setToolTip("MacroWing - ⏺️ Gravando...")
        else:
            self._tray.setToolTip("MacroWing - Gerenciador de Macros")
    
    def set_playing(self, playing: bool, macro_name: str = "") -> None:
        """Atualiza o ícone para indicar reprodução."""
        if playing:
            self._tray.setToolTip(f"MacroWing - ▶️ Executando: {macro_name}")
        else:
            self._tray.setToolTip("MacroWing - Gerenciador de Macros")
    
    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Callback quando o ícone é ativado."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window_requested.emit()
