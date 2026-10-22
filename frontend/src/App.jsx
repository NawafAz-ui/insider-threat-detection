import { useEffect, useState } from "react";
import { getUsername, isLoggedIn, logout } from "./api.js";
import { toList, useRoute } from "./router.js";
import Login from "./pages/Login.jsx";
import FlaggedSessions from "./pages/FlaggedSessions.jsx";
import SessionDetail from "./pages/SessionDetail.jsx";
import Logo from "./Logo.jsx";

export default function App() {
  const [authed, setAuthed] = useState(isLoggedIn());
  const [notice, setNotice] = useState("");
  const route = useRoute();

  useEffect(() => {
    const expired = () => { setAuthed(false); setNotice("Your session expired. Sign in again."); };
    window.addEventListener("auth-expired", expired);
    return () => window.removeEventListener("auth-expired", expired);
  }, []);

  if (!authed) return <Login notice={notice} onDone={() => { setNotice(""); setAuthed(true); }} />;
  return (
    <>
      <header className="bar">
        <button className="brand" onClick={toList}><Logo />Insider Threat Review</button>
        <span className="who">{getUsername()} · Analyst
          <button className="link" onClick={() => { logout(); setNotice(""); setAuthed(false); toList(); }}>Sign out</button></span>
      </header>
      <main className="wrap">
        {route.name === "session" ? <SessionDetail key={route.id} id={route.id} /> : <FlaggedSessions />}
      </main>
    </>
  );
}
