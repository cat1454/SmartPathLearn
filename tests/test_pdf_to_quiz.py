import re
import unittest
from pathlib import Path

from pdf_to_quiz_core.extraction import Section, extract_evidence_spans
from pdf_to_quiz_core.generation import generate_quiz_artifacts
from pdf_to_quiz_core.schema import QUESTION_FAMILY_ORDER


ROOT = Path(__file__).resolve().parents[1]


class EvidenceExtractionTests(unittest.TestCase):
    def test_negative_definition_becomes_warning(self) -> None:
        section = Section(
            source_file="sample.pdf",
            title="Agile",
            content="Agile không phải là một bộ công cụ hay một phương pháp duy nhất.",
            section_order=1,
        )
        spans = extract_evidence_spans([section])
        self.assertFalse(any(span.kind == "definition" and span.subject.lower() == "agile không phải" for span in spans))
        self.assertTrue(any(span.kind == "warning" and span.subject == "Agile" for span in spans))

    def test_count_subject_is_not_broken_by_year(self) -> None:
        section = Section(
            source_file="sample.pdf",
            title="Agile",
            content="Tuyên ngôn Agile (Agile Manifesto, 2001) bao gồm 4 giá trị và 12 nguyên tắc cốt lõi giúp định hướng nhóm phát triển.",
            section_order=1,
        )
        spans = extract_evidence_spans([section])
        count_spans = [span for span in spans if span.kind == "count"]
        self.assertTrue(count_spans)
        self.assertTrue(any(span.subject == "Tuyên ngôn Agile" for span in count_spans))
        self.assertFalse(any(span.subject.startswith("2001") for span in count_spans))

    def test_extracts_list_and_comparison(self) -> None:
        section = Section(
            source_file="sample.pdf",
            title="Vai trò Scrum",
            content=(
                "- Product Owner\n"
                "- Scrum Master\n"
                "- Developers\n"
                "Scrum Master khác với Product Owner ở trọng tâm phục vụ nhóm."
            ),
            section_order=2,
        )
        spans = extract_evidence_spans([section])
        self.assertTrue(any(span.kind == "list" for span in spans))
        self.assertTrue(any(span.kind == "comparison" for span in spans))


class IntegrationTests(unittest.TestCase):
    def test_agile_pdf_avoids_broken_stems(self) -> None:
        questions, _packs = generate_quiz_artifacts(
            ROOT / "mnt/data/3.PhuongPhap_Agile.pdf",
            max_questions=20,
            seed=42,
            mode="bank",
            llm_model=None,
        )
        self.assertTrue(questions)
        self.assertFalse(any("2001)" in question.question for question in questions))
        self.assertFalse(any(re.match(r"^[\d\W]+", question.question) for question in questions))
        self.assertTrue(any(question.question_family in {"mechanism", "contrast", "application"} for question in questions))

    def test_learning_path_keeps_family_order(self) -> None:
        questions, _packs = generate_quiz_artifacts(
            ROOT / "mnt/data/2.QuyTrinhPhanMem.pdf",
            max_questions=12,
            seed=42,
            mode="learning_path",
            llm_model=None,
        )
        self.assertTrue(questions)
        self.assertEqual(
            [question.section_order for question in questions],
            sorted(question.section_order for question in questions),
        )
        families_by_concept: dict[str, list[str]] = {}
        for question in questions:
            families_by_concept.setdefault(question.concept_id, []).append(question.question_family)
        for families in families_by_concept.values():
            order = [QUESTION_FAMILY_ORDER[family] for family in families]
            self.assertEqual(order, sorted(order))


if __name__ == "__main__":
    unittest.main()
