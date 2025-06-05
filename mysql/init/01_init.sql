-- Инициализация базы данных для TelecomBackend

-- Создание базы данных (если не существует)
CREATE DATABASE IF NOT EXISTS telecom_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Использование созданной базы данных
USE telecom_db;

-- Создание пользователя для приложения (если не существует)
CREATE USER IF NOT EXISTS 'telecom_user'@'%' IDENTIFIED BY 'telecom_password123';

-- Предоставление прав доступа
GRANT ALL PRIVILEGES ON telecom_db.* TO 'telecom_user'@'%';

-- Дополнительные права для работы с Django
GRANT CREATE, ALTER, DROP, INDEX, REFERENCES ON telecom_db.* TO 'telecom_user'@'%';

-- Обновление привилегий
FLUSH PRIVILEGES;

-- Установка часового пояса по умолчанию
SET time_zone = '+00:00';

-- Включение event_scheduler (если нужен для задач)
-- SET GLOBAL event_scheduler = ON;

-- Проверочный запрос
SELECT 'Database telecom_db initialized successfully!' as message; 