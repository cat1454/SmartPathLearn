from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Sequence

from .schema import ConceptPack, QuizQuestion, render_option_labels


def question_to_payload(question: QuizQuestion) -> dict[str, Any]:
    row = asdict(question)
    row["labeled_options"] = render_option_labels(question.options)
    return row


def build_learning_path_payload(questions: Sequence[QuizQuestion], packs: Sequence[ConceptPack]) -> dict[str, Any]:
    pack_lookup = {pack.concept_id: pack for pack in packs}
    files: list[dict[str, Any]] = []
    file_map: dict[str, dict[str, Any]] = {}
    for question in questions:
        file_entry = file_map.get(question.source_file)
        if file_entry is None:
            file_entry = {"source_file": question.source_file, "sections": []}
            file_map[question.source_file] = file_entry
            files.append(file_entry)
        sections = file_entry["sections"]
        if not sections or sections[-1]["concept_id"] != question.concept_id:
            pack = pack_lookup.get(question.concept_id)
            sections.append(
                {
                    "concept_id": question.concept_id,
                    "section_title": question.source_section,
                    "section_order": question.section_order,
                    "learning_objective": pack.learning_objective if pack else "",
                    "section_summary": question.section_summary,
                    "questions": [],
                }
            )
        sections[-1]["questions"].append(question_to_payload(question))
    return {"mode": "learning_path", "total_questions": len(questions), "files": files}


def save_json(questions: Sequence[QuizQuestion], output_path: Path, mode: str, packs: Sequence[ConceptPack]) -> None:
    payload: Any = build_learning_path_payload(questions, packs) if mode == "learning_path" else [question_to_payload(question) for question in questions]
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_csv(questions: Sequence[QuizQuestion], output_path: Path) -> None:
    fields = [
        "id",
        "type",
        "difficulty",
        "concept_id",
        "section_order",
        "question_family",
        "cognitive_level",
        "question",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "answer",
        "answer_text",
        "explanation",
        "why_correct",
        "why_wrong",
        "evidence",
        "source_file",
        "source_section",
        "source_excerpt",
        "section_summary",
        "quality",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fields)
        writer.writeheader()
        for question in questions:
            writer.writerow(
                {
                    "id": question.id,
                    "type": question.type,
                    "difficulty": question.difficulty,
                    "concept_id": question.concept_id,
                    "section_order": question.section_order,
                    "question_family": question.question_family,
                    "cognitive_level": question.cognitive_level,
                    "question": question.question,
                    "option_a": question.options[0] if len(question.options) > 0 else "",
                    "option_b": question.options[1] if len(question.options) > 1 else "",
                    "option_c": question.options[2] if len(question.options) > 2 else "",
                    "option_d": question.options[3] if len(question.options) > 3 else "",
                    "answer": question.answer,
                    "answer_text": question.answer_text,
                    "explanation": question.explanation,
                    "why_correct": question.why_correct,
                    "why_wrong": " || ".join(question.why_wrong),
                    "evidence": " || ".join(question.evidence),
                    "source_file": question.source_file,
                    "source_section": question.source_section,
                    "source_excerpt": question.source_excerpt,
                    "section_summary": question.section_summary,
                    "quality": question.quality,
                }
            )
