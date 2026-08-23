from dataclasses import dataclass

import numpy as np

from coursekit.documents import DocumentChunk
from coursekit.providers import CourseProvider


@dataclass(frozen=True)
class SearchHit:
    chunk: DocumentChunk
    score: float


class InMemoryVectorStore:
    def __init__(self, chunks: list[DocumentChunk], provider: CourseProvider):
        self.chunks = chunks
        self.provider = provider
        self.vectors = np.asarray(
            provider.embed(
                [
                    f"{chunk.document} {chunk.section} {chunk.text} {chunk.market or ''} "
                    f"{chunk.vehicle or ''} {chunk.status or ''}"
                    for chunk in chunks
                ]
            ),
            dtype=float,
        )

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        query_vector = np.asarray(self.provider.embed([query])[0], dtype=float)
        scores = self.vectors @ query_vector
        indices = np.argsort(scores)[::-1][:top_k]
        return [SearchHit(self.chunks[index], float(scores[index])) for index in indices]
