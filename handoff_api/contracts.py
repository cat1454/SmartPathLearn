from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

ACTIVITY_TYPES = {
    "case_mission",
    "error_hunt",
    "explain_back",
    "mini_project",
    "debate_defend",
}

RESPONSE_TYPES = {
    "free_text",
    "bullet_points",
    "short_essay",
}

OVERALL_VERDICTS = {
    "strong",
    "partial",
    "needs_revision",
}


class RawPayloadRequest(BaseModel):
    raw_text: str = Field(min_length=1)

    @field_validator("raw_text")
    @classmethod
    def raw_text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("raw_text must not be blank")
        return value


class SubmissionRequest(BaseModel):
    response_type: Literal["free_text", "bullet_points", "short_essay"]
    response_content: str = Field(min_length=1)

    @field_validator("response_content")
    @classmethod
    def response_content_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("response_content must not be blank")
        return value.strip()


class ValidationIssueModel(BaseModel):
    code: str
    severity: Literal["error", "warning"]
    path: str
    message: str
    expected: str | None = None


class ValidationResponse(BaseModel):
    ok: bool
    marker: str | None = None
    normalized: dict[str, Any] | None = None
    issues: list[ValidationIssueModel] = Field(default_factory=list)


class SourcePackRecordResponse(BaseModel):
    id: str
    created_at: str
    updated_at: str
    payload: dict[str, Any]


class ActivityRecordResponse(BaseModel):
    id: str
    created_at: str
    updated_at: str
    source_pack_id: str
    payload: dict[str, Any]


class SubmissionRecordResponse(BaseModel):
    activity_id: str
    created_at: str
    updated_at: str
    submission: dict[str, Any]


class FeedbackRecordResponse(BaseModel):
    id: str
    created_at: str
    updated_at: str
    activity_id: str
    payload: dict[str, Any]


class ActivityDetailResponse(BaseModel):
    activity: ActivityRecordResponse
    submission: SubmissionRecordResponse | None = None
    feedback: FeedbackRecordResponse | None = None
