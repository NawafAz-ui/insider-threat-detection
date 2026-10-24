import { useEffect, useState } from "react";
import { getUser } from "../api.js";
import { fmtDate, riskClass, riskLabel } from "../format.js";
import { toList, toSession } from "../router.js";
import RiskTimeline from "../components/RiskTimeline.jsx";

// Workflow 2: investigate a user. Read-only: their sessions over time and what is normal for them.
export default function UserPage({ id }) {
  const [d, setD] = useState(null);
  const [error, setError] = useState("");
  const load = () => { setError(""); getUser(id).then(setD).catch((e) => setError(e.status === 404 ? "No sessions were found for this user." : e.message)); };
  useEffect(load, [id]);

  if (error) return <div><button className="link" onClick={toList}>Back to flagged sessions</button><p className="error" role="alert" style={{ marginTop: 12 }}>{error}</p><button className="btn" style={{ marginTop: 12 }} onClick={load}>Try again</button></div>;
  if (!d) return <p className="muted">Loading user…</p>;

  const flagged = d.sessions.filter((s) => s.flagged).slice().reverse();      // newest first
  const stat = (k, v, s) => <div className="card"><p className="muted">{k}</p><p className="v">{v}</p><p className="muted small">{s}</p></div>;
  return (
    <section>
      <p className="crumbs"><button className="link" onClick={toList}>Flagged sessions</button> / {d.user}</p>
      <h1 style={{ marginTop: 6 }}>{d.user} <span className="muted" style={{ fontWeight: 400, fontSize: "1.1rem" }}>session history</span></h1>
      <p className="notice" style={{ marginTop: 12 }}>A flag is not proof of wrongdoing. Compare each flagged session with what is normal for this user.</p>
      <div className="stats">
        {stat("Sessions", d.summary.sessions.toLocaleString(), d.summary.shown < d.summary.sessions ? `latest ${d.summary.shown} shown` : "all shown below")}
        {stat("Flagged", d.summary.flagged, `at a score of ${d.threshold} or more`)}
        {stat("Highest risk", d.summary.highest_risk.toFixed(0), "out of 100")}
      </div>
      <div className="card">
        <h3>Risk over time</h3>
        <p className="muted small" style={{ marginBottom: 8 }}>Each dot is one session. Larger coloured dots are flagged. Select a dot to open that session.</p>
        <RiskTimeline sessions={d.sessions} threshold={d.threshold} />
      </div>
      <div className="two">
        <div className="card">
          <h3>What is normal for this user</h3>
          {d.baseline.length === 0 ? <p className="muted">No baseline yet.</p> : (
            <table className="plain"><thead><tr><th>Behavior</th><th>Average</th><th>Usual spread</th></tr></thead>
              <tbody>{d.baseline.map((b) => <tr key={b.metric}><td>{b.label}</td><td className="n">{b.mean.toFixed(1)}</td><td className="n">±{b.std.toFixed(1)}</td></tr>)}</tbody></table>)}
        </div>
        <div className="card">
          <h3>Flagged sessions of this user</h3>
          {flagged.length === 0 ? <p className="muted">No flagged sessions.</p> : (
            <table className="plain"><thead><tr><th>Level</th><th>Risk</th><th>Start</th></tr></thead>
              <tbody>{flagged.map((s) => (
                <tr key={s.session_id} className="click" tabIndex={0} onClick={() => toSession(s.session_id)} onKeyDown={(e) => e.key === "Enter" && toSession(s.session_id)}>
                  <td><span className={`pill ${riskClass(s.risk_score)}`}>{riskLabel(s.risk_score)}</span></td>
                  <td className="n">{s.risk_score.toFixed(0)}</td><td>{fmtDate(s.start)}</td></tr>))}</tbody></table>)}
        </div>
      </div>
    </section>
  );
}
