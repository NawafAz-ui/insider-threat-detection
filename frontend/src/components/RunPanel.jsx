const ROWS = [["risk_engine", "Combined risk score"], ["lr", "Logistic Regression"], ["xgb", "XGBoost"], ["iforest", "Isolation Forest"]];
const f2 = (v) => (v == null ? "-" : v.toFixed(2));
const f3 = (v) => (v == null ? "-" : v.toFixed(3));

// Test results of the last batch run, one row per model. Runs saved before calibration have no Brier score or
// validation threshold for the single models, so those cells show "-".
export default function RunPanel({ run }) {
  const test = run?.metrics?.test;
  if (!test?.risk_engine) return null;
  const threshold = (k) => (k === "risk_engine" ? run.threshold : test[k]?.validation_threshold == null ? null : test[k].validation_threshold * 100);
  return (
    <div style={{ marginBottom: 16 }}>
      <p className="muted small" style={{ marginBottom: 8 }}>
        Last batch run: {new Date(run.at).toLocaleString()} ({run.seconds} s). Results on the held-out test part, with every threshold
        chosen on validation data. Sample data is easier than real logs, so these are not research findings.
      </p>
      <div className="card tablecard">
        <table>
          <thead><tr><th>Model</th><th>Precision</th><th>Recall</th><th>F1</th><th>Average precision</th><th>Brier score</th><th>Threshold</th></tr></thead>
          <tbody>
            {ROWS.filter(([k]) => test[k]).map(([k, name]) => (
              <tr key={k}>
                <td>{name}</td>
                <td className="n">{f2(test[k].precision)}</td><td className="n">{f2(test[k].recall)}</td><td className="n">{f2(test[k].f1)}</td>
                <td className="n">{f2(test[k].pr_auc)}</td><td className="n">{f3(test[k].brier)}</td>
                <td className="n">{threshold(k) == null ? "-" : threshold(k).toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted small" style={{ marginTop: 8 }}>Brier score: lower is better (0 is perfect). Threshold is on the 0 to 100 scale.</p>
    </div>
  );
}
