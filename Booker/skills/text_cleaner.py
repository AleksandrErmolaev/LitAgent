import re
from typing import List, Dict, Any

def clean_gutenberg_text(raw_text: str) -> str:
    """
    Очищает текст, скачанный с Project Gutenberg
    Удаляет шапку, футер, номера страниц
    """
    if not raw_text:
        return ""
    
    # Удаляем всё до START OF PROJECT GUTENBERG
    start_patterns = [
        r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK .+ \*\*\*",
        r"\*\*\* START OF THIS PROJECT GUTENBERG EBOOK .+ \*\*\*",
        r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK \*\*\*",
    ]
    
    for pattern in start_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            raw_text = raw_text[match.end():]
            break
    
    # Удаляем всё после END OF PROJECT GUTENBERG
    end_patterns = [
        r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK .+ \*\*\*",
        r"\*\*\* END OF THIS PROJECT GUTENBERG EBOOK .+ \*\*\*",
        r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK \*\*\*",
    ]
    
    for pattern in end_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            raw_text = raw_text[:match.start()]
            break
    
    # Удаляем номера страниц (форматы: " 123 " или "\n123\n")
    raw_text = re.sub(r'\n\s*\d+\s*\n', '\n', raw_text)
    
    # Удаляем строки, состоящие только из символов (оглавление)
    raw_text = re.sub(r'\n[=\-~]+\n', '\n', raw_text)
    
    # Нормализуем пробелы
    raw_text = re.sub(r'\n\s*\n', '\n\n', raw_text)
    raw_text = raw_text.strip()
    
    return raw_text


def split_into_chapters(text: str) -> List[Dict[str, Any]]:
    """
    Разбивает текст на главы по маркерам
    Поддерживает русский и английский
    """
    if not text:
        return []
    
    # Паттерны для поиска глав (в порядке приоритета)
    patterns = [
        # Русские
        (r'(?i)(?:ГЛАВА|ЧАСТЬ)\s+([IVXLCDM]+|\d+)(?:\.|\s|–|—)', 'russian'),
        (r'(?i)(?:ГЛАВА|ЧАСТЬ)\s+(\w+)', 'russian'),
        # Английские
        (r'(?i)CHAPTER\s+([IVXLCDM]+|\d+)(?:\.|\s|–|—)', 'english'),
        (r'(?i)PART\s+([IVXLCDM]+|\d+)(?:\.|\s|–|—)', 'english'),
        # Просто цифры с новой строки
        (r'\n\s*(\d+)\.\s+[А-ЯA-Z]', 'numbered'),
    ]
    
    chapters = []
    
    # Пробуем каждый паттерн
    for pattern, lang in patterns:
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        
        if len(matches) >= 2:  # Нашли как минимум 2 главы
            for i, match in enumerate(matches):
                start = match.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                
                chapter_text = text[start:end].strip()
                chapter_title = match.group(0).strip()
                chapter_number = match.group(1).strip()
                
                chapters.append({
                    "number": chapter_number,
                    "title": chapter_title,
                    "text": chapter_text
                })
            break
    
    # Если не нашли глав по паттернам, возвращаем весь текст как одну главу
    if not chapters:
        chapters = [{
            "number": "1",
            "title": "Full Text",
            "text": text
        }]
    
    return chapters


def detect_language(text: str) -> str:
    """
    Простое определение языка по первым 1000 символам
    """
    sample = text[:1000]
    
    # Подсчёт кириллицы
    cyrillic = len(re.findall(r'[а-яА-ЯёЁ]', sample))
    latin = len(re.findall(r'[a-zA-Z]', sample))
    
    if cyrillic > latin:
        return "ru"
    else:
        return "en"