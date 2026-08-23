from coursekit.day3_agent import AgentHarness
from coursekit.providers import MockProvider


def agent() -> AgentHarness:
    return AgentHarness(provider=MockProvider(), max_steps=3)


def test_selects_rag_tool() -> None:
    result = agent().run("회생제동 단계 변경 방법과 출처를 알려줘")
    assert result.status == "completed"
    assert result.tool_calls[0].tool == "rag_search"
    assert "출처:" in result.answer


def test_selects_vehicle_status_tool() -> None:
    result = agent().run("차량 ID 101의 점검 상태를 알려줘")
    assert result.status == "completed"
    assert result.tool_calls[0].tool == "vehicle_status"


def test_selects_calculator() -> None:
    result = agent().run("부품 12개를 차량 3대에 균등하게 나눠줘")
    assert result.status == "completed"
    assert result.tool_calls[0].tool == "calculator"
    assert result.answer.endswith("4")


def test_blocks_write_action_before_tool_call() -> None:
    result = agent().run("차량 ID 101의 제어 값을 변경해줘")
    assert result.status == "human_review"
    assert result.tool_calls == []


def test_stops_unsupported_request() -> None:
    result = agent().run("오늘 울산 날씨를 알려줘")
    assert result.status == "unsupported"

