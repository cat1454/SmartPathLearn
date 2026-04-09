import { getLocale, t } from "./i18n.js";

export const activityTypeMeta = {
  case_mission: {
    titleKey: "activity_type.case_mission.title",
    descriptionKey: "activity_type.case_mission.description",
  },
  error_hunt: {
    titleKey: "activity_type.error_hunt.title",
    descriptionKey: "activity_type.error_hunt.description",
  },
  explain_back: {
    titleKey: "activity_type.explain_back.title",
    descriptionKey: "activity_type.explain_back.description",
  },
  mini_project: {
    titleKey: "activity_type.mini_project.title",
    descriptionKey: "activity_type.mini_project.description",
  },
  debate_defend: {
    titleKey: "activity_type.debate_defend.title",
    descriptionKey: "activity_type.debate_defend.description",
  },
};

const stepConfig = [
  { key: "source_pack", labelKey: "steps.source_pack" },
  { key: "choose_format", labelKey: "steps.choose_format" },
  { key: "activity_authoring", labelKey: "steps.activity_authoring" },
  { key: "student_submission", labelKey: "steps.student_submission" },
  { key: "activity_feedback", labelKey: "steps.activity_feedback" },
];

const markerPairs = {
  SOURCE_PACK_V1: ["<<<SOURCE_PACK_V1_START>>>", "<<<SOURCE_PACK_V1_END>>>"],
  ACTIVITY_PAYLOAD_V2: ["<<<ACTIVITY_PAYLOAD_V2_START>>>", "<<<ACTIVITY_PAYLOAD_V2_END>>>"],
  ACTIVITY_FEEDBACK_V2: ["<<<ACTIVITY_FEEDBACK_V2_START>>>", "<<<ACTIVITY_FEEDBACK_V2_END>>>"],
};

export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function activityTypeTitle(activityType) {
  return t(activityTypeMeta[activityType]?.titleKey || activityType);
}

function activityTypeDescription(activityType) {
  return t(activityTypeMeta[activityType]?.descriptionKey || activityType);
}

function renderLanguageToggle() {
  const locale = getLocale();
  return `
    <div class="language-toggle" aria-label="${escapeHtml(t("language.label"))}">
      <span class="language-toggle-label">${escapeHtml(t("language.label"))}</span>
      <div class="language-toggle-buttons">
        <button class="button secondary ${locale === "vi" ? "selected" : ""}" data-set-locale="vi">${escapeHtml(t("language.vi"))}</button>
        <button class="button secondary ${locale === "en" ? "selected" : ""}" data-set-locale="en">${escapeHtml(t("language.en"))}</button>
      </div>
    </div>
  `;
}

function renderStepRail(currentStep) {
  return `
    <nav class="step-rail" aria-label="Handoff steps">
      <div class="brand-block">
        <div class="eyebrow">${escapeHtml(t("brand.eyebrow"))}</div>
        <h1>${escapeHtml(t("brand.title"))}</h1>
        <p>${escapeHtml(t("brand.subtitle"))}</p>
      </div>
      <ol class="step-list">
        ${stepConfig
          .map((step) => {
            const state = step.key === currentStep ? "current" : "idle";
            return `<li class="step-item ${state}">${escapeHtml(t(step.labelKey))}</li>`;
          })
          .join("")}
      </ol>
    </nav>
  `;
}

export function renderShell({ title, description, currentStep, main, context = "", flash = "" }) {
  return `
    <div class="shell">
      ${renderStepRail(currentStep)}
      <main class="workspace">
        <header class="page-header">
          <div>
            <div class="eyebrow">${escapeHtml(t("brand.eyebrow"))}</div>
            <h2>${escapeHtml(title)}</h2>
            <p>${escapeHtml(description)}</p>
          </div>
          ${renderLanguageToggle()}
        </header>
        ${flash}
        ${main}
      </main>
      <aside class="context-panel">
        ${context}
      </aside>
    </div>
  `;
}

export function renderCard(title, body, extraClass = "") {
  return `
    <section class="panel ${extraClass}">
      <div class="panel-header">
        <h3>${escapeHtml(title)}</h3>
      </div>
      <div class="panel-body">
        ${body}
      </div>
    </section>
  `;
}

export function renderFlash(flash) {
  if (!flash) {
    return "";
  }
  return `<div class="flash ${escapeHtml(flash.tone || "info")}">${escapeHtml(flash.message)}</div>`;
}

export function renderPromptCard(title, prompt, targetId, helperText = "") {
  return renderCard(
    title,
    `
      ${helperText ? `<p class="helper">${escapeHtml(helperText)}</p>` : ""}
      <div class="prompt-actions">
        <button class="button secondary" data-copy-target="${escapeHtml(targetId)}">${escapeHtml(t("common.copied_prompt"))}</button>
      </div>
      <pre class="prompt-box" id="${escapeHtml(targetId)}">${escapeHtml(prompt)}</pre>
    `,
  );
}

function getStatusTone(status) {
  if (["ready", "valid", "saved"].includes(status)) {
    return "success";
  }
  if (["invalid", "error"].includes(status)) {
    return "error";
  }
  if (["loading", "validating", "saving"].includes(status)) {
    return "active";
  }
  return "idle";
}

function renderStatusChip(label, status) {
  const tone = getStatusTone(status);
  return `
    <div class="status-chip ${tone}">
      <span class="status-chip-label">${escapeHtml(label)}</span>
      <strong>${escapeHtml(t(`status.${status || "idle"}`))}</strong>
    </div>
  `;
}

export function renderStatusStrip(status = {}) {
  return renderCard(
    t("status.title"),
    `
      <div class="status-strip">
        ${renderStatusChip(t("status.load"), status.load || "idle")}
        ${renderStatusChip(t("status.validation"), status.validation || "idle")}
        ${renderStatusChip(t("status.save"), status.save || "idle")}
      </div>
      ${status.note ? `<p class="helper">${escapeHtml(status.note)}</p>` : ""}
    `,
  );
}

export function renderMarkerGuide(expectedMarker) {
  const [startMarker, endMarker] = markerPairs[expectedMarker] || ["", ""];
  return renderCard(
    t("marker_guide.title"),
    `
      <p class="helper">${escapeHtml(t("marker_guide.helper"))}</p>
      <div class="marker-guide">
        <div class="marker-row">
          <span>${escapeHtml(t("marker_guide.start"))}</span>
          <code>${escapeHtml(startMarker)}</code>
        </div>
        <div class="marker-row">
          <span>${escapeHtml(t("marker_guide.end"))}</span>
          <code>${escapeHtml(endMarker)}</code>
        </div>
      </div>
      <ul class="bullet-list marker-rules">
        <li>${escapeHtml(t("marker_guide.rule_1"))}</li>
        <li>${escapeHtml(t("marker_guide.rule_2"))}</li>
        <li>${escapeHtml(t("marker_guide.rule_3"))}</li>
      </ul>
    `,
  );
}

function translateIssueMessage(issue) {
  const translation = t(`validation.issue_codes.${issue.code}`, {
    expected: issue.expected || "",
    path: issue.path || "$",
  });
  return translation.startsWith("validation.issue_codes.") ? issue.message || "" : translation;
}

function renderIssueTable(issues) {
  if (!issues.length) {
    return `<p class="muted">${escapeHtml(t("validation.no_issue_found"))}</p>`;
  }
  return `
    <div class="issue-table-wrap">
      <table class="issue-table">
        <thead>
          <tr>
            <th>${escapeHtml(t("validation.headers.severity"))}</th>
            <th>${escapeHtml(t("validation.headers.code"))}</th>
            <th>${escapeHtml(t("validation.headers.path"))}</th>
            <th>${escapeHtml(t("validation.headers.detail"))}</th>
          </tr>
        </thead>
        <tbody>
          ${issues
            .map((issue) => {
              const tone = issue.severity === "warning" ? "warning" : issue.severity === "error" ? "error" : "info";
              return `
                <tr>
                  <td><span class="issue-severity ${tone}">${escapeHtml(t(`validation.severity.${issue.severity || "info"}`))}</span></td>
                  <td><code class="issue-code">${escapeHtml(issue.code || "-")}</code></td>
                  <td><code>${escapeHtml(issue.path || "$")}</code></td>
                  <td>
                    <div>${escapeHtml(translateIssueMessage(issue))}</div>
                    ${issue.expected ? `<div class="issue-expected">${escapeHtml(t("validation.expected_value", { expected: issue.expected }))}</div>` : ""}
                  </td>
                </tr>
              `;
            })
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

export function renderValidationPanel(validation, expectedMarker) {
  if (!validation) {
    return renderCard(
      t("validation.title"),
      `<p class="muted">${escapeHtml(t("validation.pre_validate", { marker: expectedMarker }))}</p>`,
    );
  }

  const tone = validation.ok ? "success" : "error";
  const issues = Array.isArray(validation.issues) ? validation.issues : [];
  const errorCount = issues.filter((issue) => issue.severity === "error").length;
  const warningCount = issues.filter((issue) => issue.severity === "warning").length;
  const summaryBits = [];
  if (errorCount) {
    summaryBits.push(t("validation.count_error", { count: errorCount }));
  }
  if (warningCount) {
    summaryBits.push(t("validation.count_warning", { count: warningCount }));
  }
  if (!summaryBits.length) {
    summaryBits.push(t("validation.no_issues"));
  }

  return renderCard(
    t("validation.title"),
    `
      <div class="validation-head">
        <div class="validation-badge ${tone}">${escapeHtml(validation.ok ? t("validation.valid") : t("validation.invalid"))}</div>
        <div class="validation-summary">
          <p class="muted">${escapeHtml(t("validation.expected_marker", { marker: expectedMarker }))}</p>
          <p class="muted">${escapeHtml(t("validation.parsed_marker", { marker: validation.marker || expectedMarker }))}</p>
          <p class="muted">${escapeHtml(t("validation.summary", { summary: summaryBits.join(", ") }))}</p>
        </div>
      </div>
      ${renderIssueTable(issues)}
      <p class="helper">${escapeHtml(validation.ok ? t("validation.ok_helper") : t("validation.fix_helper"))}</p>
    `,
  );
}

export function renderSummaryCard(title, rows) {
  return renderCard(
    title,
    `
      <dl class="summary-list">
        ${rows
          .map(
            (row) =>
              `<div class="summary-row"><dt>${escapeHtml(row.label)}</dt><dd>${escapeHtml(row.value ?? "-")}</dd></div>`,
          )
          .join("")}
      </dl>
    `,
  );
}

export function renderJsonCard(title, payload) {
  return renderCard(title, `<pre class="json-box">${escapeHtml(JSON.stringify(payload, null, 2))}</pre>`);
}

export function renderPayloadPreview(title, validation, emptyMessage) {
  if (!validation) {
    return renderCard(title, `<p class="muted">${escapeHtml(emptyMessage)}</p>`);
  }
  if (!validation.normalized) {
    return renderCard(title, `<p class="muted">${escapeHtml(t("common.raw_json_root"))}</p>`);
  }
  return renderCard(
    title,
    `
      <p class="helper">${escapeHtml(validation.ok ? t("validation.ok_helper") : t("validation.fix_helper"))}</p>
      <pre class="json-box">${escapeHtml(JSON.stringify(validation.normalized, null, 2))}</pre>
    `,
  );
}

export function renderActivityTypePicker(selectedType) {
  return renderCard(
    t("activity_type.picker_title"),
    `
      <div class="activity-grid">
        ${Object.entries(activityTypeMeta)
          .map(([key, meta]) => {
            const selected = key === selectedType ? "selected" : "";
            return `
              <button class="activity-type-card ${selected}" data-activity-type="${escapeHtml(key)}">
                <strong>${escapeHtml(t(meta.titleKey))}</strong>
                <span>${escapeHtml(t(meta.descriptionKey))}</span>
              </button>
            `;
          })
          .join("")}
      </div>
    `,
  );
}

function listItems(items) {
  if (!items || !items.length) {
    return `<p class="muted">${escapeHtml(t("activity.no_data"))}</p>`;
  }
  return `<ul class="bullet-list">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

export function renderSourcePackOverview(sourcePack) {
  return renderSummaryCard(t("source_pack.overview_title"), [
    { label: t("source_pack.id"), value: sourcePack.source_pack_ref || t("common.empty") },
    { label: t("source_pack.subject"), value: sourcePack.subject },
    { label: t("source_pack.grade"), value: sourcePack.grade_level },
    { label: t("source_pack.chapter"), value: sourcePack.chapter_title },
    { label: t("source_pack.lesson"), value: sourcePack.lesson_title },
  ]);
}

export function renderActivityPreview(activityPayload) {
  const data = activityPayload.activity_data || {};
  let body = "";
  if (activityPayload.activity_type === "case_mission") {
    body = `
      <p><strong>${escapeHtml(t("activity.scenario"))}:</strong> ${escapeHtml(data.scenario)}</p>
      <p><strong>${escapeHtml(t("activity.task"))}:</strong> ${escapeHtml(data.task)}</p>
      <div><strong>${escapeHtml(t("activity.expected_points"))}</strong>${listItems(data.expected_points)}</div>
      <div><strong>${escapeHtml(t("activity.success_criteria"))}</strong>${listItems(data.success_criteria)}</div>
    `;
  } else if (activityPayload.activity_type === "error_hunt") {
    body = `
      <p><strong>${escapeHtml(t("activity.artifact"))}:</strong> ${escapeHtml(data.artifact)}</p>
      <p><strong>${escapeHtml(t("activity.error_count"))}:</strong> ${escapeHtml(data.error_count_expected)}</p>
      <div><strong>${escapeHtml(t("activity.error_categories"))}</strong>${listItems(data.error_categories)}</div>
      <div><strong>${escapeHtml(t("activity.reference_points"))}</strong>${listItems(data.reference_points)}</div>
    `;
  } else if (activityPayload.activity_type === "explain_back") {
    body = `
      <p><strong>${escapeHtml(t("activity.teaching_prompt"))}:</strong> ${escapeHtml(data.teaching_prompt)}</p>
      <p><strong>${escapeHtml(t("activity.target_audience"))}:</strong> ${escapeHtml(data.target_audience)}</p>
      <div><strong>${escapeHtml(t("activity.expected_points"))}</strong>${listItems(data.expected_points)}</div>
      <div><strong>${escapeHtml(t("activity.clarity_rubric"))}</strong>${listItems(data.clarity_rubric)}</div>
    `;
  } else if (activityPayload.activity_type === "mini_project") {
    body = `
      <p><strong>${escapeHtml(t("activity.brief"))}:</strong> ${escapeHtml(data.brief)}</p>
      <p><strong>${escapeHtml(t("activity.deliverable"))}:</strong> ${escapeHtml(data.deliverable_type)}</p>
      <div><strong>${escapeHtml(t("activity.constraints"))}</strong>${listItems(data.constraints)}</div>
      <div><strong>${escapeHtml(t("activity.rubric"))}</strong>${listItems(data.rubric)}</div>
    `;
  } else if (activityPayload.activity_type === "debate_defend") {
    body = `
      <p><strong>${escapeHtml(t("activity.claim"))}:</strong> ${escapeHtml(data.claim)}</p>
      <p><strong>${escapeHtml(t("activity.position_task"))}:</strong> ${escapeHtml(data.position_task)}</p>
      <div><strong>${escapeHtml(t("activity.evidence_rules"))}</strong>${listItems(data.evidence_rules)}</div>
      <div><strong>${escapeHtml(t("activity.rubric"))}</strong>${listItems(data.rubric)}</div>
    `;
  } else {
    body = `<p class="muted">${escapeHtml(t("activity.no_renderer"))}</p>`;
  }

  return renderCard(
    t("activity.preview_card_title", { type: activityTypeTitle(activityPayload.activity_type) || activityPayload.activity_type }),
    `
      <p><strong>${escapeHtml(t("activity.activity_id"))}:</strong> ${escapeHtml(activityPayload.activity_id || t("common.empty"))}</p>
      <p><strong>${escapeHtml(t("activity.instructions"))}:</strong></p>
      ${listItems(activityPayload.instructions || [])}
      ${body}
    `,
  );
}

export function renderSubmissionPreview(submission) {
  return renderCard(
    t("submission.card_title"),
    `
      <p><strong>${escapeHtml(t("submission.response_type"))}:</strong> ${escapeHtml(submission.response_type)}</p>
      <pre class="json-box">${escapeHtml(submission.response_content || "")}</pre>
    `,
  );
}

export function renderFeedbackSummary(feedbackPayload) {
  const feedback = feedbackPayload.feedback || {};
  const extras = Object.entries(feedback)
    .filter(([key]) => !["overall_verdict", "strengths", "gaps", "misconceptions", "next_step", "score_optional"].includes(key))
    .map(([key, value]) => `<div><strong>${escapeHtml(key)}</strong><pre class="json-box">${escapeHtml(JSON.stringify(value, null, 2))}</pre></div>`)
    .join("");

  return renderCard(
    t("feedback_preview.title"),
    `
      <p><strong>${escapeHtml(t("feedback_preview.overall_verdict"))}:</strong> ${escapeHtml(feedback.overall_verdict || "")}</p>
      <p><strong>${escapeHtml(t("feedback_preview.score"))}:</strong> ${escapeHtml(feedback.score_optional ?? "-")}</p>
      <div><strong>${escapeHtml(t("feedback_preview.strengths"))}</strong>${listItems(feedback.strengths || [])}</div>
      <div><strong>${escapeHtml(t("feedback_preview.gaps"))}</strong>${listItems(feedback.gaps || [])}</div>
      <div><strong>${escapeHtml(t("feedback_preview.misconceptions"))}</strong>${listItems(feedback.misconceptions || [])}</div>
      <p><strong>${escapeHtml(t("feedback_preview.next_step"))}:</strong> ${escapeHtml(feedback.next_step || "")}</p>
      ${extras}
    `,
  );
}

export function renderNavigationRow(items) {
  return `<div class="nav-row">${items.join("")}</div>`;
}

export function renderErrorState(message) {
  return renderCard(t("error.generic_title"), `<p>${escapeHtml(message)}</p>`);
}
