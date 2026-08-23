from coursekit.day2_graph import AdaptiveRAG
from coursekit.providers import MockProvider


def system(max_retries: int = 2) -> AdaptiveRAG:
    return AdaptiveRAG(provider=MockProvider(), max_retries=max_retries)


def test_direct_question_uses_short_path() -> None:
    result = system().ask("X 차종 OTA 업데이트 조건은 무엇인가요?")
    assert result.status == "grounded"
    assert not any(item.startswith("rewrite=") for item in result.trace)


def test_failed_query_is_rewritten_and_retried() -> None:
    result = system().ask("X 차종 원격 펌웨어 갱신 조건은?")
    assert result.status == "grounded"
    assert any(item.startswith("rewrite=") for item in result.trace)
    assert result.citations[0].document_id == "regulation-ota-v2"


def test_missing_evidence_stops_within_limit() -> None:
    result = system(max_retries=1).ask("엔진오일 교환 주기는 얼마인가요?")
    assert result.status == "insufficient_evidence"
    assert "stop=max_retries_or_no_evidence" in result.trace
    assert sum(item.startswith("retrieve(") for item in result.trace) == 2
