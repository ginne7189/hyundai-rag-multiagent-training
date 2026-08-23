from pydantic import BaseModel, Field


class Citation(BaseModel):
    document: str
    page: int
    section: str
    evidence: str
    document_id: str


class RAGAnswer(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    status: str
    trace: list[str] = Field(default_factory=list)


class ToolCallRecord(BaseModel):
    tool: str
    input: dict
    output_status: str


class AgentAnswer(BaseModel):
    answer: str
    status: str
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    trace: list[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    verdict: str
    issues: list[str] = Field(default_factory=list)
    required_action: str

