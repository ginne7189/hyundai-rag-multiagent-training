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
        self.allowed_document_ids = {chunk.document_id for chunk in chunks}

    def verify(self, question: str, draft: RAGAnswer) -> VerificationResult:
        issues: list[str] = []
        if draft.status != "grounded" or not draft.citations:
            issues.append("답변을 뒷받침하는 인용 근거가 없습니다.")
        for citation in draft.citations:
            if citation.document_id not in self.allowed_document_ids:
                issues.append(f"허용되지 않거나 오래된 문서입니다: {citation.document_id}")
            if not citation.evidence.strip():
                issues.append(f"원문 근거가 비어 있습니다: {citation.document_id}")
        if draft.citations:
            evidence_tokens = _content_tokens(" ".join(c.evidence for c in draft.citations))
            answer_tokens = _content_tokens(draft.answer)
            if answer_tokens and len(answer_tokens & evidence_tokens) / len(answer_tokens) < 0.25:
                issues.append("답변의 주요 표현이 인용 근거에서 확인되지 않습니다.")
        if issues:
            action = "research_again" if draft.status != "grounded" else "stop"
            return VerificationResult(verdict="reject", issues=issues, required_action=action)
        return VerificationResult(verdict="pass", issues=[], required_action="finalize")


class SearchAndVerifySystem:
    def __init__(self, provider: CourseProvider | None = None):
        self.provider = provider or get_provider()
        self.search_agent = AdaptiveRAG(provider=self.provider)
        self.verifier = EvidenceVerifier()

    def run(self, question: str) -> MultiAgentAnswer:
        trace = ["agent=search:start"]
        draft = self.search_agent.ask(question)
        trace.extend([f"agent=search:status={draft.status}", "handoff=search_to_verifier"])
        verification = self.verifier.verify(question, draft)
        trace.append(f"agent=verifier:verdict={verification.verdict}")
        if verification.verdict == "pass":
            trace.append("route=finalize")
            return MultiAgentAnswer(
                answer=draft.answer,
                status="verified",
                search_result=draft,
                verification=verification,
                trace=trace,
            )
        trace.append(f"route={verification.required_action}")
        return MultiAgentAnswer(
            answer="검증을 통과하지 못해 답변을 제공하지 않습니다.",
            status="blocked",
            search_result=draft,
            verification=verification,
            trace=trace,
        )

