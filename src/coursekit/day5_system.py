import json
import time
from pathlib import Path

from coursekit.day3_agent import AgentHarness
from coursekit.day4_multiagent import SearchAndVerifySystem
from coursekit.models import EvaluationCaseResult, EvaluationSummary, FinalResult
from coursekit.providers import CourseProvider, get_provider


class OperationalSystem:
    def __init__(self, provider: CourseProvider | None = None):
        self.provider = provider or get_provider()
        self.agent = AgentHarness(provider=self.provider)
        self.multiagent = SearchAndVerifySystem(provider=self.provider)

    def run(self, question: str, approval: str | None = None) -> FinalResult:
        started = time.perf_counter()
        trace = [f"request={question}"]
        tool_name = self.provider.choose_tool(question, list(self.agent.tools))
        trace.append(f"route_tool={tool_name}")

        if any(action in question for action in self.agent.blocked_actions):
            trace.append("risk=high")
            if approval is None:
                return self._result(
                    "사람의 승인·수정·거부가 필요합니다.",
                    "human_review",
                    started,
                    trace + ["hitl=pending"],
                    needs_human_review=True,
                    approval_status="pending",
                )
            if approval == "approve":
                return self._result(
                    "승인이 기록되었습니다. 교육용 환경에서는 실제 변경 작업을 실행하지 않습니다.",
                    "approved_simulation",
                    started,
                    trace + ["hitl=approved", "side_effect=disabled"],
                    approval_status="approved",
                )
            return self._result(
                "요청이 거부되어 실행하지 않았습니다.",
                "rejected",
                started,
                trace + ["hitl=rejected"],
                approval_status="rejected",
            )

        if tool_name == "rag_search":
            result = self.multiagent.run(question)
            trace.extend(result.trace)
            return self._result(
                result.answer,
                result.status,
                started,
                trace,
                verifier=result.verification.verdict,
            )

        result = self.agent.run(question)
        trace.extend(result.trace)
        return self._result(result.answer, result.status, started, trace)

    @staticmethod
    def _result(
        answer: str,
        status: str,
        started: float,
        trace: list[str],
        needs_human_review: bool = False,
        approval_status: str | None = None,
        verifier: str = "not_used",
    ) -> FinalResult:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return FinalResult(
            answer=answer,
            status=status,
            needs_human_review=needs_human_review,
            approval_status=approval_status,
            metrics={"elapsed_ms": elapsed_ms, "trace_steps": len(trace), "verifier": verifier},
            trace=trace,
        )

    def evaluate(self, path: str | Path = "data/eval_cases.json") -> EvaluationSummary:
        cases = json.loads(Path(path).read_text(encoding="utf-8"))
        results: list[EvaluationCaseResult] = []
        for case in cases:
            result = self.run(case["question"])
            expected = case["expected_behavior"]
            passed = self._matches(expected, result.status)
            results.append(
                EvaluationCaseResult(
                    question=case["question"],
                    expected_behavior=expected,
                    actual_status=result.status,
                    passed=passed,
                )
            )
        passed_count = sum(case.passed for case in results)
        return EvaluationSummary(
            total=len(results),
            passed=passed_count,
            pass_rate=passed_count / len(results) if results else 0.0,
            cases=results,
        )

    @staticmethod
    def _matches(expected: str, actual: str) -> bool:
        accepted = {
            "answer": {"verified"},
            "refuse": {"blocked", "insufficient_evidence", "unsupported"},
            "tool": {"completed"},
            "human_review": {"human_review"},
        }
        return actual in accepted.get(expected, {expected})
