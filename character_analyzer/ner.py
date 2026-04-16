import spacy
import pymorphy3
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
from tqdm import tqdm
from .utils import split_text_into_chunks

class NERExtractor:
    def __init__(self, model_name: str = "ru_core_news_lg"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise RuntimeError(
                f"Модель spaCy '{model_name}' не найдена. Установите: "
                "python -m spacy download ru_core_news_lg"
            )
        # Инициализируем морфологический анализатор
        self.morph = pymorphy3.MorphAnalyzer()

    def _normalize_name(self, name: str) -> str:
        """
        Приводит имя к нормальной форме (именительный падеж, единственное число).
        Если слово не найдено в словаре, возвращает исходное.
        """
        # Очищаем от лишних символов, оставляем буквы и дефис
        clean_name = ''.join(c for c in name if c.isalpha() or c == '-')
        if not clean_name:
            return name
        try:
            parsed = self.morph.parse(clean_name)[0]
            # Приводим к именительному падежу (nomn)
            normal = parsed.inflect({'nomn'})
            if normal:
                return normal.word.capitalize()
            else:
                return clean_name.capitalize()
        except Exception:
            return name

    def _merge_mentions(
    self,
    raw_mentions: Dict[str, List[Tuple[int, int, str]]]
) -> Dict[str, List[Tuple[int, int, str]]]:
        """
        Группирует упоминания по нормализованному имени.
        Каноническое имя — нормализованная форма с заглавной буквы.
        """
        merged = defaultdict(list)
        for original_name, occs in raw_mentions.items():
            norm_name = self._normalize_name(original_name)
            merged[norm_name].extend(occs)

        # Сортируем вхождения для каждого нормализованного имени
        for norm_name in merged:
            merged[norm_name].sort(key=lambda x: x[0])

        return dict(merged)

    def extract_person_mentions(
        self, text: str
    ) -> Tuple[Dict[str, List[Tuple[int, int, str]]], List[Tuple[int, int, str]]]:
        """
        Возвращает:
          - mentions: словарь каноническое_имя -> список (start, end, текст_упоминания)
          - sentences: список предложений с глобальными позициями
        """
        chunks = split_text_into_chunks(text)
        raw_mentions: Dict[str, List[Tuple[int, int, str]]] = defaultdict(list)
        all_sentences: List[Tuple[int, int, str]] = []
        offset = 0

        for chunk in tqdm(chunks, desc="NER (spaCy)", unit="chunk"):
            doc = self.nlp(chunk)
            # Сохраняем предложения
            for sent in doc.sents:
                start = offset + sent.start_char
                end = offset + sent.end_char
                all_sentences.append((start, end, sent.text))

            # Извлекаем PERSON
            for ent in doc.ents:
                if ent.label_ == "PER":  # в русской модели PER
                    name = ent.text.strip()
                    if name:
                        start = offset + ent.start_char
                        end = offset + ent.end_char
                        raw_mentions[name].append((start, end, name))
            offset += len(chunk) + 1  # приблизительно длина пробела между чанками

        # Нормализация и объединение вариантов
        merged_mentions = self._merge_mentions(raw_mentions)
        return merged_mentions, all_sentences