ARCHETYPES = [
    "hero", "anti-hero", "mentor", "trickster", "lover",
    "innocent", "ruler", "creator", "caregiver", "everyman"
]

def build_character_prompt(name: str, context: str) -> str:
    archetypes_str = ", ".join(ARCHETYPES)
    return f"""You are a literary analyst. Based on the provided context from a novel, describe the character "{name}".

Context (excerpts mentioning the character):
---
{context}
---

Respond strictly in JSON format with no extra commentary. Fields:
- "role": character's role in the story (e.g., "protagonist", "antagonist", "secondary", "minor").
- "archetype": one of the archetypes: {archetypes_str}. Choose the closest fit.
- "traits": list of 3-5 key personality traits (adjectives or short phrases).
- "description": a brief description of the character (2-3 sentences) based solely on the context.
- "quote": one most representative quote from the character in the context (direct speech or expressive phrase). If no direct speech, choose a phrase that best characterizes them.

JSON:"""
