from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

try:
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover - dependency gate for local envs
    TestClient = None

if TestClient is not None:
    from handoff_api.main import create_app
else:  # pragma: no cover - dependency gate for local envs
    create_app = None


ROOT = Path(__file__).resolve().parents[1]
TEST_TEMP_ROOT = ROOT / ".tmp_testdata"
TEST_TEMP_ROOT.mkdir(exist_ok=True)


def marked(marker: str, payload: dict) -> str:
    pairs = {
        "SOURCE_PACK_V1": ("<<<SOURCE_PACK_V1_START>>>", "<<<SOURCE_PACK_V1_END>>>"),
        "ACTIVITY_PAYLOAD_V2": ("<<<ACTIVITY_PAYLOAD_V2_START>>>", "<<<ACTIVITY_PAYLOAD_V2_END>>>"),
        "ACTIVITY_FEEDBACK_V2": ("<<<ACTIVITY_FEEDBACK_V2_START>>>", "<<<ACTIVITY_FEEDBACK_V2_END>>>"),
    }
    start, end = pairs[marker]
    return f"{start}\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n{end}"


def sample_source_pack() -> dict:
    return {
        "payload_type": "source_pack",
        "source_pack_ref": "",
        "subject": "Sinh hoc",
        "grade_level": "lop_8",
        "chapter_title": "He co quan",
        "lesson_title": "He ho hap",
        "learning_objectives": ["Nhan biet vai tro cua he ho hap"],
        "key_concepts": ["Trao doi khi", "Oxy"],
        "formulas": [],
        "events_or_milestones": [],
        "examples": ["Kho tho khi van dong manh"],
        "common_mistakes": ["Nham he ho hap voi he tuan hoan"],
        "prerequisites": ["Biet co the can oxy"],
        "source_notes": ["Chi dung du lieu trong bai hoc."],
        "coverage_warning": "",
    }


def sample_activity(source_pack_ref: str) -> dict:
    return {
        "payload_type": "activity_authoring",
        "activity_type": "case_mission",
        "activity_id": "",
        "source_pack_ref": source_pack_ref,
        "document_title": "He ho hap",
        "lesson_title": "Co che trao doi khi",
        "student_level": "lop_8",
        "instructions": ["Doc tinh huong", "Tra loi ngan gon theo y"],
        "activity_data": {
            "scenario": "Mot benh nhan co bieu hien kho tho sau van dong.",
            "task": "Xac dinh he co quan lien quan va giai thich.",
            "expected_points": ["Nhan ra he ho hap", "Noi duoc vai tro cua oxy"],
            "success_criteria": ["Dung he co quan", "Co giai thich bang kien thuc trong bai"],
            "hint_optional": "Tap trung vao trao doi khi.",
        },
    }


def sample_feedback(activity_id: str) -> dict:
    return {
        "payload_type": "activity_feedback",
        "activity_type": "case_mission",
        "activity_id": activity_id,
        "student_submission": {
            "response_type": "free_text",
            "response_content": "Em chon he ho hap vi benh nhan kho tho va thieu oxy.",
        },
        "feedback": {
            "overall_verdict": "partial",
            "strengths": ["Da xac dinh dung he ho hap"],
            "gaps": ["Chua noi ro co che trao doi khi"],
            "misconceptions": [],
            "next_step": "Bo sung vai tro dua oxy vao co the.",
            "score_optional": "7/10",
            "missed_expected_points": ["Lien he trieu chung voi thieu oxy"],
        },
    }


@unittest.skipIf(TestClient is None, "fastapi is not installed")
class HandoffApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = TEST_TEMP_ROOT / self._testMethodName
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True, exist_ok=True)
        data_file = self.test_dir / "handoff-store.json"
        self.client = TestClient(create_app(data_file=data_file))

    def tearDown(self) -> None:
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_validate_source_pack_normalizes_payload(self) -> None:
        response = self.client.post("/source-packs/validate", json={"raw_text": marked("SOURCE_PACK_V1", sample_source_pack())})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["marker"], "SOURCE_PACK_V1")
        self.assertEqual(body["normalized"]["payload_type"], "source_pack")
        self.assertEqual(body["normalized"]["source_notes"], ["Chi dung du lieu trong bai hoc."])
        self.assertEqual(body["normalized"]["formulas"], [])
        self.assertEqual(body["normalized"]["events_or_milestones"], [])

    def test_create_source_pack_and_get_by_id(self) -> None:
        create_response = self.client.post("/source-packs", json={"raw_text": marked("SOURCE_PACK_V1", sample_source_pack())})
        self.assertEqual(create_response.status_code, 201)
        created = create_response.json()
        source_pack_id = created["id"]
        self.assertEqual(created["payload"]["source_pack_ref"], source_pack_id)

        get_response = self.client.get(f"/source-packs/{source_pack_id}")
        self.assertEqual(get_response.status_code, 200)
        loaded = get_response.json()
        self.assertEqual(loaded["id"], source_pack_id)
        self.assertEqual(loaded["payload"]["lesson_title"], "He ho hap")

    def test_activity_validate_requires_existing_source_pack(self) -> None:
        payload = sample_activity("sp_missing_001")
        response = self.client.post("/activities/validate", json={"raw_text": marked("ACTIVITY_PAYLOAD_V2", payload)})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["ok"])
        issue_codes = {issue["code"] for issue in body["issues"]}
        self.assertIn("reference_not_found", issue_codes)

    def test_validate_source_pack_rejects_string_source_notes(self) -> None:
        payload = sample_source_pack()
        payload["source_notes"] = "ghi chu don"
        response = self.client.post("/source-packs/validate", json={"raw_text": marked("SOURCE_PACK_V1", payload)})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["ok"])
        issue_codes = {issue["code"] for issue in body["issues"]}
        self.assertIn("invalid_field_type", issue_codes)

    def test_validate_activity_authoring_requires_activity_id_field(self) -> None:
        source_pack_response = self.client.post("/source-packs", json={"raw_text": marked("SOURCE_PACK_V1", sample_source_pack())})
        self.assertEqual(source_pack_response.status_code, 201)
        source_pack_id = source_pack_response.json()["id"]

        payload = sample_activity(source_pack_id)
        del payload["activity_id"]
        response = self.client.post("/activities/validate", json={"raw_text": marked("ACTIVITY_PAYLOAD_V2", payload)})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["ok"])
        issue_codes = {issue["code"] for issue in body["issues"]}
        self.assertIn("missing_required_field", issue_codes)

    def test_full_activity_submission_feedback_flow(self) -> None:
        source_pack_response = self.client.post("/source-packs", json={"raw_text": marked("SOURCE_PACK_V1", sample_source_pack())})
        self.assertEqual(source_pack_response.status_code, 201)
        source_pack_id = source_pack_response.json()["id"]

        activity_payload = sample_activity(source_pack_id)
        create_activity_response = self.client.post("/activities", json={"raw_text": marked("ACTIVITY_PAYLOAD_V2", activity_payload)})
        self.assertEqual(create_activity_response.status_code, 201)
        activity = create_activity_response.json()
        activity_id = activity["id"]
        self.assertEqual(activity["payload"]["source_pack_ref"], source_pack_id)
        self.assertTrue(activity["payload"]["activity_id"])

        detail_response = self.client.get(f"/activities/{activity_id}")
        self.assertEqual(detail_response.status_code, 200)
        detail = detail_response.json()
        self.assertIsNone(detail["submission"])
        self.assertIsNone(detail["feedback"])

        submission_response = self.client.post(
            f"/activities/{activity_id}/submission",
            json={"response_type": "free_text", "response_content": "Em chon he ho hap vi benh nhan kho tho."},
        )
        self.assertEqual(submission_response.status_code, 200)

        feedback_payload = sample_feedback(activity_id)
        validate_feedback_response = self.client.post(
            f"/activities/{activity_id}/feedback/validate",
            json={"raw_text": marked("ACTIVITY_FEEDBACK_V2", feedback_payload)},
        )
        self.assertEqual(validate_feedback_response.status_code, 200)
        self.assertTrue(validate_feedback_response.json()["ok"])

        save_feedback_response = self.client.post(
            f"/activities/{activity_id}/feedback",
            json={"raw_text": marked("ACTIVITY_FEEDBACK_V2", feedback_payload)},
        )
        self.assertEqual(save_feedback_response.status_code, 200)
        saved_feedback = save_feedback_response.json()
        self.assertEqual(saved_feedback["activity_id"], activity_id)

        detail_after_feedback = self.client.get(f"/activities/{activity_id}")
        self.assertEqual(detail_after_feedback.status_code, 200)
        detail_body = detail_after_feedback.json()
        self.assertIsNotNone(detail_body["submission"])
        self.assertIsNotNone(detail_body["feedback"])
        self.assertEqual(detail_body["feedback"]["payload"]["feedback"]["overall_verdict"], "partial")

    def test_validate_rejects_text_outside_marker(self) -> None:
        raw_text = "ghi chu ngoai block\n" + marked("SOURCE_PACK_V1", sample_source_pack())
        response = self.client.post("/source-packs/validate", json={"raw_text": raw_text})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["ok"])
        issue_codes = {issue["code"] for issue in body["issues"]}
        self.assertIn("text_outside_marker", issue_codes)

    def test_validate_feedback_rejects_invalid_response_type(self) -> None:
        source_pack_response = self.client.post("/source-packs", json={"raw_text": marked("SOURCE_PACK_V1", sample_source_pack())})
        self.assertEqual(source_pack_response.status_code, 201)
        source_pack_id = source_pack_response.json()["id"]

        create_activity_response = self.client.post(
            "/activities",
            json={"raw_text": marked("ACTIVITY_PAYLOAD_V2", sample_activity(source_pack_id))},
        )
        self.assertEqual(create_activity_response.status_code, 201)
        activity_id = create_activity_response.json()["id"]

        invalid_feedback = sample_feedback(activity_id)
        invalid_feedback["student_submission"]["response_type"] = "plain_text"
        response = self.client.post(
            f"/activities/{activity_id}/feedback/validate",
            json={"raw_text": marked("ACTIVITY_FEEDBACK_V2", invalid_feedback)},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["ok"])
        issue_codes = {issue["code"] for issue in body["issues"]}
        self.assertIn("response_type_invalid", issue_codes)

    def test_handoff_ui_routes_return_html_shell(self) -> None:
        paths = [
            "/handoff",
            "/handoff/source-packs/new",
            "/handoff/source-packs/sp_demo_001",
            "/handoff/activities/new?sourcePackId=sp_demo_001",
            "/handoff/activities/act_demo_001",
            "/handoff/activities/act_demo_001/submission",
            "/handoff/activities/act_demo_001/feedback",
        ]
        for path in paths:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn("AI Document Handoff", response.text)
            self.assertIn('id="app"', response.text)

    def test_handoff_ui_assets_are_served(self) -> None:
        app_response = self.client.get("/handoff/assets/app.js")
        self.assertEqual(app_response.status_code, 200)
        self.assertIn("renderSourcePackNewPage", app_response.text)
        self.assertIn("data-set-locale", app_response.text)

        components_response = self.client.get("/handoff/assets/components.js")
        self.assertEqual(components_response.status_code, 200)
        self.assertIn("renderStatusStrip", components_response.text)
        self.assertIn("language-toggle", components_response.text)

        i18n_response = self.client.get("/handoff/assets/i18n.js")
        self.assertEqual(i18n_response.status_code, 200)
        self.assertIn("Tiếng Việt", i18n_response.text)
        self.assertIn("English", i18n_response.text)

        css_response = self.client.get("/handoff/assets/styles.css")
        self.assertEqual(css_response.status_code, 200)
        self.assertIn(".shell", css_response.text)
        self.assertIn(".status-strip", css_response.text)
        self.assertIn(".language-toggle", css_response.text)
