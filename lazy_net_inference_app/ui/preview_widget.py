"""Виджет галереи для предпросмотра результатов."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap
import os


class PreviewWidget(QWidget):
    """Виджет для отображения галереи изображений с навигацией."""

    image_changed = pyqtSignal(int)  # Индекс текущего изображения

    def __init__(self, parent=None):
        super().__init__(parent)
        self.images = []
        self.current_index = 0

        self._init_ui()

    def _init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout(self)

        # Область для отображения изображения
        self.image_label = QLabel("Нет изображений для просмотра")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(220, 220)
        self.image_label.setStyleSheet(
            "background-color: #101218;"
            "border: 1px dashed #2C3242;"
            "border-radius: 12px;"
            "color: #8A93A8;"
        )
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.image_label)

        # Панель навигации
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(8)

        self.prev_button = QPushButton("←")
        self.prev_button.setToolTip("Предыдущее изображение")
        self.prev_button.setFixedWidth(44)
        self.prev_button.setProperty("kind", "ghost")
        self.prev_button.clicked.connect(self.show_previous)
        self.prev_button.setEnabled(False)

        self.next_button = QPushButton("→")
        self.next_button.setToolTip("Следующее изображение")
        self.next_button.setFixedWidth(44)
        self.next_button.setProperty("kind", "ghost")
        self.next_button.clicked.connect(self.show_next)
        self.next_button.setEnabled(False)

        self.counter_label = QLabel("0 / 0")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.counter_label.setStyleSheet(
            "background-color: #232834;"
            "border-radius: 10px;"
            "padding: 3px 14px;"
            "color: #E9ECF4;"
            "font-weight: 600;"
        )

        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.counter_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_button)

        layout.addLayout(nav_layout)

    def set_images(self, image_paths: list):
        """Устанавливает список изображений для просмотра."""
        self.images = [p for p in image_paths if os.path.exists(p)]
        self.current_index = 0

        if self.images:
            self.show_image(0)
            self.prev_button.setEnabled(True)
            self.next_button.setEnabled(len(self.images) > 1)
        else:
            self.image_label.setText("Нет изображений для просмотра")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.counter_label.setText("0 / 0")

    def show_image(self, index: int):
        """Отображает изображение по индексу."""
        if not self.images or index < 0 or index >= len(self.images):
            return

        self.current_index = index

        try:
            pixmap = QPixmap(self.images[index])

            # Все изображения вписываются в один и тот же квадрат,
            # чтобы картинка не меняла размер при переключении.
            label_size = self.image_label.size()
            side = max(min(label_size.width(), label_size.height()), 1)
            target = QSize(side, side)
            scaled_pixmap = pixmap.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)
            self.counter_label.setText(f"{index + 1} / {len(self.images)}")

            # Обновляем состояние кнопок
            self.prev_button.setEnabled(index > 0)
            self.next_button.setEnabled(index < len(self.images) - 1)

            self.image_changed.emit(index)

        except Exception as e:
            self.image_label.setText(f"Ошибка загрузки: {str(e)}")

    def show_previous(self):
        """Показывает предыдущее изображение."""
        if self.current_index > 0:
            self.show_image(self.current_index - 1)

    def show_next(self):
        """Показывает следующее изображение."""
        if self.current_index < len(self.images) - 1:
            self.show_image(self.current_index + 1)