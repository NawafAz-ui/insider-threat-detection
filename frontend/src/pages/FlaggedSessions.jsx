import { useEffect, useState } from "react";
import { getSessions } from "../api.js";
import { fmtDate, riskClass, riskLabel } from "../format.js";
import { toSession } from "../router.js";

const PAGE = 50;

export default function FlaggedSessions() {
  const [rows, setRows] = useState(null);
  const [meta, setMeta] = useState({ total: 0, threshold: 0, scored: 0, high: 0 });
  const [error, setError] = useState("");
  const [more, setMore] = useState(false);

  async function load(offset) {
    try {
      const r = await getSessions(offset, PAGE);
      setMeta({ total: r.total, threshold: r.threshold, scored: r.scored, high: r.high });
      setRows((prev) => (offset === 0 ? r.sessions : [...prev, ...r.sessions]));
    } catch (e) { setError(e.message); }
  }
  useEffect(() => { load(0); }, []);

  if (error) return <div><p className="error" role="alert">{error}</p><button className="btn" style={{ marginTop: 12 }} onClick={() => { setError(""); load(0); }}>Try again</button></div>;
  if (!rows) return <p className="muted">Loading flagged sessions…</p>;
  if (rows.length === 0) return <p className="muted">No flagged sessions. Run the detection engine to score new logs.</p>;

  const stat = (k, v, s) => (
    <div className="card"><p className="muted">{k}</p><p className="v">{v}</p><p className="muted small">{s}</p></div>
  );
  return (
    <section>
      <h1>Flagged sessions</h1>
      <p className="muted">Highest risk first. Select a session to see why it was flagged.</p>
      <div className="stats">
        {stat("Flagged", meta.total.toLocaleString(), `of ${meta.scored.toLocaleString()} sessions scored`)}
        {stat("Flag threshold", meta.threshold, "out of 100, set on validation data")}
        {stat("Review first", meta.high.toLocaleString(), "scored 80 or higher")}
      </div>
      <div className="card tablecard">
        <table>
          <thead><tr><th>Level</th><th>Risk score</th><th>User</th><th>Session start</th><th>Duration</th><th></th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.session_id} tabIndex={0} onClick={() => toSession(r.session_id)} onKeyDown={(e) => e.key === "Enter" && toSession(r.session_id)}>
                <td><span className={`pill ${riskClass(r.risk_score)}`}>{riskLabel(r.risk_score)}</span></td>
                <td><span className="n">{r.risk_score.toFixed(0)}</span><span className="meter"><i className={riskClass(r.risk_score)} style={{ width: `${r.risk_score}%` }} /></span></td>
                <td className="n">{r.user}</td>
                <td>{fmtDate(r.start)}</td>
                <td>{Math.round((new Date(r.end) - new Date(r.start)) / 60000)} min</td>
                <td className="muted">›</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="foot">
        <span className="muted">Showing {rows.length} of {meta.total}. A flag is not proof of wrongdoing.</span>
        {rows.length < meta.total && (
          <button className="btn" disabled={more} onClick={async () => { setMore(true); await load(rows.length); setMore(false); }}>
            {more ? "Loading…" : "Show more"}
          </button>
        )}
      </div>
    </section>
  );
}
