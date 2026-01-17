"""
Diálogo de configurações.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox, QGroupBox,
    QTabWidget, QWidget, QDialogButtonBox, QFileDialog,
    QMessageBox, QSlider, QDoubleSpinBox, QSpinBox, QComboBox
)
from PyQt6.QtCore import pyqtSignal, Qt

from .macro_editor import HotkeyLineEdit


class SettingsDialog(QDialog):
    """Diálogo de configurações da aplicação."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.setMinimumSize(500, 500)
        
        self._settings = settings.copy()
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab Geral
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Comportamento
        behavior_group = QGroupBox("Comportamento")
        behavior_layout = QFormLayout(behavior_group)
        
        self.start_minimized_check = QCheckBox("Iniciar minimizado na bandeja")
        behavior_layout.addRow(self.start_minimized_check)
        
        self.minimize_to_tray_check = QCheckBox("Minimizar para bandeja ao fechar")
        behavior_layout.addRow(self.minimize_to_tray_check)
        
        self.start_with_windows_check = QCheckBox("Iniciar com o Windows")
        behavior_layout.addRow(self.start_with_windows_check)
        
        general_layout.addWidget(behavior_group)
        
        # Tecla de pânico
        panic_group = QGroupBox("Tecla de Emergência")
        panic_layout = QFormLayout(panic_group)
        
        panic_info = QLabel(
            "Esta tecla para todas as macros em execução imediatamente."
        )
        panic_info.setWordWrap(True)
        panic_layout.addRow(panic_info)
        
        self.panic_key_edit = HotkeyLineEdit()
        panic_key_layout = QHBoxLayout()
        panic_key_layout.addWidget(self.panic_key_edit)
        clear_btn = QPushButton("✕")
        clear_btn.setMaximumWidth(40)
        clear_btn.clicked.connect(self.panic_key_edit.clear_hotkey)
        panic_key_layout.addWidget(clear_btn)
        panic_layout.addRow("Tecla:", panic_key_layout)
        
        general_layout.addWidget(panic_group)
        general_layout.addStretch()
        
        tabs.addTab(general_tab, "Geral")
        
        # Tab Movimento do Mouse
        movement_tab = QWidget()
        movement_layout = QVBoxLayout(movement_tab)
        
        # Movimento suave
        smooth_group = QGroupBox("Movimento Suave do Mouse")
        smooth_layout = QFormLayout(smooth_group)
        
        smooth_info = QLabel(
            "O movimento suave faz o cursor se mover de forma fluida\n"
            "entre os pontos, imitando o comportamento humano."
        )
        smooth_info.setWordWrap(True)
        smooth_layout.addRow(smooth_info)
        
        self.smooth_enabled_check = QCheckBox("Ativar movimento suave")
        smooth_layout.addRow(self.smooth_enabled_check)
        
        # Tipo de easing
        self.easing_combo = QComboBox()
        self.easing_combo.addItems([
            "Linear (sem easing)",
            "Ease Out Quadrático (natural)",
            "Ease Out Cúbico (mais suave)",
            "Ease Out Exponencial (muito suave)",
            "Ease In/Out (suave início e fim)"
        ])
        smooth_layout.addRow("Curva de movimento:", self.easing_combo)
        
        # Velocidade
        speed_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 30)  # 0.1x a 3.0x
        self.speed_slider.setValue(10)  # 1.0x
        self.speed_slider.valueChanged.connect(self._update_speed_label)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("1.0x")
        self.speed_label.setMinimumWidth(40)
        speed_layout.addWidget(self.speed_label)
        smooth_layout.addRow("Velocidade:", speed_layout)
        
        # Duração mínima
        self.min_duration_spin = QSpinBox()
        self.min_duration_spin.setRange(10, 500)
        self.min_duration_spin.setValue(50)
        self.min_duration_spin.setSuffix(" ms")
        smooth_layout.addRow("Duração mínima:", self.min_duration_spin)
        
        # Duração máxima
        self.max_duration_spin = QSpinBox()
        self.max_duration_spin.setRange(100, 2000)
        self.max_duration_spin.setValue(800)
        self.max_duration_spin.setSuffix(" ms")
        smooth_layout.addRow("Duração máxima:", self.max_duration_spin)
        
        movement_layout.addWidget(smooth_group)
        movement_layout.addStretch()
        
        tabs.addTab(movement_tab, "Movimento")
        
        # Tab Gravação
        recording_tab = QWidget()
        recording_layout = QVBoxLayout(recording_tab)
        
        recording_group = QGroupBox("Opções de Gravação")
        rec_form = QFormLayout(recording_group)
        
        self.default_record_movement = QCheckBox("Gravar movimentos do mouse por padrão")
        rec_form.addRow(self.default_record_movement)
        
        self.default_record_release = QCheckBox("Gravar liberação de teclas por padrão")
        rec_form.addRow(self.default_record_release)
        
        recording_layout.addWidget(recording_group)
        recording_layout.addStretch()
        
        tabs.addTab(recording_tab, "Gravação")
        
        # Tab Dados
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        data_group = QGroupBox("Gerenciamento de Dados")
        data_form = QVBoxLayout(data_group)
        
        # Localização
        location_layout = QHBoxLayout()
        self.data_location_label = QLabel()
        location_layout.addWidget(self.data_location_label, 1)
        
        open_folder_btn = QPushButton("📁 Abrir Pasta")
        open_folder_btn.clicked.connect(self._open_data_folder)
        location_layout.addWidget(open_folder_btn)
        data_form.addLayout(location_layout)
        
        # Backup
        backup_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 Exportar Todas")
        export_btn.clicked.connect(self._export_all)
        backup_layout.addWidget(export_btn)
        
        import_btn = QPushButton("📥 Importar")
        import_btn.clicked.connect(self._import_macros)
        backup_layout.addWidget(import_btn)
        
        data_form.addLayout(backup_layout)
        
        data_layout.addWidget(data_group)
        data_layout.addStretch()
        
        tabs.addTab(data_tab, "Dados")
        
        layout.addWidget(tabs)
        
        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        buttons.accepted.connect(self._save_and_close)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self._apply_settings
        )
        layout.addWidget(buttons)
    
    def _update_speed_label(self, value: int) -> None:
        """Atualiza o label de velocidade."""
        speed = value / 10.0
        self.speed_label.setText(f"{speed:.1f}x")
    
    def _load_settings(self) -> None:
        """Carrega as configurações nos widgets."""
        self.start_minimized_check.setChecked(
            self._settings.get("start_minimized", False)
        )
        self.minimize_to_tray_check.setChecked(
            self._settings.get("minimize_to_tray", True)
        )
        self.start_with_windows_check.setChecked(
            self._settings.get("start_with_windows", False)
        )
        self.panic_key_edit.setText(
            self._settings.get("panic_key", "escape")
        )
        self.default_record_movement.setChecked(
            self._settings.get("default_record_movement", False)
        )
        self.default_record_release.setChecked(
            self._settings.get("default_record_release", True)
        )
        
        # Configurações de movimento suave
        self.smooth_enabled_check.setChecked(
            self._settings.get("smooth_mouse_enabled", True)
        )
        self.easing_combo.setCurrentIndex(
            self._settings.get("smooth_mouse_easing_index", 2)  # Cúbico por padrão
        )
        speed_value = int(self._settings.get("smooth_mouse_speed", 1.0) * 10)
        self.speed_slider.setValue(speed_value)
        self._update_speed_label(speed_value)
        self.min_duration_spin.setValue(
            self._settings.get("smooth_mouse_min_duration", 50)
        )
        self.max_duration_spin.setValue(
            self._settings.get("smooth_mouse_max_duration", 800)
        )
        
        from ..utils.helpers import get_data_dir
        self.data_location_label.setText(str(get_data_dir()))
    
    def _get_settings(self) -> dict:
        """Obtém as configurações dos widgets."""
        return {
            "start_minimized": self.start_minimized_check.isChecked(),
            "minimize_to_tray": self.minimize_to_tray_check.isChecked(),
            "start_with_windows": self.start_with_windows_check.isChecked(),
            "panic_key": self.panic_key_edit.text(),
            "default_record_movement": self.default_record_movement.isChecked(),
            "default_record_release": self.default_record_release.isChecked(),
            # Configurações de movimento suave
            "smooth_mouse_enabled": self.smooth_enabled_check.isChecked(),
            "smooth_mouse_easing_index": self.easing_combo.currentIndex(),
            "smooth_mouse_speed": self.speed_slider.value() / 10.0,
            "smooth_mouse_min_duration": self.min_duration_spin.value(),
            "smooth_mouse_max_duration": self.max_duration_spin.value(),
        }
    
    def _apply_settings(self) -> None:
        """Aplica as configurações."""
        settings = self._get_settings()
        self._settings = settings
        self.settings_changed.emit(settings)
    
    def _save_and_close(self) -> None:
        """Salva e fecha o diálogo."""
        self._apply_settings()
        self.accept()
    
    def _open_data_folder(self) -> None:
        """Abre a pasta de dados no explorador."""
        import os
        from ..utils.helpers import get_data_dir
        os.startfile(str(get_data_dir()))
    
    def _export_all(self) -> None:
        """Exporta todas as macros."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Macros",
            "macros_backup.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            # Será implementado pela janela principal
            from ..utils.helpers import get_macros_file
            import shutil
            try:
                shutil.copy2(get_macros_file(), file_path)
                QMessageBox.information(
                    self, "Sucesso", "Macros exportadas com sucesso!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Falha ao exportar: {e}"
                )
    
    def _import_macros(self) -> None:
        """Importa macros de um arquivo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Macros",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            QMessageBox.information(
                self, "Info",
                "Feche este diálogo e use o botão 'Importar' na janela principal."
            )
