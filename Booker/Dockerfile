FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код (ВАЖНО: копируем все папки и файлы)
COPY agents/ ./agents/
COPY skills/ ./skills/
COPY observability/ ./observability/

# Проверяем, что файлы скопировались (для отладки)
RUN ls -la ./skills/ && ls -la ./agents/

# Открываем порт
EXPOSE 8000

# Запускаем
CMD ["python", "-m", "agents.booker_api"]