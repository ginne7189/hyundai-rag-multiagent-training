from pathlib import Path

from pydantic import BaseModel, Field


class CoursePolicy(BaseModel):
    max_retries: int = 2
    required_terms_for_regulation: list[str] = Field(default_factory=lambda: ["차종"])
    approval_actions: list[str] = Field(default_factory=list)
    prohibited_actions: list[str] = Field(default_factory=list)
    max_tool_calls: int = 3


def load_policy(path: str | Path = "data/policies.json") -> CoursePolicy:
    return CoursePolicy.model_validate_json(Path(path).read_text(encoding="utf-8"))
