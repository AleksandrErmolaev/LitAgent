from typing import List, Tuple

def collect_character_context(
    name: str,
    mentions: List[Tuple[int, int, str]],
    sentences: List[Tuple[int, int, str]],
    context_window: int = 2,
    max_context_chars: int = 2000
) -> str:
    """
    Собирает предложения вокруг всех упоминаний персонажа (по context_window с каждой стороны).
    Ограничивает общий объём до max_context_chars.
    """
    context_sents = set()
    for start_char, end_char, _ in mentions:
        # Найти индекс предложения, содержащего упоминание
        idx = None
        for i, (s_start, s_end, _) in enumerate(sentences):
            if s_start <= start_char <= s_end:
                idx = i
                break
        if idx is None:
            continue

        start_idx = max(0, idx - context_window)
        end_idx = min(len(sentences) - 1, idx + context_window)
        for j in range(start_idx, end_idx + 1):
            context_sents.add(sentences[j])

    # Сортировка по порядку в тексте
    sorted_sents = sorted(context_sents, key=lambda x: x[0])
    combined = " ".join(text for _, _, text in sorted_sents)

    if len(combined) > max_context_chars:
        truncated = ""
        length = 0
        for _, _, text in sorted_sents:
            if length + len(text) > max_context_chars:
                break
            truncated += text + " "
            length += len(text) + 1
        combined = truncated.strip()
    return combined