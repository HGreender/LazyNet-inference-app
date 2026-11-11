"""Worker для фонового выполнения инференса."""
import os
import sys
import torch
import multiprocessing

# Исправление для Python 3.14+ и Windows
try:
    multiprocessing.set_start_method('spawn', force=True)
except RuntimeError:
    pass

from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

from fast_ml_tools import LazyNet
from fast_ml_tools.ml.augmentations import (
    get_manga_panel_bubble_augmentation,
    get_imagenet_encoder_augmentation,
)


def get_model_in_channels(model) -> int:
    """Определяет количество входных каналов модели (по первому конволюционному слою энкодера)."""
    if hasattr(model, 'encoder') and hasattr(model.encoder, '_conv_stem'):
        return model.encoder._conv_stem.in_channels
    for module in model.modules():
        if isinstance(module, torch.nn.Conv2d):
            return module.in_channels
    return 3


class InferenceWorker(QThread):
    """Фоновый поток для выполнения инференса модели."""

    # Сигналы для общения с UI
    progress_updated = pyqtSignal(int)  # Процент выполнения
    log_message = pyqtSignal(str)       # Сообщение лога
    preview_ready = pyqtSignal(str)     # Путь к изображению для предпросмотра
    finished_signal = pyqtSignal(bool, str)  # (успех, сообщение)
    cancelled_signal = pyqtSignal()     # Сигнал отмены

    def __init__(
        self,
        model_path: str,
        input_dir: str,
        output_dir: str,
        model_name: str = 'efficientnetb4_unet++_1ch',
        threshold: float = 0.5,
        overlay_color: tuple = (0, 255, 0),
        overlay_strength: float = 0.5,
        save_masks: bool = True,
        save_concat: bool = False,
        save_overlay: bool = True,
        batch_size: int = 50,
        num_workers: int = 2,
        save_workers: int = 4,
        parent=None
    ):
        super().__init__(parent)

        self.model_path = model_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.model_name = model_name
        self.threshold = threshold
        self.overlay_color = overlay_color
        self.overlay_strength = overlay_strength
        self.save_masks = save_masks
        self.save_concat = save_concat
        self.save_overlay = save_overlay
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.save_workers = save_workers

        self._is_cancelled = False
        self.lazynet = None

    def cancel(self):
        """Отменяет выполнение задачи."""
        self._is_cancelled = True
        self.log_message.emit("Запрошена отмена операции...")

    def run(self):
        """Основной метод выполнения в фоновом потоке."""
        try:
            self.log_message.emit(f"Инициализация модели: {self.model_name}")

            # Создаем экземпляр LazyNet
            self.lazynet = LazyNet(
                model_name=self.model_name,
                augmentation_fn=get_manga_panel_bubble_augmentation,
                device_id=0,
                verbose=False
            )

            # Логирование типа устройства
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0)
                self.log_message.emit(
                    f"Используемое устройство: CUDA (GPU) - {device_name} (Карт доступно: {device_count})")
            else:
                self.log_message.emit("Используемое устройство: CPU")

            # Загружаем веса
            self.log_message.emit(f"Загрузка весов из: {self.model_path}")
            self.lazynet.load_weights(self.model_path)
            self.log_message.emit("Модель успешно загружена")

            # Выбираем валидационный пайплайн под фактическое число входных каналов модели:
            # 1-канальная — grayscale, 3-канальная — RGB с нормализацией ImageNet
            in_channels = get_model_in_channels(self.lazynet.model)
            if in_channels == 1:
                self.lazynet.val_augmentation = get_manga_panel_bubble_augmentation(
                    phase='valid', size=(512, 512)
                )
                self.log_message.emit("Модель: 1 канал (grayscale) — пайплайн grayscale")
            else:
                self.lazynet.val_augmentation = get_imagenet_encoder_augmentation(
                    phase='valid', size=(512, 512)
                )
                self.log_message.emit(
                    f"Модель: {in_channels} канала(ов) (RGB) — пайплайн с нормализацией ImageNet"
                )

            # Проверяем отмену перед началом инференса
            if self._is_cancelled:
                self.cancelled_signal.emit()
                return

            # Запускаем инференс с возможностью отмены
            self._run_inference_with_cancel()

        except KeyboardInterrupt:
            self.log_message.emit("Операция прервана пользователем")
            self.cancelled_signal.emit()
        except Exception as e:
            if not self._is_cancelled:
                error_msg = f"Ошибка: {str(e)}"
                self.log_message.emit(error_msg)
                self.finished_signal.emit(False, error_msg)
            else:
                self.cancelled_signal.emit()

        finally:
            # Освобождаем ресурсы
            if self.lazynet is not None:
                del self.lazynet
                import gc
                gc.collect()

    def _run_inference_with_cancel(self):
        """Запускает инференс с проверкой флага отмены."""
        import torch
        import cv2
        import numpy as np
        from tqdm import tqdm
        from torch.utils.data import DataLoader
        from concurrent.futures import ThreadPoolExecutor
        from fast_ml_tools.ml.datasets import InferenceDataset
        from fast_ml_tools.visualization import create_overlay_cv2

        self.lazynet.model.eval()

        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tif')
        all_files = [
            os.path.join(self.input_dir, f)
            for f in os.listdir(self.input_dir)
            if f.lower().endswith(valid_extensions)
        ]
        all_files.sort()

        if not all_files:
            self.log_message.emit(f"В папке {self.input_dir} не найдено изображений.")
            self.finished_signal.emit(True, "Готово!")
            return

        # ... (код создания папок masks_dir, concat_dir, overlays_dir) ...
        masks_dir = os.path.join(self.output_dir, 'masks') if self.save_masks else None
        concat_dir = os.path.join(self.output_dir, 'concat') if self.save_concat else None
        overlays_dir = os.path.join(self.output_dir, 'overlays') if self.save_overlay else None

        if masks_dir: os.makedirs(masks_dir, exist_ok=True)
        if concat_dir: os.makedirs(concat_dir, exist_ok=True)
        if overlays_dir: os.makedirs(overlays_dir, exist_ok=True)

        def identity_collate(my_batch):
            return my_batch

        inf_dataset = InferenceDataset(all_files)
        inf_loader = DataLoader(
            inf_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=0,
            pin_memory=False,
            collate_fn=identity_collate
        )

        total_batches = len(inf_loader)
        self.log_message.emit(f"Начало обработки: {len(all_files)} изображений в {total_batches} батчах...")

        executor = ThreadPoolExecutor(max_workers=self.save_workers)
        futures = []

        with torch.no_grad():
            for batch_idx, batch in enumerate(inf_loader):
                # Проверяем отмену между батчами
                if self._is_cancelled:
                    self.log_message.emit("Отмена операции...")
                    executor.shutdown(wait=False, cancel_futures=True)
                    self.cancelled_signal.emit()
                    return

                processed_tensors = []
                batch_metadata = []

                for item in batch:
                    if not item['valid']:
                        continue
                    augmented = self.lazynet.val_augmentation(image=item['image_rgb'])
                    processed_tensors.append(augmented['image'])
                    batch_metadata.append(item)

                if not processed_tensors:
                    continue

                input_batch = torch.stack(processed_tensors).to(self.lazynet.device, non_blocking=True)
                outputs = self.lazynet.model(input_batch)

                if outputs.shape[1] == 1:
                    probs = torch.sigmoid(outputs).squeeze(1)
                else:
                    probs = torch.softmax(outputs, dim=1)[:, 0, :, :]

                probs_cpu = probs.cpu().numpy()

                for i in range(len(batch_metadata)):
                    item = batch_metadata[i]
                    prob_map_np = probs_cpu[i]
                    orig_w, orig_h = item['original_size']
                    name, ext = os.path.splitext(item['filename'])

                    def _save_task(pmap, ow, oh, n, e, img_rgb):
                        # ... (код сохранения тот же, что и в предыдущем ответе) ...
                        resized = cv2.resize(pmap, (ow, oh), interpolation=cv2.INTER_LINEAR)
                        binary = (resized >= self.threshold).astype(np.uint8)

                        if self.save_masks and masks_dir:
                            cv2.imwrite(os.path.join(masks_dir, f"{n}_mask.png"), binary * 255)

                        overlay_img = None
                        if (self.save_overlay and overlays_dir) or (self.save_concat and concat_dir):
                            try:
                                overlay_img = create_overlay_cv2(
                                    img_rgb, binary, color=self.overlay_color, alpha=self.overlay_strength
                                )
                                h, w = img_rgb.shape[:2]
                                if overlay_img.shape[:2] != (h, w):
                                    overlay_img = cv2.resize(overlay_img, (w, h))
                            except Exception as ex:
                                print(f"Ошибка создания оверлея {n}: {ex}")

                        if self.save_overlay and overlays_dir and overlay_img is not None:
                            try:
                                save_path = os.path.join(overlays_dir, f"{n}_overlay{ext}")
                                cv2.imwrite(save_path, cv2.cvtColor(overlay_img, cv2.COLOR_RGB2BGR))
                            except Exception as ex:
                                print(f"Ошибка сохранения оверлея {n}: {ex}")

                        if self.save_concat and concat_dir and overlay_img is not None:
                            try:
                                mask_viz = np.stack([binary * 255] * 3, axis=-1)
                                h, w = img_rgb.shape[:2]
                                if mask_viz.shape[:2] != (h, w):
                                    mask_viz = cv2.resize(mask_viz, (w, h))
                                concat_result = np.hstack([img_rgb, mask_viz, overlay_img])
                                save_path = os.path.join(concat_dir, f"{n}_viz{ext}")
                                cv2.imwrite(save_path, cv2.cvtColor(concat_result, cv2.COLOR_RGB2BGR))
                            except Exception as ex:
                                print(f"Ошибка сохранения конката {n}: {ex}")

                    future = executor.submit(_save_task, prob_map_np, orig_w, orig_h, name, ext, item['image_rgb'])
                    futures.append(future)

                # Обновляем прогресс по батчам
                current_batch = batch_idx + 1
                progress = int((current_batch / total_batches) * 100)
                self.progress_updated.emit(progress)

                del input_batch, outputs, probs, probs_cpu, processed_tensors
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

        # Ожидаем завершения записи
        for f in futures:
            if self._is_cancelled:
                break
            f.result()

        executor.shutdown(wait=True)

        if not self._is_cancelled:
            import gc
            gc.collect()
            self.log_message.emit(f"Готово! Результаты в {self.output_dir}")
            self.finished_signal.emit(True, "Готово!")