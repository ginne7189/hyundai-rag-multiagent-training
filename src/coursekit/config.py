import json
import os
from pathlib import Path

DEFAULT_ROLES = {
    "primary_role": "regulation",
    "primary_document_ids": ["regulation-ota-v2"],
    "secondary_role": "cybersecurity",
    "secondary_document_ids": ["csms-change-v3", "cyber-req-v2", "evidence-register-v4"],
}


def resolve_data_dir(data_dir: str | Path | None = None) -> Path:
    return Path(data_dir or os.getenv("COURSE_DATA_DIR", "data"))


def load_roles(data_dir: str | Path) -> dict:
    path = Path(data_dir) / "roles.json"
    if not path.exists():
        return DEFAULT_ROLES.copy()
    configured = json.loads(path.read_text(encoding="utf-8"))
    return {**DEFAULT_ROLES, **configured}
