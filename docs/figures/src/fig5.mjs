import fs from "fs";
import { Diagram } from "./dfdlib.mjs";

const W = 650, H = 752;
const d = new Diagram(W, H);
const xA1 = 10, xB = 330, xB2 = 640, top = 8, bottom = 742, head = 34;

// partitions (swimlanes)
d.add(`<rect x="${xA1}" y="${top}" width="${xB - xA1}" height="${bottom - top}" fill="none" stroke="#000" stroke-width="1.6"/>`);
d.add(`<rect x="${xB}" y="${top}" width="${xB2 - xB}" height="${bottom - top}" fill="none" stroke="#000" stroke-width="1.6"/>`);
d.add(`<line x1="${xA1}" y1="${top + head}" x2="${xB2}" y2="${top + head}" stroke="#000" stroke-width="1.6"/>`);
d.text((xA1 + xB) / 2, top + 22, "Batch flow (administrator)", { size: 13, bold: true });
d.text((xB + xB2) / 2, top + 22, "Analyst flow (analyst)", { size: 13, bold: true });

const cA = 160, cB = 492, AW = 212, BW = 176, AH = 38;
const ys = [122, 176, 230, 284, 338, 392, 446];      // actions 1 to 7
const names = ["1 Ingest", "2 Sessions", "3 Features and baselines", "4 Models", "5 Risk score", "6 Explanation", "7 Storage"];

d.initial(cA, 76);
ys.forEach((y, i) => d.action(cA, y, AW, AH, [names[i]]));
d.flow([[cA, 84.5], [cA, ys[0] - AH / 2]]);
for (let i = 0; i < ys.length - 1; i++) d.flow([[cA, ys[i] + AH / 2], [cA, ys[i + 1] - AH / 2]]);

// datastore between the two partitions, on the row of action 7
const dsx = 330, dsy = ys[6];
d.objectNode(dsx, dsy, 92, 48, "«datastore»", ["MongoDB"]);
d.flow([[cA + AW / 2, dsy], [dsx - 46, dsy]]);
d.flow([[dsx + 46, dsy], [cB - BW / 2, dsy]]);

// analyst flow: it starts on its own, because the API is a separate process that runs independently of the batch run
const y8 = dsy, ym = 500, y9 = 556, yd = 612, y10 = 672, yf = 724;
d.initial(cB, 388);
d.flow([[cB, 396.5], [cB, y8 - AH / 2]]);
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
