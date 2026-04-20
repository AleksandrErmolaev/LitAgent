import spacy
from typing import Dict, List, Tuple
from collections import defaultdict
from tqdm import tqdm
from .utils import split_text_into_chunks

class NERExtractor:
    def __init__(self, model_name: str = "en_core_web_lg"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise RuntimeError(
                f"spaCy model '{model_name}' not found. Install: "
                "python -m spacy download en_core_web_lg"
            )

    def _normalize_name(self, name: str) -> str:
        """Clean and capitalize the name (English only)."""
        # Remove any non-alphabetic characters except hyphen
        clean = ''.join(c for c in name if c.isalpha() or c == '-')
        if not clean:
            return name
        # Capitalize first letter, keep the rest as is (e.g., "McDonald")
        return clean[0].upper() + clean[1:] if len(clean) > 1 else clean.upper()

    def _merge_mentions(
        self,
        raw_mentions: Dict[str, List[Tuple[int, int, str]]]
    ) -> Dict[str, List[Tuple[int, int, str]]]:
        """
        Group mentions by normalized name.
        Canonical name is the normalized form.
        """
        merged = defaultdict(list)
        for original_name, occs in raw_mentions.items():
            norm_name = self._normalize_name(original_name)
            merged[norm_name].extend(occs)

        # Sort occurrences by position
        for norm_name in merged:
            merged[norm_name].sort(key=lambda x: x[0])

        return dict(merged)

    def extract_person_mentions(
        self, text: str
    ) -> Tuple[Dict[str, List[Tuple[int, int, str]]], List[Tuple[int, int, str]]]:
        """
        Returns:
          - mentions: dict canonical_name -> list of (start, end, mention_text)
          - sentences: list of sentences with global positions
        """
        chunks = split_text_into_chunks(text)
        raw_mentions: Dict[str, List[Tuple[int, int, str]]] = defaultdict(list)
        all_sentences: List[Tuple[int, int, str]] = []
        offset = 0

        for chunk in tqdm(chunks, desc="NER (spaCy)", unit="chunk"):
            doc = self.nlp(chunk)
            # Save sentences
            for sent in doc.sents:
                start = offset + sent.start_char
                end = offset + sent.end_char
                all_sentences.append((start, end, sent.text))

            # Extract PERSON entities
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()
                    if name:
                        start = offset + ent.start_char
                        end = offset + ent.end_char
                        raw_mentions[name].append((start, end, name))
            offset += len(chunk) + 1  # approx space between chunks

        merged_mentions = self._merge_mentions(raw_mentions)
        return merged_mentions, all_sentences
