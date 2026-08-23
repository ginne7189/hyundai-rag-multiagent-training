from collections.abc import Callable
from dataclasses import dataclass

from coursekit.day2_graph import AdaptiveRAG
from coursekit.documents import load_documents
from coursekit.models import AgentAnswer, ToolCallRecord
from coursekit.policies import CoursePolicy, load_policy
from coursekit.providers import CourseProvider, get_provider


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    handler: Callable[[str], tuple[str, str]]
    permission: str = "read"


class AgentHarness:
    """모델의 판단을 Tool 계약, 정책, 실행 한도와 Trace로 감싸는 교육용 Harness."""

    def __init__(self, provider: CourseProvider | None = None, max_steps: int | None = None):
        self.provider = provider or get_provider()
        self.policy: CoursePolicy = load_policy()
        self.max_steps = max_steps or self.policy.max_tool_calls
        self.rag = AdaptiveRAG(provider=self.provider, max_retries=self.policy.max_retries)
        self.documents = load_documents("data/documents")
        self.tools = {
            "rag_search": ToolSpec(
                "rag_search",
                "승인된 법규·CSMS·TARA 문서에서 근거와 출처를 검색한다.",
                self._rag_search,
            ),
            "evidence_status": ToolSpec(
                "evidence_status",
                "현재 증적의 완료·누락 상태를 읽기 전용으로 조회한다.",
                self._evidence_status,
            ),
            "version_compare": ToolSpec(
                "version_compare",
                "문서 ID별 최신 승인 버전을 비교한다.",
                self._version_compare,
            ),
            "review_request_draft": ToolSpec(
                "review_request_draft",
                "사람이 검토할 요청 문안만 작성하며 전송하지 않는다.",
                self._review_request_draft,
                permission="draft_only",
            ),
        }

    def validate_request(self, question: str) -> tuple[str, str] | None:
        if "99조" in question or "99항" in question:
            return "존재 여부를 확인할 수 없는 조항은 답변하지 않습니다.", "unsupported_claim"
        if any(term in question for term in ["법규", "적용 여부"]) and not any(
            term in question for term in ["X 차종", "X차종", "차종 X"]
        ):
            return "법규 적용 판단을 위해 차종을 입력해 주세요.", "needs_input"
        return None

    def classify_action(self, question: str) -> str:
        if any(action in question for action in self.policy.prohibited_actions):
            return "forbidden"
        if any(action in question for action in self.policy.approval_actions):
            return "human_review"
        if any(word in question for word in ["충돌", "판단 불일치"]):
            return "human_review"
        return "read_only"

    def _rag_search(self, question: str) -> tuple[str, str]:
        result = self.rag.ask(question)
        citations = ", ".join(f"{c.document} v{c.version} p.{c.page}" for c in result.citations)
        text = result.answer + (f"\n출처: {citations}" if citations else "")
        return text, result.status

    @staticmethod
    def _evidence_status(question: str) -> tuple[str, str]:
        return (
            (
                "완료: 공급사 서명 증적, 보안 검증 결과. "
                "누락: 변경 후 재검증 결과, 요구사항-시험 추적성 연결."
            ),
            "ok",
        )

    def _version_compare(self, question: str) -> tuple[str, str]:
        latest: dict[str, int] = {}
        for chunk in self.documents:
            latest[chunk.document_id] = max(latest.get(chunk.document_id, 0), chunk.version)
        summary = ", ".join(f"{doc_id}=v{version}" for doc_id, version in sorted(latest.items()))
        return f"현재 승인 문서 버전: {summary}", "ok"

    @staticmethod
    def _review_request_draft(question: str) -> tuple[str, str]:
        return (
            (
                "[검토 요청 초안]\n대상: OTA 변경 검토 담당자\n"
                f"요청 내용: {question}\n확인 필요: 적용 법규, TARA 영향, 누락 증적\n"
                "※ 초안만 생성했으며 발송하지 않았습니다."
            ),
            "ok",
        )

    def run(self, question: str) -> AgentAnswer:
        trace = [f"goal={question}", f"max_steps={self.max_steps}", "validate_request"]
        validation = self.validate_request(question)
        if validation:
            answer, status = validation
            return AgentAnswer(answer=answer, status=status, trace=trace + [f"stop={status}"])

        risk = self.classify_action(question)
        trace.append(f"action_class={risk}")
        if risk == "forbidden":
            return AgentAnswer(
                answer="위험 수용·출시 승인·법규 상태 변경은 Agent가 실행할 수 없습니다.",
                status="forbidden",
                trace=trace + ["stop=policy_denied"],
            )
        if risk == "human_review":
            return AgentAnswer(
                answer="고영향 작업 또는 충돌 판단은 사람의 검토가 필요합니다.",
                status="human_review",
                trace=trace + ["stop=human_review"],
            )

        tool_name = self.provider.choose_tool(question, list(self.tools))
        trace.append(f"selected_tool={tool_name}")
        if tool_name not in self.tools:
            return AgentAnswer(
                answer="현재 제공된 도구로 처리할 수 없는 요청입니다.",
                status="unsupported",
                trace=trace + ["stop=unsupported"],
            )

        tool = self.tools[tool_name]
        output, output_status = tool.handler(question)
        record = ToolCallRecord(tool=tool.name, input={"question": question}, output_status=output_status)
        trace.extend([f"tool_permission={tool.permission}", f"tool_status={output_status}", "stop=completed"])
        return AgentAnswer(
            answer=output,
            status="completed" if output_status in {"ok", "grounded"} else output_status,
            tool_calls=[record],
            trace=trace,
        )
