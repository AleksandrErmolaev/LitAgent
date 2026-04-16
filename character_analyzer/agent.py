import logging
from typing import Dict, Any, List, Optional
from tqdm import tqdm

from .models import Character, Relationship
from .ner import NERExtractor
from .context import collect_character_context
from .prompts import build_character_prompt
from .llm_client import LLMClient
from .relationships import build_relationships

logger = logging.getLogger(__name__)

class CharacterAnalyzerAgent:
    def __init__(
        self,
        llm_model=None,
        spacy_model: str = "ru_core_news_lg",
        min_mentions: int = 5,
        context_window: int = 2,
        max_context_chars: int = 2000,
        cooccurrence_threshold: int = 1
    ):
        self.llm = LLMClient(llm_model) if llm_model else None
        self.ner_extractor = NERExtractor(spacy_model)
        self.min_mentions = min_mentions
        self.context_window = context_window
        self.max_context_chars = max_context_chars
        self.cooccurrence_threshold = cooccurrence_threshold

    def _filter_characters(self, mentions: Dict[str, List]) -> List[tuple]:
        filtered = [(name, len(occs)) for name, occs in mentions.items()
                    if len(occs) >= self.min_mentions]
        filtered.sort(key=lambda x: x[1], reverse=True)
        return filtered

    def _analyze_character(
        self,
        name: str,
        mentions: List,
        sentences: List
    ) -> Optional[Character]:
        context = collect_character_context(
            name, mentions, sentences,
            self.context_window, self.max_context_chars
        )
        if not context:
            logger.warning(f"Пустой контекст для {name}")
            return None

        if self.llm is None:
            # Заглушка для тестирования
            return Character(
                name=name,
                role="неизвестно",
                archetype="обычный человек",
                traits=[],
                description="",
                mentions_count=len(mentions),
                quote=""
            )

        prompt = build_character_prompt(name, context)
        response = self.llm.generate(prompt)
        parsed = self.llm.parse_character_response(response, name)

        if parsed is None:
            # fallback
            return Character(
                name=name,
                role="неизвестно",
                archetype="обычный человек",
                traits=[],
                description="",
                mentions_count=len(mentions),
                quote=""
            )

        return Character(
            name=name,
            role=parsed.get("role", ""),
            archetype=parsed.get("archetype", "обычный человек"),
            traits=parsed.get("traits", []),
            description=parsed.get("description", ""),
            mentions_count=len(mentions),
            quote=parsed.get("quote", "")
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        full_text = input_data["full_text"]
        if not full_text:
            raise ValueError("Отсутствует поле 'full_text'")

        logger.info("Запуск NER...")
        mentions, sentences = self.ner_extractor.extract_person_mentions(full_text)
        logger.info(f"Найдено уникальных PERSON: {len(mentions)}")

        filtered = self._filter_characters(mentions)
        if not filtered:
            return {"characters": [], "relationships": []}

        characters = []
        for name, count in tqdm(filtered, desc="Анализ персонажей"):
            char = self._analyze_character(name, mentions[name], sentences)
            if char:
                characters.append(char)
            else:
                # Добавляем минимальную запись
                characters.append(Character(
                    name=name, role="", archetype="", traits=[],
                    description="", mentions_count=count, quote=""
                ))

        logger.info(f"Обработано персонажей: {len(characters)}")

        # Преобразуем в словари для передачи в relationships
        char_dicts = [c.to_dict() for c in characters]
        relationships = build_relationships(
            full_text, char_dicts, mentions, self.cooccurrence_threshold
        )

        return {
            "characters": char_dicts,
            "relationships": [r.to_dict() for r in relationships]
        }