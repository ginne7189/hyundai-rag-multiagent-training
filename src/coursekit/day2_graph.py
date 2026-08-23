from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from coursekit.day1_rag import RAGSystem
from coursekit.models import Citation, RAGAnswer
from coursekit.providers import CourseProvider, get_provider
from coursekit.vectorstore import SearchHit


class RAGState(TypedDict):
    original_question: str
    current_query: str
    hits: list[SearchHit]
    relevant_hits: list[SearchHit]
    relevance: str
    retry_count: int
    max_retries: int
    answer: RAGAnswer | None
    trace: list[str]


class AdaptiveRAG:
    def __init__(self, provider: CourseProvider | None = None, max_retries: int = 2):
        self.provider = provider or get_provider()
        self.rag = RAGSystem(provider=self.provider)
        self.max_retries = max_retries
        self.graph = self._build_graph()

    def _retrieve(self, state: RAGState) -> dict:
        hits = self.rag.retrieve(state["current_query"])
        return {
            "hits": hits,
            "trace": state["trace"]
            + [f"retrieve(query={state['current_query']})"]
            + [f"hit={hit.chunk.document_id}:{hit.score:.3f}" for hit in hits],
        }

    def _grade(self, state: RAGState) -> dict:
        relevant = [
            hit
            for hit in state["hits"]
            if self.provider.relevant(
                f"{state['original_question']} {state['current_query']}", hit.chunk, hit.score
            )
        ]
        relevance = "sufficient" if relevant else "insufficient"
        return {
            "relevant_hits": relevant,
            "relevance": relevance,
            "trace": state["trace"] + [f"grade={relevance}"],
        }

    @staticmethod
    def _route(state: RAGState) -> Literal["generate", "rewrite", "stop"]:
        if state["relevance"] == "sufficient":
            return "generate"
        if state["retry_count"] < state["max_retries"]:
            return "rewrite"
        return "stop"

    def _rewrite(self, state: RAGState) -> dict:
        attempt = state["retry_count"] + 1
        rewritten = self.provider.rewrite(state["current_query"], attempt)
        return {
            "current_query": rewritten,
            "retry_count": attempt,
            "trace": state["trace"] + [f"rewrite={rewritten}", f"retry_count={attempt}"],
        }

    def _generate(self, state: RAGState) -> dict:
        chunks = [hit.chunk for hit in state["relevant_hits"]]
        answer_text = self.provider.answer(state["original_question"], chunks)
        citations = [
            Citation(
                document=chunk.document,
                page=chunk.page,
                section=chunk.section,
                evidence=chunk.text,
                document_id=chunk.document_id,
            )
            for chunk in chunks
        ]
        trace = state["trace"] + ["generate", "status=grounded"]
        return {
            "answer": RAGAnswer(
                answer=answer_text, citations=citations, status="grounded", trace=trace
            ),
            "trace": trace,
        }

    @staticmethod
    def _stop(state: RAGState) -> dict:
        trace = state["trace"] + ["stop=max_retries_or_no_evidence"]
        return {
            "answer": RAGAnswer(
                answer="제공된 문서에서는 해당 내용을 확인할 수 없습니다.",
                status="insufficient_evidence",
                trace=trace,
            ),
            "trace": trace,
        }

    def _build_graph(self):
        builder = StateGraph(RAGState)
        builder.add_node("retrieve", self._retrieve)
        builder.add_node("grade", self._grade)
        builder.add_node("rewrite", self._rewrite)
        builder.add_node("generate", self._generate)
        builder.add_node("stop", self._stop)
        builder.add_edge(START, "retrieve")
        builder.add_edge("retrieve", "grade")
        builder.add_conditional_edges(
            "grade", self._route, {"generate": "generate", "rewrite": "rewrite", "stop": "stop"}
        )
        builder.add_edge("rewrite", "retrieve")
        builder.add_edge("generate", END)
        builder.add_edge("stop", END)
        return builder.compile()

    def ask(self, question: str) -> RAGAnswer:
        result = self.graph.invoke(
            {
                "original_question": question,
                "current_query": question,
                "hits": [],
                "relevant_hits": [],
                "relevance": "unknown",
                "retry_count": 0,
                "max_retries": self.max_retries,
                "answer": None,
                "trace": [f"question={question}"],
            },
            {"recursion_limit": 12},
        )
        return result["answer"]
