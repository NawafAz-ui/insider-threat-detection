export const fmtDate = (iso) =>
  new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
// Every listed session is flagged, so even the lowest band is never shown as "safe" green.
export const riskClass = (s) => (s >= 80 ? "hi" : s >= 50 ? "mid" : "edge");
export const riskLabel = (s) => (s >= 80 ? "High" : s >= 50 ? "Elevated" : "Borderline");
// Deviations are capped at 10 by the engine, so 10 means "10 or more".
export const fmtStd = (z) => (z >= 9.95 ? "10 or more" : z.toFixed(1));
