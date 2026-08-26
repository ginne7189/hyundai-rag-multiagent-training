from coursekit.day4_harness.contracts import SpecialistHandoff, validate_handoff
from coursekit.day4_harness.specialists import SpecialistAgent
from coursekit.day4_harness.verifier import EvidenceVerifier
from coursekit.models import MultiAgentAnswer, RAGAnswer


class MultiAgentOrchestrator:
    """Run assigned roles, combine their handoffs, and route the verified result."""

    def __init__(self, specialists: list[SpecialistAgent], verifier: EvidenceVerifier):
        self.specialists = specialists
        self.verifier = verifier

    def run(self, question: str) -> MultiAgentAnswer:
        trace = ["orchestrator=start"]
        handoffs: list[SpecialistHandoff] = []

        # The course baseline is deliberately sequential. Parallel execution is
        # an extension only after learners can explain the same handoff contract.
        for specialist in self.specialists:
            trace.append(f"agent={specialist.name}:start")
            handoff = specialist.run(question)
            missing = validate_handoff(handoff)
            trace.append(f"agent={specialist.name}:status={handoff.result.status}")
            trace.extend(f"{specialist.name}.{step}" for step in handoff.result.trace)
            if missing:
                trace.append(f"handoff={specialist.name}:invalid:{','.join(missing)}")
            else:
                trace.append(f"handoff={specialist.name}:accepted")
                handoffs.append(handoff)

        trace.append("handoff=specialists_to_verifier")
        combined = self._combine(handoffs)
        verification = self.verifier.verify(question, combined)
        trace.append(f"agent=verifier:verdict={verification.verdict}")

        if verification.verdict == "pass":
            trace.extend(["route=finalize", "orchestrator=complete"])
            return MultiAgentAnswer(
                answer=combined.answer,
                status="verified",
                search_result=combined,
                verification=verification,
                trace=trace,
            )

        trace.extend([f"route={verification.required_action}", "orchestrator=blocked"])
        return MultiAgentAnswer(
            answer="검증을 통과하지 못해 답변을 제공하지 않습니다.",
            status="blocked",
            search_result=combined,
            verification=verification,
            trace=trace,
        )

    @staticmethod
    def _combine(handoffs: list[SpecialistHandoff]) -> RAGAnswer:
        grounded = [handoff.result for handoff in handoffs if handoff.is_grounded]
        return RAGAnswer(
            answer="\n\n".join(result.answer for result in grounded)
            or "제공된 문서에서는 해당 내용을 확인할 수 없습니다.",
            citations=[citation for result in grounded for citation in result.citations],
            status="grounded" if grounded else "insufficient_evidence",
            trace=[step for result in grounded for step in result.trace],
        )
