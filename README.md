# TelecomBackend - REST API для управления оборудованием

## Описание

Полнофункциональное веб-приложение для управления оборудованием телекоммуникационной компании. Состоит из:
- **Backend**: REST API на Django с Django REST Framework
- **Frontend**: SPA приложение на Vue.js 3

## Функциональность

### Backend (Django REST API):
- CRUD операции с оборудованием
- Управление типами оборудования  
- Валидация серийных номеров по маскам
- Мягкое удаление записей
- Поиск и фильтрация
- Пагинация результатов
- JWT аутентификация
- Административная панель

### Frontend (Vue.js SPA):
- Авторизация пользователей
- Просмотр списка оборудования с поиском
- Добавление нового оборудования (одного или массива)
- Редактирование и удаление оборудования
- Просмотр типов оборудования
- Адаптивный дизайн
- Валидация данных на клиенте

### API Endpoints

#### Оборудование:
- `GET /api/equipment/` - Список оборудования с поиском и пагинацией
- `POST /api/equipment/` - Создание оборудования (одного или массива)
- `GET /api/equipment/{id}/` - Получение оборудования по ID
- `PUT /api/equipment/{id}/` - Редактирование оборудования
- `DELETE /api/equipment/{id}/` - Мягкое удаление оборудования

#### Типы оборудования:
- `GET /api/equipment/type/` - Список типов оборудования с поиском и пагинацией

#### Аутентификация:
- `POST /api/user/login/` - Авторизация и получение JWT токена

#### Дополнительные:
- `GET /api/equipment/stats/` - Статистика по оборудованию
- `POST /api/equipment/{id}/restore/` - Восстановление удаленного оборудования

## Требования

- Python 3.8+
- Django 4.2+
- SQLite (для демо) / MySQL (для продакшена)
- Современный браузер для фронтенда

## Установка и запуск

### 1. Клонирование и установка зависимостей

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd TelecomBackend

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка базы данных

Для демонстрации используется SQLite. Для продакшена настройте MySQL:

```python
# В telecom_backend/settings.py раскомментируйте:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'telecom_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 3. Применение миграций

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate
```

### 4. Создание тестовых данных

```bash
# Создание тестовых данных
python manage.py create_test_data

# Или с очисткой существующих данных
python manage.py create_test_data --clear
```

### 5. Запуск backend сервера

```bash
python manage.py runserver
```

Backend будет доступен по адресу: http://localhost:8000

### 6. Запуск frontend

```bash
# Перейдите в папку frontend
cd frontend

# Откройте index.html в браузере
# Или запустите простой HTTP сервер:
python -m http.server 3000
```

Frontend будет доступен по адресу: http://localhost:3000

## Использование

### Тестовые учетные данные:
- **Обычный пользователь**: `testuser` / `test123`
- **Администратор**: `admin` / `admin123`

### Административная панель:
Доступна по адресу: http://localhost:8000/admin/

### Работа с приложением:

1. **Авторизация**: Войдите в систему через фронтенд
2. **Просмотр оборудования**: Список с поиском и фильтрацией
3. **Добавление**: Выберите тип и введите серийные номера
4. **Редактирование**: Нажмите "Редактировать" на карточке
5. **Удаление**: Мягкое удаление с возможностью восстановления

## Модели данных

### EquipmentType (Тип оборудования)
- `id` - Первичный ключ
- `name` - Наименование типа
- `serial_mask` - Маска серийного номера
- `created_at` - Дата создания
- `updated_at` - Дата обновления

### Equipment (Оборудование)
- `id` - Первичный ключ
- `equipment_type` - Ссылка на тип оборудования
- `serial_number` - Серийный номер (уникален в рамках типа)
- `note` - Примечание
- `created_at` - Дата создания
- `updated_at` - Дата обновления
- `deleted_at` - Дата мягкого удаления

## Валидация серийных номеров

Система поддерживает валидацию серийных номеров по маскам:

- `N` – цифра от 0 до 9
- `A` – прописная буква латинского алфавита
- `a` – строчная буква латинского алфавита  
- `X` – прописная буква латинского алфавита либо цифра от 0 до 9
- `Z` – символ из списка: "-", "_", "@"

### Примеры масок и валидных серийных номеров:

**TP-Link TL-WR74** (маска: `XXAAAAAXAA`):
- `12ABCDEF34` ❌ (не соответствует маске)
- `A1BCDEFG2H` ✅

**D-Link DIR-300** (маска: `NXXAAXZXaa`):
- `123AB4_DEf` ❌ (не соответствует маске)
- `1A2BC3@def` ✅

**D-Link DIR-300 E** (маска: `NAAAAXZXXX`):
- `1ABCD2@ABC` ✅
- `5EFGH9_XYZ` ✅
- `7IJKL3-MNO` ✅

## Примеры API запросов

### Аутентификация:
```bash
curl -X POST http://localhost:8000/api/user/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123"
  }'
```

### Получение списка оборудования:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/api/equipment/?search=ABC&equipment_type=1&page=1"
```

### Создание оборудования:
```bash
curl -X POST http://localhost:8000/api/equipment/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_type": 3,
    "serial_numbers": ["1ABCD2@ABC", "5EFGH9_XYZ"],
    "note": "Новое оборудование"
  }'
```

### Получение типов оборудования:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/api/equipment/type/?search=D-Link"
```

## Структура проекта

```
TelecomBackend/
├── equipment/              # Приложение для управления оборудованием
│   ├── models.py          # Модели данных
│   ├── serializers.py     # Сериализаторы для API
│   ├── views.py           # Представления API
│   ├── filters.py         # Фильтры для поиска
│   ├── urls.py            # URL маршруты
│   ├── admin.py           # Настройки админ панели
│   └── management/        # Команды управления
│       └── commands/
│           └── create_test_data.py
├── authentication/        # Приложение для аутентификации
│   ├── views.py           # JWT аутентификация
│   ├── serializers.py     # Сериализаторы для auth
│   └── urls.py            # URL для auth
├── telecom_backend/       # Основные настройки проекта
│   ├── settings.py        # Настройки Django
│   └── urls.py            # Основные URL маршруты
├── frontend/              # SPA приложение на Vue.js
│   ├── index.html         # Главная HTML страница
│   ├── app.js            # Основная логика Vue.js
│   └── README.md         # Документация фронтенда
├── requirements.txt       # Зависимости Python
├── manage.py             # Django management script
└── README.md             # Основная документация
```

## Технологии

### Backend:
- **Django 4.2** - веб-фреймворк
- **Django REST Framework** - для создания API
- **Django REST Framework SimpleJWT** - JWT аутентификация
- **django-cors-headers** - CORS поддержка
- **django-filter** - фильтрация данных
- **python-dotenv** - переменные окружения

### Frontend:
- **Vue.js 3** - JavaScript фреймворк
- **Bootstrap 5** - CSS фреймворк
- **Bootstrap Icons** - иконки
- **Axios** - HTTP клиент

### База данных:
- **SQLite** - для демонстрации
- **MySQL** - рекомендуется для продакшена

## Безопасность

- JWT токены для аутентификации
- CORS настройки для фронтенда
- Валидация входных данных
- Защита от SQL инъекций через ORM
- Настройки CSRF защиты
- Мягкое удаление данных

## Производительность

- Использование select_related и prefetch_related для оптимизации запросов
- Индексы на часто используемых полях
- Пагинация для больших наборов данных
- Debounce для поиска на фронтенде
- Кэширование (готово к настройке с Redis)

## Тестирование

### Backend:
```bash
# Запуск тестов Django
python manage.py test

# Проверка покрытия
coverage run --source='.' manage.py test
coverage report
```

### Frontend:
- Ручное тестирование в браузере
- Проверка адаптивности
- Тестирование API интеграции

## Развертывание

### Для продакшена:
1. Настройте MySQL базу данных
2. Установите переменные окружения
3. Соберите статические файлы: `python manage.py collectstatic`
4. Настройте веб-сервер (nginx + gunicorn)
5. Настройте SSL сертификаты
6. Настройте мониторинг и логирование

### Docker (опционально):
```dockerfile
# Можно добавить Dockerfile для контейнеризации
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Поддержка

При возникновении вопросов или проблем:
1. Проверьте логи Django
2. Убедитесь в корректности настроек базы данных
3. Проверьте наличие всех зависимостей
4. Убедитесь, что CORS настроен правильно для фронтенда

## Возможные улучшения

1. **Тестирование**: Добавить unit и integration тесты
2. **Документация API**: Swagger/OpenAPI документация
3. **Кэширование**: Redis для кэширования запросов
4. **Логирование**: Структурированное логирование
5. **Мониторинг**: Интеграция с системами мониторинга
6. **CI/CD**: Автоматизация развертывания
7. **Backup**: Автоматическое резервное копирование
8. **Масштабирование**: Поддержка кластера

## Лицензия

Проект создан для демонстрации навыков разработки полнофункционального веб-приложения с использованием Django и Vue.js. 