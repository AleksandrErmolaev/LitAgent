import httpx
import os
from typing import Optional, Dict, Any

class LitResSource:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("LITRES_API_KEY", "")
        self.base_url = "https://www.litres.ru/static/apidoc"
        self.timeout = 30.0
    
    async def search(self, title: str, author: str = "") -> Optional[Dict[str, Any]]:
        """Поиск книги в LitRes (требуется API ключ)"""
        if not self.api_key or self.api_key == "your_litres_api_key_here":
            print("⚠️ LitRes API key not configured, skipping")
            return None
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        "q": f"{title} {author}",
                        "type": "book",
                        "api_key": self.api_key
                    }
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                if data.get("results"):
                    first_result = data["results"][0]
                    return {
                        "book_id": first_result.get("id"),
                        "title": first_result.get("title"),
                        "author": first_result.get("author"),
                        "url": first_result.get("url"),
                        "year": first_result.get("year")
                    }
                
                return None
                
            except Exception as e:
                print(f"LitRes search error: {e}")
                return None
    
    async def download(self, book_id: int) -> Optional[str]:
        """Скачивание требует премиум-доступа"""
        print(f"LitRes download requires premium access for book {book_id}")
        return None
    
    async def search_and_download(self, title: str, author: str = "") -> Optional[Dict[str, Any]]:
        """Комбинированный метод"""
        search_result = await self.search(title, author)
        if not search_result:
            return None
        
        return search_result  # Без текста, только метаданные