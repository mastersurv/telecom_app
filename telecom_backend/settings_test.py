"""
Django test settings for telecom_backend project.
Оптимизированы для быстрого выполнения тестов.
"""

from .settings import *
import tempfile
from datetime import timedelta

# Отключаем DEBUG в тестах
DEBUG = False

# Используем SQLite в памяти для быстрых тестов
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Отключаем миграции для ускорения тестов
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Упрощаем хеширование паролей
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Отключаем кэширование
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Временная директория для медиа файлов
MEDIA_ROOT = tempfile.mkdtemp()

# Отключаем логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# JWT настройки для тестов
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,  # Отключаем для тестов
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'test-secret-key-for-jwt',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Отключаем CORS проверки в тестах
CORS_ALLOW_ALL_ORIGINS = True

# Email backend для тестов
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Ускоряем тесты
USE_TZ = False

# Настройки для покрытия
COVERAGE_PROCESS_START = True 