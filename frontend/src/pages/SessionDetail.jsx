import { useEffect, useState } from "react";
import { askAssistant, getSession } from "../api.js";
import { fmtDate, riskClass, riskLabel } from "../format.js";

const MODEL_NAMES = { lr: "logistic", xgb: "xgboost", iforest: "isolation forest" };
const C = 2 * Math.PI * 54;

export default function SessionDetail({ id, onBack }) {
  const [d, setD] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { getSession(id).then(setD).catch((e) => setError(e.message)); }, [id]);

  if (error) return <><button className="link" onClick={onBack}>Back to list</button><p className="error" role="alert">{error}</p></>;
  if (!d) return <p className="muted">Loading session…</p>;

  const cls = riskClass(d.risk_score);
  const color = { hi: "#c0392b", mid: "#b45f06", edge: "#5b7186" }[cls];
  const topShap = Math.max(...d.top_shap.map((s) => s.shap), 0.0001);
  const mins = Math.round((new Date(d.end) - new Date(d.start)) / 60000);

  return (
    <section>
      <p className="crumbs"><button className="link" onClick={onBack}>Flagged sessions</button> / {d.user}</p>
      <h1 style={{ marginTop: 6 }}>{d.user} <span className="muted" style={{ fontWeight: 400, fontSize: "1.1rem" }}>{fmtDate(d.start)} to {fmtDate(d.end)} · {mins} min</span></h1>
      <div className="detail">
        <div>
          <p className="notice">A flag is not proof of wrongdoing. Review the evidence before taking any action.</p>
          <div className="card scorecard">
            <svg width="130" height="130" viewBox="0 0 130 130" role="img" aria-label={`Risk score ${d.risk_score} out of 100`}>
              <circle cx="65" cy="65" r="54" fill="none" stroke="#e4e9ee" strokeWidth="12" />
              <circle cx="65" cy="65" r="54" fill="none" stroke={color} strokeWidth="12" strokeLinecap="round"
                strokeDasharray={`${(d.risk_score / 100) * C} ${C}`} transform="rotate(-90 65 65)" />
              <text x="65" y="72" textAnchor="middle" fontSize="34" fontWeight="600" fill="#0f1b2d" fontFamily="IBM Plex Mono, monospace">{d.risk_score.toFixed(0)}</text>
            </svg>
            <div style={{ flex: 1, minWidth: 200 }}>
              <span className={`pill ${cls}`}>{riskLabel(d.risk_score)} risk</span> <span className="tag" style={{ marginLeft: 6 }}>R</span>
              <p className="muted" style={{ marginTop: 10 }}>Flag threshold is {d.threshold} out of 100.</p>
              <p className="muted small" style={{ marginTop: 12 }}>Model scores</p>
              <p className="n small">{Object.entries(d.model_scores).map(([k, v]) => `${MODEL_NAMES[k] || k} ${(v * 100).toFixed(0)}`).join(" · ")}</p>
            </div>
          </div>
          <div className="two">
            <div className="card">
              <h3>What drove the score</h3>
              {d.top_shap.length === 0 ? <p className="muted">No single behavior stands out.</p> : (
                <ul className="ev">{d.top_shap.map((s, i) => (
                  <li key={s.feature} className={s.strength === "minor" ? "minor" : ""}>
                    <span className="tag">S{i + 1}</span>{s.text}{s.strength === "minor" && <span className="muted"> (minor)</span>}
                    <div className="bb"><i style={{ width: `${Math.max(4, (s.shap / topShap) * 100)}%` }} /></div>
                  </li>))}</ul>)}
            </div>
            <div className="card">
              <h3>Different from this user's normal</h3>
              {d.baseline_deviations.length === 0 ? <p className="muted">Nothing unusual compared with the user's own history.</p> : (
                <ul className="ev">{d.baseline_deviations.map((b, i) => (
                  <li key={b.metric}>
                    <span className="tag">B{i + 1}</span>{b.text} <span className="muted">{b.z.toFixed(1)} std above their mean.</span>
                    <div className="bb"><i style={{ width: `${Math.max(4, Math.min(b.z / 6, 1) * 100)}%` }} /></div>
                  </li>))}</ul>)}
            </div>
          </div>
        </div>
        <Chat id={id} evidence={d.evidence} />
      </div>
    </section>
  );
}

function Chat({ id, evidence }) {
  const [q, setQ] = useState("");
  const [log, setLog] = useState([]);
  const [busy, setBusy] = useState(false);

  async function send(e) {
    e.preventDefault();
    const question = q.trim();
    if (!question) return;
    setQ(""); setBusy(true);
    setLog((l) => [...l, { who: "you", text: question }]);
    try {
      const r = await askAssistant(id, question);
      setLog((l) => [...l, { who: "assistant", text: r.answer, used: r.fields_used }]);
    } catch (err) {
      setLog((l) => [...l, { who: "error", text: err.message }]);
    } finally { setBusy(false); }
  }

  return (
    <div className="card chat">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0 }}>Ask about this session</h3><span className="tag" style={{ margin: 0 }}>read-only</span>
      </div>
      <p className="muted small" style={{ marginTop: 8 }}>Sees only R, S1 to S3 and B1 to B3. No names, no raw logs. Cannot change a score.</p>
      <div className="log" aria-live="polite">
        {log.length === 0 && <p className="muted small">For example: why is the USB use a concern?</p>}
        {log.map((m, i) => (
          <div key={i} className={`msg ${m.who}`}>
            <p>{m.text}</p>
            {m.used && <p style={{ marginTop: 8 }}>{m.used.map((f) => <span className="tag" key={f} title={evidence[f]}>{f}</span>)}</p>}
          </div>
        ))}
      </div>
      <form onSubmit={send} className="row">
        <input value={q} onChange={(e) => setQ(e.target.value)} maxLength={300} placeholder="Ask a question" aria-label="Question" style={{ height: 44 }} />
        <button className="btn" style={{ padding: "0 18px" }} disabled={busy || !q.trim()}>{busy ? "…" : "Ask"}</button>
      </form>
    </div>
  );
}
