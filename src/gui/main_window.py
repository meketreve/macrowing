"""
Janela principal do MacroWing.
"""
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QStatusBar, QMenuBar, QMenu, QMessageBox, QFileDialog,
    QLabel, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QCloseEvent

from .styles import DARK_THEME, COLORS
from .macro_list import MacroListWidget
from .macro_editor import MacroEditorWidget
from .macro_recorder import MacroRecorderDialog
from .settings_dialog import SettingsDialog
from .tray_icon import TrayIcon

from ..core.macro import Macro
from ..core.storage import MacroStorage
from ..core.player import MacroPlayer, EasingType
from ..core.hotkey_manager import HotkeyManager
from ..utils.helpers import get_settings_file


class MainWindow(QMainWindow):
    """Janela principal da aplicação."""
    
    def __init__(self):
        super().__init__()
        
        # Componentes core
        self._storage = MacroStorage()
        self._player = MacroPlayer()
        self._hotkey_manager = HotkeyManager()
        
        # Dados
        self._macros: list[Macro] = []
        self._settings: dict = {}
        
        # UI
        self._setup_window()
        self._setup_menu()
        self._setup_ui()
        self._setup_statusbar()
        self._setup_tray()
        self._setup_callbacks()
        
        # Carrega dados
        self._load_settings()
        self._load_macros()
        
        # Inicia hotkeys
        self._hotkey_manager.start()
        self._register_hotkeys()
    
    def _setup_window(self) -> None:
        """Configura a janela."""
        self.setWindowTitle("MacroWing - Gerenciador de Macros")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)
        
        # Aplica tema
        self.setStyleSheet(DARK_THEME)
    
    def _setup_menu(self) -> None:
        """Configura a barra de menus."""
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("Arquivo")
        
        new_action = QAction("Nova Macro", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_macro)
        file_menu.addAction(new_action)
        
        record_action = QAction("Gravar Macro", self)
        record_action.setShortcut("Ctrl+R")
        record_action.triggered.connect(self._record_macro)
        file_menu.addAction(record_action)
        
        file_menu.addSeparator()
        
        import_action = QAction("Importar...", self)
        import_action.triggered.connect(self._import_macros)
        file_menu.addAction(import_action)
        
        export_action = QAction("Exportar Selecionada...", self)
        export_action.triggered.connect(self._export_selected)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("Configurações", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("Sair", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self._quit_app)
        file_menu.addAction(quit_action)
        
        # Menu Editar
        edit_menu = menubar.addMenu("Editar")
        
        duplicate_action = QAction("Duplicar Macro", self)
        duplicate_action.setShortcut("Ctrl+D")
        duplicate_action.triggered.connect(self._duplicate_selected)
        edit_menu.addAction(duplicate_action)
        
        delete_action = QAction("Excluir Macro", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self._delete_selected)
        edit_menu.addAction(delete_action)
        
        # Menu Macros
        macros_menu = menubar.addMenu("Macros")
        
        play_action = QAction("Executar Selecionada", self)
        play_action.setShortcut("F5")
        play_action.triggered.connect(self._play_selected)
        macros_menu.addAction(play_action)
        
        stop_action = QAction("Parar Execução", self)
        stop_action.setShortcut("Escape")
        stop_action.triggered.connect(self._stop_playback)
        macros_menu.addAction(stop_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("Ajuda")
        
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_ui(self) -> None:
        """Configura a interface principal."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Splitter para redimensionamento
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Lista de macros (esquerda)
        self._macro_list = MacroListWidget()
        self._macro_list.setMinimumWidth(280)
        self._macro_list.setMaximumWidth(400)
        splitter.addWidget(self._macro_list)
        
        # Editor (direita)
        self._macro_editor = MacroEditorWidget()
        splitter.addWidget(self._macro_editor)
        
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
    
    def _setup_statusbar(self) -> None:
        """Configura a barra de status."""
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        
        self._status_label = QLabel("Pronto")
        self._statusbar.addWidget(self._status_label, 1)
        
        self._playing_label = QLabel()
        self._statusbar.addPermanentWidget(self._playing_label)
    
    def _setup_tray(self) -> None:
        """Configura o ícone na bandeja."""
        self._tray = TrayIcon(self)
        self._tray.show_window_requested.connect(self._show_from_tray)
        self._tray.quit_requested.connect(self._quit_app)
        self._tray.stop_all_requested.connect(self._stop_playback)
        self._tray.toggle_macro_requested.connect(self._toggle_macro)
        self._tray.show()
    
    def _setup_callbacks(self) -> None:
        """Conecta os sinais dos widgets."""
        # Lista
        self._macro_list.macro_selected.connect(self._on_macro_selected)
        self._macro_list.macro_double_clicked.connect(self._play_macro)
        self._macro_list.new_macro_requested.connect(self._new_macro)
        self._macro_list.record_macro_requested.connect(self._record_macro)
        self._macro_list.delete_macro_requested.connect(self._delete_macro)
        self._macro_list.duplicate_macro_requested.connect(self._duplicate_macro)
        self._macro_list.play_macro_requested.connect(self._play_macro)
        
        # Editor
        self._macro_editor.macro_saved.connect(self._on_macro_saved)
        self._macro_editor.macro_test_requested.connect(self._play_macro)
        
        # Player callbacks
        self._player.on_started = self._on_playback_started
        self._player.on_stopped = self._on_playback_stopped
        
        # Hotkey manager
        self._hotkey_manager.set_panic_callback(self._stop_playback)
    
    # === Carregamento e Salvamento ===
    
    def _load_settings(self) -> None:
        """Carrega as configurações."""
        settings_file = get_settings_file()
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
            except Exception:
                self._settings = {}
        
        # Valores padrão
        self._settings.setdefault("start_minimized", False)
        self._settings.setdefault("minimize_to_tray", True)
        self._settings.setdefault("panic_key", "escape")
        self._settings.setdefault("smooth_mouse_enabled", True)
        self._settings.setdefault("smooth_mouse_speed", 1.0)
        self._settings.setdefault("smooth_mouse_min_duration", 50)
        self._settings.setdefault("smooth_mouse_max_duration", 800)
        self._settings.setdefault("smooth_mouse_easing_index", 2)
        
        # Aplica configurações
        self._hotkey_manager.panic_key = self._settings.get("panic_key", "escape")
        
        # Aplica configurações de movimento suave
        self._player.smooth_mouse_enabled = self._settings.get("smooth_mouse_enabled", True)
        self._player.smooth_mouse_speed = self._settings.get("smooth_mouse_speed", 1.0)
        self._player.smooth_mouse_min_duration = self._settings.get("smooth_mouse_min_duration", 50)
        self._player.smooth_mouse_max_duration = self._settings.get("smooth_mouse_max_duration", 800)
        
        easing_index = self._settings.get("smooth_mouse_easing_index", 2)
        easing_map = {
            0: EasingType.LINEAR,
            1: EasingType.EASE_OUT_QUAD,
            2: EasingType.EASE_OUT_CUBIC,
            3: EasingType.EASE_OUT_EXPO,
            4: EasingType.EASE_IN_OUT,
        }
        self._player.smooth_mouse_easing = easing_map.get(easing_index, EasingType.EASE_OUT_CUBIC)
    
    def _save_settings(self) -> None:
        """Salva as configurações."""
        settings_file = get_settings_file()
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(self._settings, f, indent=2)
    
    def _load_macros(self) -> None:
        """Carrega as macros salvas."""
        self._macros = self._storage.load_all()
        self._macro_list.set_macros(self._macros)
        self._tray.update_macros(self._macros)
        self._update_status(f"{len(self._macros)} macros carregadas")
    
    def _save_macros(self) -> None:
        """Salva todas as macros."""
        self._storage.save_all(self._macros)
        self._tray.update_macros(self._macros)
    
    def _register_hotkeys(self) -> None:
        """Registra hotkeys de todas as macros."""
        for macro in self._macros:
            if macro.enabled and macro.hotkey:
                self._hotkey_manager.bind(
                    macro.id,
                    macro.hotkey,
                    lambda m=macro: self._play_macro(m),
                    f"Executar: {macro.name}"
                )
    
    # === Ações de Macro ===
    
    def _new_macro(self) -> None:
        """Cria uma nova macro."""
        macro = Macro(name="Nova Macro")
        self._macros.append(macro)
        self._macro_list.add_macro(macro)
        self._macro_editor.load_macro(macro)
        self._save_macros()
        self._update_status("Nova macro criada")
    
    def _record_macro(self) -> None:
        """Abre o diálogo de gravação."""
        dialog = MacroRecorderDialog(self)
        dialog.recording_finished.connect(self._on_recording_finished)
        dialog.exec()
    
    def _on_recording_finished(self, macro: Macro) -> None:
        """Callback quando a gravação termina."""
        self._macros.append(macro)
        self._macro_list.add_macro(macro)
        self._macro_editor.load_macro(macro)
        self._save_macros()
        self._register_hotkeys()
        self._update_status(f"Macro gravada: {len(macro.actions)} ações")
    
    def _play_macro(self, macro: Macro) -> None:
        """Executa uma macro."""
        if not macro.actions:
            self._update_status("Macro vazia, nada a executar")
            return
        
        self._player.play(macro)
    
    def _play_selected(self) -> None:
        """Executa a macro selecionada."""
        macro = self._macro_list.get_selected_macro()
        if macro:
            self._play_macro(macro)
    
    def _stop_playback(self) -> None:
        """Para a execução da macro."""
        self._player.stop()
        self._update_status("Execução parada")
    
    def _delete_macro(self, macro: Macro) -> None:
        """Exclui uma macro."""
        reply = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir '{macro.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._hotkey_manager.unbind(macro.id)
            self._macros = [m for m in self._macros if m.id != macro.id]
            self._macro_list.remove_macro(macro.id)
            self._macro_editor.clear()
            self._save_macros()
            self._update_status(f"Macro '{macro.name}' excluída")
    
    def _delete_selected(self) -> None:
        """Exclui a macro selecionada."""
        macro = self._macro_list.get_selected_macro()
        if macro:
            self._delete_macro(macro)
    
    def _duplicate_macro(self, macro: Macro) -> None:
        """Duplica uma macro."""
        new_macro = macro.duplicate()
        self._macros.append(new_macro)
        self._macro_list.add_macro(new_macro)
        self._macro_editor.load_macro(new_macro)
        self._save_macros()
        self._update_status(f"Macro duplicada: {new_macro.name}")
    
    def _duplicate_selected(self) -> None:
        """Duplica a macro selecionada."""
        macro = self._macro_list.get_selected_macro()
        if macro:
            self._duplicate_macro(macro)
    
    def _toggle_macro(self, macro_id: str) -> None:
        """Alterna o estado ativo de uma macro."""
        for macro in self._macros:
            if macro.id == macro_id:
                macro.enabled = not macro.enabled
                
                if macro.enabled and macro.hotkey:
                    self._hotkey_manager.enable_binding(macro_id)
                else:
                    self._hotkey_manager.disable_binding(macro_id)
                
                self._save_macros()
                break
    
    # === Callbacks de UI ===
    
    def _on_macro_selected(self, macro: Macro) -> None:
        """Quando uma macro é selecionada na lista."""
        self._macro_editor.load_macro(macro)
    
    def _on_macro_saved(self, macro: Macro) -> None:
        """Quando uma macro é salva no editor."""
        # Atualiza na lista
        for i, m in enumerate(self._macros):
            if m.id == macro.id:
                self._macros[i] = macro
                break
        
        self._macro_list.update_macro(macro)
        self._save_macros()
        
        # Atualiza hotkey
        self._hotkey_manager.unbind(macro.id)
        if macro.enabled and macro.hotkey:
            self._hotkey_manager.bind(
                macro.id,
                macro.hotkey,
                lambda m=macro: self._play_macro(m),
                f"Executar: {macro.name}"
            )
        
        self._update_status(f"Macro '{macro.name}' salva")
    
    def _on_playback_started(self, macro: Macro) -> None:
        """Quando a reprodução inicia."""
        self._playing_label.setText(f"▶️ Executando: {macro.name}")
        self._playing_label.setStyleSheet(f"color: {COLORS['success']};")
        self._tray.set_playing(True, macro.name)
    
    def _on_playback_stopped(self, macro: Macro) -> None:
        """Quando a reprodução para."""
        self._playing_label.setText("")
        self._tray.set_playing(False)
    
    # === Import/Export ===
    
    def _import_macros(self) -> None:
        """Importa macros de um arquivo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Macros",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                imported = self._storage.import_macros(Path(file_path))
                for macro in imported:
                    self._macros.append(macro)
                    self._macro_list.add_macro(macro)
                
                self._save_macros()
                self._register_hotkeys()
                self._update_status(f"{len(imported)} macros importadas")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao importar: {e}")
    
    def _export_selected(self) -> None:
        """Exporta a macro selecionada."""
        macro = self._macro_list.get_selected_macro()
        if not macro:
            QMessageBox.warning(self, "Aviso", "Selecione uma macro para exportar.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Macro",
            f"{macro.name}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self._storage.export_macro(macro, Path(file_path))
                self._update_status(f"Macro '{macro.name}' exportada")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao exportar: {e}")
    
    # === Configurações ===
    
    def _show_settings(self) -> None:
        """Exibe o diálogo de configurações."""
        dialog = SettingsDialog(self._settings, self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()
    
    def _on_settings_changed(self, settings: dict) -> None:
        """Quando as configurações são alteradas."""
        self._settings = settings
        self._save_settings()
        
        # Aplica configuração de hotkey de pânico
        self._hotkey_manager.panic_key = settings.get("panic_key", "escape")
        
        # Aplica configurações de movimento suave
        self._player.smooth_mouse_enabled = settings.get("smooth_mouse_enabled", True)
        self._player.smooth_mouse_speed = settings.get("smooth_mouse_speed", 1.0)
        self._player.smooth_mouse_min_duration = settings.get("smooth_mouse_min_duration", 50)
        self._player.smooth_mouse_max_duration = settings.get("smooth_mouse_max_duration", 800)
        
        # Mapeia índice do combo para EasingType
        easing_index = settings.get("smooth_mouse_easing_index", 2)
        easing_map = {
            0: EasingType.LINEAR,
            1: EasingType.EASE_OUT_QUAD,
            2: EasingType.EASE_OUT_CUBIC,
            3: EasingType.EASE_OUT_EXPO,
            4: EasingType.EASE_IN_OUT,
        }
        self._player.smooth_mouse_easing = easing_map.get(easing_index, EasingType.EASE_OUT_CUBIC)
    
    # === Utilitários ===
    
    def _update_status(self, message: str) -> None:
        """Atualiza a barra de status."""
        self._status_label.setText(message)
    
    def _show_from_tray(self) -> None:
        """Mostra a janela a partir da bandeja."""
        self.show()
        self.activateWindow()
        self.raise_()
    
    def _show_about(self) -> None:
        """Exibe informações sobre o programa."""
        QMessageBox.about(
            self,
            "Sobre MacroWing",
            "<h2>MacroWing</h2>"
            "<p>Gerenciador de Macros para Teclado e Mouse</p>"
            "<p>Versão 1.0.0</p>"
            "<p>Crie, grave e execute macros para automatizar suas tarefas.</p>"
        )
    
    def _quit_app(self) -> None:
        """Encerra a aplicação."""
        self._hotkey_manager.stop()
        self._player.stop()
        self._tray.hide()
        QApplication.quit()
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Evento de fechamento da janela."""
        if self._settings.get("minimize_to_tray", True):
            event.ignore()
            self.hide()
            self._tray.show_message(
                "MacroWing",
                "Aplicação minimizada para a bandeja.",
                duration_ms=2000
            )
        else:
            self._quit_app()
            event.accept()
