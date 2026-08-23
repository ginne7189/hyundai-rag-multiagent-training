import re
from pathlib import Path

from coursekit.day2_graph import AdaptiveRAG
from coursekit.documents import load_documents
from coursekit.models import MultiAgentAnswer, RAGAnswer, VerificationResult
from coursekit.providers import CourseProvider, get_provider


def _content_tokens(text: str) -> set[str]:
    tokens = re.findall(r"[가-힣A-Za-z0-9]{2,}", text.lower())
    stop = {"합니다", "있습니다", "그리고", "대한", "해당", "사용", "차량"}
    return {token for token in tokens if token not in stop}


class EvidenceVerifier:
    def __init__(self, document_dir: str | Path = "data/documents"):
        chunks = load_documents(document_dir)
        self.latest_versions: dict[str, int] = {}
        for chunk in chunks:
            self.latest_versions[chunk.document_id] = max(
                self.latest_versions.get(chunk.document_id, 0), chunk.version
            )

    def verify(self, question: str, draft: RAGAnswer) -> VerificationResult:
        issues: list[str] = []
        if draft.status != "grounded" or not draft.citations:
            issues.append("답변을 뒷받침하는 인용 근거가 없습니다.")
        for citation in draft.citations:
            latest = self.latest_versions.get(citation.document_id)
            if latest is None:
                issues.append(f"허용되지 않은 문서입니다: {citation.document_id}")
            elif citation.version != latest:
                issues.append(f"최신 승인 버전이 아닙니다: {citation.document_id}")
            if not citation.evidence.strip():
                issues.append(f"원문 근거가 비어 있습니다: {citation.document_id}")
        if draft.citations:
            evidence_tokens = _content_tokens(" ".join(c.evidence for c in draft.citations))
            answer_tokens = _content_tokens(draft.answer)
            if answer_tokens and len(answer_tokens & evidence_tokens) / len(answer_tokens) < 0.2:
                issues.append("답변의 주요 표현이 인용 근거에서 확인되지 않습니다.")
        if issues:
            action = "research_again" if draft.status != "grounded" else "human_review"
            return VerificationResult(verdict="reject", issues=issues, required_action=action)
        return VerificationResult(verdict="pass", issues=[], required_action="finalize")


class SearchAndVerifySystem:
    """법규와 사이버보안 근거 수집을 분리하고 검증 단계에서 합치는 구조."""

    def __init__(self, provider: CourseProvider | None = None):
        self.provider = provider or get_provider()
        self.regulation_agent = AdaptiveRAG(
            provider=self.provider, allowed_document_ids={"regulation-ota-v2"}
        )
        self.cybersecurity_agent = AdaptiveRAG(
            provider=self.provider,
            allowed_document_ids={"csms-change-v3", "cyber-req-v2", "evidence-register-v4"},
        )
        self.verifier = EvidenceVerifier()

    def run(self, question: str) -> MultiAgentAnswer:
        trace = ["agent=regulation:start", "agent=cybersecurity:start"]
        regulation = self.regulation_agent.ask(question)
        cybersecurity = self.cybersecurity_agent.ask(question)
        trace.extend(
            [
                f"agent=regulation:status={regulation.status}",
                *[f"regulation.{step}" for step in regulation.trace],
                f"agent=cybersecurity:status={cybersecurity.status}",
                *[f"cybersecurity.{step}" for step in cybersecurity.trace],
                "handoff=specialists_to_verifier",
            ]
        )

        grounded = [result for result in [regulation, cybersecurity] if result.status == "grounded"]
        combined = RAGAnswer(
            answer="\n\n".join(result.answer for result in grounded)
            or "제공된 문서에서는 해당 내용을 확인할 수 없습니다.",
            citations=[citation for result in grounded for citation in result.citations],
            status="grounded" if grounded else "insufficient_evidence",
            trace=[step for result in [regulation, cybersecurity] for step in result.trace],
        )
        verification = self.verifier.verify(question, combined)
        trace.append(f"agent=verifier:verdict={verification.verdict}")
        if verification.verdict == "pass":
            trace.append("route=finalize")
            return MultiAgentAnswer(
                answer=combined.answer,
                status="verified",
                search_result=combined,
                verification=verification,
                trace=trace,
            )
        trace.append(f"route={verification.required_action}")
        return MultiAgentAnswer(
            answer="검증을 통과하지 못해 답변을 제공하지 않습니다.",
            status="blocked",
            search_result=combined,
            verification=verification,
            trace=trace,
        )
