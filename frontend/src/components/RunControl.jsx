import { useEffect, useRef, useState } from "react";
import { getRole, getRunDatasets, getRunStatus, startRun } from "../api.js";

const LABEL = { requested: "Waiting for the worker", running: "Running", done: "Finished", failed: "Failed" };
const isActive = (s) => s === "requested" || s === "running";
const when = (iso) => (iso ? new Date(iso).toLocaleString() : "");

// Start a batch run and follow it. The dashboard only files a request; the worker (python -m itd.worker) performs it.
// Administrators get the controls; analysts only see a note while a run is in progress.
export default function RunControl({ onFinished }) {
  const admin = getRole() === "admin";
  const [req, setReq] = useState(null);
  const [datasets, setDatasets] = useState(null);
  const [dataset, setDataset] = useState("");
  const [retrain, setRetrain] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [showLog, setShowLog] = useState(false);
  const previous = useRef(null);                         // status seen on the previous check
  const active = isActive(req?.status);

  async function refresh() {
    try {
      const r = await getRunStatus();
      const was = previous.current;
      previous.current = r.request ? r.request.status : null;
      setReq(r.request);
      if (isActive(was) && r.request?.status === "done") onFinished?.();     // reload the flagged list
    } catch { /* connection problems are shown by the list below */ }
  }

  useEffect(() => { refresh(); }, []);
  useEffect(() => {
    const t = setInterval(refresh, active ? 3000 : 20000);
    return () => clearInterval(t);
  }, [active]);
  useEffect(() => {
    if (!admin) return;
    getRunDatasets().then((r) => {
      setDatasets(r.datasets);
      setDataset((d) => d || (r.datasets.includes("cert_synthetic") ? "cert_synthetic" : r.datasets[0] || ""));
    }).catch((e) => { setDatasets([]); setError(e.message); });
  }, [admin]);

  async function submit() {
    setBusy(true); setError(""); setShowLog(false);
    try {
      const r = await startRun(dataset, retrain);
      previous.current = r.status;
      setReq(r);
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }

  if (!admin) {
    return active ? <p className="info" role="status">A batch run is in progress. The list updates when it finishes.</p> : null;
  }
  const waitingLong = req?.status === "requested" && Date.now() - new Date(req.requested_at).getTime() > 20000;
  return (
    <div className="card" style={{ margin: "16px 0" }}>
      <h2 style={{ marginBottom: 4 }}>Run analysis</h2>
      <p className="muted small">Score a dataset with the detection engine. Results replace the current list when the run finishes.</p>
      <div style={{ display: "flex", gap: 16, alignItems: "flex-end", flexWrap: "wrap", marginTop: 12 }}>
        <div>
          <label htmlFor="run-dataset">Dataset folder</label>
          <select id="run-dataset" value={dataset} onChange={(e) => setDataset(e.target.value)} disabled={active || busy || !datasets?.length}
            style={{ height: 46, padding: "0 10px", font: "inherit", border: "1px solid #b9c3cf", borderRadius: 8, background: "#fff" }}>
            {(datasets || []).map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
        <label htmlFor="run-retrain" style={{ display: "flex", gap: 8, alignItems: "center", height: 46, margin: 0, whiteSpace: "nowrap" }}>
          <input id="run-retrain" type="checkbox" checked={retrain} onChange={(e) => setRetrain(e.target.checked)} disabled={active || busy}
            style={{ width: 20, height: 20, padding: 0, flex: "none" }} />
          Train new models
        </label>
        <button className="btn" onClick={submit} disabled={active || busy || !dataset}>{busy ? "Sending..." : "Start run"}</button>
      </div>
      <p className="muted small" style={{ marginTop: 8 }}>
        Leave "Train new models" off to score with the saved models (faster). Turn it on for a new dataset or after changing the data rules.
      </p>
      {datasets && datasets.length === 0 && !error && <p className="muted small">No dataset folders found in the data folder.</p>}
      {error && <p className="error" role="alert" style={{ marginTop: 10 }}>{error}</p>}
      {req && (
        <div role="status" aria-live="polite" style={{ marginTop: 12 }}>
          <p>
            <strong>{LABEL[req.status] || req.status}</strong>
            <span className="muted small"> | dataset {req.dataset}{req.retrain ? ", new models" : ""} | asked by {req.requested_by} at {when(req.requested_at)}
              {req.finished_at ? ` | ended ${when(req.finished_at)}` : ""}</span>
          </p>
          {waitingLong && <p className="info">No worker has picked this up yet. Start it in a terminal with: python -m itd.worker</p>}
          {req.status === "failed" && req.message && <p className="error" role="alert">{req.message}</p>}
          {req.log && (
            <>
              <button className="link" onClick={() => setShowLog((v) => !v)}>{showLog ? "Hide details" : "Show details"}</button>
              {showLog && <pre className="small" style={{ whiteSpace: "pre-wrap", marginTop: 8, overflowX: "auto" }}>{req.log}</pre>}
            </>
          )}
        </div>
      )}
    </div>
  );
}
