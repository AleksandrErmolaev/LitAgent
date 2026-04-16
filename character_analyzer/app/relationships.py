from collections import defaultdict
from typing import Dict, List, Tuple
from .models import Relationship
from .utils import extract_paragraphs_with_positions

def build_relationships(
    text: str,
    characters: List[Dict],  # или List[Character], но для удобства dict
    mentions: Dict[str, List[Tuple[int, int, str]]],
    cooccurrence_threshold: int = 1
) -> List[Relationship]:
    """
    Строит связи на основе совместного упоминания в одном абзаце.
    """
    char_names = {c["name"] for c in characters}
    paragraphs = extract_paragraphs_with_positions(text)

    cooccur = defaultdict(int)

    for p_start, p_end, _ in paragraphs:
        present = set()
        for name, occs in mentions.items():
            if name not in char_names:
                continue
            # Есть ли хотя бы одно вхождение внутри абзаца
            for occ_start, occ_end, _ in occs:
                if p_start <= occ_start <= p_end:
                    present.add(name)
                    break
        # Попарные комбинации
        present_list = list(present)
        for i in range(len(present_list)):
            for j in range(i + 1, len(present_list)):
                pair = tuple(sorted([present_list[i], present_list[j]]))
                cooccur[pair] += 1

    max_co = max(cooccur.values()) if cooccur else 1
    relationships = []
    for (name1, name2), count in cooccur.items():
        if count >= cooccurrence_threshold:
            rel = Relationship(
                from_=name1,
                to=name2,
                type="associated_with",
                strength=round(count / max_co, 3)
            )
            relationships.append(rel)
    return relationships