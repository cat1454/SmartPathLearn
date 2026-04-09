from __future__ import annotations

import re
import secrets
import unicodedata
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .contracts import (
    ActivityDetailResponse,
    ActivityRecordResponse,
    FeedbackRecordResponse,
    RawPayloadRequest,
    SourcePackRecordResponse,
    SubmissionRecordResponse,
    SubmissionRequest,
    ValidationResponse,
)
from .storage import JsonStore, RecordAlreadyExistsError
from .validation import (
    ValidationResult,
    validate_activity_authoring_text,
    validate_feedback_text,
    validate_source_pack_text,
)


def _slugify(*parts: str) -> str:
    text = "-".join(part for part in parts if part).strip().lower()
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", errors="ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return slug or "item"


def _generate_source_pack_id(payload: dict[str, Any]) -> str:
    slug = _slugify(payload.get("subject", ""), payload.get("lesson_title", ""), payload.get("chapter_title", ""))
    return f"sp_{slug}_{secrets.token_hex(3)}"


def _generate_activity_id(payload: dict[str, Any]) -> str:
    slug = _slugify(payload.get("activity_type", ""), payload.get("lesson_title", ""), payload.get("document_title", ""))
    return f"act_{slug}_{secrets.token_hex(3)}"


def _raise_validation_error(result: ValidationResult) -> None:
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=result.to_payload())


def _raise_conflict(message: str) -> None:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"message": message})


def _raise_not_found(entity: str, entity_id: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": f"Khong tim thay {entity} `{entity_id}`."})


def create_app(*, data_file: Path | None = None) -> FastAPI:
    store = JsonStore(data_file)
    repo_root = Path(__file__).resolve().parents[1]
    handoff_ui_dir = repo_root / "handoff_ui"
    app = FastAPI(
        title="AI Document Handoff API",
        version="0.1.0",
        summary="Backend V1 cho source_pack, activity_authoring va activity_feedback.",
    )

    app.mount("/handoff/assets", StaticFiles(directory=handoff_ui_dir), name="handoff-assets")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/source-packs/validate", response_model=ValidationResponse)
    def validate_source_pack(request: RawPayloadRequest) -> ValidationResponse:
        result = validate_source_pack_text(request.raw_text)
        return ValidationResponse(**result.to_payload())

    @app.post("/source-packs", response_model=SourcePackRecordResponse, status_code=status.HTTP_201_CREATED)
    def create_source_pack(request: RawPayloadRequest) -> SourcePackRecordResponse:
        result = validate_source_pack_text(request.raw_text)
        if not result.ok or result.normalized is None:
            _raise_validation_error(result)

        payload = dict(result.normalized)
        source_pack_id = payload.get("source_pack_ref") or _generate_source_pack_id(payload)
        payload["source_pack_ref"] = source_pack_id
        try:
            record = store.create_source_pack(source_pack_id, payload)
        except RecordAlreadyExistsError as exc:
            _raise_conflict(str(exc))
        return SourcePackRecordResponse(**record)

    @app.get("/source-packs/{source_pack_id}", response_model=SourcePackRecordResponse)
    def get_source_pack(source_pack_id: str) -> SourcePackRecordResponse:
        record = store.get_source_pack(source_pack_id)
        if record is None:
            _raise_not_found("source pack", source_pack_id)
        return SourcePackRecordResponse(**record)

    @app.post("/activities/validate", response_model=ValidationResponse)
    def validate_activity(request: RawPayloadRequest) -> ValidationResponse:
        result = validate_activity_authoring_text(request.raw_text, store)
        return ValidationResponse(**result.to_payload())

    @app.post("/activities", response_model=ActivityRecordResponse, status_code=status.HTTP_201_CREATED)
    def create_activity(request: RawPayloadRequest) -> ActivityRecordResponse:
        result = validate_activity_authoring_text(request.raw_text, store)
        if not result.ok or result.normalized is None:
            _raise_validation_error(result)

        payload = dict(result.normalized)
        activity_id = payload.get("activity_id") or _generate_activity_id(payload)
        payload["activity_id"] = activity_id
        try:
            record = store.create_activity(activity_id, payload["source_pack_ref"], payload)
        except RecordAlreadyExistsError as exc:
            _raise_conflict(str(exc))
        return ActivityRecordResponse(**record)

    @app.get("/activities/{activity_id}", response_model=ActivityDetailResponse)
    def get_activity(activity_id: str) -> ActivityDetailResponse:
        activity = store.get_activity(activity_id)
        if activity is None:
            _raise_not_found("activity", activity_id)
        submission = store.get_submission(activity_id)
        feedback = store.get_feedback(activity_id)
        return ActivityDetailResponse(
            activity=ActivityRecordResponse(**activity),
            submission=SubmissionRecordResponse(**submission) if submission else None,
            feedback=FeedbackRecordResponse(**feedback) if feedback else None,
        )

    @app.post("/activities/{activity_id}/submission", response_model=SubmissionRecordResponse)
    def save_submission(activity_id: str, request: SubmissionRequest) -> SubmissionRecordResponse:
        activity = store.get_activity(activity_id)
        if activity is None:
            _raise_not_found("activity", activity_id)
        record = store.upsert_submission(activity_id, request.model_dump())
        return SubmissionRecordResponse(**record)

    @app.post("/activities/{activity_id}/feedback/validate", response_model=ValidationResponse)
    def validate_feedback(activity_id: str, request: RawPayloadRequest) -> ValidationResponse:
        result = validate_feedback_text(request.raw_text, store, expected_activity_id=activity_id)
        return ValidationResponse(**result.to_payload())

    @app.post("/activities/{activity_id}/feedback", response_model=FeedbackRecordResponse)
    def save_feedback(activity_id: str, request: RawPayloadRequest) -> FeedbackRecordResponse:
        result = validate_feedback_text(request.raw_text, store, expected_activity_id=activity_id)
        if not result.ok or result.normalized is None:
            _raise_validation_error(result)

        payload = dict(result.normalized)
        if store.get_submission(activity_id) is None:
            store.upsert_submission(activity_id, payload["student_submission"])
        record = store.upsert_feedback(activity_id, payload)
        return FeedbackRecordResponse(**record)

    def serve_handoff_shell() -> FileResponse:
        return FileResponse(handoff_ui_dir / "index.html")

    @app.get("/handoff")
    def handoff_root() -> FileResponse:
        return serve_handoff_shell()

    @app.get("/handoff/source-packs/new")
    def handoff_source_pack_new() -> FileResponse:
        return serve_handoff_shell()

    @app.get("/handoff/source-packs/{source_pack_id}")
    def handoff_source_pack_detail(source_pack_id: str) -> FileResponse:
        return serve_handoff_shell()

    @app.get("/handoff/activities/new")
    def handoff_activity_new() -> FileResponse:
        return serve_handoff_shell()

    @app.get("/handoff/activities/{activity_id}")
    def handoff_activity_detail(activity_id: str) -> FileResponse:
        return serve_handoff_shell()

    @app.get("/handoff/activities/{activity_id}/submission")
    def handoff_activity_submission(activity_id: str) -> FileResponse:
        return serve_handoff_shell()

    @app.get("/handoff/activities/{activity_id}/feedback")
    def handoff_activity_feedback(activity_id: str) -> FileResponse:
        return serve_handoff_shell()

    return app


app = create_app()
