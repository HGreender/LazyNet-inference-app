"""Константы и конфигурация приложения."""

# Поддерживаемые расширения изображений
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tif')

# Параметры по умолчанию для инференса
DEFAULT_THRESHOLD = 0.5
DEFAULT_OVERLAY_COLOR = (0, 255, 0)  # зеленый RGB
DEFAULT_OVERLAY_STRENGTH = 0.5
DEFAULT_SAVE_MASKS = True
DEFAULT_SAVE_CONCAT = False  # По умолчанию выключаем, оставляем только overlay
DEFAULT_SAVE_OVERLAY = True
DEFAULT_BATCH_SIZE = 50
DEFAULT_NUM_WORKERS = 2
DEFAULT_SAVE_WORKERS = 4

# Доступные модели в LazyNet
AVAILABLE_MODELS = [
    'efficientnetb4_unet',
    'efficientnetb4_unet_1ch',
    'efficientnetb4_unet++',
    'efficientnetb4_unet++_1ch',
]

# Модель по умолчанию
DEFAULT_MODEL_NAME = 'efficientnetb4_unet++_1ch'

# Доступные функции аугментации (fast_ml_tools.ml.augmentations)
AVAILABLE_AUGMENTATIONS = [
    'get_manga_panel_bubble_augmentation',
    'get_grayscale_imagenet_augmentation',
    'get_imagenet_encoder_augmentation',
    'get_lungs_imagenet_encoder_augmentation',
]

# Функция аугментации по умолчанию
DEFAULT_AUGMENTATION = 'get_manga_panel_bubble_augmentation'

# Путь к файлу конфигурации
CONFIG_FILE = "config.json"