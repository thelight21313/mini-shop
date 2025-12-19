# Stage 1: Сборка статики
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput

# Stage 2: Финальный образ
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка Gunicorn и других зависимостей
RUN pip install gunicorn

# Копируем собранные статические файлы
COPY --from=builder /app/static /app/static

# Копируем остальное приложение
COPY . .

# Установка Gunicorn (или других WSGI серверов)
# Предполагается, что у вас есть файл wsgi.py в корне проекта
CMD ["gunicorn", "your_project.wsgi:application", "--bind", "0.0.0.0:8000"]

# Если используете отдельный порт для Gunicorn, например, 8000
EXPOSE 8000