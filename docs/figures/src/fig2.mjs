import fs from "fs";
import { Diagram } from "./dfdlib.mjs";

const d = new Diagram(700, 530);
d.entity(80, 262, 130, 44, ["Log sources"]);
d.entity(350, 60, 140, 44, ["Administrator"]);
d.entity(350, 470, 140, 44, ["Security analyst"]);
d.entity(620, 262, 150, 50, ["Hosted language", "model (optional)"]);
d.process(350, 262, 190, 84, "0", ["Insider Threat", "Detection System"]);

const A = (pts, label, x, y, anchor) => d.arrow(pts, label ? { label, lx: x, ly: y, anchor } : {});
A([[145, 262], [255, 262]], ["CSV log files"], 200, 253);
A([[320, 82], [320, 220]], ["run command;", "account, rule,", "backup commands"], 312, 140, "end");
A([[380, 220], [380, 82]], ["run summary;", "check results,", "backups"], 388, 140, "start");
A([[320, 448], [320, 304]], ["login, questions,", "and clicks"], 312, 372, "end");
A([[380, 304], [380, 448]], ["screens"], 388, 380, "start");
A([[445, 250], [545, 250]], ["evidence,", "question"], 495, 219);
A([[545, 275], [445, 275]], ["statements,", "evidence ids"], 495, 296);
fs.writeFileSync(process.argv[2], d.svg());
