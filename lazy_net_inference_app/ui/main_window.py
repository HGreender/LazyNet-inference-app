"""Основное окно приложения для инференса LazyNet."""
import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QFileDialog,
    QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QFormLayout,
    QTextEdit, QProgressBar, QSplitter, QMessageBox,
    QColorDialog, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont

from core.inference_worker import InferenceWorker
from core.config import (
    DEFAULT_THRESHOLD, DEFAULT_OVERLAY_COLOR, DEFAULT_OVERLAY_STRENGTH,
    DEFAULT_SAVE_MASKS, DEFAULT_SAVE_CONCAT, DEFAULT_SAVE_OVERLAY,
    DEFAULT_BATCH_SIZE, DEFAULT_NUM_WORKERS, DEFAULT_SAVE_WORKERS,
    AVAILABLE_MODELS, DEFAULT_MODEL_NAME,
    AVAILABLE_AUGMENTATIONS, DEFAULT_AUGMENTATION,
    CONFIG_FILE
)
from utils.helpers import (
    validate_model_path, validate_image_folder, validate_output_folder,
    get_image_list, load_config, save_config
)
from ui.preview_widget import PreviewWidget
from ui.theme import make_app_icon


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()

        self.worker = None
        self.overlay_color = DEFAULT_OVERLAY_COLOR
        self.settings = QSettings("LazyNet", "InferenceApp")

        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("LazyNet Inference")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(make_app_icon())

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(16, 14, 16, 10)
        root_layout.setSpacing(12)

        # === Шапка приложения ===
        header = QWidget()
        header.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        logo = QLabel()
        logo.setFixedSize(40, 40)
        logo.setPixmap(make_app_icon().pixmap(40, 40))
        header_layout.addWidget(logo)

        title_block = QWidget()
        title_layout = QVBoxLayout(title_block)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        title = QLabel("LazyNet Inference")
        title.setProperty("role", "title")
        title_layout.addWidget(title)

        subtitle = QLabel("Сегментация изображений · инференс · предпросмотр")
        subtitle.setProperty("role", "subtitle")
        title_layout.addWidget(subtitle)

        header_layout.addWidget(title_block)
        header_layout.addStretch()

        version_chip = QLabel("v1.0")
        version_chip.setProperty("role", "chip")
        header_layout.addWidget(version_chip)

        root_layout.addWidget(header)

        # Сплиттер: панель управления и предпросмотр
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)

        # Левая панель - управление
        control_panel = self._create_control_panel()
        splitter.addWidget(control_panel)

        # Правая панель - предпросмотр
        preview_panel = self._create_preview_panel()
        preview_panel.setMinimumWidth(380)
        splitter.addWidget(preview_panel)

        # Устанавливаем пропорции (66% управление, 33% превью)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        root_layout.addWidget(splitter)

        # Статус-бар
        self.statusBar().showMessage("Готов к работе")

    def _create_control_panel(self) -> QWidget:
        """Создает панель управления (в прокручиваемой области)."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # === Группа: Выбор модели ===
        model_group = QGroupBox("Модель")
        model_layout = QVBoxLayout(model_group)

        # Выбор имени модели
        model_name_layout = QHBoxLayout()
        model_name_layout.addWidget(QLabel("Архитектура:"))
        self.model_name_combo = QComboBox()
        self.model_name_combo.addItems(AVAILABLE_MODELS)
        self.model_name_combo.setCurrentText(DEFAULT_MODEL_NAME)
        model_name_layout.addWidget(self.model_name_combo)
        model_layout.addLayout(model_name_layout)

        # Выбор функции аугментаций
        augmentation_layout = QHBoxLayout()
        augmentation_layout.addWidget(QLabel("Аугментация:"))
        self.augmentation_combo = QComboBox()
        self.augmentation_combo.addItems(AVAILABLE_AUGMENTATIONS)
        self.augmentation_combo.setCurrentText(DEFAULT_AUGMENTATION)
        augmentation_layout.addWidget(self.augmentation_combo)
        model_layout.addLayout(augmentation_layout)

        # Путь к файлу модели
        model_path_layout = QHBoxLayout()
        model_path_layout.addWidget(QLabel("Веса (.pth):"))
        self.model_path_edit = QLineEdit()
        self.model_path_edit.setPlaceholderText("Выберите файл модели...")
        model_path_layout.addWidget(self.model_path_edit)

        browse_model_btn = QPushButton("Обзор…")
        browse_model_btn.setProperty("kind", "ghost")
        browse_model_btn.clicked.connect(self.browse_model)
        model_path_layout.addWidget(browse_model_btn)
        model_layout.addLayout(model_path_layout)

        layout.addWidget(model_group)

        # === Группа: Входные/выходные данные ===
        data_group = QGroupBox("Данные")
        data_layout = QVBoxLayout(data_group)

        # Папка с изображениями
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Входная папка:"))
        self.input_dir_edit = QLineEdit()
        self.input_dir_edit.setPlaceholderText("Папка с изображениями...")
        input_layout.addWidget(self.input_dir_edit)

        browse_input_btn = QPushButton("Обзор…")
        browse_input_btn.setProperty("kind", "ghost")
        browse_input_btn.clicked.connect(self.browse_input_folder)
        input_layout.addWidget(browse_input_btn)
        data_layout.addLayout(input_layout)

        # Выходная папка
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Выходная папка:"))
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Папка для результатов...")
        output_layout.addWidget(self.output_dir_edit)

        browse_output_btn = QPushButton("Обзор…")
        browse_output_btn.setProperty("kind", "ghost")
        browse_output_btn.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(browse_output_btn)
        data_layout.addLayout(output_layout)

        layout.addWidget(data_group)

        # === Группа: Параметры инференса ===
        params_group = QGroupBox("Параметры инференса")
        form = QFormLayout(params_group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setSpacing(10)

        # Threshold
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.0, 1.0)
        self.threshold_spin.setSingleStep(0.05)
        self.threshold_spin.setValue(DEFAULT_THRESHOLD)
        self._limit_spin_width(self.threshold_spin)
        form.addRow("Threshold:", self.threshold_spin)

        # Overlay color
        color_row = QWidget()
        color_layout = QHBoxLayout(color_row)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setSpacing(10)
        self.overlay_color_swatch = QLabel()
        self.overlay_color_swatch.setFixedSize(56, 32)
        self.overlay_color_swatch.setToolTip("Цвет оверлея")
        self.overlay_color_btn = QPushButton("Выбрать цвет…")
        self.overlay_color_btn.setProperty("kind", "ghost")
        self.overlay_color_btn.clicked.connect(self.choose_overlay_color)
        color_layout.addWidget(self.overlay_color_btn)
        color_layout.addWidget(self.overlay_color_swatch)
        self.overlay_color_label = QLabel(f"RGB: {DEFAULT_OVERLAY_COLOR}")
        self.overlay_color_label.setProperty("role", "muted")
        color_layout.addWidget(self.overlay_color_label)
        color_layout.addStretch()
        form.addRow("Цвет оверлея:", color_row)

        # Overlay strength
        self.overlay_strength_spin = QDoubleSpinBox()
        self.overlay_strength_spin.setRange(0.0, 1.0)
        self.overlay_strength_spin.setSingleStep(0.05)
        self.overlay_strength_spin.setValue(DEFAULT_OVERLAY_STRENGTH)
        self._limit_spin_width(self.overlay_strength_spin)
        form.addRow("Прозрачность оверлея:", self.overlay_strength_spin)

        # Batch size и workers
        perf_row = QWidget()
        perf_layout = QHBoxLayout(perf_row)
        perf_layout.setContentsMargins(0, 0, 0, 0)
        perf_layout.setSpacing(8)

        perf_layout.addWidget(QLabel("Batch size:"))
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 200)
        self.batch_size_spin.setValue(DEFAULT_BATCH_SIZE)
        self._limit_spin_width(self.batch_size_spin, 72)
        perf_layout.addWidget(self.batch_size_spin)

        perf_layout.addWidget(QLabel("Workers:"))
        self.num_workers_spin = QSpinBox()
        self.num_workers_spin.setRange(0, 16)
        self.num_workers_spin.setValue(DEFAULT_NUM_WORKERS)
        self._limit_spin_width(self.num_workers_spin, 72)
        perf_layout.addWidget(self.num_workers_spin)

        perf_layout.addWidget(QLabel("Save workers:"))
        self.save_workers_spin = QSpinBox()
        self.save_workers_spin.setRange(1, 16)
        self.save_workers_spin.setValue(DEFAULT_SAVE_WORKERS)
        self._limit_spin_width(self.save_workers_spin, 72)
        perf_layout.addWidget(self.save_workers_spin)

        perf_layout.addStretch()
        form.addRow("Производительность:", perf_row)

        layout.addWidget(params_group)

        # === Группа: Сохранение результатов ===
        save_group = QGroupBox("Сохранение результатов")
        save_layout = QVBoxLayout(save_group)

        self.save_masks_check = QCheckBox("Сохранять маски")
        self.save_masks_check.setChecked(DEFAULT_SAVE_MASKS)
        save_layout.addWidget(self.save_masks_check)

        self.save_concat_check = QCheckBox("Сохранять конкат (оригинал+маска+оверлей)")
        self.save_concat_check.setChecked(DEFAULT_SAVE_CONCAT)
        save_layout.addWidget(self.save_concat_check)

        self.save_overlay_check = QCheckBox("Сохранять оверлей")
        self.save_overlay_check.setChecked(DEFAULT_SAVE_OVERLAY)
        save_layout.addWidget(self.save_overlay_check)

        layout.addWidget(save_group)

        # === Кнопки управления ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.load_model_btn = QPushButton("Загрузить модель")
        self.load_model_btn.clicked.connect(self.load_model)
        buttons_layout.addWidget(self.load_model_btn)

        self.run_btn = QPushButton("▶  Запустить инференс")
        self.run_btn.setProperty("kind", "primary")
        self.run_btn.clicked.connect(self.run_inference)
        self.run_btn.setEnabled(False)  # Отключена пока модель не загружена
        buttons_layout.addWidget(self.run_btn)

        self.cancel_btn = QPushButton("✕  Отмена")
        self.cancel_btn.setProperty("kind", "danger")
        self.cancel_btn.clicked.connect(self.cancel_inference)
        self.cancel_btn.setEnabled(False)
        buttons_layout.addWidget(self.cancel_btn)

        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # === Прогресс-бар ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # === Лог ===
        log_group = QGroupBox("Лог")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(600)
        self.log_text.setFont(QFont("JetBrains Mono", 9))
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_group)

        # Добавляем растягивающий элемент внизу
        layout.addStretch()

        scroll.setWidget(panel)
        return scroll

    def _create_preview_panel(self) -> QWidget:
        """Создает панель предпросмотра."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Заголовок
        header = QLabel("Предпросмотр результатов")
        header.setProperty("role", "section")
        layout.addWidget(header)

        # Виджет галереи
        self.preview_widget = PreviewWidget()
        layout.addWidget(self.preview_widget)

        # Нижняя секция: чекбокс + обновление.
        # Сдвинута вправо, чтобы не налезать на границу соседнего блока.
        bottom = QWidget()
        bottom_layout = QVBoxLayout(bottom)
        bottom_layout.setContentsMargins(14, 0, 0, 0)
        bottom_layout.setSpacing(10)

        # Чекбокс включения предпросмотра
        self.enable_preview_check = QCheckBox("Включить предпросмотр")
        self.enable_preview_check.setChecked(True)
        bottom_layout.addWidget(self.enable_preview_check)

        # Кнопка обновления галереи
        refresh_row = QHBoxLayout()
        refresh_btn = QPushButton("↻  Обновить галерею")
        refresh_btn.setProperty("kind", "ghost")
        refresh_btn.clicked.connect(self.refresh_preview)
        refresh_row.addWidget(refresh_btn)
        refresh_row.addStretch()
        bottom_layout.addLayout(refresh_row)

        layout.addWidget(bottom)
        layout.addStretch()

        return panel

    def _load_settings(self):
        """Загружает сохраненные настройки."""
        config = load_config(CONFIG_FILE)

        if config:
            # Восстанавливаем пути
            self.model_path_edit.setText(config.get('model_path', ''))
            self.input_dir_edit.setText(config.get('input_dir', ''))
            self.output_dir_edit.setText(config.get('output_dir', ''))

            # Восстанавливаем параметры
            self.model_name_combo.setCurrentText(
                config.get('model_name', DEFAULT_MODEL_NAME)
            )
            self.augmentation_combo.setCurrentText(
                config.get('augmentation_fn', DEFAULT_AUGMENTATION)
            )
            self.threshold_spin.setValue(
                config.get('threshold', DEFAULT_THRESHOLD)
            )
            self.overlay_strength_spin.setValue(
                config.get('overlay_strength', DEFAULT_OVERLAY_STRENGTH)
            )
            self.batch_size_spin.setValue(
                config.get('batch_size', DEFAULT_BATCH_SIZE)
            )
            self.num_workers_spin.setValue(
                config.get('num_workers', DEFAULT_NUM_WORKERS)
            )
            self.save_workers_spin.setValue(
                config.get('save_workers', DEFAULT_SAVE_WORKERS)
            )

            # Восстанавливаем чекбоксы
            overlay_color = config.get('overlay_color', DEFAULT_OVERLAY_COLOR)
            self._set_overlay_color(tuple(overlay_color))

            self.save_masks_check.setChecked(
                config.get('save_masks', DEFAULT_SAVE_MASKS)
            )
            self.save_concat_check.setChecked(
                config.get('save_concat', DEFAULT_SAVE_CONCAT)
            )
            self.save_overlay_check.setChecked(
                config.get('save_overlay', DEFAULT_SAVE_OVERLAY)
            )

    def _save_settings(self):
        """Сохраняет текущие настройки."""
        config = {
            'model_path': self.model_path_edit.text(),
            'input_dir': self.input_dir_edit.text(),
            'output_dir': self.output_dir_edit.text(),
            'model_name': self.model_name_combo.currentText(),
            'augmentation_fn': self.augmentation_combo.currentText(),
            'threshold': self.threshold_spin.value(),
            'overlay_color': list(self.overlay_color),
            'overlay_strength': self.overlay_strength_spin.value(),
            'batch_size': self.batch_size_spin.value(),
            'num_workers': self.num_workers_spin.value(),
            'save_workers': self.save_workers_spin.value(),
            'save_masks': self.save_masks_check.isChecked(),
            'save_concat': self.save_concat_check.isChecked(),
            'save_overlay': self.save_overlay_check.isChecked(),
        }

        save_config(config, CONFIG_FILE)

    def log(self, message: str):
        """Добавляет сообщение в лог."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Прокручиваем вниз
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # === Методы для работы с файлами ===

    def browse_model(self):
        """Открывает диалог выбора файла модели."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл модели",
            "",
            "PyTorch Model (*.pth);;All Files (*)"
        )

        if file_path:
            self.model_path_edit.setText(file_path)

    def browse_input_folder(self):
        """Открывает диалог выбора входной папки."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку с изображениями"
        )

        if folder_path:
            self.input_dir_edit.setText(folder_path)

    def browse_output_folder(self):
        """Открывает диалог выбора выходной папки."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для результатов"
        )

        if folder_path:
            self.output_dir_edit.setText(folder_path)

    def choose_overlay_color(self):
        """Открывает диалог выбора цвета оверлея."""
        color = QColorDialog.getColor()

        if color.isValid():
            rgb = (color.red(), color.green(), color.blue())
            self._set_overlay_color(rgb)

    def _style_overlay_color_button(self):
        """Стилизовывает свотч цвета оверлея."""
        self.overlay_color_swatch.setStyleSheet(
            f"background-color: rgb{self.overlay_color}; "
            f"border: 2px solid #3A4155; border-radius: 8px;"
        )

    @staticmethod
    def _limit_spin_width(spin, width: int = 130):
        """Ограничивает ширину спинбокса, чтобы он не растягивался на всю строку."""
        spin.setMaximumWidth(width)

    def _set_overlay_color(self, rgb: tuple):
        """Устанавливает цвет оверлея."""
        self.overlay_color = rgb
        self._style_overlay_color_button()
        self.overlay_color_label.setText(f"RGB: {rgb}")

    # === Методы управления моделью ===

    def load_model(self):
        """Загружает модель (валидация)."""
        model_path = self.model_path_edit.text()

        # Валидация пути
        is_valid, message = validate_model_path(model_path)
        if not is_valid:
            QMessageBox.warning(self, "Ошибка", message)
            return

        # Проверяем наличие входной папки
        input_dir = self.input_dir_edit.text()
        is_valid, message, count = validate_image_folder(input_dir)
        if not is_valid:
            QMessageBox.warning(self, "Предупреждение", message)
            return

        self.log(f"Модель готова к загрузке: {Path(model_path).name}")
        self.log(f"Найдено изображений: {count}")

        # Активируем кнопку запуска
        self.run_btn.setEnabled(True)
        self.load_model_btn.setText("✓  Модель выбрана")
        self.load_model_btn.setEnabled(False)
        self.statusBar().showMessage("Модель готова к загрузке")

    # === Методы инференса ===

    def run_inference(self):
        """Запускает инференс в фоновом потоке."""
        # Собираем параметры
        model_path = self.model_path_edit.text()
        input_dir = self.input_dir_edit.text()
        output_dir = self.output_dir_edit.text() or "./predictions"

        # Валидация
        is_valid, msg = validate_output_folder(output_dir)
        if not is_valid:
            QMessageBox.critical(self, "Ошибка", msg)
            return

        # Подсчет батчей для прогресс-бара
        from utils.helpers import get_image_list
        images = get_image_list(input_dir)
        batch_size = self.batch_size_spin.value()
        total_batches = max(1, (len(images) + batch_size - 1) // batch_size)

        # Создаем worker
        self.worker = InferenceWorker(
            model_path=model_path,
            input_dir=input_dir,
            output_dir=output_dir,
            model_name=self.model_name_combo.currentText(),
            augmentation_fn_name=self.augmentation_combo.currentText(),
            threshold=self.threshold_spin.value(),
            overlay_color=self.overlay_color,
            overlay_strength=self.overlay_strength_spin.value(),
            save_masks=self.save_masks_check.isChecked(),
            save_concat=self.save_concat_check.isChecked(),
            save_overlay=self.save_overlay_check.isChecked(),
            batch_size=batch_size,
            num_workers=self.num_workers_spin.value(),
            save_workers=self.save_workers_spin.value()
        )

        # Подключаем сигналы
        self.worker.log_message.connect(self.log)
        self.worker.progress_updated.connect(self.update_progress)  # <--- Новый сигнал
        self.worker.finished_signal.connect(self.on_inference_finished)
        self.worker.cancelled_signal.connect(self.on_inference_cancelled)

        # Запускаем
        self.log("=" * 50)
        self.log("Запуск инференса...")
        self.log("=" * 50)

        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.statusBar().showMessage("Выполняется инференс…")

        # Настройка прогресс-бара
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.worker.start()

        # Сохраняем настройки
        self._save_settings()

    def update_progress(self, value: int):
        """Обновляет значение прогресс-бара."""
        self.progress_bar.setValue(value)

    def cancel_inference(self):
        """Отменяет текущий инференс."""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                "Вы уверены, что хотите отменить инференс?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.worker.cancel()
                self.log("Запрошена отмена операции...")

    def on_inference_finished(self, success: bool, message: str):
        """Обработчик завершения инференса."""
        self.progress_bar.setVisible(False)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

        if success:
            self.log(message)
            self.statusBar().showMessage("Инференс завершён")
            QMessageBox.information(self, "Успех", "Инференс завершен успешно!")

            # Обновляем предпросмотр если включен
            if self.enable_preview_check.isChecked():
                self.refresh_preview()
        else:
            self.log(f"Ошибка: {message}")
            self.statusBar().showMessage("Ошибка при инференсе")
            QMessageBox.critical(self, "Ошибка", message)

        self.worker = None

    def on_inference_cancelled(self):
        """Обработчик отмены инференса."""
        self.progress_bar.setVisible(False)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.log("Операция отменена пользователем")
        self.statusBar().showMessage("Операция отменена")
        self.worker = None

    def refresh_preview(self):
        """Обновляет галерею предпросмотра."""
        output_dir = self.output_dir_edit.text() or "./predictions"
        overlays_dir = os.path.join(output_dir, "overlays")

        if os.path.exists(overlays_dir):
            images = get_image_list(overlays_dir)
            if images:
                self.preview_widget.set_images(images)
                self.log(f"Загружено {len(images)} изображений для предпросмотра")
            else:
                self.log("В папке overlays нет изображений")
        else:
            self.log(f"Папка overlays не найдена: {overlays_dir}")

    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        # Останавливаем worker если работает
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()

        # Сохраняем настройки
        self._save_settings()

        event.accept()