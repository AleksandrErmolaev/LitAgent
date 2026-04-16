# skills/gutenberg.py (дополненная версия)

import httpx
import re
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup

class GutenbergSource:
    def __init__(self):
        self.base_url = "https://www.gutenberg.org"
        self.api_url = "https://gutendex.com"  # Gutendex API для поиска
        self.timeout = 30.0
    
    async def search(self, title: str, author: str = "", language: str = "en") -> Optional[Dict[str, Any]]:
        """Поиск книги с поддержкой языка"""
        query = f"{title} {author}".strip()
        
        # Используем Gutendex API для поиска (проще и быстрее)
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                # Строим URL с фильтром по языку
                url = f"{self.api_url}/books/"
                params = {"search": query}
                
                if language and language != "en":
                    params["languages"] = language
                
                response = await client.get(url, params=params)
                
                if response.status_code != 200:
                    return await self._search_html(title, author, language)
                
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    # Если не нашли с фильтром, пробуем без фильтра и проверяем язык
                    if language and language != "en":
                        params.pop("languages", None)
                        response = await client.get(url, params=params)
                        data = response.json()
                        results = data.get("results", [])
                        
                        # Фильтруем по языку вручную
                        results = [r for r in results if language in r.get("languages", [])]
                
                if results:
                    book = results[0]
                    # Получаем ссылку на текстовый файл
                    formats = book.get("formats", {})
                    text_url = formats.get("text/plain; charset=utf-8") or \
                              formats.get("text/plain") or \
                              formats.get("text/plain; charset=us-ascii")
                    
                    # Если нет текстовой версии, пытаемся получить HTML
                    if not text_url:
                        text_url = formats.get("text/html")
                    
                    return {
                        "book_id": book.get("id"),
                        "title": book.get("title", title),
                        "author": book.get("authors", [{}])[0].get("name", author) if book.get("authors") else author,
                        "url": text_url,
                        "language": book.get("languages", ["en"])[0],
                        "download_url": text_url
                    }
                
                print(f"Book not found on Gutenberg: {title} (language: {language})")
                return None
                
            except Exception as e:
                print(f"Gutenberg API error: {e}")
                return await self._search_html(title, author, language)
    
    async def _search_html(self, title: str, author: str = "", language: str = "en") -> Optional[Dict[str, Any]]:
        """Fallback: поиск через HTML (старый метод)"""
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                # Пробуем найти на Gutenberg
                response = await client.get(
                    f"{self.base_url}/ebooks/search/",
                    params={"query": f"{title} {author}", "submit_search": "Search"}
                )
                
                if response.status_code != 200:
                    return None
                
                soup = BeautifulSoup(response.text, 'html.parser')
                result_item = soup.select_one('li.booklink')
                
                if not result_item:
                    result_item = soup.select_one('.bibrec')
                
                if result_item:
                    link = result_item.find('a', href=re.compile(r'/ebooks/\d+'))
                    if link:
                        book_id = re.search(r'/ebooks/(\d+)', link['href'])
                        if book_id:
                            # Проверяем язык книги (можно добавить логику)
                            return {
                                "book_id": int(book_id.group(1)),
                                "title": title,
                                "author": author,
                                "url": f"{self.base_url}/ebooks/{book_id.group(1)}.txt.utf-8",
                                "language": language
                            }
                
                return None
                
            except Exception as e:
                print(f"Gutenberg HTML search error: {e}")
                return None
    
    async def download(self, book_id: int) -> Optional[str]:
        """Скачивает текст книги по ID"""
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                # Пробуем UTF-8 версию
                response = await client.get(f"{self.base_url}/ebooks/{book_id}.txt.utf-8")
                
                if response.status_code == 200:
                    return response.text
                
                # Пробуем обычный txt
                response = await client.get(f"{self.base_url}/files/{book_id}/{book_id}-0.txt")
                
                if response.status_code == 200:
                    return response.text
                
                print(f"Failed to download book {book_id} from Gutenberg")
                return None
                
            except Exception as e:
                print(f"Gutenberg download error: {e}")
                return None
    
    async def search_and_download(self, title: str, author: str = "", language: str = "en") -> Optional[Dict[str, Any]]:
        """Комбинированный метод: поиск + скачивание"""
        search_result = await self.search(title, author, language)
        if not search_result:
            return None
        
        # Если у нас уже есть download_url, пробуем скачать оттуда
        if search_result.get("download_url"):
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                try:
                    response = await client.get(search_result["download_url"])
                    if response.status_code == 200:
                        search_result["text"] = response.text
                        return search_result
                except Exception:
                    pass
        
        # Иначе скачиваем по book_id
        if search_result.get("book_id"):
            text = await self.download(search_result["book_id"])
            if text:
                search_result["text"] = text
                return search_result
        
        return search_result
    
    async def get_available_languages(self) -> List[str]:
        """Получить список языков, доступных в Gutenberg"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.api_url}/books/")
                if response.status_code == 200:
                    data = response.json()
                    # Анализируем языки из результатов
                    languages = set()
                    for book in data.get("results", []):
                        for lang in book.get("languages", []):
                            languages.add(lang)
                    return sorted(languages)
            except Exception as e:
                print(f"Error getting languages: {e}")
        
        return ["en"]  # По умолчанию только английский