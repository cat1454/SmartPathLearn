async function readPayload(response) {
  const text = await response.text();
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function request(method, path, body) {
  const response = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const payload = await readPayload(response);
  if (!response.ok) {
    const error = new Error(`Request failed: ${response.status}`);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

export const api = {
  validateSourcePack(rawText) {
    return request("POST", "/source-packs/validate", { raw_text: rawText });
  },
  createSourcePack(rawText) {
    return request("POST", "/source-packs", { raw_text: rawText });
  },
  getSourcePack(sourcePackId) {
    return request("GET", `/source-packs/${encodeURIComponent(sourcePackId)}`);
  },
  validateActivity(rawText) {
    return request("POST", "/activities/validate", { raw_text: rawText });
  },
  createActivity(rawText) {
    return request("POST", "/activities", { raw_text: rawText });
  },
  getActivity(activityId) {
    return request("GET", `/activities/${encodeURIComponent(activityId)}`);
  },
  saveSubmission(activityId, submission) {
    return request("POST", `/activities/${encodeURIComponent(activityId)}/submission`, submission);
  },
  validateFeedback(activityId, rawText) {
    return request("POST", `/activities/${encodeURIComponent(activityId)}/feedback/validate`, { raw_text: rawText });
  },
  saveFeedback(activityId, rawText) {
    return request("POST", `/activities/${encodeURIComponent(activityId)}/feedback`, { raw_text: rawText });
  },
};
