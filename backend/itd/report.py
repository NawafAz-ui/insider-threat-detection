"""Run report: one self-contained HTML page about the newest batch run. It prints well; save it as PDF from the browser.
No scripts and no external files. Every value that comes from the database is escaped before it goes into the page."""
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from html import escape as _e

from .rules import RULE_NAMES

MODELS = [("risk_engine", "Combined risk score"), ("lr", "Logistic Regression"), ("xgb", "XGBoost"), ("iforest", "Isolation Forest")]
REFERENCES = [(k, RULE_NAMES[k]) for k in ("rule_deviation", "rule_hand_written", "rule_after_hours", "no_skill")]
TOP = 10

CSS = """
body { font-family: "Segoe UI", system-ui, sans-serif; color: #0f1b2d; max-width: 920px; margin: 24px auto; padding: 0 16px; line-height: 1.45; }
h1 { font-size: 1.5rem; margin: 0 0 4px; } h2 { font-size: 1.1rem; margin: 26px 0 8px; border-bottom: 1px solid #dfe4ea; padding-bottom: 4px; }
table { border-collapse: collapse; width: 100%; font-size: .9rem; } th, td { border: 1px solid #dfe4ea; padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: #f3f5f8; } td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; }
.muted { color: #5b6877; font-size: .85rem; } .group td { background: #f3f5f8; color: #5b6877; font-size: .85rem; }
ul { margin: 0; padding-left: 18px; } .note { border-left: 4px solid #0e7c86; background: #eef6f7; padding: 8px 12px; margin: 12px 0; }
@media print { body { margin: 0; max-width: none; } h2 { break-after: avoid; } tr { break-inside: avoid; } }
"""


def _f(v, n=2):
    """Fixed decimals, ties rounded up like the dashboard (JavaScript toFixed), so both show the same number."""
    if v is None:
        return "-"
    return str(Decimal(v).quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP))


def _utc(t):
    if isinstance(t, (int, float)):
        t = datetime.fromtimestamp(t, timezone.utc)
    return t.strftime("%Y-%m-%d %H:%M") + " UTC" if t else "-"


def _threshold(test, k, run):
    if k == "risk_engine":
        return run.get("threshold")
    if k.startswith("rule_"):
        return test[k].get("threshold")
    if k == "no_skill":
        return None
    t = test[k].get("validation_threshold")
    return None if t is None else t * 100


def _metrics_rows(run, test, rows):
    out = []
    for k, name in rows:
        m = test[k]
        out.append(f'<tr><td>{_e(name)}</td><td class="n">{_f(m.get("precision"))}</td><td class="n">{_f(m.get("recall"))}</td>'
                   f'<td class="n">{_f(m.get("f1"))}</td><td class="n">{_f(m.get("pr_auc"))}</td><td class="n">{_f(m.get("brier"), 3)}</td>'
                   f'<td class="n">{_f(_threshold(test, k, run), 1)}</td></tr>')
    return "".join(out)


def _why(doc):
    texts = [x.get("text", "") for x in (doc.get("top_shap") or [])[:2]] + [x.get("text", "") for x in (doc.get("baseline_deviations") or [])[:1]]
    seen, items = set(), []
    for t in texts:
        if t and t not in seen:
            seen.add(t)
            items.append(f"<li>{_e(t)}</li>")
    return "<ul>" + "".join(items) + "</ul>" if items else "-"


def render(run, top, now=None):
    """run: the newest document of the runs collection. top: the highest-risk flagged result documents of that run."""
    now = now or datetime.now(timezone.utc)
    test = (run.get("metrics") or {}).get("test") or {}
    models = [(k, n) for k, n in MODELS if k in test]
    refs = [(k, n) for k, n in REFERENCES if k in test]
    sessions, flagged = run.get("sessions", 0), run.get("flagged", 0)
    share = f" ({100 * flagged / sessions:.1f}% of sessions)" if sessions else ""
    weights = ", ".join(f"{_e(str(k))} {v:.2f}" for k, v in (run.get("weights") or {}).items()) or "-"
    val = run.get("validation") or {}
    val_text = (f"{_e(str(val.get('status', '-')))} ({val.get('errors', 0)} errors, {val.get('warnings', 0)} warnings)" if val else "not recorded")

    body = [f"<h1>Insider Threat Review: batch run report</h1>",
            f'<p class="muted">Report created {_utc(now)}. Run finished {_utc(run.get("at"))}.</p>',
            "<h2>1. Run summary</h2><table>",
            f"<tr><th>Sessions scored</th><td>{sessions:,}</td></tr>",
            f"<tr><th>Flagged sessions</th><td>{flagged:,}{share}</td></tr>",
            f'<tr><th>Flag threshold</th><td>{_f(run.get("threshold"), 1)} out of 100, chosen on validation data</td></tr>',
            f"<tr><th>Model weights</th><td>{weights}</td></tr>",
            f'<tr><th>Run time</th><td>{_f(run.get("seconds"), 1)} seconds</td></tr>',
            f"<tr><th>Input validation</th><td>{val_text}</td></tr></table>"]

    body.append("<h2>2. Test results and comparison with simple methods</h2>")
    if test.get("risk_engine"):
        body.append('<table><thead><tr><th>Method</th><th class="n">Precision</th><th class="n">Recall</th><th class="n">F1</th>'
                    '<th class="n">Average precision</th><th class="n">Brier score</th><th class="n">Threshold</th></tr></thead><tbody>')
        body.append(_metrics_rows(run, test, models))
        if refs:
            body.append('<tr class="group"><td colspan="7">Simple reference methods (no learning; the threshold is chosen on validation data)</td></tr>')
            body.append(_metrics_rows(run, test, refs))
        body.append("</tbody></table>")
        if refs:
            best = max([test[k].get("f1") or 0 for k, _ in refs if k.startswith("rule_")] + [0])
            ns = test.get("no_skill", {}).get("f1")
            body.append(f'<p class="note">The combined risk score reaches F1 {_f(test["risk_engine"].get("f1"))}. The best simple rule reaches '
                        f'{_f(best)}{" and flagging every session reaches " + _f(ns) if ns is not None else ""}.</p>')
        else:
            body.append('<p class="muted">This run was trained before the simple reference methods existed. Train again to add them.</p>')
        body.append('<p class="muted">Results are on the held-out, time-ordered test part. Every threshold was chosen on validation data. '
                    "Brier score: lower is better. Threshold: 0 to 100 for the models, in the units of each rule for the rules.</p>")
    else:
        body.append('<p class="muted">This run has no stored test results.</p>')

    body.append(f"<h2>3. The {TOP} highest-risk flagged sessions</h2>")
    if top:
        body.append('<table><thead><tr><th class="n">#</th><th class="n">Risk</th><th>User</th><th>Session start</th><th class="n">Minutes</th><th>Why it was flagged</th></tr></thead><tbody>')
        for i, d in enumerate(top[:TOP], 1):
            minutes = int((d["end"] - d["start"]).total_seconds() // 60)
            body.append(f'<tr><td class="n">{i}</td><td class="n">{_f(d.get("risk_score"), 0)}</td><td>{_e(str(d.get("user", "")))}</td>'
                        f'<td>{_utc(d["start"])}</td><td class="n">{minutes}</td><td>{_why(d)}</td></tr>')
        body.append("</tbody></table>")
        body.append('<p class="muted">The explanation lists what pushed the XGBoost score up and how far the session was from the user\'s own normal. It does not cover the other two models.</p>')
    else:
        body.append('<p class="muted">No flagged sessions in this run.</p>')

    body.append("<h2>4. Limits</h2><ul>"
                "<li>The data is generated in the CERT layout. It is easier than real logs, so these numbers are not research findings.</li>"
                "<li>A flag is a lead for a human to check, not proof of wrongdoing.</li>"
                "<li>The simple methods are references: they show what a hand-written rule or a deviation check reaches without learning.</li>"
                "<li>XGBoost results can differ a little between computers, even with the same versions and seed.</li></ul>")
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>Batch run report</title><style>{CSS}</style></head><body>{''.join(body)}</body></html>")
