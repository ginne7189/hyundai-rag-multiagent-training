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
        trace = [f"request={question}", "validate_request"]
        validation = self.agent.validate_request(question)
        if validation:
            answer, status = validation
            return self._result(answer, status, started, trace + [f"stop={status}"])

        action_class = self.agent.classify_action(question)
        trace.append(f"action_class={action_class}")
        if action_class == "forbidden":
            return self._result(
                "위험 수용·출시 승인·법규 상태 변경은 자동화 대상이 아닙니다.",
                "forbidden",
                started,
                trace + ["policy=deny"],
            )
        tool_name = self.provider.choose_tool(question, list(self.agent.tools))
        trace.append(f"route_tool={tool_name}")

        if action_class == "human_review":
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
                citations=result.search_result.citations,
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
        citations=None,
    ) -> FinalResult:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return FinalResult(
            answer=answer,
            status=status,
            needs_human_review=needs_human_review,
            approval_status=approval_status,
            metrics={"elapsed_ms": elapsed_ms, "trace_steps": len(trace), "verifier": verifier},
            citations=citations or [],
            trace=trace,
        )

    def evaluate(self, path: str | Path = "data/eval_cases.json") -> EvaluationSummary:
        cases = json.loads(Path(path).read_text(encoding="utf-8"))
        results: list[EvaluationCaseResult] = []
        for case in cases:
            result = self.run(case["question"])
            expected = case["expected_behavior"]
            expected_documents = case.get("expected_documents", [])
            actual_documents = sorted({citation.document_id for citation in result.citations})
            behavior_passed = self._matches(expected, result.status)
            documents_passed = all(doc in actual_documents for doc in expected_documents)
            expected_trace = case.get("expected_trace_contains")
            has_lifecycle_trace = bool(result.trace) and any(
                step.startswith(("route", "stop", "policy", "agent=")) for step in result.trace
            )
            trace_passed = has_lifecycle_trace and (
                expected_trace is None or any(expected_trace in step for step in result.trace)
            )
            passed = behavior_passed and documents_passed and trace_passed
            results.append(
                EvaluationCaseResult(
                    question=case["question"],
                    expected_behavior=expected,
                    actual_status=result.status,
                    expected_documents=expected_documents,
                    actual_documents=actual_documents,
                    behavior_passed=behavior_passed,
                    documents_passed=documents_passed,
                    trace_passed=trace_passed,
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
            "refuse": {"blocked", "insufficient_evidence", "unsupported", "unsupported_claim"},
            "tool": {"completed"},
            "human_review": {"human_review"},
            "needs_input": {"needs_input"},
            "forbidden": {"forbidden"},
        }
        return actual in accepted.get(expected, {expected})
