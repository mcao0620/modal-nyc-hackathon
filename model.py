from dataclasses import dataclass
from typing import List


@dataclass
class CodeDocument:
    path: str
    file_contents: str
    embedding: List[List[float]]
