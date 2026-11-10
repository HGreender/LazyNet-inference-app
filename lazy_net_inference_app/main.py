"""Точка входа в приложение LazyNet Inference."""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Запуск приложения."""
    app = QApplication(sys.argv)

    # Устанавливаем стиль приложения (опционально)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()