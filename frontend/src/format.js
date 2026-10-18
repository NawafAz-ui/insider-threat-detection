export const fmtDate = (iso) =>
  new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
// Every listed session is flagged, so even the lowest band is never shown as "safe" green.
export const riskClass = (s) => (s >= 80 ? "hi" : s >= 50 ? "mid" : "edge");
export const riskLabel = (s) => (s >= 80 ? "High" : s >= 50 ? "Elevated" : "Borderline");
