import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agents.character_analyzer import CharacterAnalyzerAgent

class MockLLM:
    def generate(self, prompt: str) -> str:
        return json.dumps({
            "role": "главный герой",
            "archetype": "герой",
            "traits": ["смелый", "решительный"],
            "description": "Молодой человек, ищущий смысл жизни.",
            "quote": "Я этого не забуду!"
        }, ensure_ascii=False)

def test_character_analyzer():
    sample_text = """
    Евгений Онегин был молодой повеса. Он устал от светской жизни и уехал в деревню.
    Там он познакомился с Владимиром Ленским, юным поэтом. Ленский представил Онегина
    семье Лариных. Татьяна Ларина влюбилась в Онегина и написала ему письмо.
    Онегин отверг её чувства. Позже на балу Онегин флиртовал с Ольгой, невестой Ленского.
    Ленский вызвал Онегина на дуэль. Онегин убил Ленского.
    """
    agent = CharacterAnalyzerAgent(llm_model=MockLLM(), min_mentions=2)
    result = agent.process({"full_text": sample_text})

    print("=== Результат Character Analyzer ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Проверки
    names = {c["name"] for c in result["characters"]}
    assert "Онегин" in names, "Онегин не найден в персонажах"
    assert "Ленский" in names, "Ленский не найден в персонажах"
    assert len(result["characters"]) == 2, f"Ожидалось 2 персонажа, получено {len(result['characters'])}"

    assert len(result["relationships"]) == 1
    rel = result["relationships"][0]
    assert {rel["from_"], rel["to"]} == {"Онегин", "Ленский"}

    print("✅ Все проверки пройдены!")

if __name__ == "__main__":
    test_character_analyzer()