"""
MacroWing - Gerenciador de Macros para Teclado e Mouse

Entry point da aplicação.
"""
import os
import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.gui.main_window import MainWindow


def is_admin() -> bool:
    """Verifica se está rodando com privilégios elevados."""
    if sys.platform == "win32":
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    # Fora do Windows: root (a biblioteca `keyboard` exige root no Linux,
    # mas o backend padrão do Linux usa pynput e não precisa).
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def request_admin():
    """Solicita elevação de privilégios (somente Windows)."""
    if sys.platform != "win32":
        return
    if is_admin():
        return

    import ctypes
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
