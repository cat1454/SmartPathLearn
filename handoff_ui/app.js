import { api } from "./api.js";
import {
  activityTypeMeta,
  renderActivityPreview,
  renderActivityTypePicker,
  renderCard,
  renderErrorState,
  renderFeedbackSummary,
  renderFlash,
  renderJsonCard,
  renderMarkerGuide,
  renderNavigationRow,
  renderPayloadPreview,
  renderPromptCard,
  renderShell,
  renderSourcePackOverview,
  renderStatusStrip,
  renderSubmissionPreview,
  renderSummaryCard,
  renderValidationPanel,
} from "./components.js";
import { getLocale, initLocale, isLocale, setLocale, t } from "./i18n.js";
import { buildActivityPrompt, buildFeedbackPrompt, buildRepairPrompt, buildSourcePackPrompt } from "./prompts.js";
import { parseRoute } from "./router.js";

initLocale();

const root = document.querySelector("#app");

function createOperationStatus() {
  return {
    load: "idle",
    validation: "idle",
    save: "idle",
    note: "",
  };
}

const state = {
  flash: null,
  lessonShell: {
    document_title: "",
    lesson_title: "",
    student_level: "",
    attached_files_note: "",
  },
  sourcePackDraft: {
    rawText: "",
    validation: null,
  },
  activityDraft: {
    selectedType: "case_mission",
    rawText: "",
    validation: null,
  },
  submissionDrafts: {},
  feedbackDrafts: {},
  status: {
    sourcePack: createOperationStatus(),
    activity: createOperationStatus(),
    submission: createOperationStatus(),
    feedback: createOperationStatus(),
  },
  cache: {
    sourcePacks: {},
    activityDetails: {},
  },
};

function navigate(path, replace = false) {
  if (replace) {
    window.history.replaceState({}, "", path);
  } else {
    window.history.pushState({}, "", path);
  }
  render().catch((error) => showFatalError(error, "loading"));
}

function setFlash(message, tone = "info") {
  state.flash = { message, tone };
}

function takeFlash() {
  const flash = state.flash;
  state.flash = null;
  return flash;
}

function getTextareaValue(id) {
  return document.getElementById(id)?.value ?? "";
}

function getActivityTypeTitle(activityType) {
  return t(activityTypeMeta[activityType]?.titleKey || activityType);
}

function getActivityTypeDescription(activityType) {
  return t(activityTypeMeta[activityType]?.descriptionKey || activityType);
}

function getErrorMessage(error) {
  return error?.payload?.detail?.message || error?.payload?.message || error?.message || t("common.unknown_error");
}

function updateStatus(scope, patch) {
  state.status[scope] = {
    ...state.status[scope],
    ...patch,
  };
}

function summarizeValidation(validation, successKey, failureKey) {
  if (!validation) {
    return "";
  }
  const issues = Array.isArray(validation.issues) ? validation.issues : [];
  const errorCount = issues.filter((issue) => issue.severity === "error").length;
  const warningCount = issues.filter((issue) => issue.severity === "warning").length;
  if (validation.ok) {
    return t(successKey);
  }
  const counts = [];
  if (errorCount) {
    counts.push(t("validation.count_error", { count: errorCount }));
  }
  if (warningCount) {
    counts.push(t("validation.count_warning", { count: warningCount }));
  }
  return counts.length ? `${t(failureKey)} (${counts.join(", ")})` : t(failureKey);
}

function setValidationStatus(scope, validation, successKey, failureKey) {
  updateStatus(scope, {
    validation: validation?.ok ? "valid" : "invalid",
    note: summarizeValidation(validation, successKey, failureKey),
  });
}

function copyElementText(targetId) {
  const node = document.getElementById(targetId);
  if (!node) {
    return;
  }
  const text = "value" in node ? node.value : node.textContent || "";
  navigator.clipboard.writeText(text).then(() => {
    setFlash(t("common.copy_success"), "success");
    render().catch((error) => showFatalError(error, "loading"));
  });
}

async function fetchSourcePack(sourcePackId) {
  if (!sourcePackId) {
    throw new Error(getLocale() === "en" ? "Missing source pack id." : "Thiếu source pack id.");
  }
  if (!state.cache.sourcePacks[sourcePackId]) {
    state.cache.sourcePacks[sourcePackId] = await api.getSourcePack(sourcePackId);
  }
  return state.cache.sourcePacks[sourcePackId];
}

async function fetchActivityDetail(activityId, force = false) {
  if (!activityId) {
    throw new Error(getLocale() === "en" ? "Missing activity id." : "Thiếu activity id.");
  }
  if (force || !state.cache.activityDetails[activityId]) {
    state.cache.activityDetails[activityId] = await api.getActivity(activityId);
  }
  return state.cache.activityDetails[activityId];
}

function renderContextFromSourcePack(record) {
  if (!record) {
    return renderCard(t("source_pack.overview_title"), `<p class="muted">${t("common.no_source_pack")}</p>`);
  }
  return [
    renderSourcePackOverview(record.payload),
    renderSummaryCard(t("common.canh_bao"), [
      { label: t("source_pack_detail.coverage_warning"), value: record.payload.coverage_warning || t("common.empty") },
      { label: t("source_pack_detail.key_concepts"), value: String(record.payload.key_concepts.length) },
    ]),
  ].join("");
}

function renderRepairCard(marker, validation, rawText) {
  if (!validation || validation.ok) {
    return "";
  }
  const prompt = buildRepairPrompt(marker, validation.issues || [], rawText || "");
  const title = getLocale() === "en" ? "Repair prompt" : "Prompt sửa payload";
  const helper = getLocale() === "en" ? "Copy this prompt and ask AI to repair the schema." : "Copy prompt này sang AI để sửa format.";
  return renderPromptCard(title, prompt, `${marker.toLowerCase()}-repair-prompt`, helper);
}

function syncLessonShellFromInputs() {
  state.lessonShell = {
    document_title: document.getElementById("lesson-document-title")?.value ?? "",
    lesson_title: document.getElementById("lesson-title")?.value ?? "",
    student_level: document.getElementById("lesson-student-level")?.value ?? "",
    attached_files_note: document.getElementById("lesson-files-note")?.value ?? "",
  };
}

function attachPayloadDirtyReset(textareaId, scope, draftGetter, noteKey) {
  document.getElementById(textareaId)?.addEventListener("change", () => {
    const draft = draftGetter();
    const nextRawText = getTextareaValue(textareaId);
    const changed = draft.rawText !== nextRawText;
    draft.rawText = nextRawText;
    if (changed && draft.validation) {
      draft.validation = null;
      updateStatus(scope, {
        validation: "idle",
        save: "idle",
        note: t(noteKey),
      });
      render().catch((error) => showFatalError(error, "loading"));
    }
  });
}

async function renderSourcePackNewPage() {
  updateStatus("sourcePack", { load: "ready" });
  const prompt = buildSourcePackPrompt(state.lessonShell);
  const validation = state.sourcePackDraft.validation;

  root.innerHTML = renderShell({
    title: t("source_pack.title"),
    description: t("source_pack.description"),
    currentStep: "source_pack",
    flash: renderFlash(takeFlash()),
    main: [
      renderStatusStrip(state.status.sourcePack),
      renderCard(
        t("source_pack.lesson_shell"),
        `
          <div class="grid-two">
            <div class="field-stack">
              <label for="lesson-document-title">${t("source_pack.document_title")}</label>
              <input class="input" id="lesson-document-title" value="${state.lessonShell.document_title}">
            </div>
            <div class="field-stack">
              <label for="lesson-title">${t("source_pack.lesson_title")}</label>
              <input class="input" id="lesson-title" value="${state.lessonShell.lesson_title}">
            </div>
            <div class="field-stack">
              <label for="lesson-student-level">${t("source_pack.student_level")}</label>
              <input class="input" id="lesson-student-level" value="${state.lessonShell.student_level}">
            </div>
            <div class="field-stack">
              <label for="lesson-files-note">${t("source_pack.attached_files_note")}</label>
              <input class="input" id="lesson-files-note" value="${state.lessonShell.attached_files_note}">
            </div>
          </div>
        `,
      ),
      renderPromptCard(t("source_pack.prompt_title"), prompt, "source-pack-prompt", t("source_pack.prompt_helper")),
      renderCard(
        t("source_pack.payload_title"),
        `
          <div class="form-actions">
            <button class="button secondary" id="validate-source-pack">${t("source_pack.validate")}</button>
            <button class="button primary" id="save-source-pack"${validation?.ok ? "" : " disabled"}>${t("source_pack.save")}</button>
          </div>
          <div class="field-stack">
            <label for="source-pack-raw">${t("source_pack.raw_label")}</label>
            <textarea class="textarea" id="source-pack-raw" placeholder="${t("source_pack.raw_placeholder")}">${state.sourcePackDraft.rawText}</textarea>
          </div>
        `,
      ),
      renderValidationPanel(validation, "SOURCE_PACK_V1"),
      renderMarkerGuide("SOURCE_PACK_V1"),
      renderRepairCard("SOURCE_PACK_V1", validation, state.sourcePackDraft.rawText),
      renderPayloadPreview(t("source_pack.normalized_title"), validation, t("source_pack.normalized_empty")),
    ].join(""),
    context: [
      renderCard(t("common.workflow_status"), `<p class="muted">${t("source_pack.context_status_body")}</p>`),
      renderCard(t("common.schema_quick"), `<p class="muted">${t("source_pack.context_schema_body")}</p>`),
    ].join(""),
  });

  document.getElementById("validate-source-pack")?.addEventListener("click", async () => {
    syncLessonShellFromInputs();
    state.sourcePackDraft.rawText = getTextareaValue("source-pack-raw");
    updateStatus("sourcePack", {
      validation: "validating",
      save: "idle",
      note: t("source_pack.validate_running"),
    });
    render().catch((error) => showFatalError(error, "loading"));
    try {
      state.sourcePackDraft.validation = await api.validateSourcePack(state.sourcePackDraft.rawText);
      setValidationStatus("sourcePack", state.sourcePackDraft.validation, "source_pack.validate_ok", "source_pack.validate_fail");
      render().catch((error) => showFatalError(error, "loading"));
    } catch (error) {
      handleApiError(error, {
        scope: "sourcePack",
        draftKey: "sourcePackDraft",
        stage: "validation",
        successKey: "source_pack.validate_ok",
        failureKey: "source_pack.validate_fail",
        saveFailedKey: "source_pack.save_failed",
      });
    }
  });

  document.getElementById("save-source-pack")?.addEventListener("click", async () => {
    try {
      state.sourcePackDraft.rawText = getTextareaValue("source-pack-raw");
      updateStatus("sourcePack", {
        save: "saving",
        note: t("source_pack.save_running"),
      });
      render().catch((error) => showFatalError(error, "loading"));
      const record = await api.createSourcePack(state.sourcePackDraft.rawText);
      state.cache.sourcePacks[record.id] = record;
      updateStatus("sourcePack", {
        save: "saved",
        note: t("source_pack.save_success"),
      });
      setFlash(t("source_pack.save_success"), "success");
      navigate(`/handoff/activities/new?sourcePackId=${encodeURIComponent(record.id)}`);
    } catch (error) {
      handleApiError(error, {
        scope: "sourcePack",
        draftKey: "sourcePackDraft",
        stage: "save",
        successKey: "source_pack.validate_ok",
        failureKey: "source_pack.validate_fail",
        saveFailedKey: "source_pack.save_failed",
      });
    }
  });

  attachPayloadDirtyReset("source-pack-raw", "sourcePack", () => state.sourcePackDraft, "source_pack.dirty_note");
}

async function renderSourcePackDetailPage(sourcePackId) {
  const record = await fetchSourcePack(sourcePackId);
  root.innerHTML = renderShell({
    title: t("source_pack_detail.title"),
    description: t("source_pack_detail.description"),
    currentStep: "choose_format",
    flash: renderFlash(takeFlash()),
    main: [
      renderSourcePackOverview(record.payload),
      renderJsonCard(t("source_pack_detail.payload_title"), record.payload),
      renderNavigationRow([
        `<button class="button primary" data-navigate="/handoff/activities/new?sourcePackId=${encodeURIComponent(record.id)}">${t("source_pack_detail.create_activity")}</button>`,
      ]),
    ].join(""),
    context: renderContextFromSourcePack(record),
  });
}

async function renderActivityCreatePage(sourcePackId) {
  if (!sourcePackId) {
    root.innerHTML = renderShell({
      title: t("activity.missing_source_pack_title"),
      description: t("activity.missing_source_pack_description"),
      currentStep: "choose_format",
      flash: renderFlash(takeFlash()),
      main: renderErrorState(t("activity.missing_source_pack_body")),
      context: renderCard(t("common.link"), `<button class="button primary" data-navigate="/handoff/source-packs/new">${t("activity.missing_source_pack_action")}</button>`),
    });
    return;
  }

  updateStatus("activity", { load: "ready" });
  const sourcePackRecord = await fetchSourcePack(sourcePackId);
  const validation = state.activityDraft.validation;
  const prompt = buildActivityPrompt(sourcePackRecord.payload, state.activityDraft.selectedType);

  root.innerHTML = renderShell({
    title: t("activity.title"),
    description: t("activity.description"),
    currentStep: "activity_authoring",
    flash: renderFlash(takeFlash()),
    main: [
      renderStatusStrip(state.status.activity),
      renderSourcePackOverview(sourcePackRecord.payload),
      renderActivityTypePicker(state.activityDraft.selectedType),
      renderPromptCard(t("activity.prompt_title"), prompt, "activity-prompt", t("activity.prompt_helper")),
      renderCard(
        t("activity.payload_title"),
        `
          <div class="form-actions">
            <button class="button secondary" id="validate-activity">${t("activity.validate")}</button>
            <button class="button primary" id="save-activity"${validation?.ok ? "" : " disabled"}>${t("activity.save")}</button>
          </div>
          <div class="field-stack">
            <label for="activity-raw">${t("activity.raw_label")}</label>
            <textarea class="textarea" id="activity-raw" placeholder="${t("activity.raw_placeholder")}">${state.activityDraft.rawText}</textarea>
          </div>
        `,
      ),
      renderValidationPanel(validation, "ACTIVITY_PAYLOAD_V2"),
      renderMarkerGuide("ACTIVITY_PAYLOAD_V2"),
      renderRepairCard("ACTIVITY_PAYLOAD_V2", validation, state.activityDraft.rawText),
      renderPayloadPreview(t("activity.preview_title"), validation, t("activity.preview_empty")),
      validation?.normalized
        ? renderActivityPreview(validation.normalized)
        : renderCard(t("activity.preview_card_title", { type: getActivityTypeTitle(state.activityDraft.selectedType) }), `<p class="muted">${t("activity.structured_preview_empty")}</p>`),
    ].join(""),
    context: [
      renderContextFromSourcePack(sourcePackRecord),
      renderSummaryCard(t("activity_type.format_selected"), [
        { label: t("activity_type.type"), value: getActivityTypeTitle(state.activityDraft.selectedType) },
        { label: t("activity_type.description"), value: getActivityTypeDescription(state.activityDraft.selectedType) },
      ]),
    ].join(""),
  });

  document.querySelectorAll("[data-activity-type]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activityDraft.selectedType = button.getAttribute("data-activity-type") || "case_mission";
      state.activityDraft.validation = null;
      updateStatus("activity", {
        validation: "idle",
        save: "idle",
        note: t("activity.dirty_note"),
      });
      render().catch((error) => showFatalError(error, "loading"));
    });
  });

  document.getElementById("validate-activity")?.addEventListener("click", async () => {
    state.activityDraft.rawText = getTextareaValue("activity-raw");
    updateStatus("activity", {
      validation: "validating",
      save: "idle",
      note: t("activity.validate_running"),
    });
    render().catch((error) => showFatalError(error, "loading"));
    try {
      state.activityDraft.validation = await api.validateActivity(state.activityDraft.rawText);
      setValidationStatus("activity", state.activityDraft.validation, "activity.validate_ok", "activity.validate_fail");
      render().catch((error) => showFatalError(error, "loading"));
    } catch (error) {
      handleApiError(error, {
        scope: "activity",
        draftKey: "activityDraft",
        stage: "validation",
        successKey: "activity.validate_ok",
        failureKey: "activity.validate_fail",
        saveFailedKey: "activity.save_failed",
      });
    }
  });

  document.getElementById("save-activity")?.addEventListener("click", async () => {
    try {
      state.activityDraft.rawText = getTextareaValue("activity-raw");
      updateStatus("activity", {
        save: "saving",
        note: t("activity.save_running"),
      });
      render().catch((error) => showFatalError(error, "loading"));
      const record = await api.createActivity(state.activityDraft.rawText);
      state.cache.activityDetails[record.id] = { activity: record, submission: null, feedback: null };
      updateStatus("activity", {
        save: "saved",
        note: t("activity.save_success"),
      });
      setFlash(t("activity.save_success"), "success");
      navigate(`/handoff/activities/${encodeURIComponent(record.id)}`);
    } catch (error) {
      handleApiError(error, {
        scope: "activity",
        draftKey: "activityDraft",
        stage: "save",
        successKey: "activity.validate_ok",
        failureKey: "activity.validate_fail",
        saveFailedKey: "activity.save_failed",
      });
    }
  });

  attachPayloadDirtyReset("activity-raw", "activity", () => state.activityDraft, "activity.dirty_note");
}

async function renderActivityDetailPage(activityId) {
  const detail = await fetchActivityDetail(activityId, true);
  const sourcePackRecord = await fetchSourcePack(detail.activity.source_pack_id);
  root.innerHTML = renderShell({
    title: t("activity_detail.title"),
    description: t("activity_detail.description"),
    currentStep: detail.feedback ? "activity_feedback" : detail.submission ? "student_submission" : "activity_authoring",
    flash: renderFlash(takeFlash()),
    main: [
      renderActivityPreview(detail.activity.payload),
      detail.submission
        ? renderSubmissionPreview(detail.submission.submission)
        : renderCard(t("submission.card_title"), `<p class="muted">${t("activity_detail.submission_empty")}</p>`),
      detail.feedback
        ? renderFeedbackSummary(detail.feedback.payload)
        : renderCard(t("feedback_preview.title"), `<p class="muted">${t("activity_detail.feedback_empty")}</p>`),
      renderNavigationRow([
        `<button class="button secondary" data-navigate="/handoff/activities/${encodeURIComponent(activityId)}/submission">${t("activity_detail.open_submission")}</button>`,
        `<button class="button primary" data-navigate="/handoff/activities/${encodeURIComponent(activityId)}/feedback">${t("activity_detail.open_feedback")}</button>`,
      ]),
    ].join(""),
    context: [
      renderContextFromSourcePack(sourcePackRecord),
      renderSummaryCard(t("common.link"), [
        { label: t("activity.activity_id"), value: detail.activity.id },
        { label: t("activity_detail.source_pack"), value: detail.activity.source_pack_id },
        { label: t("activity_detail.activity_type"), value: detail.activity.payload.activity_type },
      ]),
    ].join(""),
  });
}

async function renderSubmissionPage(activityId) {
  updateStatus("submission", { load: "ready" });
  const detail = await fetchActivityDetail(activityId, true);
  const sourcePackRecord = await fetchSourcePack(detail.activity.source_pack_id);
  const existingDraft = state.submissionDrafts[activityId] || detail.submission?.submission || {
    response_type: "free_text",
    response_content: "",
  };
  state.submissionDrafts[activityId] = existingDraft;
  const prompt = buildFeedbackPrompt(sourcePackRecord.payload, detail.activity.payload, existingDraft);

  root.innerHTML = renderShell({
    title: t("submission.title"),
    description: t("submission.description"),
    currentStep: "student_submission",
    flash: renderFlash(takeFlash()),
    main: [
      renderStatusStrip(state.status.submission),
      renderActivityPreview(detail.activity.payload),
      renderCard(
        t("submission.card_title"),
        `
          <div class="field-stack">
            <label for="submission-response-type">${t("submission.response_type")}</label>
            <select class="select" id="submission-response-type">
              <option value="free_text"${existingDraft.response_type === "free_text" ? " selected" : ""}>free_text</option>
              <option value="bullet_points"${existingDraft.response_type === "bullet_points" ? " selected" : ""}>bullet_points</option>
              <option value="short_essay"${existingDraft.response_type === "short_essay" ? " selected" : ""}>short_essay</option>
            </select>
          </div>
          <div class="field-stack">
            <label for="submission-response-content">${t("submission.response_content")}</label>
            <textarea class="textarea" id="submission-response-content">${existingDraft.response_content}</textarea>
          </div>
          <div class="form-actions">
            <button class="button primary" id="save-submission">${t("submission.save")}</button>
            <button class="button secondary" data-navigate="/handoff/activities/${encodeURIComponent(activityId)}/feedback">${t("submission.go_feedback")}</button>
          </div>
        `,
      ),
      renderPromptCard(t("submission.prompt_title"), prompt, "feedback-prompt-from-submission", t("submission.prompt_helper")),
    ].join(""),
    context: [
      renderContextFromSourcePack(sourcePackRecord),
      renderSummaryCard(t("submission.activity_context"), [
        { label: t("feedback.activity"), value: detail.activity.id },
        { label: t("submission.type"), value: detail.activity.payload.activity_type },
      ]),
    ].join(""),
  });

  document.getElementById("save-submission")?.addEventListener("click", async () => {
    const submission = {
      response_type: document.getElementById("submission-response-type")?.value || "free_text",
      response_content: document.getElementById("submission-response-content")?.value || "",
    };
    state.submissionDrafts[activityId] = submission;
    updateStatus("submission", {
      save: "saving",
      note: t("submission.save_running"),
    });
    render().catch((error) => showFatalError(error, "loading"));
    try {
      await api.saveSubmission(activityId, submission);
      await fetchActivityDetail(activityId, true);
      updateStatus("submission", {
        save: "saved",
        note: t("submission.save_success"),
      });
      setFlash(t("submission.save_success"), "success");
      render().catch((error) => showFatalError(error, "loading"));
    } catch (error) {
      handleApiError(error, {
        scope: "submission",
        stage: "save",
        saveFailedKey: "submission.save_failed",
      });
    }
  });
}

async function renderFeedbackPage(activityId) {
  updateStatus("feedback", { load: "ready" });
  const detail = await fetchActivityDetail(activityId, true);
  const sourcePackRecord = await fetchSourcePack(detail.activity.source_pack_id);
  const submission = detail.submission?.submission || state.submissionDrafts[activityId];
  const feedbackDraft = state.feedbackDrafts[activityId] || { rawText: "", validation: null };
  state.feedbackDrafts[activityId] = feedbackDraft;
  const prompt = submission
    ? buildFeedbackPrompt(sourcePackRecord.payload, detail.activity.payload, submission)
    : t("feedback.missing_submission_prompt");

  root.innerHTML = renderShell({
    title: t("feedback.title"),
    description: t("feedback.description"),
    currentStep: "activity_feedback",
    flash: renderFlash(takeFlash()),
    main: [
      renderStatusStrip(state.status.feedback),
      renderActivityPreview(detail.activity.payload),
      submission
        ? renderSubmissionPreview(submission)
        : renderCard(
            t("feedback.submission_missing_title"),
            `<p class="muted">${t("feedback.submission_missing_body")}</p><button class="button primary" data-navigate="/handoff/activities/${encodeURIComponent(activityId)}/submission">${t("feedback.submission_missing_action")}</button>`,
          ),
      renderPromptCard(t("feedback.prompt_title"), prompt, "feedback-prompt", t("feedback.prompt_helper")),
      renderCard(
        t("feedback.payload_title"),
        `
          <div class="form-actions">
            <button class="button secondary" id="validate-feedback"${submission ? "" : " disabled"}>${t("feedback.validate")}</button>
            <button class="button primary" id="save-feedback"${feedbackDraft.validation?.ok ? "" : " disabled"}>${t("feedback.save")}</button>
          </div>
          <div class="field-stack">
            <label for="feedback-raw">${t("feedback.raw_label")}</label>
            <textarea class="textarea" id="feedback-raw" placeholder="${t("feedback.raw_placeholder")}">${feedbackDraft.rawText}</textarea>
          </div>
        `,
      ),
      renderValidationPanel(feedbackDraft.validation, "ACTIVITY_FEEDBACK_V2"),
      renderMarkerGuide("ACTIVITY_FEEDBACK_V2"),
      renderRepairCard("ACTIVITY_FEEDBACK_V2", feedbackDraft.validation, feedbackDraft.rawText),
      renderPayloadPreview(t("feedback.preview_title"), feedbackDraft.validation, t("feedback.preview_empty")),
      feedbackDraft.validation?.normalized
        ? renderFeedbackSummary(feedbackDraft.validation.normalized)
        : detail.feedback
          ? renderFeedbackSummary(detail.feedback.payload)
          : renderCard(t("feedback_preview.title"), `<p class="muted">${t("feedback.preview_empty")}</p>`),
    ].join(""),
    context: [
      renderContextFromSourcePack(sourcePackRecord),
      renderSummaryCard(t("feedback.context_title"), [
        { label: t("feedback.activity"), value: detail.activity.id },
        { label: t("feedback.submission"), value: submission ? t("feedback.yes") : t("feedback.no") },
      ]),
    ].join(""),
  });

  document.getElementById("validate-feedback")?.addEventListener("click", async () => {
    feedbackDraft.rawText = getTextareaValue("feedback-raw");
    updateStatus("feedback", {
      validation: "validating",
      save: "idle",
      note: t("feedback.validate_running"),
    });
    render().catch((error) => showFatalError(error, "loading"));
    try {
      feedbackDraft.validation = await api.validateFeedback(activityId, feedbackDraft.rawText);
      setValidationStatus("feedback", feedbackDraft.validation, "feedback.validate_ok", "feedback.validate_fail");
      render().catch((error) => showFatalError(error, "loading"));
    } catch (error) {
      handleApiError(error, {
        scope: "feedback",
        activityId,
        stage: "validation",
        successKey: "feedback.validate_ok",
        failureKey: "feedback.validate_fail",
        saveFailedKey: "feedback.save_failed",
      });
    }
  });

  document.getElementById("save-feedback")?.addEventListener("click", async () => {
    try {
      feedbackDraft.rawText = getTextareaValue("feedback-raw");
      updateStatus("feedback", {
        save: "saving",
        note: t("feedback.save_running"),
      });
      render().catch((error) => showFatalError(error, "loading"));
      await api.saveFeedback(activityId, feedbackDraft.rawText);
      await fetchActivityDetail(activityId, true);
      updateStatus("feedback", {
        save: "saved",
        note: t("feedback.save_success"),
      });
      setFlash(t("feedback.save_success"), "success");
      navigate(`/handoff/activities/${encodeURIComponent(activityId)}`);
    } catch (error) {
      handleApiError(error, {
        scope: "feedback",
        activityId,
        stage: "save",
        successKey: "feedback.validate_ok",
        failureKey: "feedback.validate_fail",
        saveFailedKey: "feedback.save_failed",
      });
    }
  });

  attachPayloadDirtyReset("feedback-raw", "feedback", () => state.feedbackDrafts[activityId], "feedback.dirty_note");
}

function handleApiError(
  error,
  {
    draftKey = null,
    scope = null,
    activityId = null,
    stage = "loading",
    successKey = "validation.valid",
    failureKey = "validation.invalid",
    saveFailedKey = null,
  } = {},
) {
  if (error?.status === 422 && error.payload?.detail) {
    const validation = error.payload.detail;
    if (draftKey === "sourcePackDraft") {
      state.sourcePackDraft.validation = validation;
    } else if (draftKey === "activityDraft") {
      state.activityDraft.validation = validation;
    } else if (activityId && state.feedbackDrafts[activityId]) {
      state.feedbackDrafts[activityId].validation = validation;
    }
    if (scope) {
      setValidationStatus(scope, validation, successKey, failureKey);
      if (stage === "save") {
        updateStatus(scope, {
          save: "error",
          note: t(saveFailedKey || "common.save_error"),
        });
      }
    }
    setFlash(stage === "save" ? t(saveFailedKey || "common.save_error") : t(failureKey), "error");
    render().catch((renderError) => showFatalError(renderError, "loading"));
    return;
  }
  if (scope) {
    if (stage === "loading") {
      updateStatus(scope, { load: "error", note: getErrorMessage(error) });
    } else if (stage === "validation") {
      updateStatus(scope, { validation: "error", note: getErrorMessage(error) });
    } else if (stage === "save") {
      updateStatus(scope, { save: "error", note: getErrorMessage(error) });
    }
  }
  showFatalError(error, stage);
}

function showFatalError(error, stage = "loading") {
  console.error(error);
  const stageLabel =
    stage === "save"
      ? t("common.save_error")
      : stage === "validation"
        ? t("common.validation_error")
        : t("common.loading_error");
  const message = getErrorMessage(error);
  root.innerHTML = renderShell({
    title: t("error.render_title"),
    description: t("error.render_description"),
    currentStep: "source_pack",
    flash: renderFlash({ message: `${stageLabel}: ${message}`, tone: "error" }),
    main: renderErrorState(message),
    context: renderCard(t("common.link"), `<button class="button primary" data-navigate="/handoff/source-packs/new">${t("common.back_to_start")}</button>`),
  });
}

async function render() {
  const route = parseRoute(window.location);
  if (route.name === "root") {
    navigate("/handoff/source-packs/new", true);
    return;
  }
  if (route.name === "not-found") {
    root.innerHTML = renderShell({
      title: t("error.route_not_found_title"),
      description: t("error.route_not_found_description"),
      currentStep: "source_pack",
      flash: renderFlash(takeFlash()),
      main: renderErrorState(t("error.missing_route_body")),
      context: renderCard(t("common.link"), `<button class="button primary" data-navigate="/handoff/source-packs/new">${t("common.back_to_first_route")}</button>`),
    });
    return;
  }

  if (route.name === "source-pack-new") {
    await renderSourcePackNewPage();
    return;
  }
  if (route.name === "source-pack-detail") {
    await renderSourcePackDetailPage(route.sourcePackId);
    return;
  }
  if (route.name === "activity-new") {
    await renderActivityCreatePage(route.sourcePackId);
    return;
  }
  if (route.name === "activity-detail") {
    await renderActivityDetailPage(route.activityId);
    return;
  }
  if (route.name === "activity-submission") {
    await renderSubmissionPage(route.activityId);
    return;
  }
  if (route.name === "activity-feedback") {
    await renderFeedbackPage(route.activityId);
  }
}

root.addEventListener("click", (event) => {
  const nav = event.target.closest("[data-navigate]");
  if (nav) {
    event.preventDefault();
    navigate(nav.getAttribute("data-navigate"));
    return;
  }

  const copy = event.target.closest("[data-copy-target]");
  if (copy) {
    event.preventDefault();
    copyElementText(copy.getAttribute("data-copy-target"));
    return;
  }

  const localeButton = event.target.closest("[data-set-locale]");
  if (localeButton) {
    event.preventDefault();
    const locale = localeButton.getAttribute("data-set-locale");
    if (isLocale(locale)) {
      setLocale(locale);
      render().catch((error) => showFatalError(error, "loading"));
    }
  }
});

window.addEventListener("popstate", () => {
  render().catch((error) => showFatalError(error, "loading"));
});

render().catch((error) => showFatalError(error, "loading"));
