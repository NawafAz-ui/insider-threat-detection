import fs from "fs";
import { Diagram } from "./dfdlib.mjs";

// Figure 3: level-1 data-flow diagram (Gane-Sarson), four processes around one data store.
// usage: node fig3.mjs out.svg
const W = 780, H = 650, DY = 18;                 // DY: top margin for the run-request flows above the administrator
const d = new Diagram(W, H);
d.add(`<g transform="translate(0 ${DY})">`);
const PW = 140, PH = 58;

// external entities
d.entity(400, 45, 120, 38, ["Administrator"]);
d.entity(70, 175, 100, 38, ["Log sources"]);
d.entity(115, 455, 110, 40, ["Security analyst"]);
d.entity(625, 570, 120, 46, ["Hosted language", "model (optional)"]);

// processes
d.process(270, 175, PW, PH, "P1", ["Read logs and", "score sessions"]);
d.process(530, 175, PW, PH, "P2", ["Administer", "database"]);
d.process(400, 455, PW, PH, "P3", ["Serve analysts"]);
d.process(400, 570, PW, PH, "P4", ["Answer", "questions"]);

// data store
d.storeHorizontal(190, 600, 315, 38, "D1", "MongoDB database");

const A = (pts, label, x, y, anchor) => d.arrow(pts, { label, lx: x, ly: y, anchor });

// batch engine (started by a run command, or by the worker for a run request read from D1)
A([[120, 175], [200, 175]], ["CSV log", "files"], 160, 151);
A([[340, 38], [250, 38], [250, 146]], "run command", 242, 100, "end");
A([[290, 146], [290, 56], [340, 56]], "run summary", 298, 100, "start");
A([[250, 296], [250, 204]], ["saved", "baselines,", "models,", "run requests"], 242, 234, "end");
A([[290, 204], [290, 296]], ["results, baselines,", "models, run record,", "run status"], 298, 240, "start");

// administration
A([[460, 38], [555, 38], [555, 146]], ["account, rule,", "backup commands"], 563, 95, "start");
A([[505, 146], [505, 56], [460, 56]], ["check results,", "backups"], 497, 95, "end");
A([[510, 296], [510, 204]], ["data to check", "and back up"], 502, 246, "end");
A([[550, 204], [550, 296]], ["accounts, rules,", "restored data"], 558, 246, "start");

// dashboard runs: the administrator asks through the dashboard and follows the status there
A([[430, 26], [430, 10], [690, 10], [690, 445], [470, 445]], "run request", 682, 395, "end");
A([[470, 468], [712, 468], [712, -8], [415, -8], [415, 26]], "run status", 720, 240, "start");

// serving analysts
A([[380, 334], [380, 426]], ["results, runs,", "baselines, accounts,", "access log, run status"], 372, 362, "end");
A([[420, 426], [420, 334]], ["access log", "entries,", "run requests"], 428, 366, "start");
A([[170, 445], [330, 445]], ["login, questions,", "and clicks"], 250, 421);
A([[330, 468], [170, 468]], "screens", 250, 485);

// assistant and hosted language model
A([[380, 484], [380, 541]], ["stored session,", "question"], 372, 506, "end");
A([[420, 541], [420, 484]], ["answer,", "evidence ids"], 428, 506, "start");
A([[470, 556], [565, 556]], ["evidence,", "question"], 517, 532);
A([[565, 584], [470, 584]], ["statements,", "evidence ids"], 517, 600);

d.add("</g>");
fs.writeFileSync(process.argv[2], d.svg());
