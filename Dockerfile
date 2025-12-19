# Stage 1: Сборка статики
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Собираем статику в папку /app/staticfiles
RUN python manage.py collectstatic --noinput

# Stage 2: Финальный образ
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем зависимости и Gunicorn ПРЯМО ЗДЕСЬ
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем само приложение
COPY . .

# Копируем статику из первого этапа (убедитесь, что пути совпадают)
# В Stage 1 Django соберет их туда, где указано в STATIC_ROOT
COPY --from=builder /app/staticfiles /app/staticfiles

EXPOSE 8000

CMD ["gunicorn", "login.wsgi:application", "--bind", "0.0.0.0:8000"]
