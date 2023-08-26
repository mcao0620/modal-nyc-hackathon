from dataclasses import dataclass
from typing import List


@dataclass
class CodeChunk:
    path: str
    chunk_contents: str
    embedding: List[List[float]]
