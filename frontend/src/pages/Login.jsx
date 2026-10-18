import { useState } from "react";
import { login } from "../api.js";
import Logo from "../Logo.jsx";

export default function Login({ onDone }) {
  const [username, setU] = useState("");
  const [password, setP] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true); setError("");
    try { await login(username, password); onDone(); }
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
        <form onSubmit={submit}>
          <h2>Sign in</h2>
          <p className="muted">Use your analyst account.</p>
          <label htmlFor="u">Username</label>
          <input id="u" value={username} onChange={(e) => setU(e.target.value)} autoComplete="username" autoFocus />
          <label htmlFor="p">Password</label>
          <input id="p" type="password" value={password} onChange={(e) => setP(e.target.value)} autoComplete="current-password" />
          {error && <p className="error" role="alert" style={{ marginTop: 14 }}>{error}</p>}
          <button className="btn" style={{ width: "100%", marginTop: 18 }} disabled={busy || !username || !password}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
          <p className="muted small" style={{ marginTop: 14 }}>Sessions expire after 30 minutes. After 5 failed attempts, sign-in pauses for 15 minutes.</p>
        </form>
      </div>
    </div>
  );
}
