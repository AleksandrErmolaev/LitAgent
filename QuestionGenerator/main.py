from typing import List, Dict, Any
from dataclasses import dataclass
import random

def call_llm(prompt: str, max_tokens: int = 512) -> str:
    return f"[LLM OUTPUT]: {prompt[:200]}..."


@dataclass
class Question:
    text: str
    difficulty: str
    options: List[str]
    correct_answer: str
    quote_evidence: str
    chapter: int


class QuestionGeneratorAgent:
    def __init__(self, num_questions: int = 10):
        self.num_questions = num_questions

    def run(
        self,
        full_text: str,
        chapters: List[str],
        characters: List[Dict] = None
    ) -> Dict[str, Any]:

        questions: List[Question] = []

        # 1. Выделяем "события" (упрощенно = главы)
        events = self._extract_events(chapters)

        # 2. Генерация вопросов
        for i, event in enumerate(events):
            q = self._generate_question(event, i)
            questions.append(q)

            if len(questions) >= self.num_questions:
                break

        return {
            "questions": [q.__dict__ for q in questions]
        }


    def _extract_events(self, chapters: List[str]) -> List[str]:
        return chapters

    def _generate_question(self, event: str, chapter_idx: int) -> Question:
        difficulty = random.choice(["easy", "medium", "hard"])

        prompt = f"""
Ты — преподаватель литературы.

Сгенерируй 1 вопрос по тексту.

Требования:
- 4 варианта ответа
- 1 правильный
- добавь цитату-доказательство
- сложность: {difficulty}

Текст:
{event}

Формат:
Вопрос:
A)
B)
C)
D)
Ответ:
Цитата:
"""

        raw = call_llm(prompt)

        return self._parse_llm_output(raw, difficulty, chapter_idx)

    def _parse_llm_output(self, raw: str, difficulty: str, chapter_idx: int) -> Question:
        """
        Очень простой парсер (MVP)
        """
        lines = raw.split("\n")

        question = "Не удалось распарсить вопрос"
        options = []
        correct = ""
        quote = ""

        for line in lines:
            line = line.strip()

            if line.lower().startswith("вопрос"):
                question = line

            elif line.startswith(("A)", "B)", "C)", "D)")):
                options.append(line)

            elif line.lower().startswith("ответ"):
                correct = line

            elif line.lower().startswith("цитата"):
                quote = line

        if len(options) < 4:
            options = [
                "A) Вариант 1",
                "B) Вариант 2",
                "C) Вариант 3",
                "D) Вариант 4"
            ]
            correct = options[0]

        return Question(
            text=question,
            difficulty=difficulty,
            options=options,
            correct_answer=correct,
            quote_evidence=quote,
            chapter=chapter_idx + 1
        )