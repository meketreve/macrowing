"""
Estilos e tema dark para o MacroWing.
"""

# Paleta de cores
COLORS = {
    "background": "#1a1a2e",
    "surface": "#16213e",
    "surface_light": "#1f2942",
    "primary": "#e94560",
    "primary_hover": "#ff6b6b",
    "primary_dark": "#c73e54",
    "secondary": "#0f3460",
    "secondary_light": "#1a4a7a",
    "accent": "#00d9ff",
    "text": "#eaeaea",
    "text_secondary": "#a0a0a0",
    "text_muted": "#6a6a6a",
    "success": "#00c853",
    "warning": "#ffc107",
    "error": "#ff5252",
    "border": "#2a2a4a",
}


DARK_THEME = f"""
/* ========== Janela Principal ========== */
QMainWindow, QDialog {{
    background-color: {COLORS["background"]};
    color: {COLORS["text"]};
}}

QWidget {{
    background-color: transparent;
    color: {COLORS["text"]};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}}

/* ========== Menus ========== */
QMenuBar {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text"]};
    padding: 4px;
    border-bottom: 1px solid {COLORS["border"]};
}}

QMenuBar::item:selected {{
    background-color: {COLORS["secondary"]};
    border-radius: 4px;
}}

QMenu {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS["secondary"]};
}}

QMenu::separator {{
    height: 1px;
    background-color: {COLORS["border"]};
    margin: 4px 8px;
}}

/* ========== Botões ========== */
QPushButton {{
    background-color: {COLORS["secondary"]};
    color: {COLORS["text"]};
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {COLORS["secondary_light"]};
}}

QPushButton:pressed {{
    background-color: {COLORS["primary_dark"]};
}}

QPushButton:disabled {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text_muted"]};
}}

QPushButton#primaryButton {{
    background-color: {COLORS["primary"]};
}}

QPushButton#primaryButton:hover {{
    background-color: {COLORS["primary_hover"]};
}}

QPushButton#dangerButton {{
    background-color: {COLORS["error"]};
}}

QPushButton#successButton {{
    background-color: {COLORS["success"]};
}}

/* ========== Inputs ========== */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text"]};
    border: 2px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 10px 14px;
    min-height: 20px;
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {COLORS["primary"]};
}}

QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
    background-color: {COLORS["surface_light"]};
    color: {COLORS["text_muted"]};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS["text"]};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    selection-background-color: {COLORS["secondary"]};
}}

/* ========== Listas e Tabelas ========== */
QListWidget, QTableWidget, QTreeWidget {{
    background-color: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}

QListWidget::item {{
    padding: 12px;
    border-radius: 6px;
    margin: 2px;
}}

QListWidget::item:selected {{
    background-color: {COLORS["secondary"]};
    color: {COLORS["text"]};
}}

QListWidget::item:hover {{
    background-color: {COLORS["surface_light"]};
}}

QTableWidget {{
    gridline-color: {COLORS["border"]};
}}

QHeaderView::section {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text_secondary"]};
    padding: 10px;
    border: none;
    border-bottom: 1px solid {COLORS["border"]};
    font-weight: bold;
}}

/* ========== ScrollBars ========== */
QScrollBar:vertical {{
    background-color: {COLORS["surface"]};
    width: 12px;
    border-radius: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS["secondary"]};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS["secondary_light"]};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {COLORS["surface"]};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS["secondary"]};
    border-radius: 6px;
    min-width: 30px;
}}

/* ========== Labels ========== */
QLabel {{
    color: {COLORS["text"]};
}}

QLabel#titleLabel {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS["text"]};
}}

QLabel#subtitleLabel {{
    font-size: 14px;
    color: {COLORS["text_secondary"]};
}}

QLabel#sectionLabel {{
    font-size: 16px;
    font-weight: bold;
    color: {COLORS["text"]};
    padding: 8px 0;
}}

/* ========== GroupBox ========== */
QGroupBox {{
    background-color: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 12px;
    margin-top: 20px;
    padding-top: 10px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    padding: 0 8px;
    color: {COLORS["text"]};
}}

/* ========== TabWidget ========== */
QTabWidget::pane {{
    background-color: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 8px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS["text_secondary"]};
    padding: 12px 24px;
    margin-right: 4px;
    border-bottom: 3px solid transparent;
}}

QTabBar::tab:selected {{
    color: {COLORS["text"]};
    border-bottom-color: {COLORS["primary"]};
}}

QTabBar::tab:hover:!selected {{
    color: {COLORS["text"]};
    background-color: {COLORS["surface_light"]};
}}

/* ========== Checkboxes e Radio ========== */
QCheckBox, QRadioButton {{
    color: {COLORS["text"]};
    spacing: 8px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {COLORS["border"]};
    background-color: {COLORS["surface"]};
}}

QCheckBox::indicator {{
    border-radius: 4px;
}}

QRadioButton::indicator {{
    border-radius: 10px;
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {COLORS["primary"]};
    border-color: {COLORS["primary"]};
}}

/* ========== Sliders ========== */
QSlider::groove:horizontal {{
    background-color: {COLORS["surface"]};
    height: 8px;
    border-radius: 4px;
}}

QSlider::handle:horizontal {{
    background-color: {COLORS["primary"]};
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
}}

QSlider::handle:horizontal:hover {{
    background-color: {COLORS["primary_hover"]};
}}

/* ========== ProgressBar ========== */
QProgressBar {{
    background-color: {COLORS["surface"]};
    border: none;
    border-radius: 8px;
    height: 16px;
    text-align: center;
    color: {COLORS["text"]};
}}

QProgressBar::chunk {{
    background-color: {COLORS["primary"]};
    border-radius: 8px;
}}

/* ========== ToolTip ========== */
QToolTip {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 8px;
}}

/* ========== StatusBar ========== */
QStatusBar {{
    background-color: {COLORS["surface"]};
    border-top: 1px solid {COLORS["border"]};
    padding: 4px;
}}

QStatusBar::item {{
    border: none;
}}

/* ========== Splitter ========== */
QSplitter::handle {{
    background-color: {COLORS["border"]};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

/* ========== Frame ========== */
QFrame#cardFrame {{
    background-color: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 12px;
    padding: 16px;
}}
"""
