from coursekit.day1_rag import RAGSystem
from coursekit.day5_system import OperationalSystem
from coursekit.project import validate_day1_project, validate_project
from coursekit.providers import MockProvider

PROJECT_DIR = "projects/template"


def test_project_template_is_valid() -> None:
    result = validate_project(PROJECT_DIR)
    assert result["valid"] is True
    assert result["document_count"] == 2
    assert result["evaluation_case_count"] == 5


def test_day1_project_check_only_requires_brief_and_documents() -> None:
    result = validate_day1_project(PROJECT_DIR)
    assert result["valid"] is True
    assert result["document_count"] == 2
    assert "evaluation_case_count" not in result


def test_project_documents_run_without_changing_course_data() -> None:
    result = RAGSystem(
        provider=MockProvider(), document_dir=f"{PROJECT_DIR}/documents"
    ).ask("프로젝트 A의 변경 영향평가 절차와 출처는?")
    assert result.status == "grounded"
    assert "change-process-v1" in {citation.document_id for citation in result.citations}


def test_project_evaluation_runs_from_its_own_directory() -> None:
    result = OperationalSystem(provider=MockProvider(), data_dir=PROJECT_DIR).evaluate()
    assert result.total == 5
    assert result.passed == 5
