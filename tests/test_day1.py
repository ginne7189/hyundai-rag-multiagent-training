from coursekit.day1_rag import RAGSystem
from coursekit.providers import MockProvider


def system() -> RAGSystem:
    return RAGSystem(provider=MockProvider())


def test_returns_grounded_answer_with_citation() -> None:
    result = system().ask("X 차종 OTA 업데이트에 필요한 조건과 출처는?")
    assert result.status == "grounded"
    assert result.citations
    citations = {citation.document_id: citation for citation in result.citations}
    assert "regulation-ota-v2" in citations
    assert citations["regulation-ota-v2"].version == 2
    assert result.citations[0].evidence


def test_refuses_when_evidence_is_missing() -> None:
    result = system().ask("엔진오일 교환 주기는 얼마인가요?")
    assert result.status == "insufficient_evidence"
    assert result.citations == []
