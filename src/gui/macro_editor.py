"""
Editor de macros.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QComboBox, QCheckBox,
    QGroupBox, QFrame, QMenu, QMessageBox, QDialog,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence

from ..core.macro import Macro, MacroAction, ActionType
from .styles import COLORS


class HotkeyLineEdit(QLineEdit):
    """LineEdit especial para capturar hotkeys."""
    
    hotkey_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Clique e pressione uma combinação...")
        self.setReadOnly(True)
        self._keys = []
    
    def keyPressEvent(self, event):
        """Captura a combinação de teclas."""
        key = event.key()
        modifiers = event.modifiers()
        
        parts = []
        
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("Ctrl")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("Alt")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("Shift")
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            parts.append("Win")
        
        # Adiciona a tecla se não for um modificador
        if key not in (Qt.Key.Key_Control, Qt.Key.Key_Alt, 
                       Qt.Key.Key_Shift, Qt.Key.Key_Meta):
            key_text = QKeySequence(key).toString()
            if key_text:
                parts.append(key_text)
        
        if parts:
            hotkey = "+".join(parts)
            self.setText(hotkey)
            self.hotkey_changed.emit(hotkey)
    
    def clear_hotkey(self):
        """Limpa a hotkey."""
        self.clear()
        self.hotkey_changed.emit("")


class ActionListItem(QListWidgetItem):
    """Item para lista de ações."""
    
    def __init__(self, action: MacroAction, index: int):
        super().__init__()
        self.action = action
        self.index = index
        self.update_display()
    
    def update_display(self) -> None:
        """Atualiza o texto exibido."""
        delay_str = ""
        if self.action.delay_before > 0:
            delay_str = f"[+{self.action.delay_before:.0f}ms] "
        
        self.setText(f"{self.index + 1}. {delay_str}{self.action.get_description()}")


class AddActionDialog(QDialog):
    """Diálogo para adicionar ação manualmente."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Ação")
        self.setMinimumWidth(350)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Tipo de ação
        type_layout = QFormLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "⌨️ Pressionar Tecla",
            "⌨️ Soltar Tecla",
            "🖱️ Clique do Mouse",
            "🖱️ Mover Mouse",
            "⏱️ Delay"
        ])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addRow("Tipo:", self.type_combo)
        layout.addLayout(type_layout)
        
        # Container para campos dinâmicos
        self.fields_container = QWidget()
        self.fields_layout = QFormLayout(self.fields_container)
        layout.addWidget(self.fields_container)
        
        # Campos
        self._create_fields()
        
        # Delay antes
        delay_layout = QFormLayout()
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 60000)
        self.delay_spin.setSuffix(" ms")
        delay_layout.addRow("Delay antes:", self.delay_spin)
        layout.addLayout(delay_layout)
        
        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self._on_type_changed(0)
    
    def _create_fields(self) -> None:
        """Cria todos os campos possíveis."""
        # Campo de tecla
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("Ex: a, space, enter, f1")
        
        # Campos de mouse
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        
        self.button_combo = QComboBox()
        self.button_combo.addItems(["left", "right", "middle"])
        
        # Campo de delay
        self.delay_ms_spin = QSpinBox()
        self.delay_ms_spin.setRange(1, 60000)
        self.delay_ms_spin.setValue(100)
        self.delay_ms_spin.setSuffix(" ms")
    
    def _clear_fields_layout(self) -> None:
        """Remove todos os widgets do layout de campos."""
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
    
    def _on_type_changed(self, index: int) -> None:
        """Atualiza os campos com base no tipo selecionado."""
        self._clear_fields_layout()
        
        if index in (0, 1):  # Tecla
            self.fields_layout.addRow("Tecla:", self.key_edit)
        elif index == 2:  # Clique
            self.fields_layout.addRow("X:", self.x_spin)
            self.fields_layout.addRow("Y:", self.y_spin)
            self.fields_layout.addRow("Botão:", self.button_combo)
        elif index == 3:  # Mover
            self.fields_layout.addRow("X:", self.x_spin)
            self.fields_layout.addRow("Y:", self.y_spin)
        elif index == 4:  # Delay
            self.fields_layout.addRow("Tempo:", self.delay_ms_spin)
    
    def get_action(self) -> MacroAction | None:
        """Retorna a ação criada."""
        index = self.type_combo.currentIndex()
        delay = self.delay_spin.value()
        
        if index == 0:  # Key press
            key = self.key_edit.text().strip()
            if not key:
                return None
            return MacroAction(
                action_type=ActionType.KEY_PRESS,
                data={"key": key},
                delay_before=delay
            )
        
        elif index == 1:  # Key release
            key = self.key_edit.text().strip()
            if not key:
                return None
            return MacroAction(
                action_type=ActionType.KEY_RELEASE,
                data={"key": key},
                delay_before=delay
            )
        
        elif index == 2:  # Mouse click
            return MacroAction(
                action_type=ActionType.MOUSE_CLICK,
                data={
                    "x": self.x_spin.value(),
                    "y": self.y_spin.value(),
                    "button": self.button_combo.currentText()
                },
                delay_before=delay
            )
        
        elif index == 3:  # Mouse move
            return MacroAction(
                action_type=ActionType.MOUSE_MOVE,
                data={
                    "x": self.x_spin.value(),
                    "y": self.y_spin.value()
                },
                delay_before=delay
            )
        
        elif index == 4:  # Delay
            return MacroAction(
                action_type=ActionType.DELAY,
                data={"ms": self.delay_ms_spin.value()},
                delay_before=delay
            )
        
        return None


class MacroEditorWidget(QWidget):
    """Editor de macro."""
    
    # Sinais
    macro_saved = pyqtSignal(Macro)
    macro_test_requested = pyqtSignal(Macro)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_macro: Macro | None = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configura a interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Título
        self.title_label = QLabel("📝 Editor de Macro")
        self.title_label.setObjectName("sectionLabel")
        layout.addWidget(self.title_label)
        
        # Informações básicas
        info_group = QGroupBox("Informações")
        info_layout = QFormLayout(info_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nome da macro")
        info_layout.addRow("Nome:", self.name_edit)
        
        self.hotkey_edit = HotkeyLineEdit()
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(self.hotkey_edit)
        clear_btn = QPushButton("✕")
        clear_btn.setMaximumWidth(40)
        clear_btn.clicked.connect(self.hotkey_edit.clear_hotkey)
        hotkey_layout.addWidget(clear_btn)
        info_layout.addRow("Hotkey:", hotkey_layout)
        
        layout.addWidget(info_group)
        
        # Repetição
        loop_group = QGroupBox("Repetição")
        loop_layout = QFormLayout(loop_group)
        
        self.loop_count_spin = QSpinBox()
        self.loop_count_spin.setRange(0, 9999)
        self.loop_count_spin.setValue(1)
        self.loop_count_spin.setSpecialValueText("∞ Infinito")
        loop_layout.addRow("Repetir:", self.loop_count_spin)
        
        self.loop_delay_spin = QSpinBox()
        self.loop_delay_spin.setRange(0, 60000)
        self.loop_delay_spin.setSuffix(" ms")
        loop_layout.addRow("Delay entre loops:", self.loop_delay_spin)
        
        layout.addWidget(loop_group)
        
        # Lista de ações
        actions_group = QGroupBox("Ações")
        actions_layout = QVBoxLayout(actions_group)
        
        # Toolbar de ações
        actions_toolbar = QHBoxLayout()
        
        self.btn_add_action = QPushButton("➕ Adicionar")
        self.btn_add_action.clicked.connect(self._add_action)
        actions_toolbar.addWidget(self.btn_add_action)
        
        self.btn_remove_action = QPushButton("🗑️ Remover")
        self.btn_remove_action.clicked.connect(self._remove_action)
        actions_toolbar.addWidget(self.btn_remove_action)
        
        self.btn_move_up = QPushButton("⬆️")
        self.btn_move_up.setMaximumWidth(50)
        self.btn_move_up.clicked.connect(self._move_action_up)
        actions_toolbar.addWidget(self.btn_move_up)
        
        self.btn_move_down = QPushButton("⬇️")
        self.btn_move_down.setMaximumWidth(50)
        self.btn_move_down.clicked.connect(self._move_action_down)
        actions_toolbar.addWidget(self.btn_move_down)
        
        actions_toolbar.addStretch()
        actions_layout.addLayout(actions_toolbar)
        
        self.actions_list = QListWidget()
        actions_layout.addWidget(self.actions_list)
        
        layout.addWidget(actions_group, 1)
        
        # Botões finais
        buttons_layout = QHBoxLayout()
        
        self.btn_test = QPushButton("▶️ Testar")
        self.btn_test.clicked.connect(self._test_macro)
        buttons_layout.addWidget(self.btn_test)
        
        buttons_layout.addStretch()
        
        self.btn_save = QPushButton("💾 Salvar")
        self.btn_save.setObjectName("primaryButton")
        self.btn_save.clicked.connect(self._save_macro)
        buttons_layout.addWidget(self.btn_save)
        
        layout.addLayout(buttons_layout)
        
        # Estado inicial
        self.set_enabled(False)
    
    def set_enabled(self, enabled: bool) -> None:
        """Ativa/desativa o editor."""
        self.name_edit.setEnabled(enabled)
        self.hotkey_edit.setEnabled(enabled)
        self.loop_count_spin.setEnabled(enabled)
        self.loop_delay_spin.setEnabled(enabled)
        self.actions_list.setEnabled(enabled)
        self.btn_add_action.setEnabled(enabled)
        self.btn_remove_action.setEnabled(enabled)
        self.btn_move_up.setEnabled(enabled)
        self.btn_move_down.setEnabled(enabled)
        self.btn_test.setEnabled(enabled)
        self.btn_save.setEnabled(enabled)
    
    def load_macro(self, macro: Macro) -> None:
        """Carrega uma macro para edição."""
        self._current_macro = macro
        
        self.name_edit.setText(macro.name)
        self.hotkey_edit.setText(macro.hotkey)
        self.loop_count_spin.setValue(macro.loop_count)
        self.loop_delay_spin.setValue(int(macro.loop_delay))
        
        self._refresh_actions_list()
        self.set_enabled(True)
        self.title_label.setText(f"📝 Editando: {macro.name}")
    
    def clear(self) -> None:
        """Limpa o editor."""
        self._current_macro = None
        self.name_edit.clear()
        self.hotkey_edit.clear()
        self.loop_count_spin.setValue(1)
        self.loop_delay_spin.setValue(0)
        self.actions_list.clear()
        self.set_enabled(False)
        self.title_label.setText("📝 Editor de Macro")
    
    def _refresh_actions_list(self) -> None:
        """Atualiza a lista de ações."""
        self.actions_list.clear()
        
        if not self._current_macro:
            return
        
        for i, action in enumerate(self._current_macro.actions):
            item = ActionListItem(action, i)
            self.actions_list.addItem(item)
    
    def _add_action(self) -> None:
        """Adiciona uma nova ação."""
        if not self._current_macro:
            return
        
        dialog = AddActionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            action = dialog.get_action()
            if action:
                self._current_macro.add_action(action)
                self._refresh_actions_list()
    
    def _remove_action(self) -> None:
        """Remove a ação selecionada."""
        if not self._current_macro:
            return
        
        current = self.actions_list.currentItem()
        if isinstance(current, ActionListItem):
            self._current_macro.remove_action(current.index)
            self._refresh_actions_list()
    
    def _move_action_up(self) -> None:
        """Move a ação selecionada para cima."""
        if not self._current_macro:
            return
        
        current = self.actions_list.currentItem()
        if isinstance(current, ActionListItem) and current.index > 0:
            self._current_macro.move_action(current.index, current.index - 1)
            self._refresh_actions_list()
            self.actions_list.setCurrentRow(current.index - 1)
    
    def _move_action_down(self) -> None:
        """Move a ação selecionada para baixo."""
        if not self._current_macro:
            return
        
        current = self.actions_list.currentItem()
        if isinstance(current, ActionListItem):
            if current.index < len(self._current_macro.actions) - 1:
                self._current_macro.move_action(current.index, current.index + 1)
                self._refresh_actions_list()
                self.actions_list.setCurrentRow(current.index + 1)
    
    def _save_macro(self) -> None:
        """Salva as alterações na macro."""
        if not self._current_macro:
            return
        
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Erro", "O nome da macro é obrigatório.")
            return
        
        self._current_macro.name = name
        self._current_macro.hotkey = self.hotkey_edit.text()
        self._current_macro.loop_count = self.loop_count_spin.value()
        self._current_macro.loop_delay = self.loop_delay_spin.value()
        
        self.macro_saved.emit(self._current_macro)
        self.title_label.setText(f"📝 Editando: {name}")
    
    def _test_macro(self) -> None:
        """Testa a macro atual."""
        if self._current_macro:
            self.macro_test_requested.emit(self._current_macro)
