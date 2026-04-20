# LitAgent — Мультиагентная система литературного анализа

Распределённая система для автоматического анализа литературных произведений: загрузка книг, извлечение персонажей, суммаризация, генерация вопросов и формирование отчёта. Реализована на FastAPI, spaCy, LLM (Qwen/Llama), Redis, Docker, с полным стеком наблюдаемости.

## Обзор

LitAgent принимает название книги и автора, загружает полный текст из открытых источников (Gutenberg, Wikisource и др.), после чего выполняет:

- Распознавание персонажей (NER) + извлечение роли, архетипа, черт с помощью LLM
- Многоуровневую суммаризацию (сверхкраткую, краткую, подробную)
- Генерацию вопросов (easy/medium/hard) с вариантами ответов и цитатой-подтверждением
- Построение графа связей между персонажами
- Итоговый отчёт в форматах JSON и Markdown

Все агенты работают в изолированных Docker-контейнерах, взаимодействуют через REST, используют Redis для кеширования и экспортируют метрики/логи/трассировки.

## Агенты

| Агент | Порт | Описание |
|-------|------|----------|
| Booker | 8000 | Загружает полный текст из Gutenberg/Wikisource/GoogleBooks/LitRes; кеширует в Redis. |
| Summarizer | 8001 | Генерирует сверхкраткое, краткое и подробное содержание + ключевые цитаты + аннотации глав. |
| QuestionGenerator | 8002 | Создаёт 10 вопросов (на книгу) с 4 вариантами, уровнем сложности и цитатой-доказательством. |
| CharacterAnalyzer | 8004 | Извлекает персонажей (spaCy), обогащает через LLM (роль, архетип, черты), строит граф связей. |
| Оркестратор | 8003 | Координирует весь пайплайн (эндпоинт `POST /analyze`). |
| Reporter | (внутренний) | Агрегирует данные в финальный JSON/Markdown отчёт. |

## Технологический стек

- **Python 3.11** + **FastAPI** – асинхронные REST API
- **spaCy** (`en_core_web_lg`) – NER для персонажей
- **LLM** – Qwen
- **Redis** – кеш загруженных книг (TTL 30 дней)
- **Docker** + **Docker Compose** – оркестрация контейнеров
- **Prometheus** – сбор метрик
- **Loki + Promtail** – агрегация логов
- **Jaeger** – распределённая трассировка
- **Grafana** – дашборды
- **cAdvisor** – мониторинг ресурсов контейнеров

## Требования

- Docker Engine ≥ 20.10
- Docker Compose ≥ 2.0
- (Опционально) GPU для локального инференса LLM
- Минимум 4 ГБ ОЗУ (рекомендуется 8 ГБ)

## Установка и запуск

1. **Клонировать репозиторий**
   ```bash
   git clone https://github.com/AleksandrErmolaev/LitAgent.git
   cd LitAgent
   ```
   
2. **Собрать и запустить все сервисы**
   ```bash
   docker-compose up --build
   ```
   Запустятся: Redis, Booker, Summarizer, QuestionGenerator, CharacterAnalyzer, Reporter, Оркестратор.
   (Опционально) Prometheus, Loki, Grafana, Jaeger, cAdvisor – из `observability/docker-compose.yml`.

3. **Проверить работоспособность**
   ```bash
   curl http://localhost:8003/health   # оркестратор
   curl http://localhost:8000/health   # booker
   ```

## Использование API

### 1. Полный анализ (через Оркестратор)

```bash
curl -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{"title":"Crime and punishment","author":"Dostoevsky","language":"en"}'
```

Ответ содержит `metadata`, `summary`, `questions`, `characters`.

### 2. Прямые вызовы агентов

#### Booker – получить полный текст
```bash
curl -X POST http://localhost:8000/fetch_full \
  -d '{"title":"War and Peace","author":"Tolstoy","language":"en"}'
```

#### Summarizer
```bash
curl -X POST http://localhost:8001/summarize \
  -d '{"text":"...","chapters":["..."]}'
```

#### Character Analyzer
```bash
curl -X POST http://localhost:8004/analyze \
  -d '{"full_text":"..."}'
```

#### Question Generator
```bash
curl -X POST http://localhost:8002/generate \
  -d '{"text":"...","chapters":["..."],"characters":[...]}'
```

### 3. Сброс кеша (Booker)
```bash
curl -X DELETE "http://localhost:8000/cache/{title}/{author}"
```

## Структура проекта

```
LitAgent/
├── Booker/                    # Агент загрузки книг
│   ├── agents/                # booker.py, booker_api.py
│   ├── skills/                # gutenberg.py, wikisource.py, cache.py, text_cleaner.py
│   ├── observability/         # metrics.py, logging_config.py
│   ├── evals/                 # test_booker.py, test_russian.py
│   ├── Dockerfile
│   └── requirements.txt
├── Summarizer/                # Агент суммаризации
│   ├── main.py
│   ├── test.py
│   └── Dockerfile
├── QuestionGenerator/         # Агент генерации вопросов
│   ├── main.py
│   └── Dockerfile
├── character_analyzer/        # Агент анализа персонажей
│   ├── agent.py, api.py, ner.py, context.py, prompts.py, llm_client.py, relationships.py
│   ├── models.py, utils.py
│   ├── tests/
│   └── Dockerfile
├── orchestrator/              # Агент-оркестратор
│   ├── main.py
│   └── Dockerfile
├── reporter/                  # Агент формирования отчёта (внутренний)
│   ├── main.py
│   └── Dockerfile
├── knowledge_system/          # База знаний и оценка качества
│   ├── agent_roles.md
│   ├── evaluation_criteria.md
│   ├── few_shot_examples_summarizer.md
│   └── few_shot_examples_qa.md
├── observability/             # Стек мониторинга (опционально)
│   ├── docker-compose.yml
│   ├── prometheus/prometheus.yml
│   ├── loki/loki-config.yml
│   ├── promtail/promtail-config.yml
│   └── grafana/provisioning/
├── docker-compose.yml         # Основной compose-файл (агенты + redis)
└── README.md
```

## Тестирование

### Функциональные тесты (Booker)
```bash
cd Booker
python evals/test_booker.py
```

### Character analyzer
```bash
cd character_analyzer
python -m pytest tests/
```

### Ручное тестирование на примерах
```bash
python Summarizer/test.py
python QuestionGenerator/test.py
python reporter/test.py
```

## Наблюдаемость

При запуске `observability/docker-compose.yml` становятся доступны следующие сервисы:

| Сервис | URL | Учётные данные |
|--------|-----|----------------|
| **Prometheus** | http://localhost:9090 | – |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Jaeger UI** | http://localhost:16686 | – |
| **Loki** | (внутренний) | – |
| **cAdvisor** | http://localhost:8080 | – |