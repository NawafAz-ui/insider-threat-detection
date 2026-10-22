import { useEffect, useState } from "react";

// Hash routes: #/ (flagged list) and #/session/S0000123. The browser Back button and links work.
export function parse(hash) {
  const m = /^#\/session\/(S\d{1,12})$/.exec(hash);
  return m ? { name: "session", id: m[1] } : { name: "list" };
}
export const toList = () => { window.location.hash = "#/"; };
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
