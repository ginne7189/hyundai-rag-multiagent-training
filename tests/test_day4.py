from coursekit.day4_harness.contracts import SpecialistHandoff, validate_handoff
from coursekit.day4_multiagent import EvidenceVerifier, SearchAndVerifySystem
from coursekit.models import Citation, RAGAnswer
from coursekit.providers import MockProvider


def test_valid_search_answer_passes_independent_verifier() -> None:
    result = SearchAndVerifySystem(provider=MockProvider()).run(
        "X 차종 OTA 변경의 적용 법규와 사이버보안 증적을 알려줘"
    )
    assert result.status == "verified"
    assert result.verification.verdict == "pass"
    assert "handoff=specialists_to_verifier" in result.trace
    assert result.trace[0] == "orchestrator=start"
    assert result.trace[-1] == "orchestrator=complete"
    assert {"regulation-ota-v2", "cyber-req-v2"} & {
        citation.document_id for citation in result.search_result.citations
    }


def test_nonexistent_or_old_source_is_rejected() -> None:
    draft = RAGAnswer(
        answer="OTA 업데이트에는 무결성 검증이 필요합니다.",
        status="grounded",
        citations=[
            Citation(
                document="사이버보안 요구사항",
                page=3,
                section="업데이트 무결성",
                evidence="OTA 업데이트에는 무결성 검증이 필요합니다.",
                document_id="cyber-req-v2",
                version=1,
            )
        ],
    )
    result = EvidenceVerifier().verify("OTA 업데이트 조건은?", draft)
    assert result.verdict == "reject"
    assert any("최신 승인 버전" in issue for issue in result.issues)


def test_unsupported_claim_is_rejected() -> None:
    draft = RAGAnswer(
        answer="배터리를 즉시 교체해야 합니다.",
        status="grounded",
        citations=[
            Citation(
                document="사이버보안 요구사항",
                page=3,
                section="업데이트 무결성",
                evidence="서명과 무결성 검증 결과를 보존합니다.",
                document_id="cyber-req-v2",
                version=2,
            )
        ],
    )
    result = EvidenceVerifier().verify("OTA 업데이트 조건은?", draft)
    assert result.verdict == "reject"
    assert any("주요 표현" in issue for issue in result.issues)


def test_handoff_rejects_grounded_result_without_citations() -> None:
    handoff = SpecialistHandoff(
        role="regulation",
        result=RAGAnswer(answer="근거 없는 답변", status="grounded", citations=[], trace=["generate"]),
    )
    assert validate_handoff(handoff) == ["citations"]
