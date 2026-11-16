import fs from "fs";
import { Diagram } from "./dfdlib.mjs";

// Figure 1: UML component diagram. Three tier packages, components with the component symbol,
// dashed arrows = "uses" (dependency). usage: node fig1.mjs out.svg
const W = 750, H = 700;
const d = new Diagram(W, H);

function pkg(x1, y1, x2, y2, tabW, title) {      // package: tab at the top left, body below
  d.add(`<rect x="${x1}" y="${y1 + 20}" width="${x2 - x1}" height="${y2 - y1 - 20}" fill="none" stroke="#000" stroke-width="1.6"/>`);
  d.add(`<rect x="${x1}" y="${y1}" width="${tabW}" height="20" fill="#fff" stroke="#000" stroke-width="1.6"/>`);
  d.text(x1 + tabW / 2, y1 + 14.5, title, { size: 12.5, bold: true });
}
function icon(x, y) {                            // UML component symbol: a box with two small tabs
  d.add(`<rect x="${x}" y="${y}" width="16" height="11" fill="#fff" stroke="#000" stroke-width="1.1"/>` +
    `<rect x="${x - 4}" y="${y + 2}" width="8" height="3" fill="#fff" stroke="#000" stroke-width="1.1"/>` +
    `<rect x="${x - 4}" y="${y + 6.5}" width="8" height="3" fill="#fff" stroke="#000" stroke-width="1.1"/>`);
}
function comp(x1, y1, x2, y2, iconDx = 26, iconDy = 7) {
  d.add(`<rect x="${x1}" y="${y1}" width="${x2 - x1}" height="${y2 - y1}" fill="#fff" stroke="#000" stroke-width="1.5"/>`);
  icon(x2 - iconDx, y1 + iconDy);
}
function artifact(x1, y1, x2, y2) {              // document with a folded corner
  const f = 14;
  d.add(`<path d="M${x1} ${y1} H${x2 - f} L${x2} ${y1 + f} V${y2} H${x1} Z" fill="#fff" stroke="#000" stroke-width="1.5"/>` +
    `<path d="M${x2 - f} ${y1} V${y1 + f} H${x2}" fill="none" stroke="#000" stroke-width="1.2"/>`);
}
function cylinder(x1, x2, yTop, yBot, ry) {      // database symbol
  const rx = (x2 - x1) / 2, cx = (x1 + x2) / 2;
  d.add(`<path d="M${x1} ${yTop} V${yBot} A${rx} ${ry} 0 0 0 ${x2} ${yBot} V${yTop}" fill="#fff" stroke="#000" stroke-width="1.5"/>` +
    `<ellipse cx="${cx}" cy="${yTop}" rx="${rx}" ry="${ry}" fill="#fff" stroke="#000" stroke-width="1.5"/>`);
  return (x) => yTop - ry * Math.sqrt(1 - ((x - cx) / rx) ** 2);   // y of the top edge at x
}

// tiers
pkg(365, 15, 555, 125, 130, "Presentation tier");
pkg(20, 150, 560, 470, 120, "Application tier");
pkg(20, 540, 560, 685, 70, "Data tier");

// presentation tier
comp(380, 52, 540, 108);
d.text(460, 85, "React dashboard", { size: 12.5, bold: true });

// application tier
comp(35, 205, 190, 370);
d.text(112, 240, "Batch engine", { size: 12.5, bold: true });
d.text(112, 262, ["checks the folder,", "reads logs, builds", "sessions and features,", "scores with three", "models, explains", "and stores results"], { size: 12, lh: 15.5 });

comp(205, 205, 360, 370);
d.text(282, 252, ["Administration", "commands"], { size: 12.5, bold: true, lh: 15 });
d.text(282, 291, ["analyst accounts,", "database rules,", "backup and restore"], { size: 12, lh: 15.5 });

comp(375, 205, 545, 370);
d.text(460, 240, "REST API", { size: 12.5, bold: true });
d.text(460, 257, "FastAPI, eleven endpoints", { size: 11.5 });
comp(388, 270, 532, 306, 24, 5);
d.text(446, 292, "Security controls", { size: 12 });
comp(388, 316, 532, 352, 24, 5);
d.text(446, 338, "Assistant", { size: 12 });

comp(205, 395, 320, 455);                        // performs the runs that the dashboard requests
d.text(255, 428, "Run worker", { size: 12.5, bold: true });
d.text(255, 444, "one run at a time", { size: 11 });

// outside the tiers
artifact(35, 40, 190, 100);
d.text(112, 66, "CSV log files", { size: 12.5, bold: true });
d.text(112, 83, "(CERT layout)", { size: 12 });

comp(636, 294, 740, 374);
d.text(688, 328, "«external»", { size: 11.5 });
d.text(688, 344, ["Hosted language", "model (optional)"], { size: 12, lh: 15 });

// data tier
const top = cylinder(55, 525, 585, 650, 10);
d.text(290, 617, "MongoDB", { size: 12.5, bold: true });
d.text(290, 632, "results, user_baselines, trained_models (GridFS),", { size: 11.5 });
d.text(290, 646, "runs, run_requests, analyst_accounts, access_log", { size: 11.5 });

// dependencies ("uses")
d.dashed([[460, 108], [460, 205]], { label: ["calls", "over HTTP"], lx: 468, ly: 148, anchor: "start" });
d.dashed([[170, 205], [170, 100]], { label: "reads", lx: 178, ly: 135, anchor: "start" });
d.dashed([[532, 334], [636, 334]], { label: ["evidence,", "question"], lx: 598, ly: 312 });
d.dashed([[205, 425], [150, 425], [150, 370]], { label: "runs", lx: 178, ly: 418 });
d.dashed([[110, 370], [110, top(110)]], { label: ["writes results, runs,", "baselines, models;", "reads saved baselines", "and models"], lx: 118, ly: 487, anchor: "start" });
d.dashed([[262, 455], [262, top(262)]], { label: ["requests,", "status"], lx: 270, ly: 492, anchor: "start" });
d.dashed([[345, 370], [345, top(345)]], { label: ["accounts, rules,", "backups"], lx: 353, ly: 492, anchor: "start" });
d.dashed([[470, 370], [470, top(470)]], { label: ["reads stored data;", "writes access log", "and run requests"], lx: 478, ly: 487, anchor: "start" });

fs.writeFileSync(process.argv[2], d.svg());
