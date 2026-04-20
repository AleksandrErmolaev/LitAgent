import logging
from typing import Dict, Any, List, Optional
from tqdm import tqdm

from character_analyzer.models import Character
from character_analyzer.ner import NERExtractor
from character_analyzer.context import collect_character_context
from character_analyzer.prompts import build_character_prompt
from character_analyzer.llm_client import LLMClient
from character_analyzer.relationships import build_relationships

logger = logging.getLogger(__name__)

class CharacterAnalyzerAgent:
    def __init__(
        self,
        llm_model=None,
        spacy_model: str = "en_core_web_lg",
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
            logger.warning(f"Empty context for {name}")
            return None

        if self.llm is None:
            return Character(
                name=name,
                role="unknown",
                archetype="everyman",
                traits=[],
                description="",
                mentions_count=len(mentions),
                quote=""
            )

        prompt = build_character_prompt(name, context)
        response = self.llm.generate(prompt)
        parsed = self.llm.parse_character_response(response, name)

        if parsed is None:
            return Character(
                name=name,
                role="unknown",
                archetype="everyman",
                traits=[],
                description="",
                mentions_count=len(mentions),
                quote=""
            )

        return Character(
            name=name,
            role=parsed.get("role", ""),
            archetype=parsed.get("archetype", "everyman"),
            traits=parsed.get("traits", []),
            description=parsed.get("description", ""),
            mentions_count=len(mentions),
            quote=parsed.get("quote", "")
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        full_text = input_data["full_text"]
        if not full_text:
            raise ValueError("Missing 'full_text' field")

        logger.info("Running NER...")
        mentions, sentences = self.ner_extractor.extract_person_mentions(full_text)
        logger.info(f"Unique PERSON entities found: {len(mentions)}")

        filtered = self._filter_characters(mentions)
        if not filtered:
            return {"characters": [], "relationships": []}

        characters = []
        for name, count in tqdm(filtered, desc="Analyzing characters"):
            char = self._analyze_character(name, mentions[name], sentences)
            if char:
                characters.append(char)
            else:
                characters.append(Character(
                    name=name, role="", archetype="", traits=[],
                    description="", mentions_count=count, quote=""
                ))

        logger.info(f"Characters processed: {len(characters)}")

        char_dicts = [c.to_dict() for c in characters]
        relationships = build_relationships(
            full_text, char_dicts, mentions, self.cooccurrence_threshold
        )

        return {
            "characters": char_dicts,
            "relationships": [r.to_dict() for r in relationships]
        }