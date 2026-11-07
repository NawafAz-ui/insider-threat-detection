import { useState } from "react";
import { downloadRunReport } from "../api.js";

const MODELS = [["risk_engine", "Combined risk score"], ["lr", "Logistic Regression"], ["xgb", "XGBoost"], ["iforest", "Isolation Forest"]];
const REFERENCES = [
  ["rule_deviation", "Rule: largest deviation from the user's own normal"],
  ["rule_hand_written", "Rule: after hours with a removable device or leak site"],
  ["rule_after_hours", "Rule: after-hours session"],
  ["no_skill", "No skill: flag every session"],
];
const f2 = (v) => (v == null ? "-" : v.toFixed(2));
const f3 = (v) => (v == null ? "-" : v.toFixed(3));

// F1 as a short bar next to the number
const Bar = ({ v }) => (
  <span className="meter"><i style={{ width: `${Math.max(0, Math.min(1, v ?? 0)) * 100}%`, background: "var(--teal)" }} /></span>
);

// Test results of the last batch run: the three models and the combined score, then the simple reference methods the
// models must beat. Runs saved before calibration have no Brier score or validation threshold for the single models, and
// runs that trained before the reference methods existed have no reference rows; those cells show "-".
export default function RunPanel({ run }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function report() {
    setBusy(true); setError("");
    try { await downloadRunReport(); } catch (e) { setError(e.message); } finally { setBusy(false); }
  }
  const test = run?.metrics?.test;
  if (!test?.risk_engine) return null;
  const threshold = (k) => {
    if (k === "risk_engine") return run.threshold;
    if (k.startsWith("rule_")) return test[k]?.threshold ?? null;
    if (k === "no_skill") return null;
    return test[k]?.validation_threshold == null ? null : test[k].validation_threshold * 100;
  };
  const row = ([k, name]) => (
    <tr key={k}>
      <td>{name}</td>
      <td className="n">{f2(test[k].precision)}</td><td className="n">{f2(test[k].recall)}</td>
      <td className="n">{f2(test[k].f1)}<Bar v={test[k].f1} /></td>
      <td className="n">{f2(test[k].pr_auc)}</td><td className="n">{f3(test[k].brier)}</td>
      <td className="n">{threshold(k) == null ? "-" : threshold(k).toFixed(1)}</td>
    </tr>
  );
  const models = MODELS.filter(([k]) => test[k]);
  const refs = REFERENCES.filter(([k]) => test[k]);
  const bestRule = Math.max(0, ...refs.filter(([k]) => k.startsWith("rule_")).map(([k]) => test[k].f1 ?? 0));
  return (
    <div style={{ marginBottom: 16 }}>
      <p className="muted small" style={{ marginBottom: 8 }}>
        Last batch run: {new Date(run.at).toLocaleString()} ({run.seconds} s). Results on the held-out test part, with every threshold
        chosen on validation data. Sample data is easier than real logs, so these are not research findings.
      </p>
      <div className="card tablecard">
        <table>
          <thead><tr><th>Method</th><th>Precision</th><th>Recall</th><th>F1</th><th>Average precision</th><th>Brier score</th><th>Threshold</th></tr></thead>
          <tbody>
            {models.map(row)}
            {refs.length > 0 && (
              <tr><td colSpan={7} className="muted small" style={{ background: "var(--bg)" }}>
                Simple reference methods (no learning; the threshold is chosen on validation data)
              </td></tr>
            )}
            {refs.map(row)}
          </tbody>
        </table>
      </div>
      <p className="muted small" style={{ marginTop: 8 }}>Brier score: lower is better (0 is perfect). Threshold is on the 0 to 100 scale for the models and in the units of each rule for the rules.</p>
      {refs.length > 0 ? (
        <p className="small" style={{ marginTop: 4 }}>
          The combined risk score reaches F1 {f2(test.risk_engine.f1)}. The best simple rule reaches {f2(bestRule)}
          {test.no_skill ? ` and flagging every session reaches ${f2(test.no_skill.f1)}` : ""}.
        </p>
      ) : (
        <p className="muted small" style={{ marginTop: 4 }}>Run again with Train new models to add the simple reference methods to this table.</p>
      )}
      <div style={{ marginTop: 12 }}>
        <button className="btn" onClick={report} disabled={busy}>{busy ? "Preparing..." : "Download run report"}</button>
        <span className="muted small" style={{ marginLeft: 12 }}>One page you can open in a browser and save as PDF (Ctrl+P).</span>
        {error && <p className="error" role="alert" style={{ marginTop: 8 }}>{error}</p>}
      </div>
    </div>
  );
}
