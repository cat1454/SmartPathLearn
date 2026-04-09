import { t } from "./i18n.js";

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

const SOURCE_PACK_SKELETON = {
  payload_type: "source_pack",
  source_pack_ref: "",
  subject: "",
  grade_level: "",
  chapter_title: "",
  lesson_title: "",
  learning_objectives: [],
  key_concepts: [],
  formulas: [],
  events_or_milestones: [],
  examples: [],
  common_mistakes: [],
  prerequisites: [],
  source_notes: [],
  coverage_warning: "",
};

const AUTHORING_SKELETONS = {
  case_mission: {
    scenario: "",
    task: "",
    expected_points: [],
    success_criteria: [],
    hint_optional: "",
  },
  error_hunt: {
    artifact: "",
    error_count_expected: 0,
    error_categories: [],
    reference_points: [],
  },
  explain_back: {
    teaching_prompt: "",
    target_audience: "",
    expected_points: [],
    clarity_rubric: [],
  },
  mini_project: {
    brief: "",
    deliverable_type: "",
    constraints: [],
    rubric: [],
  },
  debate_defend: {
    claim: "",
    position_task: "",
    evidence_rules: [],
    rubric: [],
  },
};

export function buildSourcePackPrompt(lessonShell) {
  return [
    t("prompt.source_pack_header"),
    "",
    t("prompt.lesson_shell"),
    pretty(lessonShell),
    "",
    t("prompt.source_pack_requirements"),
    `- ${t("prompt.source_pack_rule_1")}`,
    `- ${t("prompt.source_pack_rule_2")}`,
    `- ${t("prompt.source_pack_rule_3")}`,
    `- ${t("prompt.source_pack_rule_4")}`,
    "",
    t("prompt.return_block"),
    "<<<SOURCE_PACK_V1_START>>>",
    pretty(SOURCE_PACK_SKELETON),
    "<<<SOURCE_PACK_V1_END>>>",
  ].join("\n");
}

export function buildActivityPrompt(sourcePackPayload, activityType) {
  const activityEnvelope = {
    payload_type: "activity_authoring",
    activity_type: activityType,
    activity_id: "",
    source_pack_ref: sourcePackPayload.source_pack_ref,
    document_title: sourcePackPayload.chapter_title,
    lesson_title: sourcePackPayload.lesson_title,
    student_level: sourcePackPayload.grade_level,
    instructions: [],
    activity_data: AUTHORING_SKELETONS[activityType],
  };

  return [
    t("prompt.activity_header", { activityType }),
    "",
    t("prompt.source_pack_label"),
    pretty(sourcePackPayload),
    "",
    t("prompt.activity_requirements"),
    `- ${t("prompt.activity_rule_1")}`,
    `- ${t("prompt.activity_rule_2")}`,
    `- ${t("prompt.activity_rule_3")}`,
    "",
    t("prompt.return_block"),
    "<<<ACTIVITY_PAYLOAD_V2_START>>>",
    pretty(activityEnvelope),
    "<<<ACTIVITY_PAYLOAD_V2_END>>>",
  ].join("\n");
}

export function buildFeedbackPrompt(sourcePackPayload, activityPayload, submission) {
  const feedbackEnvelope = {
    payload_type: "activity_feedback",
    activity_type: activityPayload.activity_type,
    activity_id: activityPayload.activity_id,
    student_submission: submission,
    feedback: {
      overall_verdict: "partial",
      strengths: [],
      gaps: [],
      misconceptions: [],
      next_step: "",
      score_optional: null,
    },
  };

  return [
    t("prompt.feedback_header", { activityType: activityPayload.activity_type }),
    "",
    t("prompt.source_pack_label"),
    pretty(sourcePackPayload),
    "",
    t("prompt.activity_label"),
    pretty(activityPayload),
    "",
    t("prompt.student_submission"),
    pretty(submission),
    "",
    t("prompt.feedback_requirements"),
    `- ${t("prompt.feedback_rule_1")}`,
    `- ${t("prompt.feedback_rule_2")}`,
    `- ${t("prompt.feedback_rule_3")}`,
    "",
    t("prompt.return_block"),
    "<<<ACTIVITY_FEEDBACK_V2_START>>>",
    pretty(feedbackEnvelope),
    "<<<ACTIVITY_FEEDBACK_V2_END>>>",
  ].join("\n");
}

export function buildRepairPrompt(expectedMarker, issues, brokenOutput) {
  const issueLines = issues.length
    ? issues.map((issue) => `- ${issue.path}: ${issue.message}`).join("\n")
    : `- ${t("prompt.no_issue_default")}`;

  return [
    t("prompt.repair_header", { marker: expectedMarker }),
    "",
    t("prompt.repair_issues"),
    issueLines,
    "",
    t("prompt.feedback_requirements"),
    `- ${t("prompt.repair_rule_1")}`,
    `- ${t("prompt.repair_rule_2")}`,
    `- ${t("prompt.repair_rule_3")}`,
    "",
    t("prompt.previous_payload"),
    brokenOutput || t("prompt.empty_payload"),
  ].join("\n");
}
