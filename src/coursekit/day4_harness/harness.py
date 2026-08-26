from pathlib import Path

from coursekit.config import load_roles, resolve_data_dir
from coursekit.day4_harness.orchestrator import MultiAgentOrchestrator
from coursekit.day4_harness.specialists import build_course_specialists
from coursekit.day4_harness.verifier import EvidenceVerifier
from coursekit.models import MultiAgentAnswer
from coursekit.providers import CourseProvider, get_provider


class MultiAgentHarness:
    """Prepare roles and boundaries, then expose one safe entry point."""

    def __init__(
        self,
        provider: CourseProvider | None = None,
        data_dir: str | Path | None = None,
    ):
        self.provider = provider or get_provider()
        self.data_dir = resolve_data_dir(data_dir)
        roles = load_roles(self.data_dir)
        self.primary_role = roles["primary_role"]
        self.secondary_role = roles["secondary_role"]
        self.specialists = build_course_specialists(
            self.provider,
            document_dir=self.data_dir / "documents",
            primary_role=self.primary_role,
            primary_document_ids=set(roles["primary_document_ids"]),
            secondary_role=self.secondary_role,
            secondary_document_ids=set(roles["secondary_document_ids"]),
        )
        self.verifier = EvidenceVerifier(self.data_dir / "documents")
        self.orchestrator = MultiAgentOrchestrator(self.specialists, self.verifier)

        # Compatibility names used by the existing Day 4/5 teaching code.
        self.regulation_agent = self.specialists[0].rag
        self.cybersecurity_agent = self.specialists[1].rag

    def run(self, question: str) -> MultiAgentAnswer:
        return self.orchestrator.run(question)


class SearchAndVerifySystem(MultiAgentHarness):
    """Backward-compatible course name for the Day 4 harness."""
