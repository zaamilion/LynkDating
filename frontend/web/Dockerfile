# Используем базовый образ Nginx
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Копируем статические файлы в контейнер
COPY . /usr/share/nginx/html

# Указываем порт, который будет использовать Nginx
EXPOSE 80