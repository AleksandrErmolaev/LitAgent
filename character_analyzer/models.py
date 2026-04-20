from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Character:
    name: str
    role: str
    archetype: str
    traits: List[str]
    description: str
    mentions_count: int
    quote: str

    def to_dict(self):
        return asdict(self)

@dataclass
class Relationship:
    from_: str
    to: str
    type: str
    strength: float

    def to_dict(self):
        return asdict(self)