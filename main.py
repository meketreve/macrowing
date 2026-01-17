"""
MacroWing - Gerenciador de Macros para Teclado e Mouse

Entry point da aplicação.
"""
import sys
import ctypes

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.gui.main_window import MainWindow


def is_admin() -> bool:
    """Verifica se está rodando como administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def request_admin():
    """Solicita elevação de privilégios."""
    if not is_admin():
        # Re-executa como admin
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


def main():
    """Função principal."""
    # Tenta rodar como admin para funcionar em jogos
    # Comente as linhas abaixo se não precisar de privilégios elevados
    # request_admin()
    
    # Permite escalonamento de DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("MacroWing")
    app.setApplicationDisplayName("MacroWing")
    app.setOrganizationName("MacroWing")
    
    # Evita fechar quando a janela fecha (para bandeja)
    app.setQuitOnLastWindowClosed(False)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
