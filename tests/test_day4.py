from coursekit.day4_multiagent import EvidenceVerifier, SearchAndVerifySystem
from coursekit.models import Citation, RAGAnswer
from coursekit.providers import MockProvider


def test_valid_search_answer_passes_independent_verifier() -> None:
    result = SearchAndVerifySystem(provider=MockProvider()).run("회생제동 단계 변경 방법과 출처를 알려줘")
    assert result.status == "verified"
    assert result.verification.verdict == "pass"
    assert "handoff=search_to_verifier" in result.trace


def test_nonexistent_or_old_source_is_rejected() -> None:
    draft = RAGAnswer(
        answer="패들 시프트로 회생제동 단계를 조절합니다.",
        status="grounded",
        citations=[
            Citation(
                document="전기차 사용자 안내서",
                page=42,
                section="회생제동 시스템",
                evidence="패들 시프트로 회생제동 단계를 조절합니다.",
                document_id="ev-manual-v1",
            )
        ],
    )
    result = EvidenceVerifier().verify("회생제동 단계는?", draft)
    assert result.verdict == "reject"
    assert any("오래된" in issue for issue in result.issues)


def test_unsupported_claim_is_rejected() -> None:
    draft = RAGAnswer(
        answer="배터리를 즉시 교체해야 합니다.",
        status="grounded",
        citations=[
            Citation(
                document="전기차 사용자 안내서",
                page=42,
                section="회생제동 시스템",
                evidence="패들 시프트로 회생제동 단계를 조절할 수 있습니다.",
                document_id="ev-manual-v2",
            )
        ],
    )
    result = EvidenceVerifier().verify("회생제동 단계는?", draft)
    assert result.verdict == "reject"
    assert any("주요 표현" in issue for issue in result.issues)

