export function parseRoute(location) {
  const pathname = location.pathname.replace(/\/+$/, "") || "/";
  const searchParams = new URLSearchParams(location.search);

  if (pathname === "/handoff" || pathname === "/handoff/") {
    return { name: "root" };
  }

  if (pathname === "/handoff/source-packs/new") {
    return { name: "source-pack-new" };
  }

  const sourcePackDetail = pathname.match(/^\/handoff\/source-packs\/([^/]+)$/);
  if (sourcePackDetail) {
    return { name: "source-pack-detail", sourcePackId: decodeURIComponent(sourcePackDetail[1]) };
  }

  if (pathname === "/handoff/activities/new") {
    return { name: "activity-new", sourcePackId: searchParams.get("sourcePackId") || "" };
  }

  const submissionMatch = pathname.match(/^\/handoff\/activities\/([^/]+)\/submission$/);
  if (submissionMatch) {
    return { name: "activity-submission", activityId: decodeURIComponent(submissionMatch[1]) };
  }

  const feedbackMatch = pathname.match(/^\/handoff\/activities\/([^/]+)\/feedback$/);
  if (feedbackMatch) {
    return { name: "activity-feedback", activityId: decodeURIComponent(feedbackMatch[1]) };
  }

  const activityDetail = pathname.match(/^\/handoff\/activities\/([^/]+)$/);
  if (activityDetail) {
    return { name: "activity-detail", activityId: decodeURIComponent(activityDetail[1]) };
  }

  return { name: "not-found" };
}
