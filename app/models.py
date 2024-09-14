from dataclasses import dataclass
from typing import List

@dataclass
class Article:
    id: str
    title: str
    content: str
    published_at: str
    similarity_score: float = 0.0  # default value

@dataclass
class User:
    id: str
    request_count: int


