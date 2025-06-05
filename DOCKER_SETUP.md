# Docker Setup для TelecomBackend

## Описание

Данная конфигурация Docker Compose включает в себя:
- **MySQL 8.0** - основная база данных
- **phpMyAdmin** - веб-интерфейс для управления базой данных
- **Redis** - для кэширования (опционально)

## Требования

- Docker Desktop или Docker Engine + Docker Compose
- Минимум 2GB свободной оперативной памяти
- Свободное место на диске: ~1GB

## Быстрый старт

### 1. Подготовка файла с переменными окружения

```bash
# Скопируйте пример файла окружения
cp env.example .env

# Отредактируйте .env файл при необходимости
```

### 2. Запуск контейнеров

```bash
# Запуск всех сервисов
docker-compose up -d

# Или запуск только MySQL
docker-compose up -d mysql

# Просмотр логов
docker-compose logs -f mysql
```

### 3. Настройка Django для работы с MySQL

```bash
# Установите переменную окружения для использования MySQL
export USE_MYSQL=true

# Или добавьте в .env файл:
echo "USE_MYSQL=true" >> .env
```

### 4. Применение миграций Django

```bash
# Установите MySQL драйвер
pip install mysqlclient

# Выполните миграции
python manage.py migrate

# Создайте суперпользователя
python manage.py createsuperuser

# Загрузите тестовые данные
python manage.py create_test_data
```

## Сервисы и порты

| Сервис | Порт | Описание | URL |
|--------|------|----------|-----|
| MySQL | 3306 | База данных | localhost:3306 |
| phpMyAdmin | 8080 | Веб-интерфейс БД | http://localhost:8080 |
| Redis | 6379 | Кэширование | localhost:6379 |

## Подключение к базе данных

### Из Django приложения
Настройки автоматически считываются из переменных окружения при установке `USE_MYSQL=true`.

### Из внешних приложений
```
Хост: localhost
Порт: 3306
База данных: telecom_db
Пользователь: telecom_user
Пароль: telecom_password123
```

### Через phpMyAdmin
1. Откройте http://localhost:8080
2. Логин: `telecom_user`
3. Пароль: `telecom_password123`

## Переменные окружения

### Основные переменные (.env файл):

```env
# Database Configuration
MYSQL_ROOT_PASSWORD=rootpassword123
MYSQL_DATABASE=telecom_db
MYSQL_USER=telecom_user
MYSQL_PASSWORD=telecom_password123

# Django Configuration
USE_MYSQL=true
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Дополнительные переменные:

```env
# Хост MySQL (для Docker обычно mysql)
MYSQL_HOST=localhost

# Порт MySQL
MYSQL_PORT=3306

# Redis настройки
REDIS_URL=redis://localhost:6379/0
```

## Команды Docker Compose

### Управление контейнерами

```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Перезапуск сервисов
docker-compose restart

# Просмотр статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f [service_name]
```

### Работа с данными

```bash
# Резервное копирование базы данных
docker-compose exec mysql mysqldump -u telecom_user -p telecom_db > backup.sql

# Восстановление из резервной копии
docker-compose exec -T mysql mysql -u telecom_user -p telecom_db < backup.sql

# Подключение к MySQL через командную строку
docker-compose exec mysql mysql -u telecom_user -p telecom_db
```

### Очистка

```bash
# Остановка и удаление контейнеров
docker-compose down

# Удаление контейнеров и volumes (ВНИМАНИЕ: удалит все данные!)
docker-compose down -v

# Удаление images
docker-compose down --rmi all
```

## Конфигурационные файлы

### MySQL конфигурация
- `mysql/conf.d/mysql.cnf` - основная конфигурация MySQL
- `mysql/init/01_init.sql` - SQL скрипт инициализации

### Docker Compose
- `docker-compose.yml` - основная конфигурация контейнеров
- `.env` - переменные окружения

## Мониторинг и отладка

### Проверка работоспособности

```bash
# Проверка подключения к MySQL
docker-compose exec mysql mysql -u telecom_user -p -e "SELECT 1"

# Проверка статуса контейнеров
docker-compose ps

# Просмотр использования ресурсов
docker stats
```

### Логи

```bash
# Все логи
docker-compose logs

# Логи конкретного сервиса
docker-compose logs mysql
docker-compose logs phpmyadmin

# Логи в реальном времени
docker-compose logs -f mysql
```

## Производственная среда

### Рекомендации для продакшена:

1. **Безопасность**:
   ```env
   # Используйте сложные пароли
   MYSQL_ROOT_PASSWORD=very_complex_password_here
   MYSQL_PASSWORD=another_complex_password
   
   # Ограничьте доступ
   MYSQL_HOST=mysql  # только внутри Docker сети
   ```

2. **Производительность**:
   - Увеличьте `innodb_buffer_pool_size` в `mysql.cnf`
   - Настройте логирование
   - Используйте SSD диски для volumes

3. **Backup**:
   ```bash
   # Автоматическое резервное копирование
   docker-compose exec mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD --all-databases > backup_$(date +%Y%m%d).sql
   ```

## Решение проблем

### Частые проблемы

1. **Порт 3306 занят**:
   ```bash
   # Измените порт в docker-compose.yml
   ports:
     - "3307:3306"  # вместо 3306:3306
   ```

2. **Ошибки подключения Django к MySQL**:
   ```bash
   # Проверьте переменные окружения
   echo $USE_MYSQL
   
   # Установите драйвер MySQL
   pip install mysqlclient
   ```

3. **Проблемы с правами**:
   ```bash
   # Пересоздайте пользователя MySQL
   docker-compose exec mysql mysql -u root -p
   DROP USER 'telecom_user'@'%';
   CREATE USER 'telecom_user'@'%' IDENTIFIED BY 'new_password';
   GRANT ALL PRIVILEGES ON telecom_db.* TO 'telecom_user'@'%';
   FLUSH PRIVILEGES;
   ```

### Полная переустановка

```bash
# Остановите и удалите все
docker-compose down -v --rmi all

# Удалите volumes
docker volume prune

# Запустите заново
docker-compose up -d
```

## Альтернативные драйверы

Если возникают проблемы с `mysqlclient`, можно использовать `PyMySQL`:

```bash
# Установите PyMySQL
pip install PyMySQL

# Добавьте в settings.py (уже настроено)
import pymysql
pymysql.install_as_MySQLdb()
```

---

**Примечание**: Данная конфигурация оптимизирована для разработки. Для продакшена рекомендуется дополнительная настройка безопасности и производительности. 