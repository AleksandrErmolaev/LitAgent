import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError

# --- Pydantic models for input validation ---

class SummaryData(BaseModel):
    super_short: str = Field(..., description="Сверхкраткое содержание (1-2 предложения)")
    short: str = Field(..., description="Краткое содержание (абзац)")
    detailed: str = Field(..., description="Подробное содержание (несколько абзацев)")
    key_quotes: List[str] = Field(default_factory=list, description="Ключевые цитаты")
    chapter_summaries: Dict[str, str] = Field(default_factory=dict, description="Краткое содержание по главам")

class CharacterData(BaseModel):
    name: str
    role: str = ""
    archetype: str = ""
    traits: List[str] = Field(default_factory=list)
    description: str = ""
    mentions_count: int = 0
    quote: str = ""

class RelationshipData(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    type: str = ""
    strength: float = 0.0

    class Config:
        populate_by_name = True

class CharacterAnalysis(BaseModel):
    characters: List[CharacterData] = Field(default_factory=list)
    relationships: List[RelationshipData] = Field(default_factory=list)

class QuestionData(BaseModel):
    text: str
    difficulty: str = "medium"  # easy, medium, hard
    options: List[str] = Field(default_factory=list)
    correct_answer: str
    quote_evidence: str = ""
    chapter: str = ""

class QuestionsData(BaseModel):
    questions: List[QuestionData] = Field(default_factory=list)

class Metadata(BaseModel):
    title: str
    author: str
    language: str = "ru"
    word_count: int = 0
    year: Optional[str] = None
    source_url: Optional[str] = None

class ReportInput(BaseModel):
    summary: SummaryData
    characters: CharacterAnalysis
    questions: QuestionsData
    metadata: Metadata
    model_used: str = "meta-llama/Llama-3-8B-Instruct"
    processing_time_ms: int = 0  # будет перезаписано

# --- Reporter Agent ---

class ReporterAgent:
    """Агент для формирования итогового отчёта в форматах JSON и Markdown."""
    
    def __init__(self, language: str = "ru", model_name: Optional[str] = None):
        """
        Args:
            language: Язык заголовков отчёта ('ru' или 'en')
            model_name: Имя используемой LLM (если не передано в данных)
        """
        self.language = language
        self.model_name = model_name or "meta-llama/Llama-3-8B-Instruct"
        self.logger = logging.getLogger("ReporterAgent")

    def generate_report(self, data: Dict[str, Any], start_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Генерирует JSON и Markdown отчёты.
        
        Args:
            data: Словарь с данными от предыдущих агентов.
            start_time: Время начала обработки (для расчёта processing_time_ms).
            
        Returns:
            Словарь с ключами 'json_report' (dict) и 'markdown_report' (str).
        """
        # Валидация входных данных
        try:
            input_data = ReportInput(**data)
        except ValidationError as e:
            self.logger.error(f"Validation error in reporter input: {e}")
            raise ValueError(f"Invalid input data: {e}") from e
        
        # Расчёт времени обработки
        if start_time is not None:
            processing_time_ms = int((time.time() - start_time) * 1000)
        else:
            processing_time_ms = data.get("processing_time_ms", 0)
        
        # Формирование JSON отчёта
        json_report = self._build_json_report(input_data, processing_time_ms)
        
        # Формирование Markdown отчёта
        markdown_report = self._build_markdown_report(input_data)
        
        return {
            "json_report": json_report,
            "markdown_report": markdown_report
        }
    
    def _build_json_report(self, data: ReportInput, processing_time_ms: int) -> Dict[str, Any]:
        """Создаёт структуру JSON отчёта."""
        return {
            "metadata": {
                "title": data.metadata.title,
                "author": data.metadata.author,
                "language": data.metadata.language,
                "word_count": data.metadata.word_count,
                "year": data.metadata.year,
                "source_url": data.metadata.source_url,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "processing_time_ms": processing_time_ms,
                "model_used": data.model_used
            },
            "summary": data.summary.dict(),
            "characters": {
                "list": [c.dict() for c in data.characters.characters],
                "relationships": [r.dict(by_alias=True) for r in data.characters.relationships]
            },
            "questions": [q.dict() for q in data.questions.questions]
        }
    
    def _build_markdown_report(self, data: ReportInput) -> str:
        """Генерирует человеко-читаемый Markdown отчёт."""
        md = []
        lang = self.language if self.language in ("ru", "en") else "ru"
        
        # Заголовок
        md.append(f"# Анализ произведения: «{data.metadata.title}» — {data.metadata.author}")
        md.append("")
        
        # Метаинформация
        md.append("## Общая информация")
        md.append("")
        md.append(f"- **Название**: {data.metadata.title}")
        md.append(f"- **Автор**: {data.metadata.author}")
        md.append(f"- **Язык**: {'русский' if data.metadata.language == 'ru' else 'английский'}")
        md.append(f"- **Объём**: {data.metadata.word_count:,} слов")
        if data.metadata.year:
            md.append(f"- **Год публикации**: {data.metadata.year}")
        if data.metadata.source_url:
            md.append(f"- **Источник**: [{data.metadata.source_url}]({data.metadata.source_url})")
        md.append("")
        
        md.append("## Содержание")
        md.append("")
        md.append("### Сверхкраткое содержание")
        md.append(data.summary.super_short)
        md.append("")
        md.append("### Краткое содержание")
        md.append(data.summary.short)
        md.append("")
        md.append("### Подробное содержание")
        md.append(data.summary.detailed)
        md.append("")
        
        if data.summary.key_quotes:
            md.append("### Ключевые цитаты")
            md.append("")
            for quote in data.summary.key_quotes:
                md.append(f"> {quote}")
                md.append("")
            md.append("")
        
        if data.summary.chapter_summaries:
            md.append("### Содержание по главам")
            md.append("")
            for chapter, summary in data.summary.chapter_summaries.items():
                md.append(f"**{chapter}**: {summary}")
                md.append("")
            md.append("")
        
        md.append("## Персонажи")
        md.append("")
        if data.characters.characters:
            md.append("| Имя | Роль | Архетип | Черты | Упоминаний |")
            md.append("|-----|------|---------|-------|-----------|")
            for char in data.characters.characters:
                traits_str = ", ".join(char.traits[:3]) + ("..." if len(char.traits) > 3 else "")
                md.append(f"| {char.name} | {char.role} | {char.archetype} | {traits_str} | {char.mentions_count} |")
            md.append("")
            
            md.append("### Описания персонажей")
            md.append("")
            for char in data.characters.characters:
                md.append(f"#### {char.name}")
                md.append(f"**Роль**: {char.role}  ")
                md.append(f"**Архетип**: {char.archetype}  ")
                md.append(f"**Черты**: {', '.join(char.traits)}  ")
                md.append(f"**Описание**: {char.description}  ")
                if char.quote:
                    md.append(f"**Цитата**: *«{char.quote}»*  ")
                md.append("")
        
        if data.characters.relationships:
            md.append("### Связи между персонажами")
            md.append("")
            md.append("| От | К | Тип связи | Сила |")
            md.append("|----|---|-----------|------|")
            for rel in data.characters.relationships:
                md.append(f"| {rel.from_} | {rel.to} | {rel.type} | {rel.strength:.2f} |")
            md.append("")
            
            md.append("#### Схема связей")
            md.append("```")
            md.append(self._generate_ascii_graph(data.characters.relationships))
            md.append("```")
            md.append("")
        
        md.append("## Вопросы для самопроверки")
        md.append("")
        if data.questions.questions:
            for i, q in enumerate(data.questions.questions, 1):
                md.append(f"### Вопрос {i} (уровень: {q.difficulty})")
                md.append(f"**{q.text}**")
                md.append("")
                md.append("Варианты ответов:")
                for opt in q.options:
                    md.append(f"- {opt}")
                md.append("")
                md.append(f"Правильный ответ: **{q.correct_answer}**")
                if q.quote_evidence:
                    md.append(f"Доказательство из текста: *«{q.quote_evidence}»*")
                if q.chapter:
                    md.append(f"Глава: {q.chapter}")
                md.append("")
        else:
            md.append("*Вопросы не были сгенерированы.*")
            md.append("")
        
        md.append("---")
        md.append("")
        
        return "\n".join(md)
    
    def _generate_ascii_graph(self, relationships: List[RelationshipData]) -> str:
        """Создаёт простое текстовое представление графа связей."""
        if not relationships:
            return "Нет данных о связях."
        
        nodes = set()
        edges = []
        for rel in relationships:
            nodes.add(rel.from_)
            nodes.add(rel.to)
            edges.append((rel.from_, rel.to, rel.type, rel.strength))
        
        lines = []
        lines.append("Граф связей персонажей:")
        for from_, to, rel_type, strength in edges:
            lines.append(f"  {from_} --> {to} [{rel_type}, strength={strength:.2f}]")
        return "\n".join(lines)


def save_json_report(report: Dict[str, Any], filepath: str) -> None:
    """Сохраняет JSON отчёт в файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report["json_report"], f, ensure_ascii=False, indent=2)

def save_markdown_report(report: Dict[str, Any], filepath: str) -> None:
    """Сохраняет Markdown отчёт в файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report["markdown_report"])
