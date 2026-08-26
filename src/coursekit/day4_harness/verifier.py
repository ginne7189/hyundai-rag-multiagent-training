import re
from pathlib import Path

from coursekit.documents import load_documents
from coursekit.models import RAGAnswer, VerificationResult


def _content_tokens(text: str) -> set[str]:
    tokens = re.findall(r"[가-힣A-Za-z0-9]{2,}", text.lower())
    stop = {"합니다", "있습니다", "그리고", "대한", "해당", "사용", "차량"}
    return {token for token in tokens if token not in stop}


class EvidenceVerifier:
    """Reject missing, outdated, or unsupported evidence before final output."""

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
