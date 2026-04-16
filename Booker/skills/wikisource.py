# skills/wikisource.py

import httpx
import re
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup

# Словарь для транслитерации русских названий книг на английские
RUSSIAN_BOOK_TITLES = {
    "война и мир": "War and Peace",
    "евгений онегин": "Eugene Onegin",
    "преступление и наказание": "Crime and Punishment",
    "анна каренина": "Anna Karenina",
    "мёртвые души": "Dead Souls",
    "отцы и дети": "Fathers and Sons",
    "тихий дон": "And Quiet Flows the Don",
    "мастер и маргарита": "The Master and Margarita",
    "идиот": "The Idiot",
    "братья карамазовы": "The Brothers Karamazov",
    "обломов": "Oblomov",
    "человек в футляре": "The Man in a Case",
    "вишнёвый сад": "The Cherry Orchard",
    "три сестры": "Three Sisters",
    "чайка": "The Seagull",
}

class WikisourceSource:
    def __init__(self):
        self.base_url = "https://wikisource.org"
        self.api_url = "https://wikisource.org/w/api.php"
        self.export_url = "https://ws-export.wmcloud.org"
        self.timeout = 30.0
        
        # Языковые поддомены
        self.language_domains = {
            "ru": "https://ru.wikisource.org",
            "en": "https://en.wikisource.org",
            "fr": "https://fr.wikisource.org",
            "de": "https://de.wikisource.org",
        }
    
    def _get_domain(self, language: str) -> str:
        """Получить домен для языка"""
        if language in self.language_domains:
            return self.language_domains[language]
        return self.base_url
    
    def _normalize_title(self, title: str, language: str) -> str:
        """
        Нормализует название для поиска
        Если язык русский, но название на русском — пробуем найти английский эквивалент
        """
        if language == "ru":
            # Проверяем словарь русских названий
            title_lower = title.lower()
            if title_lower in RUSSIAN_BOOK_TITLES:
                english_title = RUSSIAN_BOOK_TITLES[title_lower]
                print(f"🔁 Transliterating: '{title}' -> '{english_title}' for search")
                return english_title
        
        # Заменяем пробелы на подчёркивания для URL
        return title.replace(" ", "_")
    
    async def search(self, title: str, author: str = "", language: str = "ru") -> Optional[Dict[str, Any]]:
        """
        Поиск книги в Wikisource
        """
        domain = self._get_domain(language)
        api_url = f"{domain}/w/api.php"
        
        # Нормализуем название для поиска
        search_title = self._normalize_title(title, language)
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                # Пробуем прямой доступ по URL (самый надёжный способ)
                direct_url = f"{domain}/wiki/{search_title}"
                direct_response = await client.get(direct_url)
                
                if direct_response.status_code == 200:
                    # Страница существует!
                    soup = BeautifulSoup(direct_response.text, 'html.parser')
                    page_title = soup.find("title")
                    
                    if page_title and "Page not found" not in page_title.text:
                        print(f"✅ Found directly: {direct_url}")
                        return {
                            "book_id": hash(search_title),
                            "title": title,
                            "author": author,
                            "language": language,
                            "page_title": search_title,
                            "url": direct_url,
                            "direct_found": True
                        }
                
                # Если прямой доступ не сработал, пробуем поиск
                params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": f"{title} {author}",
                    "srwhat": "text",
                    "srlimit": 5,
                    "format": "json",
                }
                
                response = await client.get(api_url, params=params)
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                results = data.get("query", {}).get("search", [])
                
                if results:
                    first_result = results[0]
                    page_title = first_result.get("title")
                    
                    return {
                        "book_id": first_result.get("pageid"),
                        "title": page_title,
                        "author": author,
                        "language": language,
                        "page_title": page_title,
                        "url": f"{domain}/wiki/{page_title.replace(' ', '_')}",
                    }
                
                print(f"❌ Book not found on Wikisource: {title}")
                return None
                
            except Exception as e:
                print(f"Wikisource search error: {e}")
                return None
    
    async def download_via_export(self, page_title: str, language: str = "ru") -> Optional[str]:
        """
        Скачивание книги через WS Export Tool
        """
        domain = self._get_domain(language)
        page_url = f"{domain}/wiki/{page_title.replace(' ', '_')}"
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(
                    self.export_url,
                    params={
                        "format": "txt",
                        "page": page_url
                    }
                )
                
                if response.status_code == 200 and len(response.text) > 1000:
                    return response.text
                
                return None
                
            except Exception as e:
                print(f"WS Export error: {e}")
                return None
    
    async def download_via_parse(self, page_title: str, language: str = "ru") -> Optional[str]:
        """
        Альтернативный метод: парсинг HTML
        """
        domain = self._get_domain(language)
        page_url = f"{domain}/wiki/{page_title.replace(' ', '_')}"
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(page_url)
                
                if response.status_code != 200:
                    return None
                
                soup = BeautifulSoup(response.text, 'html.parser')
                text_section = soup.find("div", {"class": "mw-parser-output"})
                
                if text_section:
                    # Удаляем навигационные элементы
                    for nav in text_section.find_all(["table", "div"], class_=["navbox", "toc", "metadata"]):
                        nav.decompose()
                    
                    text = text_section.get_text().strip()
                    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
                    
                    return text if len(text) > 1000 else None
                
                return None
                
            except Exception as e:
                print(f"Wikisource parse error: {e}")
                return None
    
    async def search_and_download(self, title: str, author: str = "", language: str = "ru") -> Optional[Dict[str, Any]]:
        """
        Основной метод: поиск + скачивание
        """
        print(f"🔍 Searching Wikisource for: {title} (language: {language})")
        
        # 1. Поиск
        search_result = await self.search(title, author, language)
        if not search_result:
            return None
        
        page_title = search_result.get("page_title")
        
        # 2. Скачивание
        text = await self.download_via_export(page_title, language)
        
        if not text:
            print(f"📄 Export failed, trying HTML parse...")
            text = await self.download_via_parse(page_title, language)
        
        if not text:
            print(f"❌ Failed to download {title}")
            return None
        
        print(f"✅ Downloaded {title}: {len(text)} characters")
        
        return {
            "book_id": search_result.get("book_id"),
            "title": title,
            "author": author,
            "language": language,
            "source": "wikisource",
            "url": search_result.get("url"),
            "text": text,
            "word_count": len(text.split())
        }