from coursekit.day1_rag import RAGSystem
from coursekit.providers import MockProvider


def system() -> RAGSystem:
    return RAGSystem(provider=MockProvider())


def test_returns_grounded_answer_with_citation() -> None:
    result = system().ask("회생제동 단계는 어떻게 조절하나요?")
    assert result.status == "grounded"
    assert result.citations
    assert result.citations[0].document_id == "ev-manual-v2"
    assert result.citations[0].page == 42
    assert result.citations[0].evidence


def test_refuses_when_evidence_is_missing() -> None:
    result = system().ask("엔진오일 교환 주기는 얼마인가요?")
    assert result.status == "insufficient_evidence"
    assert result.citations == []

