import json

from ..agent import CharacterAnalyzerAgent

class MockLLM:
    def generate(self, prompt: str) -> str:
        return json.dumps({
            "role": "protagonist",
            "archetype": "hero",
            "traits": ["brave", "intelligent"],
            "description": "A young man seeking adventure.",
            "quote": "I will not forget this!"
        })

def test_character_analyzer():
    sample_text = """
    Sherlock Holmes took his violin and began to play. Dr. Watson sat by the fire,
    watching his friend. "Watson, the game is afoot!" Holmes exclaimed suddenly.
    Watson nodded and reached for his revolver. Later, Inspector Lestrade arrived
    with news of a fresh crime. Holmes listened intently, while Watson took notes.
    Holmes and Watson visited the crime scene together. Watson was puzzled, but Holmes
    saw the clues everyone else missed. "Elementary, my dear Watson," said Holmes.
    """

    agent = CharacterAnalyzerAgent(llm_model=MockLLM(), min_mentions=2)
    result = agent.process({"full_text": sample_text})

    print("=== Character Analyzer Result ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    names = {c["name"] for c in result["characters"]}
    assert "Holmes" in names or "Sherlock" in names  # depending on NER
    assert "Watson" in names
    assert len(result["characters"]) >= 2
    assert len(result["relationships"]) > 0
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_character_analyzer()