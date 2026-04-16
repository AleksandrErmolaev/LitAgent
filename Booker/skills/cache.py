import redis
import hashlib
import json
import os
from typing import Optional, Dict, Any

class TextCache:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis = None
        self.ttl_seconds = 30 * 24 * 3600  # 30 дней
        self._connect()
    
    def _connect(self):
        """Подключение к Redis с обработкой ошибок"""
        try:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            self.redis.ping()
            print(f"✅ Connected to Redis at {self.redis_url}")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}. Running without cache.")
            self.redis = None
    
    def _make_key(self, title: str, author: str) -> str:
        """Генерирует ключ кеша на основе названия и автора"""
        content = f"{title.lower().strip()}_{author.lower().strip()}"
        return f"book:{hashlib.md5(content.encode()).hexdigest()}"
    
    def get(self, title: str, author: str) -> Optional[Dict[str, Any]]:
        """Получить книгу из кеша"""
        if not self.redis:
            return None
        
        key = self._make_key(title, author)
        data = self.redis.get(key)
        
        if data:
            print(f"📦 Cache HIT for '{title}' by {author}")
            return json.loads(data)
        
        print(f"💾 Cache MISS for '{title}' by {author}")
        return None
    
    def set(self, title: str, author: str, book_data: Dict[str, Any]):
        """Сохранить книгу в кеш"""
        if not self.redis:
            return
        
        key = self._make_key(title, author)
        self.redis.setex(key, self.ttl_seconds, json.dumps(book_data, ensure_ascii=False))
        print(f"💾 Cached '{title}' by {author} for {self.ttl_seconds // 86400} days")
    
    def clear(self, title: str, author: str):
        """Очистить конкретную книгу из кеша"""
        if not self.redis:
            return
        key = self._make_key(title, author)
        self.redis.delete(key)
    
    def clear_all(self):
        """Очистить весь кеш"""
        if not self.redis:
            return
        for key in self.redis.scan_iter("book:*"):
            self.redis.delete(key)