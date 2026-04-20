FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей для spaCy и сборщиков
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЁ содержимое проекта в /app/character_analyzer
COPY . /app/character_analyzer/

# Убеждаемся, что папка является Python-пакетом
RUN touch /app/character_analyzer/__init__.py

# Добавляем /app в PYTHONPATH, чтобы Python нашёл пакет character_analyzer
ENV PYTHONPATH=/app

# Открываем порт FastAPI
EXPOSE 8000

# Запускаем Uvicorn, указывая на модуль character_analyzer.api:app
# (предполагается, что в api.py есть объект app = FastAPI())
CMD ["uvicorn", "character_analyzer.api:app", "--host", "0.0.0.0", "--port", "8000"]