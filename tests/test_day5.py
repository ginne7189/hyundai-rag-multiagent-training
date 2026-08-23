from coursekit.day5_system import OperationalSystem
from coursekit.providers import MockProvider


def system() -> OperationalSystem:
    return OperationalSystem(provider=MockProvider())


def test_high_impact_action_requires_human_review() -> None:
    result = system().run("차량 ID 101의 제어 값을 변경해줘")
    assert result.status == "human_review"
    assert result.needs_human_review is True
    assert result.approval_status == "pending"


def test_approval_is_recorded_without_real_side_effect() -> None:
    result = system().run("차량 ID 101의 제어 값을 변경해줘", approval="approve")
    assert result.status == "approved_simulation"
    assert "side_effect=disabled" in result.trace


def test_final_evaluation_covers_all_behavior_types() -> None:
    summary = system().evaluate()
    assert summary.total == 4
    assert summary.passed == 4
    assert summary.pass_rate == 1.0

