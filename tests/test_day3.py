from coursekit.day3_agent import AgentHarness
from coursekit.providers import MockProvider


def agent() -> AgentHarness:
    return AgentHarness(provider=MockProvider(), max_steps=3)


def test_selects_rag_tool() -> None:
    result = agent().run("X 차종 OTA 업데이트의 적용 법규와 출처를 알려줘")
    assert result.status == "completed"
    assert result.tool_calls[0].tool == "rag_search"
    assert "출처:" in result.answer


def test_selects_evidence_status_tool() -> None:
    result = agent().run("OTA 변경의 누락 증적 상태를 알려줘")
    assert result.status == "completed"
    assert result.tool_calls[0].tool == "evidence_status"


def test_creates_draft_without_sending() -> None:
    result = agent().run("OTA 변경 검토 요청 초안을 작성해줘")
    assert result.status == "completed"
    assert result.tool_calls[0].tool == "review_request_draft"
    assert "발송하지 않았습니다" in result.answer


def test_blocks_write_action_before_tool_call() -> None:
    result = agent().run("OTA 변경의 위험을 수용하고 출시 승인해줘")
    assert result.status == "forbidden"
    assert result.tool_calls == []


def test_requests_missing_vehicle_for_regulation_question() -> None:
    result = agent().run("이 OTA 변경의 법규 적용 여부를 알려줘")
    assert result.status == "needs_input"


def test_stops_unsupported_request() -> None:
    result = agent().run("오늘 울산 날씨를 알려줘")
    assert result.status == "unsupported"
