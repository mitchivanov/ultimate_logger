# Многоступенчатая сборка для минимизации размера образа
FROM python:3.11-slim AS builder

# Установка зависимостей сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Финальный образ
FROM python:3.11-slim

# Настройка окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH"

# Копирование виртуального окружения
COPY --from=builder /opt/venv /opt/venv

# Рабочая директория
WORKDIR /app

# Копируем ВСЮ структуру проекта
COPY . /app

# Меняем рабочую директорию на родительскую
WORKDIR /app/services/fastapi

# Порт приложения
EXPOSE 8000

# Запуск приложения с правильным путем
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--no-access-log"] 