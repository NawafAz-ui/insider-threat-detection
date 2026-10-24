import { useEffect, useState } from "react";

// Hash routes: #/ (flagged list), #/session/S0000123 and #/user/U0027. The browser Back button and links work.
export function parse(hash) {
  let m = /^#\/session\/(S\d{1,12})$/.exec(hash);
  if (m) return { name: "session", id: m[1] };
  m = /^#\/user\/([A-Za-z0-9_.-]{1,64})$/.exec(hash);
  return m ? { name: "user", id: m[1] } : { name: "list" };
}
export const toList = () => { window.location.hash = "#/"; };
export const toUser = (id) => { window.location.hash = `#/user/${id}`; };
export const toSession = (id) => { window.location.hash = `#/session/${id}`; };

export function useRoute() {
  const [route, setRoute] = useState(parse(window.location.hash));
  useEffect(() => {
    const on = () => { setRoute(parse(window.location.hash)); window.scrollTo(0, 0); };
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);
  return route;
}
