FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей, необходимых для spaCy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код агента и api
COPY . /app/agents/character_analyzer/

# Устанавливаем переменную окружения, чтобы Python видел пакеты в /app
ENV PYTHONPATH=/app

# Порт, на котором будет работать FastAPI
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "agents.character_analyzer.api:app", "--host", "0.0.0.0", "--port", "8000"]