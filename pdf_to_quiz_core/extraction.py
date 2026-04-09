from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Optional, Sequence

try:
    import pdfplumber
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "Thiếu thư viện pdfplumber. Hãy cài: pip install pdfplumber pypdf"
    ) from exc

from pypdf import PdfReader

from .schema import CORE_KIND_PRIORITY, ConceptPack, EvidenceSpan, Section

SCRIPT_DIR = Path(__file__).resolve().parent.parent
TRUNCATED_TAILS = {
    "và",
    "hoặc",
    "để",
    "nhằm",
    "gồm",
    "bao gồm",
    "như",
    "là",
    "có",
    "các",
    "những",
    "một",
    "theo",
    "trong",
    "khi",
}
SUBJECT_STOPWORDS = {
    "không",
    "mỗi",
    "các",
    "một",
    "của",
    "cua",
    "đây",
    "vì",
    "do",
    "khi",
    "nếu",
    "việc",
    "điều",
    "đó",
    "cần",
    "nơi",
    "sau",
    "trong",
    "theo",
}
NOISY_TERMS = {
    "mục tiêu",
    "nội dung",
    "nội dung môn học",
    "câu hỏi",
    "ví dụ",
    "kết quả",
    "ưu điểm",
    "nhược điểm",
    "tổng kết",
    "bài tập",
}
CAUSE_EFFECT_MARKERS = (
    "giúp",
    "nhằm",
    "để",
    "cho phép",
    "vì vậy",
    "do đó",
    "nên",
    "mục tiêu là",
    "đóng vai trò",
)
PROCESS_MARKERS = (
    "quy trình",
    "giai đoạn",
    "bước",
    "vòng lặp",
    "chu kỳ",
    "hoạt động",
    "workflow",
)
WARNING_MARKERS = ("không nên", "tránh", "không phải", "không được")
EXAMPLE_MARKERS = ("ví dụ", "chẳng hạn", "giả sử", "nếu ")
HEADING_PATTERNS = [
    re.compile(r"^CHƯƠNG\s+\d+", re.IGNORECASE),
    re.compile(r"^\d+(\.\d+)*\s+[A-ZÀ-Ỵa-zà-ỵ]"),
    re.compile(r"^[A-ZÀ-Ỵ0-9\-–,:() ]{5,120}$"),
]
BULLET_RE = re.compile(r"^(?:[-•▪❖➢*]+\s*|\d+[.)]\s+)")
COUNT_PATTERNS = [
    re.compile(
        r"(?P<subject>[A-ZÀ-Ỵa-zà-ỵ0-9 ()/\-–,]{3,140}?)\s+(?:bao gồm|gồm|có)\s+(?P<count>\d{1,3})\s+(?P<thing>[A-ZÀ-Ỵa-zà-ỵ ]{2,60})",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?P<count>\d{1,3})\s+(?P<thing>giá trị|nguyên tắc|hoạt động|vai trò|trụ cột|pha|bước|giai đoạn|khía cạnh|sự kiện)",
        re.IGNORECASE,
    ),
]
DEFINITION_PATTERNS = [
    re.compile(r"^(?P<term>[A-ZÀ-Ỵa-zà-ỵ0-9 ()/\-–]{3,120}?)\s+là\s+(?P<definition>.+)$", re.IGNORECASE),
    re.compile(r"^(?P<term>[A-ZÀ-Ỵa-zà-ỵ0-9 ()/\-–]{3,120}?)\s+được coi là\s+(?P<definition>.+)$", re.IGNORECASE),
    re.compile(r"^(?P<term>[A-ZÀ-Ỵa-zà-ỵ0-9 ()/\-–]{3,120}?)\s+đóng vai trò\s+(?P<definition>.+)$", re.IGNORECASE),
]
COMPARISON_PATTERNS = [
    re.compile(
        r"(?P<a>[A-ZÀ-Ỵa-zà-ỵ0-9 ()/\-–]{3,80}?)\s+(?:khác với|so với|trái với|thay vì)\s+(?P<b>[A-ZÀ-Ỵa-zà-ỵ0-9 ()/\-–]{3,80})",
        re.IGNORECASE,
    ),
]
NOISE_RE = re.compile(r"[^\w\sÀ-Ỵà-ỵ.,:;!?()/\-–%+&]")


def unique_paths(paths: Iterable[Path]) -> list[Path]:
    seen = set()
    result: list[Path] = []
    for path in paths:
        candidate = path.expanduser()
        key = str(candidate.resolve(strict=False)).lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(candidate)
    return result


def build_path_candidates(raw_path: Path) -> list[Path]:
    text = str(raw_path).strip()
    if not text:
        return []
    path = Path(text).expanduser()
    normalized = text.replace("\\", "/")
    candidates: list[Path] = [path]
    rooted_without_drive = normalized.startswith("/") and not re.match(r"^[A-Za-z]:", normalized)
    if rooted_without_drive:
        relative_tail = normalized.lstrip("/")
        if relative_tail:
            relative_path = Path(relative_tail)
            candidates.extend([Path.cwd() / relative_path, SCRIPT_DIR / relative_path])
    elif not path.is_absolute():
        candidates.extend([Path.cwd() / path, SCRIPT_DIR / path])
    return unique_paths(candidates)


def resolve_existing_path(raw_path: Path) -> Path:
    for candidate in build_path_candidates(raw_path):
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Không tìm thấy file/thư mục PDF: {raw_path}")


def resolve_output_path(raw_path: Path) -> Path:
    candidates = build_path_candidates(raw_path)
    if not candidates:
        return raw_path
    for candidate in candidates:
        if candidate.parent.exists():
            return candidate
    return candidates[0]


def discover_pdf_files(input_path: Path) -> list[Path]:
    resolved_input = resolve_existing_path(input_path)
    if resolved_input.is_file() and resolved_input.suffix.lower() == ".pdf":
        return [resolved_input]
    if resolved_input.is_dir():
        return sorted(path for path in resolved_input.iterdir() if path.suffix.lower() == ".pdf")
    raise FileNotFoundError(f"Không tìm thấy file/thư mục PDF: {input_path}")


def extract_pdf_text(pdf_path: Path) -> str:
    texts: list[str] = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                if text.strip():
                    texts.append(text)
    except Exception:
        texts = []
    if texts:
        return "\n".join(texts)
    try:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                texts.append(text)
    except Exception as exc:
        raise RuntimeError(f"Không thể đọc PDF: {pdf_path}") from exc
    return "\n".join(texts)


def normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\u200b", "", text)
    return text.strip()


def clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip(" \t|:;-")).strip()


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.replace("Đ", "D").replace("đ", "d"))
    return "".join(char for char in normalized if not unicodedata.combining(char))


def slugify(text: str) -> str:
    ascii_text = strip_accents(text).lower()
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text)
    return ascii_text.strip("-") or "concept"


def clip_text(text: str, limit: int = 160) -> str:
    compact = clean_line(text)
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit].rsplit(' ', 1)[0]}..."


def normalize_subject_phrase(text: str, fallback: str = "") -> str:
    subject = clean_line(text)
    subject = re.sub(r"^\d+(\.\d+)*[.)]?\s*", "", subject)
    subject = re.sub(r"^(?:ví dụ|chẳng hạn|giả sử|nếu|trong trường hợp)\s+", "", subject, flags=re.IGNORECASE)
    subject = re.sub(r"\([^)]*(?:\d{4}|[A-Za-z]{3,})[^)]*\)", "", subject)
    subject = re.sub(r"\s+(?:bao gồm|gồm|có|là|được coi là|đóng vai trò|nhằm|giúp)\b.*$", "", subject, flags=re.IGNORECASE)
    subject = subject.strip(" ,:;-")
    if "," in subject and len(subject) > 36:
        first_clause = clean_line(subject.split(",", 1)[0])
        if first_clause:
            subject = first_clause
    return clean_line(subject) or clean_line(fallback)


def is_heading(line: str) -> bool:
    raw = clean_line(line)
    if not raw or len(raw) < 3 or BULLET_RE.match(raw) or raw.isdigit():
        return False
    if "http" in raw.lower() or "@" in raw or raw.count(",") >= 3:
        return False
    if any(pattern.match(raw) for pattern in HEADING_PATTERNS):
        return True
    words = raw.split()
    letters = [char for char in raw if char.isalpha()]
    if raw == raw.upper() and len(letters) >= 5:
        return True
    if letters:
        uppercase_ratio = sum(1 for char in letters if char.isupper()) / len(letters)
        return 1 <= len(words) <= 12 and len(raw) >= 10 and uppercase_ratio >= 0.55
    return False


def split_sections(text: str, source_file: str) -> list[Section]:
    sections: list[Section] = []
    current_title = "Mở đầu"
    current_lines: list[str] = []
    section_order = 1
    for raw_line in text.splitlines():
        line = clean_line(raw_line)
        if not line:
            continue
        if is_heading(line):
            if current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    sections.append(Section(source_file, current_title, content, section_order))
                    section_order += 1
                current_lines = []
            current_title = line[:180]
        else:
            current_lines.append(line)
    if current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            sections.append(Section(source_file, current_title, content, section_order))
    return sections


def split_sentences(text: str) -> list[str]:
    lines = [clean_line(line) for line in text.splitlines() if clean_line(line)]
    sentences: list[str] = []
    for line in lines:
        if BULLET_RE.match(line):
            line = BULLET_RE.sub("", line).strip()
            if line:
                sentences.append(line)
            continue
        for part in re.split(r"(?<=[.!?])\s+|\s*[;•▪]\s*", line):
            part = clean_line(part)
            if len(part) >= 12:
                sentences.append(part)
    return sentences


def looks_truncated(text: str) -> bool:
    compact = clean_line(text)
    if not compact or compact.endswith((",", "-", "/", "(")) or compact.count("(") != compact.count(")"):
        return True
    tokens = compact.lower().split()
    return bool(tokens and (tokens[-1] in TRUNCATED_TAILS or (len(tokens) >= 2 and " ".join(tokens[-2:]) in TRUNCATED_TAILS)))


def has_too_much_noise(text: str) -> bool:
    compact = clean_line(text)
    weird_chars = len(NOISE_RE.findall(compact))
    return not compact or weird_chars > max(4, len(compact) // 10) or compact.count("|") >= 2 or "�" in compact


def is_valid_subject(subject: str) -> bool:
    normalized = normalize_subject_phrase(subject)
    lowered = normalized.lower()
    first_word = lowered.split()[0] if lowered.split() else ""
    return (
        3 <= len(normalized) <= 120
        and lowered not in NOISY_TERMS
        and first_word not in SUBJECT_STOPWORDS
        and not re.match(r"^\d", normalized)
        and not lowered.endswith("không phải")
        and not (normalized == normalized.lower() and len(normalized.split()) > 3)
        and len(re.findall(r"[A-Za-zÀ-Ỵà-ỵ]", normalized)) >= 3
    )


def is_clean_evidence_text(text: str) -> bool:
    compact = clean_line(text)
    return len(compact) >= 12 and not looks_truncated(compact) and not has_too_much_noise(compact)


def build_span_id(index: int) -> str:
    return f"EV{index:04d}"


def make_concept_id(section: Section, subject: str) -> str:
    return f"{slugify(Path(section.source_file).stem)}__s{section.section_order:02d}__{slugify(subject)[:24]}"


def build_count_claim(subject: str, count: int, counted_thing: str) -> str:
    return f"{subject} có {count} {counted_thing}"


def span_claim_text(span: EvidenceSpan) -> str:
    if span.kind == "definition" and span.detail:
        return span.detail
    if span.kind == "count" and span.count is not None and span.counted_thing:
        return build_count_claim(span.subject, span.count, span.counted_thing)
    if span.kind == "list" and span.items:
        return f"{span.subject} gồm: {', '.join(span.items[:4])}"
    return span.detail or span.text


def concise_claim_fragment(span: EvidenceSpan) -> str:
    claim = span_claim_text(span)
    claim = re.sub(r"^[A-ZÀ-Ỵa-zà-ỵ0-9 ()/\-–]{3,120}?\s+(?:là|được coi là|đóng vai trò)\s+", "", claim, flags=re.IGNORECASE)
    return clip_text(re.sub(r"^[,.:;\- ]+", "", claim), 80)


def extract_list_evidence(section: Section, start_index: int) -> tuple[list[EvidenceSpan], int]:
    spans: list[EvidenceSpan] = []
    index = start_index
    current_items: list[str] = []

    def flush_items(items: list[str], current_index: int) -> int:
        if len(items) < 3:
            return current_index
        dedup: list[str] = []
        seen: set[str] = set()
        for item in items:
            key = item.lower()
            if key not in seen:
                dedup.append(item)
                seen.add(key)
        if len(dedup) < 3:
            return current_index
        subject = normalize_subject_phrase(section.title, section.title)
        spans.append(
            EvidenceSpan(
                span_id=build_span_id(current_index),
                kind="list",
                subject=subject,
                text=f"{subject} gồm: {', '.join(dedup[:6])}",
                detail=f"{subject} gồm: {', '.join(dedup[:6])}",
                items=dedup,
                source_file=section.source_file,
                source_section=section.title,
                section_order=section.section_order,
            )
        )
        return current_index + 1

    for raw_line in section.content.splitlines() + [""]:
        line = raw_line.strip()
        cleaned = clean_line(line)
        is_bullet = bool(BULLET_RE.match(line) or BULLET_RE.match(cleaned))
        if is_bullet:
            item = clean_line(BULLET_RE.sub("", line).strip()).rstrip(".:;")
            if 4 <= len(item) <= 120 and not is_heading(item) and not has_too_much_noise(item) and not looks_truncated(item):
                current_items.append(item)
            continue
        index = flush_items(current_items, index)
        current_items = []
    return spans, index


def make_sentence_span(
    index: int,
    section: Section,
    kind: str,
    subject: str,
    text: str,
    *,
    detail: str = "",
    count: Optional[int] = None,
    counted_thing: str = "",
    related_subjects: Optional[list[str]] = None,
) -> EvidenceSpan:
    return EvidenceSpan(
        span_id=build_span_id(index),
        kind=kind,
        subject=normalize_subject_phrase(subject, section.title),
        text=clean_line(text),
        detail=clean_line(detail),
        count=count,
        counted_thing=clean_line(counted_thing),
        related_subjects=related_subjects or [],
        source_file=section.source_file,
        source_section=section.title,
        section_order=section.section_order,
    )


def extract_sentence_evidence(section: Section, start_index: int) -> tuple[list[EvidenceSpan], int]:
    spans: list[EvidenceSpan] = []
    index = start_index
    for sentence in split_sentences(section.content):
        cleaned = clean_line(sentence).rstrip(".:")
        lowered = cleaned.lower()
        if not is_clean_evidence_text(cleaned):
            continue
        negative_match = re.search(r"\bkhông phải là\b", cleaned, flags=re.IGNORECASE)
        if negative_match:
            subject = normalize_subject_phrase(cleaned[: negative_match.start()], section.title)
            detail = clean_line(cleaned[negative_match.end() :])
            if is_valid_subject(subject) and detail:
                spans.append(make_sentence_span(index, section, "warning", subject, cleaned, detail=f"không phải là {detail}"))
                index += 1
                continue
        matched_definition = False
        for pattern in DEFINITION_PATTERNS:
            match = pattern.match(cleaned)
            if not match:
                continue
            term = normalize_subject_phrase(match.group("term"), section.title)
            detail = clean_line(match.group("definition"))
            if is_valid_subject(term) and is_clean_evidence_text(detail):
                spans.append(make_sentence_span(index, section, "definition", term, cleaned, detail=detail))
                index += 1
                matched_definition = True
            break
        if matched_definition:
            continue
        matched_count = False
        for pattern in COUNT_PATTERNS:
            match = pattern.search(cleaned)
            if not match:
                continue
            count = int(match.group("count"))
            counted_thing = clean_line(match.group("thing"))
            subject = normalize_subject_phrase(match.groupdict().get("subject") or section.title, section.title)
            if not is_valid_subject(subject):
                subject = normalize_subject_phrase(section.title, section.title)
            if is_valid_subject(subject) and 2 <= count <= 20:
                spans.append(make_sentence_span(index, section, "count", subject, cleaned, detail=build_count_claim(subject, count, counted_thing), count=count, counted_thing=counted_thing))
                index += 1
                matched_count = True
            break
        if matched_count:
            continue
        comparison_match = next((pattern.search(cleaned) for pattern in COMPARISON_PATTERNS if pattern.search(cleaned)), None)
        if comparison_match:
            subject_a = normalize_subject_phrase(comparison_match.group("a"), section.title)
            subject_b = normalize_subject_phrase(comparison_match.group("b"), section.title)
            if is_valid_subject(subject_a) and is_valid_subject(subject_b):
                spans.append(make_sentence_span(index, section, "comparison", subject_a, cleaned, detail=cleaned, related_subjects=[subject_b]))
                index += 1
                continue
        subject = normalize_subject_phrase(section.title, section.title)
        if any(marker in lowered for marker in EXAMPLE_MARKERS):
            spans.append(make_sentence_span(index, section, "example", subject, cleaned, detail=cleaned))
            index += 1
        elif any(marker in lowered for marker in WARNING_MARKERS):
            spans.append(make_sentence_span(index, section, "warning", subject, cleaned, detail=cleaned))
            index += 1
        elif any(marker in lowered for marker in PROCESS_MARKERS):
            spans.append(make_sentence_span(index, section, "process", subject, cleaned, detail=cleaned))
            index += 1
        elif any(marker in lowered for marker in CAUSE_EFFECT_MARKERS):
            spans.append(make_sentence_span(index, section, "cause_effect", subject, cleaned, detail=cleaned))
            index += 1
    return spans, index


def dedupe_spans(spans: Sequence[EvidenceSpan]) -> list[EvidenceSpan]:
    result: list[EvidenceSpan] = []
    seen: set[tuple[str, str, str, str]] = set()
    for span in spans:
        key = (span.kind, span.subject.lower(), span.text.lower(), span.source_section.lower())
        if key not in seen:
            seen.add(key)
            result.append(span)
    return result


def extract_evidence_spans(sections: Sequence[Section]) -> list[EvidenceSpan]:
    all_spans: list[EvidenceSpan] = []
    index = 1
    for section in sections:
        list_spans, index = extract_list_evidence(section, index)
        sentence_spans, index = extract_sentence_evidence(section, index)
        all_spans.extend(list_spans)
        all_spans.extend(sentence_spans)
    return dedupe_spans(all_spans)


def choose_core_span(spans: Sequence[EvidenceSpan]) -> EvidenceSpan:
    return sorted(spans, key=lambda span: (CORE_KIND_PRIORITY.get(span.kind, 99), len(span.text)))[0]


def build_section_summary(subject: str, spans: Sequence[EvidenceSpan]) -> str:
    core = choose_core_span(spans)
    if core.kind == "definition" and core.detail:
        return clip_text(f"{subject}: {core.detail}", 180)
    if core.kind == "count" and core.count is not None:
        return clip_text(build_count_claim(subject, core.count, core.counted_thing), 180)
    if core.kind == "list" and core.items:
        return clip_text(f"{subject} gồm {', '.join(core.items[:4])}", 180)
    return clip_text(span_claim_text(core), 180)


def build_learning_objective(subject: str, spans: Sequence[EvidenceSpan]) -> str:
    kinds = {span.kind for span in spans}
    if "comparison" in kinds:
        return f"Phân biệt {subject} với các khái niệm gần nhau trong tài liệu."
    if "process" in kinds or "list" in kinds:
        return f"Hiểu cấu phần và cách vận hành của {subject}."
    if "cause_effect" in kinds or "warning" in kinds:
        return f"Hiểu khi nào nên áp dụng và hiểu đúng về {subject}."
    if "count" in kinds:
        return f"Nắm ý chính và các con số quan trọng của {subject}."
    return f"Nắm định nghĩa và ý chính của {subject}."


def build_concept_packs(sections: Sequence[Section], spans: Sequence[EvidenceSpan]) -> list[ConceptPack]:
    section_lookup = {(section.source_file, section.section_order): section for section in sections}
    spans_by_subject: dict[tuple[str, int, str], list[EvidenceSpan]] = defaultdict(list)
    for span in spans:
        subject = normalize_subject_phrase(span.subject, span.source_section)
        if not is_valid_subject(subject):
            subject = normalize_subject_phrase(span.source_section, span.source_section)
        spans_by_subject[(span.source_file, span.section_order, subject)].append(span)
    packs: list[ConceptPack] = []
    for (source_file, section_order, subject), group_spans in spans_by_subject.items():
        section = section_lookup[(source_file, section_order)]
        ordered_spans = sorted(group_spans, key=lambda span: (CORE_KIND_PRIORITY.get(span.kind, 99), span.span_id))[:6]
        core_span = choose_core_span(ordered_spans)
        fallback_subject = normalize_subject_phrase(section.title, section.title)
        final_subject = subject if is_valid_subject(subject) else fallback_subject
        if not is_valid_subject(final_subject):
            continue
        packs.append(
            ConceptPack(
                concept_id=make_concept_id(section, final_subject),
                source_file=source_file,
                source_section=section.title,
                section_order=section_order,
                subject=final_subject,
                learning_objective=build_learning_objective(final_subject, ordered_spans),
                core_claim=span_claim_text(core_span),
                section_summary=build_section_summary(final_subject, ordered_spans),
                supporting_evidence=ordered_spans,
            )
        )
    packs_by_file: dict[str, list[ConceptPack]] = defaultdict(list)
    for pack in packs:
        packs_by_file[pack.source_file].append(pack)
    for file_packs in packs_by_file.values():
        file_packs.sort(key=lambda pack: pack.section_order)
        for pack in file_packs:
            neighbors = sorted((other for other in file_packs if other.concept_id != pack.concept_id), key=lambda other: (abs(other.section_order - pack.section_order), other.section_order))
            for other in neighbors:
                if other.subject.lower() != pack.subject.lower() and other.subject not in pack.neighbor_concepts:
                    pack.neighbor_concepts.append(other.subject)
                if len(pack.neighbor_concepts) >= 6:
                    break
            related: list[str] = []
            for span in pack.supporting_evidence:
                related.extend(span.related_subjects)
            for item in related + pack.neighbor_concepts[:3]:
                if item and item.lower() != pack.subject.lower() and item not in pack.common_confusions:
                    pack.common_confusions.append(item)
            pack.common_confusions = pack.common_confusions[:4]
    return packs
