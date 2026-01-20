"""
Widget de gravação de macros.
"""
import keyboard
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QCheckBox, QProgressBar, QFrame, QDialog, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from ..core.macro import Macro, MacroAction
from ..core.recorder import MacroRecorder


class MacroRecorderDialog(QDialog):
    """Diálogo de gravação de macro."""
    
    recording_finished = pyqtSignal(Macro)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gravar Macro - MacroWing")
        self.setMinimumSize(400, 350)
        self.setModal(True)
        
        self._recorder = MacroRecorder()
        self._recorder.on_action_recorded = self._on_action_recorded
        self._action_count = 0
        self._countdown_value = 3
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Instruções
        instructions = QLabel(
            "Clique em 'Iniciar' e execute as ações que deseja gravar.\n"
            "Pressione F10 ou ESC para parar a gravação."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        # Opções
        options_frame = QFrame()
        options_frame.setObjectName("cardFrame")
        options_layout = QVBoxLayout(options_frame)
        
        self.record_movement_check = QCheckBox("Gravar movimentos do mouse")
        self.record_movement_check.setChecked(False)
        options_layout.addWidget(self.record_movement_check)
        
        self.record_release_check = QCheckBox("Gravar liberação de teclas")
        self.record_release_check.setChecked(True)
        options_layout.addWidget(self.record_release_check)
        
        # Configuração de contagem regressiva
        countdown_layout = QHBoxLayout()
        countdown_layout.addWidget(QLabel("Contagem regressiva:"))
        self.countdown_spin = QSpinBox()
        self.countdown_spin.setRange(0, 10)
        self.countdown_spin.setValue(3)
        self.countdown_spin.setSuffix(" segundos")
        self.countdown_spin.setToolTip("0 = sem contagem")
        countdown_layout.addWidget(self.countdown_spin)
        countdown_layout.addStretch()
        options_layout.addLayout(countdown_layout)
        
        layout.addWidget(options_frame)
        
        # Display da contagem regressiva (grande, no centro)
        self.countdown_display = QLabel("")
        self.countdown_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_display.setStyleSheet(
            "font-size: 72px; font-weight: bold; color: #e94560;"
        )
        self.countdown_display.hide()
        layout.addWidget(self.countdown_display)
        
        # Status
        self.status_label = QLabel("Pronto para gravar")
        self.status_label.setObjectName("subtitleLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Contador
        self.counter_label = QLabel("0 ações gravadas")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.counter_label)
        
        # Indicador de gravação
        self.recording_indicator = QLabel("⏺️ GRAVANDO")
        self.recording_indicator.setStyleSheet(
            "color: #ff5252; font-size: 18px; font-weight: bold;"
        )
        self.recording_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recording_indicator.hide()
        layout.addWidget(self.recording_indicator)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("⏺️ Iniciar Gravação")
        self.btn_start.setObjectName("primaryButton")
        self.btn_start.clicked.connect(self._start_countdown)
        buttons_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("⏹️ Parar")
        self.btn_stop.clicked.connect(self._stop_recording)
        self.btn_stop.setEnabled(False)
        buttons_layout.addWidget(self.btn_stop)
        
        layout.addLayout(buttons_layout)
        
        # Timers
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._blink_indicator)
        self._blink_visible = True
        
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._countdown_tick)
    
    def _start_countdown(self) -> None:
        """Inicia a contagem regressiva antes de gravar."""
        countdown_seconds = self.countdown_spin.value()
        
        if countdown_seconds == 0:
            # Sem contagem, inicia direto
            self._start_recording()
            return
        
        # Prepara para contagem
        self._countdown_value = countdown_seconds
        self._action_count = 0
        self.counter_label.setText("0 ações gravadas")
        
        # Atualiza UI para modo contagem
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.record_movement_check.setEnabled(False)
        self.record_release_check.setEnabled(False)
        self.countdown_spin.setEnabled(False)
        
        # Mostra contagem
        self.countdown_display.setText(str(self._countdown_value))
        self.countdown_display.show()
        self.status_label.setText("Preparando...")
        
        # Inicia timer (1 segundo)
        self._countdown_timer.start(1000)
    
    def _countdown_tick(self) -> None:
        """Atualiza a contagem regressiva."""
        self._countdown_value -= 1
        
        if self._countdown_value > 0:
            self.countdown_display.setText(str(self._countdown_value))
        else:
            # Contagem terminou, inicia gravação
            self._countdown_timer.stop()
            self.countdown_display.setText("🎬")
            QTimer.singleShot(300, self._finish_countdown)
    
    def _finish_countdown(self) -> None:
        """Finaliza a contagem e inicia a gravação."""
        self.countdown_display.hide()
        self._start_recording()
    
    def _start_recording(self) -> None:
        """Inicia a gravação."""
        self._action_count = 0
        self.counter_label.setText("0 ações gravadas")
        
        # Configura o gravador
        self._recorder.record_mouse_movement = self.record_movement_check.isChecked()
        self._recorder.record_key_release = self.record_release_check.isChecked()
        
        # Registra hotkey global para parar (F10)
        try:
            keyboard.add_hotkey('f10', self._on_stop_hotkey, suppress=True)
        except Exception:
            pass  # Ignora se não conseguir registrar
        
        # Inicia
        self._recorder.start()
        
        # Atualiza UI
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.record_movement_check.setEnabled(False)
        self.record_release_check.setEnabled(False)
        self.countdown_spin.setEnabled(False)
        self.status_label.setText("Gravando... Pressione F10 para parar")
        self.recording_indicator.show()
        self._blink_timer.start(500)
    
    def _on_stop_hotkey(self) -> None:
        """Callback quando a hotkey de parar é pressionada."""
        # Usa QTimer para chamar no thread principal
        QTimer.singleShot(0, self._stop_recording)
    
    def _stop_recording(self) -> None:
        """Para a gravação."""
        # Remove hotkey global
        try:
            keyboard.remove_hotkey('f10')
        except Exception:
            pass  # Ignora se não estava registrada
        
        # Para timers
        self._blink_timer.stop()
        self._countdown_timer.stop()
        self.countdown_display.hide()
        
        # Se ainda estava na contagem, apenas cancela
        if not self._recorder.is_recording:
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.record_movement_check.setEnabled(True)
            self.record_release_check.setEnabled(True)
            self.countdown_spin.setEnabled(True)
            self.status_label.setText("Gravação cancelada")
            self.recording_indicator.hide()
            return
        
        actions = self._recorder.stop()
        
        # Atualiza UI
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.record_movement_check.setEnabled(True)
        self.record_release_check.setEnabled(True)
        self.countdown_spin.setEnabled(True)
        self.status_label.setText(f"Gravação finalizada: {len(actions)} ações")
        self.recording_indicator.hide()
        
        # Se tem ações, cria macro e emite sinal
        if actions:
            macro = self._recorder.create_macro("Macro Gravada")
            self.recording_finished.emit(macro)
            self.accept()
        else:
            self.status_label.setText("Nenhuma ação gravada")
    
    def _on_action_recorded(self, action: MacroAction) -> None:
        """Callback quando uma ação é gravada."""
        self._action_count += 1
        self.counter_label.setText(f"{self._action_count} ações gravadas")
    
    def _blink_indicator(self) -> None:
        """Animação do indicador de gravação."""
        self._blink_visible = not self._blink_visible
        self.recording_indicator.setVisible(self._blink_visible)
    
    def keyPressEvent(self, event):
        """Captura ESC para parar gravação."""
        if event.key() == Qt.Key.Key_Escape:
            if self._recorder.is_recording or self._countdown_timer.isActive():
                self._stop_recording()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Garante que a gravação para ao fechar."""
        # Remove hotkey global
        try:
            keyboard.remove_hotkey('f10')
        except Exception:
            pass
        
        self._countdown_timer.stop()
        if self._recorder.is_recording:
            self._recorder.stop()
        super().closeEvent(event)

