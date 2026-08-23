import hashlib
import math
import os
import re
from abc import ABC, abstractmethod

from dotenv import load_dotenv

from coursekit.documents import DocumentChunk

load_dotenv()


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[가-힣A-Za-z0-9]+", text.lower())
    grams: list[str] = []
    for word in words:
        grams.append(word)
        if len(word) >= 3:
            grams.extend(word[i : i + 3] for i in range(len(word) - 2))
    return grams


class CourseProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def relevant(self, question: str, chunk: DocumentChunk, score: float) -> bool: ...

    @abstractmethod
    def answer(self, question: str, chunks: list[DocumentChunk]) -> str: ...

    def rewrite(self, question: str, attempt: int) -> str:
        return question

    def choose_tool(self, question: str, tool_names: list[str]) -> str:
        return "unsupported"


class MockProvider(CourseProvider):
    dimension = 384

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimension
            for token in _tokens(text):
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dimension
                vector[index] += 1.0
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors

    def relevant(self, question: str, chunk: DocumentChunk, score: float) -> bool:
        query = set(_tokens(question))
        content = set(_tokens(f"{chunk.section} {chunk.text}"))
        return score >= 0.08 and bool(query & content)

    def answer(self, question: str, chunks: list[DocumentChunk]) -> str:
        if not chunks:
            return "제공된 문서에서는 해당 내용을 확인할 수 없습니다."
        sentences = re.split(r"(?<=[.!?다요])\s+", chunks[0].text)
        return " ".join(sentences[:2]).strip()

    def rewrite(self, question: str, attempt: int) -> str:
        replacements = {
            "브레이크 에너지 회수": "회생제동",
            "세기": "단계",
            "바꾸는": "조절하는",
            "공기 넣기": "타이어 공기압 보충",
        }
        rewritten = question
        for source, target in replacements.items():
            rewritten = rewritten.replace(source, target)
        return rewritten

    def choose_tool(self, question: str, tool_names: list[str]) -> str:
        if any(word in question for word in ["차량 ID", "점검 상태", "상태 조회"]):
            return "vehicle_status"
        if any(word in question for word in ["계산", "합계", "균등", "나누"]):
            return "calculator"
        if any(word in question for word in ["방법", "절차", "문서", "출처", "회생", "충전", "타이어"]):
            return "rag_search"
        return "unsupported"


class OpenAIProvider(CourseProvider):
    def __init__(self) -> None:
        from openai import OpenAI

        self.client = OpenAI()
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.embedding_model, input=texts)
        return [item.embedding for item in response.data]

    def _text(self, instructions: str, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=prompt,
            store=False,
            text={"verbosity": "low"},
        )
        return response.output_text.strip()

    def relevant(self, question: str, chunk: DocumentChunk, score: float) -> bool:
        result = self._text(
            "질문에 답할 직접 근거가 문서에 있으면 YES, 없으면 NO만 출력한다.",
            f"질문: {question}\n문서: {chunk.text}",
        )
        return result.upper().startswith("YES")

    def answer(self, question: str, chunks: list[DocumentChunk]) -> str:
        context = "\n\n".join(f"[{c.document} p.{c.page}] {c.text}" for c in chunks)
        return self._text(
            "제공된 문서 근거만 사용해 한국어로 간결하게 답한다. 근거 밖의 내용을 추가하지 않는다.",
            f"질문: {question}\n\n문서 근거:\n{context}",
        )

    def rewrite(self, question: str, attempt: int) -> str:
        return self._text(
            "원래 의미와 조건을 유지하면서 문서 검색에 적합한 한국어 검색어 한 줄만 출력한다.",
            f"원래 질문: {question}\n재시도 횟수: {attempt}",
        )

    def choose_tool(self, question: str, tool_names: list[str]) -> str:
        result = self._text(
            "허용된 Tool 중 하나만 선택한다. 적절한 Tool이 없으면 unsupported를 출력한다.",
            f"요청: {question}\n허용 Tool: {', '.join(tool_names)}",
        )
        return result.strip() if result.strip() in tool_names else "unsupported"


def get_provider() -> CourseProvider:
    mode = os.getenv("COURSE_MODE", "mock").lower()
    if mode == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("COURSE_MODE=openai requires OPENAI_API_KEY")
        return OpenAIProvider()
    return MockProvider()
