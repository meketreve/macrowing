"""
Widget de lista de macros.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMenu, QMessageBox, QLineEdit,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from ..core.macro import Macro
from .styles import COLORS


class MacroListItem(QListWidgetItem):
    """Item customizado para lista de macros."""
    
    def __init__(self, macro: Macro):
        super().__init__()
        self.macro = macro
        self.update_display()
    
    def update_display(self) -> None:
        """Atualiza o texto exibido."""
        status = "🟢" if self.macro.enabled else "🔴"
        hotkey = f"[{self.macro.hotkey}]" if self.macro.hotkey else ""
        actions_count = len(self.macro.actions)
        
        self.setText(f"{status} {self.macro.name} {hotkey}\n"
                    f"    {actions_count} ações")


class MacroListWidget(QWidget):
    """Lista de macros com barra de ferramentas."""
    
    # Sinais
    macro_selected = pyqtSignal(Macro)
    macro_double_clicked = pyqtSignal(Macro)
    new_macro_requested = pyqtSignal()
    record_macro_requested = pyqtSignal()
    delete_macro_requested = pyqtSignal(Macro)
    duplicate_macro_requested = pyqtSignal(Macro)
    play_macro_requested = pyqtSignal(Macro)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._macros: list[Macro] = []
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configura a interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Título
        title = QLabel("📋 Macros")
        title.setObjectName("sectionLabel")
        layout.addWidget(title)
        
        # Barra de busca
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Buscar macros...")
        self.search_box.textChanged.connect(self._filter_macros)
        layout.addWidget(self.search_box)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.btn_new = QPushButton("➕ Nova")
        self.btn_new.setObjectName("primaryButton")
        self.btn_new.clicked.connect(lambda: self.new_macro_requested.emit())
        button_layout.addWidget(self.btn_new)
        
        self.btn_record = QPushButton("⏺️ Gravar")
        self.btn_record.clicked.connect(lambda: self.record_macro_requested.emit())
        button_layout.addWidget(self.btn_record)
        
        layout.addLayout(button_layout)
        
        # Lista de macros
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget, 1)
        
        # Status
        self.status_label = QLabel("0 macros")
        self.status_label.setObjectName("subtitleLabel")
        layout.addWidget(self.status_label)
    
    def set_macros(self, macros: list[Macro]) -> None:
        """Define a lista de macros."""
        self._macros = macros
        self._refresh_list()
    
    def add_macro(self, macro: Macro) -> None:
        """Adiciona uma macro à lista."""
        self._macros.append(macro)
        self._refresh_list()
        # Seleciona a nova macro
        self._select_macro_by_id(macro.id)
    
    def update_macro(self, macro: Macro) -> None:
        """Atualiza uma macro na lista."""
        for i, m in enumerate(self._macros):
            if m.id == macro.id:
                self._macros[i] = macro
                break
        self._refresh_list()
        self._select_macro_by_id(macro.id)
    
    def remove_macro(self, macro_id: str) -> None:
        """Remove uma macro da lista."""
        self._macros = [m for m in self._macros if m.id != macro_id]
        self._refresh_list()
    
    def get_selected_macro(self) -> Macro | None:
        """Retorna a macro selecionada."""
        current = self.list_widget.currentItem()
        if isinstance(current, MacroListItem):
            return current.macro
        return None
    
    def _refresh_list(self) -> None:
        """Atualiza a lista visual."""
        self.list_widget.clear()
        
        for macro in self._macros:
            if self._matches_filter(macro):
                item = MacroListItem(macro)
                self.list_widget.addItem(item)
        
        self.status_label.setText(f"{len(self._macros)} macros")
    
    def _matches_filter(self, macro: Macro) -> bool:
        """Verifica se a macro corresponde ao filtro de busca."""
        filter_text = self.search_box.text().lower().strip()
        if not filter_text:
            return True
        return (filter_text in macro.name.lower() or 
                filter_text in macro.hotkey.lower())
    
    def _filter_macros(self) -> None:
        """Filtra as macros com base no texto de busca."""
        self._refresh_list()
    
    def _select_macro_by_id(self, macro_id: str) -> None:
        """Seleciona uma macro pelo ID."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if isinstance(item, MacroListItem) and item.macro.id == macro_id:
                self.list_widget.setCurrentItem(item)
                break
    
    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """Callback quando um item é clicado."""
        if isinstance(item, MacroListItem):
            self.macro_selected.emit(item.macro)
    
    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """Callback quando um item é duplo-clicado."""
        if isinstance(item, MacroListItem):
            self.macro_double_clicked.emit(item.macro)
    
    def _show_context_menu(self, pos) -> None:
        """Exibe menu de contexto."""
        item = self.list_widget.itemAt(pos)
        if not isinstance(item, MacroListItem):
            return
        
        macro = item.macro
        menu = QMenu(self)
        
        play_action = menu.addAction("▶️ Executar")
        play_action.triggered.connect(lambda: self.play_macro_requested.emit(macro))
        
        menu.addSeparator()
        
        duplicate_action = menu.addAction("📋 Duplicar")
        duplicate_action.triggered.connect(
            lambda: self.duplicate_macro_requested.emit(macro))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("🗑️ Excluir")
        delete_action.triggered.connect(
            lambda: self.delete_macro_requested.emit(macro))
        
        menu.exec(self.list_widget.mapToGlobal(pos))
