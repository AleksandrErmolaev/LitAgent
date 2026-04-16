from typing import List, Dict, Any
import re
from dataclasses import dataclass
from fastapi import FastAPI

app = FastAPI()
def call_llm(prompt: str, max_tokens: int = 512) -> str:
    # TODO: подключить реальную модель (Llama-3-8B-Instruct)
    return f"[LLM OUTPUT]: {prompt[:200]}..."


@dataclass
class SummaryResult:
    super_short: str
    short: str
    detailed: str
    key_quotes: List[str]
    chapter_summaries: List[str]


class SummarizerAgent:
    def __init__(self, max_tokens_per_chunk: int = 8000):
        self.max_tokens_per_chunk = max_tokens_per_chunk

    def run(self, full_text: str, chapters: List[str]) -> Dict[str, Any]:

        chapter_summaries = []

        for idx, chapter in enumerate(chapters):
            summary = self._summarize_chapter(chapter, idx)
            chapter_summaries.append(summary)

        detailed = self._aggregate_summaries(chapter_summaries, level="detailed")
        short = self._aggregate_summaries(chapter_summaries, level="short")
        super_short = self._aggregate_summaries(chapter_summaries, level="super_short")

        key_quotes = self._extract_key_quotes(full_text)

        return SummaryResult(
            super_short=super_short,
            short=short,
            detailed=detailed,
            key_quotes=key_quotes,
            chapter_summaries=chapter_summaries
        ).__dict__

    def _summarize_chapter(self, chapter: str, idx: int, lang: str) -> str:
        prompt = f"""
    Ты — профессиональный литературный аналитик.

    Тебе дан текст (возможно на английском).
    Сделай краткое содержание главы НА РУССКОМ ЯЗЫКЕ.

    Требования:
    - 5–7 предложений
    - сохранить смысл
    - не добавлять ничего от себя

    Глава {idx + 1}:
    {chapter}
    """
        return call_llm(prompt)

    def _aggregate_summaries(self, summaries: List[str], level: str) -> str:
        if level == "detailed":
            instruction = "Объедини в подробное содержание (300-500 слов)"
        elif level == "short":
            instruction = "Сократи до краткого содержания (100-150 слов)"
        elif level == "super_short":
            instruction = "Сожми до 2-3 предложений"
        else:
            raise ValueError("Unknown level")

        combined = "\n".join(summaries)

        prompt = f"""
Ты — литературный аналитик.

{instruction}

Текст:
{combined}
"""
        return call_llm(prompt, max_tokens=500)

    def _extract_key_quotes(self, text: str, max_quotes: int = 5) -> List[str]:
        """
        Простая эвристика:
        - ищем текст в кавычках
        - берем первые N
        """
        quotes = re.findall(r'["«](.*?)["»]', text)

        quotes = [q.strip() for q in quotes if len(q.split()) > 5]

        return quotes[:max_quotes]

@app.post("/summarize")
def summarize(data: dict):
    text = data.get("text", "")
    chapters = data.get("chapters", [])

    return {
        "super_short": "Короткое содержание",
        "short": "Среднее содержание",
        "detailed": "Подробное содержание",
        "key_quotes": [],
        "chapter_summaries": []
    }