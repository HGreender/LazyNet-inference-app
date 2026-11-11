"""Точка входа в приложение LazyNet Inference."""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.theme import apply_theme


def main():
    """Запуск приложения."""
    app = QApplication(sys.argv)

    # Тёмная тема оформления
    apply_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()