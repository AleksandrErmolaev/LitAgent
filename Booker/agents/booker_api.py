from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

from agents.booker import BookerAgent
from observability.metrics import get_metrics
from observability.logging_config import logger

app = FastAPI(
    title="Booker Agent API",
    description="Загрузчик литературных произведений для LitAgent системы",
    version="1.0.0"
)

booker = BookerAgent()


class BookRequest(BaseModel):
    title: str = Field(..., description="Название произведения", example="Преступление и наказание")
    author: str = Field(default="", description="Автор", example="Фёдор Достоевский")
    language: str = Field(default="ru", description="Язык (ru/en)", example="ru")
    source_hint: Optional[str] = Field(default=None, description="Принудительный источник", example="gutenberg")


class BookResponse(BaseModel):
    status: str
    title: str
    author: str
    language: str
    word_count: int
    chapters_count: int
    source: str
    cached: bool
    processing_time_ms: int


@app.get("/health")
async def health():
    """Проверка здоровья сервиса"""
    return {"status": "ok", "agent": "Booker", "version": "1.0.0"}


@app.post("/fetch", response_model=BookResponse)
async def fetch_book(request: BookRequest):
    """
    Загрузить книгу по названию и автору
    """
    logger.info("api.request", title=request.title, author=request.author)
    
    result = await booker.run(request.dict())
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result)
    
    # Сокращённый ответ для API (полный текст не возвращаем через HTTP)
    return {
        "status": result["status"],
        "title": result["title"],
        "author": result["author"],
        "language": result["language"],
        "word_count": result["word_count"],
        "chapters_count": len(result.get("chapters", [])),
        "source": result["source"],
        "cached": result.get("cached", False),
        "processing_time_ms": result["processing_time_ms"]
    }


@app.post("/fetch_full")
async def fetch_book_full(request: BookRequest):
    """
    Загрузить книгу с полным текстом (осторожно, большой ответ!)
    """
    result = await booker.run(request.dict())
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result)
    
    return result


@app.get("/metrics")
async def metrics():
    """Prometheus метрики"""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(get_metrics().decode())


@app.delete("/cache/{title}/{author}")
async def clear_cache(title: str, author: str):
    """Очистить кеш для конкретной книги"""
    booker.cache.clear(title, author)
    return {"status": "ok", "message": f"Cache cleared for '{title}' by {author}"}


if __name__ == "__main__":
    uvicorn.run(
        "agents.booker_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )