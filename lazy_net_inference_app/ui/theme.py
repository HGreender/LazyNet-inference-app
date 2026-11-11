"""Тёмная тема оформления LazyNet Inference App.

Палитра, QSS-стили, палитра Qt для нативных диалогов и иконка приложения.
"""
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import (
    QColor, QFont, QIcon, QLinearGradient, QPainter, QPalette, QPixmap,
)

# === Палитра ===
BG = "#14151B"            # фон окна
SURFACE = "#1B1E27"       # панели и группы
SURFACE_2 = "#232834"     # приподнятые элементы (кнопки, инпуты)
INPUT = "#1F2430"         # поля ввода
BORDER = "#2C3242"        # обычные рамки
BORDER_LIGHT = "#3A4155"  # заметные рамки
TEXT = "#E9ECF4"
MUTED = "#8A93A8"
ACCENT = "#6C8CFF"
ACCENT_HOVER = "#84A0FF"
ACCENT_PRESSED = "#5777E8"
ACCENT_DEEP = "#4A5FC9"
DANGER = "#FF6B7A"
LOG_BG = "#101218"
LOG_TEXT = "#B8C0D4"

STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {BG};
}}

QWidget {{
    color: {TEXT};
    font-size: 13px;
}}

QLabel {{
    background-color: transparent;
}}

QLabel[role="title"] {{
    font-size: 19px;
    font-weight: 700;
}}

QLabel[role="section"] {{
    font-size: 15px;
    font-weight: 700;
}}

QLabel[role="subtitle"] {{
    color: {MUTED};
    font-size: 12px;
}}

QLabel[role="muted"] {{
    color: {MUTED};
}}

QLabel[role="chip"] {{
    color: {MUTED};
    background-color: {SURFACE_2};
    border-radius: 10px;
    padding: 3px 12px;
    font-size: 12px;
}}

QGroupBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    margin-top: 14px;
    padding: 10px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0px 8px;
    color: {ACCENT};
    font-weight: 600;
    background-color: {BG};
}}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    min-height: 20px;
    selection-background-color: {ACCENT};
    selection-color: #FFFFFF;
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {ACCENT};
}}

QComboBox {{
    padding-right: 28px;
}}

QComboBox::drop-down {{
    border: none;
    width: 26px;
    background-color: transparent;
}}

QComboBox::down-arrow {{
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {MUTED};
    margin-right: 11px;
}}

QComboBox QAbstractItemView {{
    background-color: {SURFACE_2};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 8px;
    padding: 4px;
    outline: none;
    selection-background-color: {ACCENT};
    selection-color: #FFFFFF;
}}

QSpinBox, QDoubleSpinBox {{
    padding-right: 24px;
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    background-color: {SURFACE_2};
    border-top-right-radius: 7px;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    background-color: {SURFACE_2};
    border-bottom-right-radius: 7px;
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid {MUTED};
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {MUTED};
}}

QPushButton {{
    background-color: {SURFACE_2};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 8px;
    padding: 7px 14px;
    color: {TEXT};
}}

QPushButton:hover {{
    border-color: {ACCENT};
    background-color: #2A3040;
}}

QPushButton:pressed {{
    background-color: #262C3A;
}}

QPushButton:disabled {{
    color: #565E72;
    background-color: {SURFACE};
    border-color: {BORDER};
}}

QPushButton[kind="primary"] {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {ACCENT}, stop:1 {ACCENT_DEEP});
    border: none;
    color: #FFFFFF;
    font-weight: 600;
}}

QPushButton[kind="primary"]:hover {{
    background-color: {ACCENT_HOVER};
}}

QPushButton[kind="primary"]:pressed {{
    background-color: {ACCENT_PRESSED};
}}

QPushButton[kind="primary"]:disabled {{
    background-color: {SURFACE_2};
    border: 1px solid {BORDER};
    color: #565E72;
}}

QPushButton[kind="danger"] {{
    background-color: transparent;
    border: 1px solid {DANGER};
    color: {DANGER};
}}

QPushButton[kind="danger"]:hover {{
    background-color: rgba(255, 107, 122, 40);
}}

QPushButton[kind="danger"]:disabled {{
    background-color: transparent;
    border-color: {BORDER};
    color: #565E72;
}}

QPushButton[kind="ghost"] {{
    background-color: transparent;
    border: 1px solid {BORDER_LIGHT};
    color: {MUTED};
    padding: 6px 12px;
}}

QPushButton[kind="ghost"]:hover {{
    color: {TEXT};
    border-color: {ACCENT};
    background-color: rgba(108, 140, 255, 25);
}}

QPushButton[kind="ghost"]:disabled {{
    color: #565E72;
    border-color: {BORDER};
    background-color: transparent;
}}

QCheckBox {{
    spacing: 8px;
    background-color: transparent;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid {BORDER_LIGHT};
    background-color: {INPUT};
}}

QCheckBox::indicator:hover {{
    border-color: {ACCENT};
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}

QProgressBar {{
    background-color: {INPUT};
    border: 1px solid {BORDER};
    border-radius: 9px;
    min-height: 20px;
    text-align: center;
    color: #FFFFFF;
    font-weight: 600;
}}

QProgressBar::chunk {{
    border-radius: 8px;
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_DEEP}, stop:1 {ACCENT});
}}

QTextEdit {{
    background-color: {LOG_BG};
    border: 1px solid {BORDER};
    border-radius: 10px;
    color: {LOG_TEXT};
    selection-background-color: {ACCENT};
    selection-color: #FFFFFF;
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QSplitter::handle {{
    background-color: {BORDER};
}}

QStatusBar {{
    background-color: {SURFACE};
    color: {MUTED};
    border-top: 1px solid {BORDER};
}}

QMenu {{
    background-color: {SURFACE_2};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 6px 18px;
    border-radius: 6px;
}}

QMenu::item:selected {{
    background-color: {ACCENT};
    color: #FFFFFF;
}}

QScrollBar:vertical {{
    background-color: transparent;
    width: 10px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background-color: {BORDER_LIGHT};
    border-radius: 4px;
    min-height: 32px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #4A5268;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    width: 0;
    height: 0;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background-color: transparent;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 10px;
    margin: 2px;
}}

QScrollBar::handle:horizontal {{
    background-color: {BORDER_LIGHT};
    border-radius: 4px;
    min-width: 32px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: #4A5268;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
    height: 0;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background-color: transparent;
}}

QToolTip {{
    background-color: {SURFACE_2};
    color: {TEXT};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 6px;
    padding: 4px 8px;
}}
"""


def apply_theme(app) -> None:
    """Применяет тёмную тему к QApplication (стиль, QSS, палитра диалогов)."""
    app.setStyle("Fusion")
    app.setFont(QFont("Inter", 10))
    app.setStyleSheet(STYLESHEET)

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(INPUT))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(SURFACE_2))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor(SURFACE_2))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(SURFACE_2))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(MUTED))
    app.setPalette(palette)


_ICON_CACHE: dict[int, QIcon] = {}


def make_app_icon(size: int = 128) -> QIcon:
    """Генерирует иконку приложения (градиентный скругленный квадрат с буквой N)."""
    if size in _ICON_CACHE:
        return _ICON_CACHE[size]

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    margin = size * 0.05
    rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    radius = size * 0.24

    gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
    gradient.setColorAt(0.0, QColor(ACCENT))
    gradient.setColorAt(1.0, QColor("#8A5CFF"))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    painter.drawRoundedRect(rect, radius, radius)

    painter.setFont(QFont("Segoe UI", int(size * 0.42), QFont.Weight.Bold))
    painter.setPen(QColor("#FFFFFF"))
    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "N")

    painter.end()

    icon = QIcon(pixmap)
    _ICON_CACHE[size] = icon
    return icon