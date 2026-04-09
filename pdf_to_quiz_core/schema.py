from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

QUESTION_FAMILIES = ("anchor", "mechanism", "contrast", "application")
QUESTION_FAMILY_ORDER = {family: index for index, family in enumerate(QUESTION_FAMILIES)}
COGNITIVE_LEVEL_BY_FAMILY = {
    "anchor": "remember",
    "mechanism": "understand",
    "contrast": "understand",
    "application": "apply",
}
DIFFICULTY_BY_FAMILY = {
    "anchor": "easy",
    "mechanism": "medium",
    "contrast": "medium",
    "application": "hard",
}
CORE_KIND_PRIORITY = {
    "definition": 0,
    "process": 1,
    "cause_effect": 2,
    "comparison": 3,
    "list": 4,
    "count": 5,
    "warning": 6,
    "example": 7,
}
MECHANISM_KINDS = ("process", "cause_effect", "list", "count", "definition", "warning")
APPLICATION_KINDS = ("example", "warning", "cause_effect")


@dataclass
class Section:
    source_file: str
    title: str
    content: str
    section_order: int


@dataclass
class EvidenceSpan:
    span_id: str
    kind: str
    subject: str
    text: str
    source_file: str
    source_section: str
    section_order: int
    detail: str = ""
    items: list[str] = field(default_factory=list)
    count: int | None = None
    counted_thing: str = ""
    related_subjects: list[str] = field(default_factory=list)


@dataclass
class ConceptPack:
    concept_id: str
    source_file: str
    source_section: str
    section_order: int
    subject: str
    learning_objective: str
    core_claim: str
    section_summary: str
    supporting_evidence: list[EvidenceSpan] = field(default_factory=list)
    neighbor_concepts: list[str] = field(default_factory=list)
    common_confusions: list[str] = field(default_factory=list)


@dataclass
class QuizQuestion:
    id: str
    type: str
    difficulty: str
    question: str
    options: list[str]
    answer: str
    answer_text: str
    explanation: str
    source_file: str
    source_section: str
    source_excerpt: str
    quality: str
    concept_id: str = ""
    section_order: int = 0
    question_family: str = "anchor"
    cognitive_level: str = "remember"
    evidence: list[str] = field(default_factory=list)
    why_correct: str = ""
    why_wrong: list[str] = field(default_factory=list)
    section_summary: str = ""


def make_question_id(index: int) -> str:
    return f"Q{index:04d}"


def render_option_labels(options: Sequence[str]) -> list[str]:
    return [f"{chr(ord('A') + index)}. {option}" for index, option in enumerate(options)]
