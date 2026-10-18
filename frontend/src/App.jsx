import { useState } from "react";
import { getUsername, isLoggedIn, logout } from "./api.js";
import Login from "./pages/Login.jsx";
import FlaggedSessions from "./pages/FlaggedSessions.jsx";
import SessionDetail from "./pages/SessionDetail.jsx";
import Logo from "./Logo.jsx";

export default function App() {
  const [authed, setAuthed] = useState(isLoggedIn());
  const [openId, setOpenId] = useState(null);

  if (!authed) return <Login onDone={() => setAuthed(true)} />;
  return (
    <>
      <header className="bar">
        <button className="brand" onClick={() => setOpenId(null)}><Logo />Insider Threat Review</button>
        <span className="who">{getUsername()} · Analyst
          <button className="link" onClick={() => { logout(); setAuthed(false); }}>Sign out</button></span>
      </header>
      <main className="wrap">
        {openId ? <SessionDetail id={openId} onBack={() => setOpenId(null)} /> : <FlaggedSessions onOpen={setOpenId} />}
      </main>
    </>
  );
}
