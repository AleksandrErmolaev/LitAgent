import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

def split_text_into_chunks(text: str, max_chunk_size: int = 100_000) -> List[str]:
    """
    Разбивает текст на чанки по границам предложений.
    Каждый чанк не превышает max_chunk_size символов.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = []
    current_len = 0

    for sent in sentences:
        sent_len = len(sent)
        if current_len + sent_len > max_chunk_size and current:
            chunks.append(" ".join(current))
            current = []
            current_len = 0
        current.append(sent)
        current_len += sent_len + 1  # +1 за пробел

    if current:
        chunks.append(" ".join(current))
    return chunks

def extract_paragraphs_with_positions(text: str) -> List[Tuple[int, int, str]]:
    """
    Разбивает текст на абзацы (по двойному переводу строки) и возвращает
    список кортежей (start_char, end_char, paragraph_text).
    """
    paragraphs = []
    pattern = r'\n\s*\n'
    parts = re.split(pattern, text)
    offset = 0
    for part in parts:
        start = offset
        end = offset + len(part)
        paragraphs.append((start, end, part))
        offset = end + 2  # приблизительно длина разделителя
    return paragraphs