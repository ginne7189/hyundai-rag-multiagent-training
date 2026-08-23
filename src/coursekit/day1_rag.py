from pathlib import Path

from coursekit.documents import load_documents
from coursekit.models import Citation, RAGAnswer
from coursekit.providers import CourseProvider, get_provider
from coursekit.vectorstore import InMemoryVectorStore


class RAGSystem:
    def __init__(self, provider: CourseProvider | None = None, document_dir: str | Path = "data/documents"):
        self.provider = provider or get_provider()
        self.chunks = load_documents(document_dir)
        self.store = InMemoryVectorStore(self.chunks, self.provider)

    def retrieve(self, question: str, top_k: int = 3):
        return self.store.search(question, top_k=top_k)

    def ask(self, question: str) -> RAGAnswer:
        trace = [f"question={question}", "retrieve"]
        hits = self.retrieve(question)
        relevant = [hit.chunk for hit in hits if self.provider.relevant(question, hit.chunk, hit.score)]
        trace.extend(f"hit={hit.chunk.document_id}:{hit.score:.3f}" for hit in hits)
        if not relevant:
            trace.append("status=insufficient_evidence")
            return RAGAnswer(
                answer="제공된 문서에서는 해당 내용을 확인할 수 없습니다.",
                status="insufficient_evidence",
                trace=trace,
            )
        answer = self.provider.answer(question, relevant)
        citations = [
            Citation(
                document=chunk.document,
                page=chunk.page,
                section=chunk.section,
                evidence=chunk.text,
                document_id=chunk.document_id,
            )
            for chunk in relevant
        ]
        trace.extend(["generate", f"citations={len(citations)}", "status=grounded"])
        return RAGAnswer(answer=answer, citations=citations, status="grounded", trace=trace)

