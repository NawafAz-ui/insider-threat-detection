import fs from "fs";
import { Diagram } from "./dfdlib.mjs";

const W = 650, H = 884;
const d = new Diagram(W, H);
const xA1 = 10, xB = 330, xB2 = 640, top = 8, bottom = 874, head = 50;

// partitions (swimlanes)
d.add(`<rect x="${xA1}" y="${top}" width="${xB - xA1}" height="${bottom - top}" fill="none" stroke="#000" stroke-width="1.6"/>`);
d.add(`<rect x="${xB}" y="${top}" width="${xB2 - xB}" height="${bottom - top}" fill="none" stroke="#000" stroke-width="1.6"/>`);
d.add(`<line x1="${xA1}" y1="${top + head}" x2="${xB2}" y2="${top + head}" stroke="#000" stroke-width="1.6"/>`);
d.text((xA1 + xB) / 2, top + 22, "Batch flow (administrator)", { size: 13, bold: true });
d.text((xA1 + xB) / 2, top + 40, "started from the command line or the dashboard", { size: 11.5 });
d.text((xB + xB2) / 2, top + 22, "Analyst flow (analyst)", { size: 13, bold: true });

const cA = 160, cB = 492, AW = 212, BW = 176, AH = 38;

// input check: errors stop the batch flow before anything is read (flow final node)
d.initial(cA, 92);
d.action(cA, 138, AW, AH, ["0 Validate input"]);
d.flow([[cA, 100.5], [cA, 138 - AH / 2]]);
const yv = 190;
d.diamond(cA, yv, 46, 30);
d.flow([[cA, 138 + AH / 2], [cA, yv - 15]]);
const fx = 292;
d.flow([[cA + 23, yv], [fx - 11, yv]], { label: ["[input errors]"], lx: 232, ly: yv - 8 });
d.add(`<circle cx="${fx}" cy="${yv}" r="10" fill="#fff" stroke="#000" stroke-width="1.5"/>` +
  `<path d="M${fx - 7} ${yv - 7} L${fx + 7} ${yv + 7} M${fx + 7} ${yv - 7} L${fx - 7} ${yv + 7}" stroke="#000" stroke-width="1.5"/>`);

const ys = [254, 308, 362, 416, 470, 524, 578];      // actions 1 to 7
const names = ["1 Ingest", "2 Sessions", "3 Features and baselines", "4 Models", "5 Risk score", "6 Explanation", "7 Storage"];
ys.forEach((y, i) => d.action(cA, y, AW, AH, [names[i]]));
d.flow([[cA, yv + 15], [cA, ys[0] - AH / 2]], { label: ["[no errors]"], lx: cA + 8, ly: yv + 33, anchor: "start" });
for (let i = 0; i < ys.length - 1; i++) d.flow([[cA, ys[i] + AH / 2], [cA, ys[i + 1] - AH / 2]]);

// datastore between the two partitions, on the row of action 7
const dsx = 330, dsy = ys[6];
d.objectNode(dsx, dsy, 92, 48, "«datastore»", ["MongoDB"]);
d.flow([[cA + AW / 2, dsy], [dsx - 46, dsy]]);
d.flow([[dsx + 46, dsy], [cB - BW / 2, dsy]]);

// analyst flow: it starts on its own, because the API is a separate process that runs independently of the batch run
const y8 = dsy, ym = y8 + 54, y9 = ym + 56, yd = y9 + 56, y10 = yd + 60, yf = y10 + 52;
d.initial(cB, y8 - 58);
d.flow([[cB, y8 - 49.5], [cB, y8 - AH / 2]]);
d.action(cB, y8, BW, AH, ["8 REST API"]);
d.diamond(cB, ym, 46, 30);                       // merge: first arrival and return from the assistant
d.flow([[cB, y8 + AH / 2], [cB, ym - 15]]);
d.action(cB, y9, BW, AH, ["9 Dashboard"]);
d.flow([[cB, ym + 15], [cB, y9 - AH / 2]]);
d.diamond(cB, yd, 46, 34);                       // decision: the analyst may ask any number of questions, or none
d.flow([[cB, y9 + AH / 2], [cB, yd - 17]]);
d.action(cB, y10, BW, AH, ["10 Assistant"]);
d.flow([[cB, yd + 17], [cB, y10 - AH / 2]], { label: ["[question asked]"], lx: cB + 8, ly: yd + 31, anchor: "start" });
d.flow([[cB - BW / 2, y10], [cB - 120, y10], [cB - 120, ym], [cB - 23, ym]]);   // back to the dashboard
d.finalNode(cB, yf);
d.flow([[cB + 23, yd], [cB + 100, yd], [cB + 100, yf], [cB + 11, yf]], { label: ["[no question]"], lx: cB + 30, ly: yd - 7, anchor: "start" });

fs.writeFileSync(process.argv[2], d.svg());
