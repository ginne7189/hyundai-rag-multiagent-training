import re
from collections.abc import Callable
from dataclasses import dataclass

from coursekit.day2_graph import AdaptiveRAG
from coursekit.models import AgentAnswer, ToolCallRecord
from coursekit.providers import CourseProvider, get_provider


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    handler: Callable[[str], tuple[str, str]]
    permission: str = "read"


class AgentHarness:
    def __init__(self, provider: CourseProvider | None = None, max_steps: int = 3):
        self.provider = provider or get_provider()
        self.max_steps = max_steps
        self.rag = AdaptiveRAG(provider=self.provider)
        self.tools = {
            "rag_search": ToolSpec(
                "rag_search",
                "차량 매뉴얼·정비·품질 문서에서 근거와 출처를 검색한다.",
                self._rag_search,
            ),
            "vehicle_status": ToolSpec(
                "vehicle_status",
                "차량 ID의 읽기 전용 점검 상태를 조회한다. 값을 변경하지 않는다.",
                self._vehicle_status,
            ),
            "calculator": ToolSpec(
                "calculator",
                "수량의 합계·나눗셈 등 단순 계산을 수행한다.",
                self._calculator,
            ),
        }
        self.blocked_actions = (
            "값을 변경",
            "제어 값을",
            "문서를 삭제",
            "외부로 전송",
            "승인 없이",
        )

    def _rag_search(self, question: str) -> tuple[str, str]:
        result = self.rag.ask(question)
        citations = ", ".join(f"{c.document} p.{c.page}" for c in result.citations)
        text = result.answer + (f"\n출처: {citations}" if citations else "")
        return text, result.status

    @staticmethod
    def _vehicle_status(question: str) -> tuple[str, str]:
        match = re.search(r"(?:ID\s*)?(\d+)", question, re.IGNORECASE)
        vehicle_id = match.group(1) if match else "unknown"
        statuses = {
            "101": "정기 점검 완료 · 다음 점검 예정일 2026-09-15",
            "102": "점검 필요 · 타이어 공기압 확인 예정",
        }
        if vehicle_id not in statuses:
            return f"차량 ID {vehicle_id}의 상태를 찾을 수 없습니다.", "not_found"
        return f"차량 ID {vehicle_id}: {statuses[vehicle_id]}", "ok"

    @staticmethod
    def _calculator(question: str) -> tuple[str, str]:
        numbers = [float(value) for value in re.findall(r"\d+(?:\.\d+)?", question)]
        if len(numbers) < 2:
            return "계산에 필요한 숫자가 부족합니다.", "invalid_input"
        if any(word in question for word in ["균등", "나누", "대당"]):
            if numbers[1] == 0:
                return "0으로 나눌 수 없습니다.", "invalid_input"
            return f"계산 결과: {numbers[0] / numbers[1]:g}", "ok"
        return f"계산 결과: {sum(numbers):g}", "ok"

    def run(self, question: str) -> AgentAnswer:
        trace = [f"goal={question}", f"max_steps={self.max_steps}"]
        if any(action in question for action in self.blocked_actions):
            trace.append("blocked=write_or_high_impact_action")
            return AgentAnswer(
                answer="변경 또는 고영향 작업은 자동 실행하지 않습니다. 사람의 승인이 필요합니다.",
                status="human_review",
                trace=trace,
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
