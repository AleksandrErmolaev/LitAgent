# agents/booker.py
import time
from typing import Optional, Dict, Any
from datetime import datetime

# Прямые импорты без промежуточных модулей
from skills.cache import TextCache
from skills.text_cleaner import clean_gutenberg_text, split_into_chapters, detect_language
from skills.gutenberg import GutenbergSource
from skills.litres import LitResSource
from skills.google_books import GoogleBooksSource
from skills.wikisource import WikisourceSource

# Простой логгер (без structlog для начала)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BookerAgent:
    def __init__(self):
        self.sources = {
            "wikisource": WikisourceSource(),
            "gutenberg": GutenbergSource(),
            "litres": LitResSource(),
            "google_books": GoogleBooksSource()
        }
        self.cache = TextCache()
    
    async def _try_source(self, source_name: str, title: str, author: str, language: str = "en") -> Optional[Dict[str, Any]]:
        """Попытка получить книгу из одного источника с учётом языка"""
        source = self.sources.get(source_name)
        if not source:
            return None
        
        logger.info(f"Trying source: {source_name} for {title} (language: {language})")
        
        try:
            if hasattr(source, 'search_and_download'):
                # Передаём язык в поиск
                result = await source.search_and_download(title, author, language)
            else:
                search_result = await source.search(title, author, language)
                if not search_result:
                    return None
                if hasattr(source, 'download'):
                    text = await source.download(search_result.get("book_id"))
                    if not text:
                        return None
                    result = {**search_result, "text": text}
                else:
                    result = search_result
            
            if result and result.get("text"):
                logger.info(f"Success from {source_name}")
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error from {source_name}: {e}")
            return None
    
    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Основной метод агента"""
        start_time = time.time()
        
        title = request.get("title", "").strip()
        author = request.get("author", "").strip()
        
        if not title:
            return {
                "status": "error",
                "error_code": "MISSING_TITLE",
                "message": "Title is required"
            }
        
        logger.info(f"Searching for: {title} by {author}")
        
        # Проверяем кеш
        cached = self.cache.get(title, author)
        if cached:
            cached["cached"] = True
            cached["processing_time_ms"] = int((time.time() - start_time) * 1000)
            logger.info(f"Cache HIT for {title}")
            return cached
        
        sources_to_try = ["wikisource", "gutenberg", "litres", "google_books"]
        book_data = None
        
        for source_name in sources_to_try:
            result = await self._try_source(source_name, title, author)
            if result and result.get("text"):
                book_data = result
                book_data["source"] = source_name
                break
        
        if not book_data or not book_data.get("text"):
            return {
                "status": "error",
                "error_code": "BOOK_NOT_FOUND",
                "message": f"Book '{title}' not found",
                "attempted_sources": sources_to_try
            }
        
        # Очищаем текст
        cleaned_text = clean_gutenberg_text(book_data.get("text", ""))
        language = detect_language(cleaned_text)
        chapters = split_into_chapters(cleaned_text)
        
        result = {
            "status": "success",
            "title": book_data.get("title", title),
            "author": book_data.get("author", author),
            "language": language,
            "source": book_data.get("source", "unknown"),
            "text": cleaned_text,
            "word_count": len(cleaned_text.split()),
            "chapters": chapters,
            "cached": False,
            "processing_time_ms": int((time.time() - start_time) * 1000)
        }
        
        # Сохраняем в кеш
        self.cache.set(title, author, result)
        
        return result