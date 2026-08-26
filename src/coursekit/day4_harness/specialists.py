from pathlib import Path

from coursekit.day2_graph import AdaptiveRAG
from coursekit.day4_harness.contracts import SpecialistHandoff
from coursekit.providers import CourseProvider


class SpecialistAgent:
    """Search only the document collection assigned to one specialist role."""

    def __init__(
        self,
        *,
        name: str,
        allowed_document_ids: set[str],
        provider: CourseProvider,
        document_dir: str | Path = "data/documents",
    ):
        self.name = name
        self.rag = AdaptiveRAG(
            provider=provider,
            document_dir=document_dir,
            allowed_document_ids=allowed_document_ids,
        )

    def run(self, question: str) -> SpecialistHandoff:
        return SpecialistHandoff(role=self.name, result=self.rag.ask(question))


def build_course_specialists(
    provider: CourseProvider,
    *,
    document_dir: str | Path = "data/documents",
    primary_role: str = "regulation",
    primary_document_ids: set[str] | None = None,
    secondary_role: str = "cybersecurity",
    secondary_document_ids: set[str] | None = None,
) -> list[SpecialistAgent]:
    return [
        SpecialistAgent(
            name=primary_role,
            provider=provider,
            document_dir=document_dir,
            allowed_document_ids=primary_document_ids or {"regulation-ota-v2"},
        ),
        SpecialistAgent(
            name=secondary_role,
            provider=provider,
            document_dir=document_dir,
            allowed_document_ids=secondary_document_ids
            or {
                "csms-change-v3",
                "cyber-req-v2",
                "evidence-register-v4",
            },
        ),
    ]
