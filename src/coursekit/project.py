import json
from pathlib import Path

from coursekit.config import load_roles, resolve_data_dir
from coursekit.documents import load_documents
from coursekit.policies import load_policy


def validate_project(data_dir: str | Path | None = None) -> dict:
    project_dir = resolve_data_dir(data_dir)
    required = [
        project_dir / "project_brief.md",
        project_dir / "policies.json",
        project_dir / "roles.json",
        project_dir / "eval_cases.json",
        project_dir / "documents",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        return {"valid": False, "missing": missing, "errors": []}

    errors: list[str] = []
    try:
        documents = load_documents(project_dir / "documents")
    except (OSError, ValueError) as exc:  # 파일 위치와 원인을 함께 보여준다.
        documents = []
        errors.append(f"documents: {exc}")

    try:
        policy = load_policy(project_dir / "policies.json")
    except (OSError, ValueError) as exc:
        policy = None
        errors.append(f"policies.json: {exc}")

    try:
        roles = load_roles(project_dir)
    except (OSError, ValueError) as exc:
        roles = {}
        errors.append(f"roles.json: {exc}")

    try:
        cases = json.loads((project_dir / "eval_cases.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        cases = []
        errors.append(f"eval_cases.json: {exc}")

    document_ids = {chunk.document_id for chunk in documents}
    role_ids = set(roles.get("primary_document_ids", [])) | set(
        roles.get("secondary_document_ids", [])
    )
    unknown_role_ids = sorted(role_ids - document_ids)
    if unknown_role_ids:
        errors.append(f"roles.json에 존재하지 않는 문서 ID: {', '.join(unknown_role_ids)}")
    if len(document_ids) < 2:
        errors.append("서로 다른 document_id를 가진 문서가 2개 이상 필요합니다.")
    if len(cases) < 5:
        errors.append("정상·정보 부족·거절·사람 검토·금지 평가 Case가 최소 5개 필요합니다.")
    required_case_fields = {"question", "expected_behavior", "expected_documents"}
    for index, case in enumerate(cases, start=1):
        missing_fields = required_case_fields - set(case)
        if missing_fields:
            errors.append(f"평가 Case {index} 필드 누락: {', '.join(sorted(missing_fields))}")

    return {
        "valid": not errors,
        "project_dir": str(project_dir),
        "document_count": len(document_ids),
        "chunk_count": len(documents),
        "evaluation_case_count": len(cases),
        "max_retries": policy.max_retries if policy else None,
        "roles": {
            "primary": roles.get("primary_role"),
            "secondary": roles.get("secondary_role"),
        },
        "errors": errors,
    }
