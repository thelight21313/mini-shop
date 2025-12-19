# Stage 1: Сборка статики
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput

RUN pip install gunicorn

COPY --from=builder /app/static /app/static

COPY . .

CMD ["gunicorn", "your_project.wsgi:application", "--bind", "0.0.0.0:8000"]

EXPOSE 8000