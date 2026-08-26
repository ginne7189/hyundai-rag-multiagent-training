from pydantic import BaseModel

from coursekit.models import RAGAnswer


class SpecialistHandoff(BaseModel):
    """A specialist's result in the shape expected by the orchestrator."""

    role: str
    result: RAGAnswer

    @property
    def is_grounded(self) -> bool:
        return self.result.status == "grounded" and bool(self.result.citations)


def validate_handoff(handoff: SpecialistHandoff) -> list[str]:
    """Return missing fields instead of letting an incomplete handoff pass silently."""

    missing: list[str] = []
    if not handoff.result.answer.strip():
        missing.append("answer")
    if handoff.result.status == "grounded" and not handoff.result.citations:
        missing.append("citations")
    if not handoff.result.trace:
        missing.append("trace")
    return missing
