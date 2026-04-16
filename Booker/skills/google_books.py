import httpx
from typing import Optional, Dict, Any

class GoogleBooksSource:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1"
        self.timeout = 30.0
    
    async def search(self, title: str, author: str = "") -> Optional[Dict[str, Any]]:
        """Поиск книги в Google Books API"""
        query = f"intitle:{title}"
        if author:
            query += f"+inauthor:{author}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/volumes",
                    params={"q": query, "maxResults": 1}
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                if data.get("totalItems", 0) > 0:
                    book = data["items"][0]
                    volume_info = book.get("volumeInfo", {})
                    
                    return {
                        "book_id": book.get("id"),
                        "title": volume_info.get("title", title),
                        "author": volume_info.get("authors", [author])[0] if author else volume_info.get("authors", [""])[0],
                        "year": volume_info.get("publishedDate", "").split("-")[0],
                        "url": volume_info.get("infoLink"),
                        "is_preview_only": True
                    }
                
                return None
                
            except Exception as e:
                print(f"Google Books search error: {e}")
                return None
    
    async def download(self, book_id: str) -> Optional[str]:
        """Google Books не даёт скачать полный текст"""
        print(f"Google Books: only preview available for {book_id}")
        return None
    
    async def search_and_download(self, title: str, author: str = "") -> Optional[Dict[str, Any]]:
        """Комбинированный метод"""
        return await self.search(title, author)