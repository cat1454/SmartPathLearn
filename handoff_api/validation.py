from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .contracts import ACTIVITY_TYPES, OVERALL_VERDICTS, RESPONSE_TYPES
from .storage import JsonStore

MARKER_PAIRS = {
    "SOURCE_PACK_V1": ("<<<SOURCE_PACK_V1_START>>>", "<<<SOURCE_PACK_V1_END>>>"),
    "ACTIVITY_PAYLOAD_V2": ("<<<ACTIVITY_PAYLOAD_V2_START>>>", "<<<ACTIVITY_PAYLOAD_V2_END>>>"),
    "ACTIVITY_FEEDBACK_V2": ("<<<ACTIVITY_FEEDBACK_V2_START>>>", "<<<ACTIVITY_FEEDBACK_V2_END>>>"),
}


@dataclass
class ValidationResult:
    ok: bool
    marker: str | None
    normalized: dict[str, Any] | None
    issues: list[dict[str, Any]]

    def to_payload(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "marker": self.marker,
            "normalized": self.normalized,
            "issues": self.issues,
        }


def _issue(
    code: str,
    severity: str,
    path: str,
    message: str,
    *,
    expected: str | None = None,
) -> dict[str, Any]:
    payload = {
        "code": code,
        "severity": severity,
        "path": path,
        "message": message,
    }
    if expected is not None:
        payload["expected"] = expected
    return payload


def _has_errors(issues: list[dict[str, Any]]) -> bool:
    return any(issue["severity"] == "error" for issue in issues)


def parse_marked_json(raw_text: str, marker: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    start_marker, end_marker = MARKER_PAIRS[marker]
    start_hits = [match.start() for match in re.finditer(re.escape(start_marker), raw_text)]
    end_hits = [match.start() for match in re.finditer(re.escape(end_marker), raw_text)]

    if len(start_hits) != 1 or len(end_hits) != 1:
        issues.append(
            _issue(
                "missing_marker",
                "error",
                "$",
                f"Payload phai co dung 1 cap marker {marker}.",
                expected=f"{start_marker} ... {end_marker}",
            )
        )
        return None, issues

    start_index = start_hits[0]
    end_index = end_hits[0]
    if start_index > end_index:
        issues.append(_issue("invalid_marker_pair", "error", "$", "Thu tu marker start/end khong hop le."))
        return None, issues

    prefix = raw_text[:start_index].strip()
    suffix = raw_text[end_index + len(end_marker) :].strip()
    if prefix or suffix:
        issues.append(_issue("text_outside_marker", "error", "$", "Khong duoc co text ngoai marker."))

    json_text = raw_text[start_index + len(start_marker) : end_index].strip()
    if not json_text:
        issues.append(_issue("json_parse_failed", "error", "$", "Khong tim thay JSON nam giua marker."))
        return None, issues

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        issues.append(_issue("json_parse_failed", "error", "$", f"JSON khong hop le: {exc.msg}."))
        return None, issues

    if not isinstance(data, dict):
        issues.append(_issue("invalid_field_type", "error", "$", "JSON root phai la object."))
        return None, issues

    return data, issues


def _warn_unknown_keys(data: dict[str, Any], allowed: set[str], issues: list[dict[str, Any]], path: str) -> None:
    for key in sorted(data.keys() - allowed):
        issues.append(_issue("unknown_field", "warning", f"{path}.{key}", f"Field `{key}` khong nam trong schema Wave 1."))


def _string_field(
    data: dict[str, Any],
    key: str,
    issues: list[dict[str, Any]],
    *,
    path: str,
    required: bool = True,
    allow_empty: bool = True,
    severity_if_empty: str = "warning",
) -> str | None:
    if key not in data:
        if required:
            issues.append(_issue("missing_required_field", "error", f"{path}.{key}", f"Thieu field `{key}`."))
        return None
    value = data[key]
    if not isinstance(value, str):
        issues.append(_issue("invalid_field_type", "error", f"{path}.{key}", f"`{key}` phai la string."))
        return None
    normalized = value.strip()
    if not normalized and not allow_empty:
        issues.append(_issue("empty_string", "error", f"{path}.{key}", f"`{key}` khong duoc rong."))
    elif not normalized:
        issues.append(_issue("empty_string", severity_if_empty, f"{path}.{key}", f"`{key}` dang rong."))
    return normalized


def _list_of_strings_field(
    data: dict[str, Any],
    key: str,
    issues: list[dict[str, Any]],
    *,
    path: str,
    required: bool = True,
    severity_if_empty: str = "warning",
) -> list[str] | None:
    if key not in data:
        if required:
            issues.append(_issue("missing_required_field", "error", f"{path}.{key}", f"Thieu field `{key}`."))
        return None
    value = data[key]
    if not isinstance(value, list):
        issues.append(_issue("invalid_field_type", "error", f"{path}.{key}", f"`{key}` phai la array string."))
        return None
    normalized: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            issues.append(
                _issue(
                    "invalid_field_type",
                    "error",
                    f"{path}.{key}[{index}]",
                    f"`{key}[{index}]` phai la string.",
                )
            )
            continue
        normalized.append(item.strip())
    if not normalized:
        issues.append(_issue("empty_array", severity_if_empty, f"{path}.{key}", f"`{key}` dang rong."))
    return normalized


def _int_field(
    data: dict[str, Any],
    key: str,
    issues: list[dict[str, Any]],
    *,
    path: str,
    required: bool = True,
) -> int | None:
    if key not in data:
        if required:
            issues.append(_issue("missing_required_field", "error", f"{path}.{key}", f"Thieu field `{key}`."))
        return None
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, int):
        issues.append(_issue("invalid_field_type", "error", f"{path}.{key}", f"`{key}` phai la integer."))
        return None
    return value


def _dict_field(
    data: dict[str, Any],
    key: str,
    issues: list[dict[str, Any]],
    *,
    path: str,
    required: bool = True,
) -> dict[str, Any] | None:
    if key not in data:
        if required:
            issues.append(_issue("missing_required_field", "error", f"{path}.{key}", f"Thieu field `{key}`."))
        return None
    value = data[key]
    if not isinstance(value, dict):
        issues.append(_issue("invalid_field_type", "error", f"{path}.{key}", f"`{key}` phai la object."))
        return None
    return value


def _generated_id_field(
    data: dict[str, Any],
    key: str,
    issues: list[dict[str, Any]],
    *,
    path: str,
) -> str | None:
    if key not in data:
        issues.append(_issue("missing_required_field", "error", f"{path}.{key}", f"Thieu field `{key}`."))
        return None
    value = data[key]
    if not isinstance(value, str):
        issues.append(_issue("invalid_field_type", "error", f"{path}.{key}", f"`{key}` phai la string."))
        return None
    return value.strip()


def _optional_reference_field(
    data: dict[str, Any],
    key: str,
    issues: list[dict[str, Any]],
    *,
    path: str,
) -> str | None:
    if key not in data:
        issues.append(_issue("missing_required_field", "error", f"{path}.{key}", f"Thieu field `{key}`."))
        return None
    value = data[key]
    if not isinstance(value, str):
        issues.append(_issue("invalid_field_type", "error", f"{path}.{key}", f"`{key}` phai la string."))
        return None
    return value.strip()


def validate_source_pack_text(raw_text: str) -> ValidationResult:
    marker = "SOURCE_PACK_V1"
    data, issues = parse_marked_json(raw_text, marker)
    if data is None:
        return ValidationResult(ok=False, marker=marker, normalized=None, issues=issues)

    allowed = {
        "payload_type",
        "source_pack_ref",
        "subject",
        "grade_level",
        "chapter_title",
        "lesson_title",
        "learning_objectives",
        "key_concepts",
        "formulas",
        "events_or_milestones",
        "examples",
        "common_mistakes",
        "prerequisites",
        "source_notes",
        "coverage_warning",
    }
    _warn_unknown_keys(data, allowed, issues, "$")

    payload_type = data.get("payload_type")
    if payload_type != "source_pack":
        issues.append(_issue("payload_type_invalid", "error", "$.payload_type", "`payload_type` phai la `source_pack`."))

    source_pack_ref = _optional_reference_field(data, "source_pack_ref", issues, path="$")

    subject = _string_field(data, "subject", issues, path="$")
    grade_level = _string_field(data, "grade_level", issues, path="$")
    chapter_title = _string_field(data, "chapter_title", issues, path="$")
    lesson_title = _string_field(data, "lesson_title", issues, path="$")
    learning_objectives = _list_of_strings_field(data, "learning_objectives", issues, path="$")
    key_concepts = _list_of_strings_field(data, "key_concepts", issues, path="$")
    formulas = _list_of_strings_field(data, "formulas", issues, path="$") or []
    events_or_milestones = _list_of_strings_field(data, "events_or_milestones", issues, path="$") or []
    examples = _list_of_strings_field(data, "examples", issues, path="$")
    common_mistakes = _list_of_strings_field(data, "common_mistakes", issues, path="$")
    prerequisites = _list_of_strings_field(data, "prerequisites", issues, path="$")
    source_notes = _list_of_strings_field(data, "source_notes", issues, path="$") or []
    coverage_warning = _string_field(data, "coverage_warning", issues, path="$")

    normalized = {
        "payload_type": "source_pack",
        "source_pack_ref": source_pack_ref if source_pack_ref else None,
        "subject": subject or "",
        "grade_level": grade_level or "",
        "chapter_title": chapter_title or "",
        "lesson_title": lesson_title or "",
        "learning_objectives": learning_objectives or [],
        "key_concepts": key_concepts or [],
        "formulas": formulas,
        "events_or_milestones": events_or_milestones,
        "examples": examples or [],
        "common_mistakes": common_mistakes or [],
        "prerequisites": prerequisites or [],
        "source_notes": source_notes,
        "coverage_warning": coverage_warning or "",
    }
    return ValidationResult(ok=not _has_errors(issues), marker=marker, normalized=normalized, issues=issues)


def _validate_case_mission(data: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, Any]:
    _warn_unknown_keys(data, {"scenario", "task", "expected_points", "success_criteria", "hint_optional"}, issues, "$.activity_data")
    return {
        "scenario": _string_field(data, "scenario", issues, path="$.activity_data") or "",
        "task": _string_field(data, "task", issues, path="$.activity_data", allow_empty=False, severity_if_empty="error") or "",
        "expected_points": _list_of_strings_field(data, "expected_points", issues, path="$.activity_data") or [],
        "success_criteria": _list_of_strings_field(data, "success_criteria", issues, path="$.activity_data") or [],
        "hint_optional": _string_field(data, "hint_optional", issues, path="$.activity_data", required=False) or "",
    }


def _validate_error_hunt(data: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, Any]:
    _warn_unknown_keys(data, {"artifact", "error_count_expected", "error_categories", "reference_points"}, issues, "$.activity_data")
    return {
        "artifact": _string_field(data, "artifact", issues, path="$.activity_data", allow_empty=False) or "",
        "error_count_expected": _int_field(data, "error_count_expected", issues, path="$.activity_data") or 0,
        "error_categories": _list_of_strings_field(data, "error_categories", issues, path="$.activity_data") or [],
        "reference_points": _list_of_strings_field(data, "reference_points", issues, path="$.activity_data") or [],
    }


def _validate_explain_back(data: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, Any]:
    _warn_unknown_keys(data, {"teaching_prompt", "target_audience", "expected_points", "clarity_rubric"}, issues, "$.activity_data")
    return {
        "teaching_prompt": _string_field(data, "teaching_prompt", issues, path="$.activity_data", allow_empty=False) or "",
        "target_audience": _string_field(data, "target_audience", issues, path="$.activity_data", allow_empty=False) or "",
        "expected_points": _list_of_strings_field(data, "expected_points", issues, path="$.activity_data") or [],
        "clarity_rubric": _list_of_strings_field(data, "clarity_rubric", issues, path="$.activity_data") or [],
    }


def _validate_mini_project(data: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, Any]:
    _warn_unknown_keys(data, {"brief", "deliverable_type", "constraints", "rubric"}, issues, "$.activity_data")
    return {
        "brief": _string_field(data, "brief", issues, path="$.activity_data", allow_empty=False) or "",
        "deliverable_type": _string_field(data, "deliverable_type", issues, path="$.activity_data", allow_empty=False) or "",
        "constraints": _list_of_strings_field(data, "constraints", issues, path="$.activity_data") or [],
        "rubric": _list_of_strings_field(data, "rubric", issues, path="$.activity_data") or [],
    }


def _validate_debate_defend(data: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, Any]:
    _warn_unknown_keys(data, {"claim", "position_task", "evidence_rules", "rubric"}, issues, "$.activity_data")
    return {
        "claim": _string_field(data, "claim", issues, path="$.activity_data", allow_empty=False) or "",
        "position_task": _string_field(data, "position_task", issues, path="$.activity_data", allow_empty=False) or "",
        "evidence_rules": _list_of_strings_field(data, "evidence_rules", issues, path="$.activity_data") or [],
        "rubric": _list_of_strings_field(data, "rubric", issues, path="$.activity_data") or [],
    }


ACTIVITY_DATA_VALIDATORS = {
    "case_mission": _validate_case_mission,
    "error_hunt": _validate_error_hunt,
    "explain_back": _validate_explain_back,
    "mini_project": _validate_mini_project,
    "debate_defend": _validate_debate_defend,
}


def validate_activity_authoring_text(raw_text: str, store: JsonStore) -> ValidationResult:
    marker = "ACTIVITY_PAYLOAD_V2"
    data, issues = parse_marked_json(raw_text, marker)
    if data is None:
        return ValidationResult(ok=False, marker=marker, normalized=None, issues=issues)

    allowed = {
        "payload_type",
        "activity_type",
        "activity_id",
        "source_pack_ref",
        "document_title",
        "lesson_title",
        "student_level",
        "instructions",
        "activity_data",
    }
    _warn_unknown_keys(data, allowed, issues, "$")

    payload_type = data.get("payload_type")
    if payload_type != "activity_authoring":
        issues.append(_issue("payload_type_invalid", "error", "$.payload_type", "`payload_type` phai la `activity_authoring`."))

    activity_type = _string_field(data, "activity_type", issues, path="$", allow_empty=False, severity_if_empty="error")
    if activity_type and activity_type not in ACTIVITY_TYPES:
        issues.append(_issue("activity_type_invalid", "error", "$.activity_type", "Wave 1 chi nhan 5 activity_type da chot."))

    activity_id = _generated_id_field(data, "activity_id", issues, path="$")
    source_pack_ref = _string_field(data, "source_pack_ref", issues, path="$", allow_empty=False, severity_if_empty="error")
    if source_pack_ref and not store.has_source_pack(source_pack_ref):
        issues.append(_issue("reference_not_found", "error", "$.source_pack_ref", f"Khong tim thay source pack `{source_pack_ref}`."))

    document_title = _string_field(data, "document_title", issues, path="$")
    lesson_title = _string_field(data, "lesson_title", issues, path="$")
    student_level = _string_field(data, "student_level", issues, path="$")
    instructions = _list_of_strings_field(data, "instructions", issues, path="$")
    activity_data = _dict_field(data, "activity_data", issues, path="$")

    normalized_activity_data: dict[str, Any] = {}
    if activity_type in ACTIVITY_DATA_VALIDATORS and activity_data is not None:
        normalized_activity_data = ACTIVITY_DATA_VALIDATORS[activity_type](activity_data, issues)
    elif activity_data is not None and activity_type:
        issues.append(_issue("activity_type_invalid", "error", "$.activity_type", f"Khong ho tro activity_type `{activity_type}`."))

    normalized = {
        "payload_type": "activity_authoring",
        "activity_type": activity_type or "",
        "activity_id": activity_id or None,
        "source_pack_ref": source_pack_ref or "",
        "document_title": document_title or "",
        "lesson_title": lesson_title or "",
        "student_level": student_level or "",
        "instructions": instructions or [],
        "activity_data": normalized_activity_data,
    }
    return ValidationResult(ok=not _has_errors(issues), marker=marker, normalized=normalized, issues=issues)


def _validate_feedback_addon(
    activity_type: str,
    feedback: dict[str, Any],
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    allowed = {
        "overall_verdict",
        "strengths",
        "gaps",
        "misconceptions",
        "next_step",
        "score_optional",
    }
    extras: dict[str, Any] = {}

    if activity_type == "case_mission":
        allowed |= {"missed_expected_points"}
        extras["missed_expected_points"] = _list_of_strings_field(
            feedback,
            "missed_expected_points",
            issues,
            path="$.feedback",
            required=False,
        ) or []
    elif activity_type == "error_hunt":
        allowed |= {"missed_errors", "false_positives"}
        extras["missed_errors"] = _list_of_strings_field(feedback, "missed_errors", issues, path="$.feedback", required=False) or []
        extras["false_positives"] = _list_of_strings_field(
            feedback,
            "false_positives",
            issues,
            path="$.feedback",
            required=False,
        ) or []
    elif activity_type == "explain_back":
        allowed |= {"missing_points", "clarity_notes"}
        extras["missing_points"] = _list_of_strings_field(feedback, "missing_points", issues, path="$.feedback", required=False) or []
        extras["clarity_notes"] = _list_of_strings_field(feedback, "clarity_notes", issues, path="$.feedback", required=False) or []
    elif activity_type == "mini_project":
        allowed |= {"rubric_breakdown"}
        rubric_breakdown = feedback.get("rubric_breakdown", [])
        if rubric_breakdown is None:
            rubric_breakdown = []
        if not isinstance(rubric_breakdown, list):
            issues.append(_issue("invalid_field_type", "error", "$.feedback.rubric_breakdown", "`rubric_breakdown` phai la array object."))
            extras["rubric_breakdown"] = []
        else:
            normalized_breakdown = []
            for index, item in enumerate(rubric_breakdown):
                if not isinstance(item, dict):
                    issues.append(
                        _issue(
                            "invalid_field_type",
                            "error",
                            f"$.feedback.rubric_breakdown[{index}]",
                            "Moi muc rubric_breakdown phai la object.",
                        )
                    )
                    continue
                normalized_breakdown.append(
                    {
                        "criterion": _string_field(item, "criterion", issues, path=f"$.feedback.rubric_breakdown[{index}]", allow_empty=False, severity_if_empty="error") or "",
                        "verdict": _string_field(item, "verdict", issues, path=f"$.feedback.rubric_breakdown[{index}]", allow_empty=False, severity_if_empty="error") or "",
                        "note": _string_field(item, "note", issues, path=f"$.feedback.rubric_breakdown[{index}]") or "",
                    }
                )
            extras["rubric_breakdown"] = normalized_breakdown
    elif activity_type == "debate_defend":
        allowed |= {"argument_quality", "evidence_quality", "logic_gaps"}
        extras["argument_quality"] = _string_field(feedback, "argument_quality", issues, path="$.feedback", required=False) or ""
        extras["evidence_quality"] = _string_field(feedback, "evidence_quality", issues, path="$.feedback", required=False) or ""
        extras["logic_gaps"] = _list_of_strings_field(feedback, "logic_gaps", issues, path="$.feedback", required=False) or []

    _warn_unknown_keys(feedback, allowed, issues, "$.feedback")
    return extras


def validate_feedback_text(raw_text: str, store: JsonStore, *, expected_activity_id: str | None = None) -> ValidationResult:
    marker = "ACTIVITY_FEEDBACK_V2"
    data, issues = parse_marked_json(raw_text, marker)
    if data is None:
        return ValidationResult(ok=False, marker=marker, normalized=None, issues=issues)

    allowed = {"payload_type", "activity_type", "activity_id", "student_submission", "feedback"}
    _warn_unknown_keys(data, allowed, issues, "$")

    payload_type = data.get("payload_type")
    if payload_type != "activity_feedback":
        issues.append(_issue("payload_type_invalid", "error", "$.payload_type", "`payload_type` phai la `activity_feedback`."))

    activity_type = _string_field(data, "activity_type", issues, path="$", allow_empty=False, severity_if_empty="error")
    if activity_type and activity_type not in ACTIVITY_TYPES:
        issues.append(_issue("activity_type_invalid", "error", "$.activity_type", "Wave 1 chi nhan 5 activity_type da chot."))

    activity_id = _string_field(data, "activity_id", issues, path="$", allow_empty=False, severity_if_empty="error")
    if expected_activity_id and activity_id and activity_id != expected_activity_id:
        issues.append(_issue("route_mismatch", "error", "$.activity_id", f"`activity_id` phai khop route `{expected_activity_id}`."))

    activity_record = store.get_activity(activity_id) if activity_id else None
    if activity_id and activity_record is None:
        issues.append(_issue("reference_not_found", "error", "$.activity_id", f"Khong tim thay activity `{activity_id}`."))
    if activity_record is not None and activity_type and activity_record["payload"]["activity_type"] != activity_type:
        issues.append(_issue("activity_type_invalid", "error", "$.activity_type", "activity_type trong feedback khong khop activity da luu."))

    submission = _dict_field(data, "student_submission", issues, path="$")
    normalized_submission = {"response_type": "", "response_content": ""}
    if submission is not None:
        response_type = _string_field(submission, "response_type", issues, path="$.student_submission", allow_empty=False, severity_if_empty="error")
        if response_type and response_type not in RESPONSE_TYPES:
            issues.append(_issue("response_type_invalid", "error", "$.student_submission.response_type", "Wave 1 chi nhan free_text, bullet_points, short_essay."))
        response_content = _string_field(
            submission,
            "response_content",
            issues,
            path="$.student_submission",
            allow_empty=False,
            severity_if_empty="error",
        )
        normalized_submission = {
            "response_type": response_type or "",
            "response_content": response_content or "",
        }
        _warn_unknown_keys(submission, {"response_type", "response_content"}, issues, "$.student_submission")

    feedback = _dict_field(data, "feedback", issues, path="$")
    normalized_feedback: dict[str, Any] = {
        "overall_verdict": "",
        "strengths": [],
        "gaps": [],
        "misconceptions": [],
        "next_step": "",
        "score_optional": None,
    }
    if feedback is not None:
        overall_verdict = _string_field(feedback, "overall_verdict", issues, path="$.feedback", allow_empty=False, severity_if_empty="error")
        if overall_verdict and overall_verdict not in OVERALL_VERDICTS:
            issues.append(_issue("invalid_field_type", "error", "$.feedback.overall_verdict", "overall_verdict chi nhan strong, partial, needs_revision."))
        strengths = _list_of_strings_field(feedback, "strengths", issues, path="$.feedback")
        gaps = _list_of_strings_field(feedback, "gaps", issues, path="$.feedback")
        misconceptions = _list_of_strings_field(feedback, "misconceptions", issues, path="$.feedback")
        next_step = _string_field(feedback, "next_step", issues, path="$.feedback", allow_empty=False, severity_if_empty="error")
        score_optional = feedback.get("score_optional")
        if score_optional is not None and not isinstance(score_optional, (str, int, float)):
            issues.append(_issue("invalid_field_type", "error", "$.feedback.score_optional", "`score_optional` phai la string, number hoac null."))
            score_optional = None
        extras = _validate_feedback_addon(activity_type or "", feedback, issues) if activity_type in ACTIVITY_TYPES else {}
        normalized_feedback = {
            "overall_verdict": overall_verdict or "",
            "strengths": strengths or [],
            "gaps": gaps or [],
            "misconceptions": misconceptions or [],
            "next_step": next_step or "",
            "score_optional": score_optional,
            **extras,
        }

    normalized = {
        "payload_type": "activity_feedback",
        "activity_type": activity_type or "",
        "activity_id": activity_id or "",
        "student_submission": normalized_submission,
        "feedback": normalized_feedback,
    }
    return ValidationResult(ok=not _has_errors(issues), marker=marker, normalized=normalized, issues=issues)
