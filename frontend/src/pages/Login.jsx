import { useState } from "react";
import { login } from "../api.js";
import Logo from "../Logo.jsx";

const USER_RE = /^[A-Za-z0-9_.-]{1,64}$/;   // same rule as the server

function check(username, password) {
  const e = {};
  if (!username.trim()) e.username = "Enter your username.";
  else if (!USER_RE.test(username.trim())) e.username = "Use letters, numbers, dot, dash or underscore (up to 64 characters).";
  if (!password) e.password = "Enter your password.";
  else if (password.length > 128) e.password = "The password is too long (128 characters at most).";
  return e;
}

export default function Login({ onDone, notice }) {
  const [username, setU] = useState("");
  const [password, setP] = useState("");
  const [touched, setTouched] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const errors = check(username, password);
  const show = (k) => touched[k] && errors[k];

  async function submit(e) {
    e.preventDefault();
    setTouched({ username: true, password: true });
    if (Object.keys(errors).length) return;
    setBusy(true); setError("");
    try { await login(username.trim(), password); onDone(); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  return (
    <div className="login">
      <div className="hero">
        <div className="brand"><Logo />Insider Threat Review</div>
        <h1>See which work sessions need a second look.</h1>
        <p>Every flag comes with a risk score, the behaviors behind it, and how it differs from that user's own normal.</p>
        <p className="note">Read-only review. Use HTTPS in any real deployment.</p>
      </div>
      <div className="formside">
        <form onSubmit={submit} noValidate>
          <h2>Sign in</h2>
          <p className="muted">Use your analyst account.</p>
          {notice && <p className="info" role="status">{notice}</p>}
          <label htmlFor="u">Username</label>
          <input id="u" value={username} onChange={(e) => setU(e.target.value)} onBlur={() => setTouched((t) => ({ ...t, username: true }))}
            autoComplete="username" autoFocus aria-invalid={!!show("username")} aria-describedby="u-err" />
          <p id="u-err" className="field-error" role="alert">{show("username") || ""}</p>
          <label htmlFor="p">Password</label>
          <input id="p" type="password" value={password} onChange={(e) => setP(e.target.value)} onBlur={() => setTouched((t) => ({ ...t, password: true }))}
            autoComplete="current-password" aria-invalid={!!show("password")} aria-describedby="p-err" />
          <p id="p-err" className="field-error" role="alert">{show("password") || ""}</p>
          {error && <p className="error" role="alert" style={{ marginTop: 14 }}>{error}</p>}
          <button className="btn" style={{ width: "100%", marginTop: 18 }} disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
          <p className="muted small" style={{ marginTop: 14 }}>Sessions expire after 30 minutes. After 5 failed attempts, sign-in pauses for 15 minutes.</p>
        </form>
      </div>
    </div>
  );
}
