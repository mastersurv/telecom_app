FROM nginx:alpine

LABEL maintainer="TelecomBackend Team"
LABEL description="Frontend for Equipment Management System"

# Установка дополнительных пакетов
RUN apk add --no-cache curl

# Копирование статических файлов
COPY . /usr/share/nginx/html/

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Создание пользователя для nginx
RUN addgroup -g 1001 -S nginx-app && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx-app -g nginx-app nginx-app

# Изменение прав доступа
RUN chown -R nginx-app:nginx-app /usr/share/nginx/html && \
    chown -R nginx-app:nginx-app /var/cache/nginx && \
    chown -R nginx-app:nginx-app /var/log/nginx && \
    chown -R nginx-app:nginx-app /etc/nginx/conf.d

# Создание директории для pid файла
RUN mkdir -p /var/run/nginx && \
    chown -R nginx-app:nginx-app /var/run/nginx

# Переключение на пользователя приложения
USER nginx-app

# Открытие порта
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Команда запуска
CMD ["nginx", "-g", "daemon off;"] 