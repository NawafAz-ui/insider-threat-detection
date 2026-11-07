import fs from "fs";
import { Diagram } from "./dfdlib.mjs";

const d = new Diagram(660, 618);
d.boundary(125, 16, 535, 602, "Insider Threat Detection System");

const OW = 172, OH = 50, L = 230, R = 430;
const uc = {};
const place = (id, cx, cy, lines) => { uc[id] = { cx, cy, a: OW / 2 }; d.usecase(cx, cy, OW, OH, lines); };
// analyst use cases in one column; UC4 sits above UC3 because it extends it (the user page, UC5, also opens from the flagged list, so it extends nothing)
place("UC1", L, 84, ["UC1", "Sign in"]);
place("UC2", L, 150, ["UC2 View flagged", "sessions"]);
place("UC4", L, 232, ["UC4 Ask the", "assistant"]);
place("UC3", L, 318, ["UC3 Open session", "detail"]);
place("UC5", L, 404, ["UC5 Investigate", "a user"]);
place("UC6", L, 478, ["UC6 View latest", "batch run"]);
place("UC7", L, 544, ["UC7", "Sign out"]);
// administrator use cases
place("UC8", R, 318, ["UC8 Run the", "batch engine"]);
place("UC9", R, 380, ["UC9 Manage analyst", "accounts"]);
place("UC10", R, 442, ["UC10 Apply and check", "database rules"]);
place("UC11", R, 504, ["UC11 Back up", "and restore"]);
place("UC12", R, 566 - 0, ["UC12 Check", "system health"]);

// actors outside the boundary
const ax = 58, ay = 290;
d.actor(ax, ay, ["Security", "analyst"]);
const bx = 600, by = 420;
d.actor(bx, by, ["Administrator"]);
const mx = 600, my = 170;
d.actor(mx, my, ["Hosted language", "model (optional)"]);

// associations: plain lines without arrowheads, from the actor to the near tip of the use case
const from = (x, y) => [x, y];
for (const id of ["UC1", "UC2", "UC4", "UC3", "UC5", "UC6", "UC7"]) d.line([ax + 14, ay + 38], [uc[id].cx - uc[id].a, uc[id].cy]);
for (const id of ["UC8", "UC9", "UC10", "UC11", "UC12"]) d.line([bx - 14, by + 38], [uc[id].cx + uc[id].a, uc[id].cy]);
d.line([mx - 14, my + 38], [uc.UC4.cx + uc.UC4.a, uc.UC4.cy]);

// extend: dashed arrow from the extending use case to the use case it extends
const gap = OH / 2;
d.dashed([[L, uc.UC4.cy + gap], [L, uc.UC3.cy - gap]], { label: ["«extend»"], lx: L + 8, ly: (uc.UC4.cy + uc.UC3.cy) / 2 + 4, anchor: "start" });

fs.writeFileSync(process.argv[2], d.svg());
