"""Вспомогательные функции для приложения."""
import os
from pathlib import Path
from typing import Tuple, List


def validate_model_path(path: str) -> Tuple[bool, str]:
    """Проверяет существование файла модели."""
    if not path:
        return False, "Путь к модели не указан"

    path_obj = Path(path)
    if not path_obj.exists():
        return False, f"Файл модели не найден: {path}"

    if not path_obj.is_file():
        return False, f"Указанный путь не является файлом: {path}"

    if path_obj.suffix.lower() != '.pth':
        return False, f"Ожидался файл .pth, получен: {path_obj.suffix}"

    return True, "OK"


def validate_image_folder(path: str) -> Tuple[bool, str, int]:
    """Проверяет папку с изображениями и подсчитывает их количество."""
    if not path:
        return False, "Папка с изображениями не указана", 0

    path_obj = Path(path)
    if not path_obj.exists():
        return False, f"Папка не найдена: {path}", 0

    if not path_obj.is_dir():
        return False, f"Указанный путь не является папкой: {path}", 0

    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.webp')
    images = [
        f for f in os.listdir(path)
        if f.lower().endswith(valid_extensions)
    ]

    if not images:
        return False, f"В папке не найдено изображений ({', '.join(valid_extensions)})", 0

    return True, f"Найдено {len(images)} изображений", len(images)


def validate_output_folder(path: str) -> Tuple[bool, str]:
    """Проверяет или создает выходную папку."""
    if not path:
        return False, "Выходная папка не указана"

    try:
        os.makedirs(path, exist_ok=True)
        return True, "OK"
    except Exception as e:
        return False, f"Ошибка создания папки: {str(e)}"


def get_image_list(folder: str) -> List[str]:
    """Получает список путей к изображениям в папке."""
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.webp')
    images = []

    for f in sorted(os.listdir(folder)):
        if f.lower().endswith(valid_extensions):
            images.append(os.path.join(folder, f))

    return images


def format_size(size_bytes: int) -> str:
    """Форматирует размер файла в читаемый вид."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def load_config(config_path: str = "config.json") -> dict:
    """Загружает конфигурацию из JSON файла."""
    import json
    from pathlib import Path

    config_file = Path(config_path)
    if not config_file.exists():
        return {}

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config: dict, config_path: str = "config.json") -> bool:
    """Сохраняет конфигурацию в JSON файл."""
    import json
    from pathlib import Path

    try:
        with open(Path(config_path), 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False