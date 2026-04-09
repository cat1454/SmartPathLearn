from __future__ import annotations

import json
import os
import random
import re
from typing import Any, Iterable, Optional, Sequence

from .extraction import (
    build_concept_packs,
    build_count_claim,
    clean_line,
    clip_text,
    concise_claim_fragment,
    discover_pdf_files,
    extract_evidence_spans,
    extract_pdf_text,
    is_valid_subject,
    normalize_text,
    span_claim_text,
    split_sections,
)
from .schema import (
    APPLICATION_KINDS,
    COGNITIVE_LEVEL_BY_FAMILY,
    DIFFICULTY_BY_FAMILY,
    MECHANISM_KINDS,
    QUESTION_FAMILIES,
    QUESTION_FAMILY_ORDER,
    ConceptPack,
    EvidenceSpan,
    QuizQuestion,
    make_question_id,
)


def find_primary_span(pack: ConceptPack, kinds: Sequence[str]) -> Optional[EvidenceSpan]:
    for kind in kinds:
        for span in pack.supporting_evidence:
            if span.kind == kind:
                return span
    return None


def choose_neighbor_packs(pack: ConceptPack, packs: Sequence[ConceptPack]) -> list[ConceptPack]:
    neighbors = [
        other
        for other in packs
        if other.concept_id != pack.concept_id and other.source_file == pack.source_file and other.subject != pack.subject
    ]
    neighbors.sort(key=lambda other: (abs(other.section_order - pack.section_order), other.section_order))
    return neighbors


def unique_texts(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = clean_line(value)
        key = cleaned.lower()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
    return result


def pick_subject_distractors(pack: ConceptPack, packs: Sequence[ConceptPack], k: int, rng: random.Random) -> list[str]:
    candidates = unique_texts(other.subject for other in choose_neighbor_packs(pack, packs))
    if len(candidates) < k:
        return candidates
    return rng.sample(candidates, k)


def pick_claim_distractors(pack: ConceptPack, packs: Sequence[ConceptPack], k: int, rng: random.Random) -> list[str]:
    candidates: list[str] = []
    for other in choose_neighbor_packs(pack, packs):
        span = find_primary_span(other, MECHANISM_KINDS)
        candidates.append(clip_text(span_claim_text(span) if span else other.core_claim, 120))
    dedup = unique_texts(candidates)
    if len(dedup) < k:
        return dedup
    return rng.sample(dedup, k)


def pick_list_item_distractors(pack: ConceptPack, packs: Sequence[ConceptPack], current_items: Sequence[str], k: int, rng: random.Random) -> list[str]:
    candidates: list[str] = []
    current_set = {item.lower() for item in current_items}
    for other in choose_neighbor_packs(pack, packs):
        span = find_primary_span(other, ("list",))
        if not span:
            continue
        for item in span.items:
            if item.lower() not in current_set:
                candidates.append(item)
    dedup = unique_texts(candidates)
    if len(dedup) < k:
        return dedup
    return rng.sample(dedup, k)


def make_wrong_reason_rows(options: Sequence[str], correct_text: str, reason_map: dict[str, str]) -> list[str]:
    rows: list[str] = []
    for index, option in enumerate(options):
        if option == correct_text:
            continue
        rows.append(f"{chr(ord('A') + index)}. {reason_map.get(option, 'Phương án này không khớp với evidence của câu hỏi.')}")
    return rows


def build_question(
    *,
    pack: ConceptPack,
    question_text: str,
    options: Sequence[str],
    correct_text: str,
    family: str,
    evidence: Sequence[str],
    why_correct: str,
    wrong_reason_map: dict[str, str],
    quality: str,
) -> Optional[QuizQuestion]:
    cleaned_options = unique_texts(options)
    if len(cleaned_options) != 4 or correct_text not in cleaned_options:
        return None
    question = clean_line(question_text)
    if not question.endswith("?"):
        question = f"{question}?"
    return QuizQuestion(
        id="",
        type="single_choice",
        difficulty=DIFFICULTY_BY_FAMILY[family],
        question=question,
        options=cleaned_options,
        answer=chr(ord("A") + cleaned_options.index(correct_text)),
        answer_text=correct_text,
        explanation=why_correct,
        source_file=pack.source_file,
        source_section=pack.source_section,
        source_excerpt=" | ".join(clip_text(item, 120) for item in evidence)[:240],
        quality=quality,
        concept_id=pack.concept_id,
        section_order=pack.section_order,
        question_family=family,
        cognitive_level=COGNITIVE_LEVEL_BY_FAMILY[family],
        evidence=[clip_text(item, 160) for item in evidence],
        why_correct=why_correct,
        why_wrong=make_wrong_reason_rows(cleaned_options, correct_text, wrong_reason_map),
        section_summary=pack.section_summary,
    )


def build_anchor_question(pack: ConceptPack, packs: Sequence[ConceptPack], rng: random.Random, quality: str) -> Optional[QuizQuestion]:
    definition_span = find_primary_span(pack, ("definition", "warning", "process", "cause_effect"))
    if definition_span and is_valid_subject(pack.subject):
        distractors = pick_subject_distractors(pack, packs, 3, rng)
        if len(distractors) == 3:
            claim = clip_text(concise_claim_fragment(definition_span), 140)
            options = distractors + [pack.subject]
            rng.shuffle(options)
            return build_question(
                pack=pack,
                question_text=f"Khái niệm nào khớp nhất với mô tả sau: {claim}",
                options=options,
                correct_text=pack.subject,
                family="anchor",
                evidence=[definition_span.text],
                why_correct=f'Evidence trong tài liệu mô tả trực tiếp "{pack.subject}" là: {claim}.',
                wrong_reason_map={item: f'"{item}" xuất hiện trong cùng tài liệu nhưng không khớp với mô tả này.' for item in distractors},
                quality=quality,
            )

    list_span = find_primary_span(pack, ("list",))
    if list_span and len(list_span.items) >= 3:
        correct_item = rng.choice(list_span.items)
        distractors = pick_list_item_distractors(pack, packs, list_span.items, 3, rng)
        if len(distractors) == 3:
            options = distractors + [correct_item]
            rng.shuffle(options)
            return build_question(
                pack=pack,
                question_text=f"Đâu là một mục thuộc phần {pack.source_section}",
                options=options,
                correct_text=correct_item,
                family="anchor",
                evidence=[list_span.text],
                why_correct=f'Tài liệu liệt kê "{correct_item}" trong section {pack.source_section}.',
                wrong_reason_map={item: f'"{item}" nằm ở concept/section khác, không thuộc danh sách của {pack.subject}.' for item in distractors},
                quality=quality,
            )

    count_span = find_primary_span(pack, ("count",))
    if count_span and count_span.count is not None:
        wrong_numbers = [str(value) for value in sorted({count_span.count - 2, count_span.count - 1, count_span.count + 1, count_span.count + 2, count_span.count + 3}) if value > 0][:3]
        if len(wrong_numbers) == 3:
            options = wrong_numbers + [str(count_span.count)]
            rng.shuffle(options)
            return build_question(
                pack=pack,
                question_text=f"Theo tài liệu, {count_span.subject} có bao nhiêu {count_span.counted_thing}",
                options=options,
                correct_text=str(count_span.count),
                family="anchor",
                evidence=[count_span.text],
                why_correct=f'Tài liệu nêu trực tiếp: {build_count_claim(count_span.subject, count_span.count, count_span.counted_thing)}.',
                wrong_reason_map={item: f'Tài liệu nêu rõ con số đúng là {count_span.count}, không phải {item}.' for item in wrong_numbers},
                quality=quality,
            )
    return None


def build_mechanism_question(pack: ConceptPack, packs: Sequence[ConceptPack], rng: random.Random, quality: str) -> Optional[QuizQuestion]:
    span = find_primary_span(pack, MECHANISM_KINDS)
    if not span:
        return None
    correct_claim = clip_text(span_claim_text(span), 120)
    distractors = pick_claim_distractors(pack, packs, 3, rng)
    if len(distractors) != 3:
        return None
    options = unique_texts(distractors + [correct_claim])
    if len(options) != 4:
        return None
    rng.shuffle(options)
    return build_question(
        pack=pack,
        question_text=f"Phát biểu nào diễn giải đúng nhất vai trò hoặc cách vận hành của {pack.subject}",
        options=options,
        correct_text=correct_claim,
        family="mechanism",
        evidence=[span.text],
        why_correct=f'Evidence cho thấy {pack.subject} được mô tả như sau: {correct_claim}.',
        wrong_reason_map={item: f'Phương án này mô tả concept khác trong cùng tài liệu, không phải vai trò/cơ chế của {pack.subject}.' for item in distractors},
        quality=quality,
    )


def build_contrast_question(pack: ConceptPack, packs: Sequence[ConceptPack], quality: str) -> Optional[QuizQuestion]:
    current_span = find_primary_span(pack, ("definition", "process", "cause_effect", "warning"))
    if not current_span:
        return None
    neighbor_pack = None
    neighbor_span = None
    for candidate in choose_neighbor_packs(pack, packs):
        candidate_span = find_primary_span(candidate, ("definition", "process", "cause_effect", "warning"))
        if candidate_span:
            neighbor_pack = candidate
            neighbor_span = candidate_span
            break
    if not neighbor_pack or not neighbor_span:
        return None
    current_fragment = concise_claim_fragment(current_span)
    neighbor_fragment = concise_claim_fragment(neighbor_span)
    if current_fragment.lower() == neighbor_fragment.lower():
        return None
    correct_option = f"{pack.subject}: {current_fragment}; {neighbor_pack.subject}: {neighbor_fragment}"
    swapped_option = f"{pack.subject}: {neighbor_fragment}; {neighbor_pack.subject}: {current_fragment}"
    same_current_option = f"{pack.subject} và {neighbor_pack.subject} đều: {current_fragment}"
    same_neighbor_option = f"{pack.subject} và {neighbor_pack.subject} đều: {neighbor_fragment}"
    return build_question(
        pack=pack,
        question_text=f"Phát biểu nào phân biệt đúng giữa {pack.subject} và {neighbor_pack.subject}",
        options=[correct_option, swapped_option, same_current_option, same_neighbor_option],
        correct_text=correct_option,
        family="contrast",
        evidence=[current_span.text, neighbor_span.text],
        why_correct=f'Tài liệu mô tả {pack.subject} là "{current_fragment}", còn {neighbor_pack.subject} là "{neighbor_fragment}".',
        wrong_reason_map={
            swapped_option: f"Phương án này đã tráo mô tả giữa {pack.subject} và {neighbor_pack.subject}.",
            same_current_option: f"Phương án này đánh đồng {neighbor_pack.subject} với mô tả của {pack.subject}.",
            same_neighbor_option: f"Phương án này đánh đồng {pack.subject} với mô tả của {neighbor_pack.subject}.",
        },
        quality=quality,
    )


def build_application_question(pack: ConceptPack, packs: Sequence[ConceptPack], rng: random.Random, quality: str) -> Optional[QuizQuestion]:
    span = find_primary_span(pack, APPLICATION_KINDS)
    if not span or not is_valid_subject(pack.subject):
        return None
    distractors = pick_subject_distractors(pack, packs, 3, rng)
    if len(distractors) != 3:
        return None
    options = distractors + [pack.subject]
    rng.shuffle(options)
    return build_question(
        pack=pack,
        question_text=f"Tình huống sau minh họa rõ nhất cho khái niệm nào: {clip_text(span.text, 180)}",
        options=options,
        correct_text=pack.subject,
        family="application",
        evidence=[span.text],
        why_correct=f'Tình huống bám trực tiếp vào evidence mô tả {pack.subject}: {clip_text(span_claim_text(span), 140)}.',
        wrong_reason_map={item: f'"{item}" liên quan đến tài liệu nhưng không phải khái niệm được minh họa rõ nhất bởi tình huống này.' for item in distractors},
        quality=quality,
    )


def pack_supports_family(pack: ConceptPack, family: str, packs: Sequence[ConceptPack]) -> bool:
    if family == "anchor":
        return bool(find_primary_span(pack, ("definition", "list", "count", "process", "warning", "cause_effect")))
    if family == "mechanism":
        return bool(find_primary_span(pack, MECHANISM_KINDS))
    if family == "contrast":
        return any(find_primary_span(other, ("definition", "process", "cause_effect", "warning")) for other in choose_neighbor_packs(pack, packs))
    if family == "application":
        return bool(find_primary_span(pack, APPLICATION_KINDS))
    return False


def extract_json_object(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Phản hồi LLM không chứa JSON object hợp lệ.")
    return stripped[start : end + 1]


class LLMQuestionGenerator:
    def __init__(self, model: str) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("Để dùng --llm-model, hãy thiết lập biến môi trường OPENAI_API_KEY.")
        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Thiếu thư viện openai. Hãy cài: pip install openai") from exc
        self.model = model
        self.client = OpenAI()

    def _chat_json(self, system_prompt: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)},
            ],
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(extract_json_object(content))

    def generate_question(self, pack: ConceptPack, family: str) -> dict[str, Any]:
        payload = {
            "section_title": pack.source_section,
            "learning_objective": pack.learning_objective,
            "evidence_spans": [span.text for span in pack.supporting_evidence],
            "neighbor_concepts": pack.neighbor_concepts,
            "question_family": family,
            "language": "vi",
        }
        system_prompt = (
            "Bạn là chuyên gia sư phạm. Hãy viết đúng 1 câu hỏi trắc nghiệm 4 lựa chọn bằng tiếng Việt. "
            "Câu hỏi phải bám sát evidence, không bịa kiến thức ngoài tài liệu, và ưu tiên hiểu sâu. "
            "Trả về JSON object duy nhất với các khóa: question, options, answer, answer_text, evidence, why_correct, why_wrong. "
            "why_wrong phải là mảng 3 chuỗi ngắn giải thích vì sao mỗi distractor sai."
        )
        return self._chat_json(system_prompt, payload)

    def judge_question(self, pack: ConceptPack, family: str, candidate: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "section_title": pack.source_section,
            "learning_objective": pack.learning_objective,
            "evidence_spans": [span.text for span in pack.supporting_evidence],
            "neighbor_concepts": pack.neighbor_concepts,
            "question_family": family,
            "language": "vi",
            "candidate": candidate,
        }
        system_prompt = (
            "Bạn là giám khảo chất lượng câu hỏi. Hãy đánh giá candidate theo 5 tiêu chí nhị phân: "
            "grounded, clear_stem, single_best_answer, good_distractors, tests_understanding_not_copy. "
            "Trả về JSON object với các khóa: grounded, clear_stem, single_best_answer, good_distractors, "
            "tests_understanding_not_copy, passed, notes."
        )
        return self._chat_json(system_prompt, payload)


def coerce_llm_question_payload(candidate: dict[str, Any], family: str) -> Optional[dict[str, Any]]:
    question = clean_line(str(candidate.get("question", "")))
    options = unique_texts(str(option) for option in candidate.get("options", []))
    answer = str(candidate.get("answer", "")).strip().upper()
    answer_text = clean_line(str(candidate.get("answer_text", "")))
    evidence = [clean_line(str(item)) for item in candidate.get("evidence", []) if clean_line(str(item))]
    why_correct = clean_line(str(candidate.get("why_correct", "")))
    why_wrong = [clean_line(str(item)) for item in candidate.get("why_wrong", []) if clean_line(str(item))]
    if len(options) != 4 or not question or not why_correct or not evidence:
        return None
    if answer_text not in options:
        if answer in {"A", "B", "C", "D"}:
            answer_text = options[ord(answer) - ord("A")]
        else:
            return None
    if len(why_wrong) < 3:
        return None
    return {
        "question": question,
        "options": options,
        "answer": chr(ord("A") + options.index(answer_text)),
        "answer_text": answer_text,
        "evidence": evidence,
        "why_correct": why_correct,
        "why_wrong": why_wrong[:3],
        "family": family,
    }


def build_question_from_llm_candidate(pack: ConceptPack, family: str, candidate: dict[str, Any]) -> QuizQuestion:
    wrong_reason_map: dict[str, str] = {}
    wrong_iter = iter(candidate["why_wrong"])
    for option in candidate["options"]:
        if option != candidate["answer_text"]:
            wrong_reason_map[option] = next(wrong_iter, "Phương án này không khớp với evidence của câu hỏi.")
    return QuizQuestion(
        id="",
        type="single_choice",
        difficulty=DIFFICULTY_BY_FAMILY[family],
        question=candidate["question"] if candidate["question"].endswith("?") else f"{candidate['question']}?",
        options=candidate["options"],
        answer=candidate["answer"],
        answer_text=candidate["answer_text"],
        explanation=candidate["why_correct"],
        source_file=pack.source_file,
        source_section=pack.source_section,
        source_excerpt=" | ".join(clip_text(item, 120) for item in candidate["evidence"])[:240],
        quality="hybrid_reviewed",
        concept_id=pack.concept_id,
        section_order=pack.section_order,
        question_family=family,
        cognitive_level=COGNITIVE_LEVEL_BY_FAMILY[family],
        evidence=[clip_text(item, 160) for item in candidate["evidence"]],
        why_correct=candidate["why_correct"],
        why_wrong=make_wrong_reason_rows(candidate["options"], candidate["answer_text"], wrong_reason_map),
        section_summary=pack.section_summary,
    )


def generate_question_with_llm(generator: LLMQuestionGenerator, pack: ConceptPack, family: str) -> Optional[QuizQuestion]:
    for _attempt in range(2):
        candidate = generator.generate_question(pack, family)
        coerced = coerce_llm_question_payload(candidate, family)
        if not coerced:
            continue
        verdict = generator.judge_question(pack, family, coerced)
        passed = bool(
            verdict.get("passed")
            and verdict.get("grounded")
            and verdict.get("clear_stem")
            and verdict.get("single_best_answer")
            and verdict.get("good_distractors")
            and verdict.get("tests_understanding_not_copy")
        )
        if passed:
            return build_question_from_llm_candidate(pack, family, coerced)
    return None


def build_questions_for_pack(pack: ConceptPack, packs: Sequence[ConceptPack], rng: random.Random, llm_generator: Optional[LLMQuestionGenerator]) -> list[QuizQuestion]:
    if llm_generator is not None:
        result: list[QuizQuestion] = []
        for family in QUESTION_FAMILIES:
            if pack_supports_family(pack, family, packs):
                question = generate_question_with_llm(llm_generator, pack, family)
                if question:
                    result.append(question)
        return result
    quality = "offline_curated"
    builders = {
        "anchor": lambda: build_anchor_question(pack, packs, rng, quality),
        "mechanism": lambda: build_mechanism_question(pack, packs, rng, quality),
        "contrast": lambda: build_contrast_question(pack, packs, quality),
        "application": lambda: build_application_question(pack, packs, rng, quality),
    }
    result = []
    for family in QUESTION_FAMILIES:
        if pack_supports_family(pack, family, packs):
            question = builders[family]()
            if question:
                result.append(question)
    return result


def dedupe_questions(questions: Sequence[QuizQuestion]) -> list[QuizQuestion]:
    dedup: list[QuizQuestion] = []
    seen: set[tuple[str, str]] = set()
    question_seen: set[str] = set()
    for question in questions:
        family_key = (question.concept_id, question.question_family)
        question_key = re.sub(r"\s+", " ", question.question.strip().lower())
        if family_key in seen or question_key in question_seen:
            continue
        seen.add(family_key)
        question_seen.add(question_key)
        dedup.append(question)
    return dedup


def sort_learning_path_questions(questions: Sequence[QuizQuestion]) -> list[QuizQuestion]:
    return sorted(questions, key=lambda question: (question.source_file.lower(), question.section_order, QUESTION_FAMILY_ORDER.get(question.question_family, 99), question.question.lower()))


def generate_quiz_artifacts(input_path, max_questions: int, seed: int, mode: str, llm_model: Optional[str]) -> tuple[list[QuizQuestion], list[ConceptPack]]:
    rng = random.Random(seed)
    pdf_files = discover_pdf_files(input_path)
    all_sections = []
    for pdf_file in pdf_files:
        text = normalize_text(extract_pdf_text(pdf_file))
        all_sections.extend(split_sections(text, pdf_file.name))
    evidence_spans = extract_evidence_spans(all_sections)
    concept_packs = build_concept_packs(all_sections, evidence_spans)
    if not concept_packs:
        raise RuntimeError("Không trích xuất được concept pack nào từ tài liệu.")
    llm_generator = LLMQuestionGenerator(llm_model) if llm_model else None
    questions: list[QuizQuestion] = []
    for pack in concept_packs:
        questions.extend(build_questions_for_pack(pack, concept_packs, rng, llm_generator))
    questions = dedupe_questions(questions)
    questions = sort_learning_path_questions(questions) if mode == "learning_path" else random.Random(seed).sample(questions, k=len(questions)) if questions else []
    questions = questions[:max_questions]
    for index, question in enumerate(questions, start=1):
        question.id = make_question_id(index)
    return questions, concept_packs
