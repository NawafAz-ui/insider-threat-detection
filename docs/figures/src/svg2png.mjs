// usage: node svg2png.mjs in.svg out.png [scale] [workdir]
// Rasterises an SVG with headless Chrome. The helper HTML page and the browser profile go to the work directory, not next to the output.
import fs from "fs";
import path from "path";
import os from "os";
import { execFileSync } from "child_process";
const [svg, png, scaleArg, workArg] = process.argv.slice(2);
const scale = Number(scaleArg || 3);
const work = path.resolve(workArg || fs.mkdtempSync(path.join(os.tmpdir(), "svg2png-")));
fs.mkdirSync(work, { recursive: true });
const s = fs.readFileSync(svg, "utf8");
const m = s.match(/width="(\d+)" height="(\d+)"/);
const w = Number(m[1]), h = Number(m[2]);
const html = path.join(work, path.basename(png).replace(/\.png$/, ".html"));
fs.writeFileSync(html, `<!doctype html><html><body style="margin:0;background:#fff"><img src="file://${path.resolve(svg)}" width="${w}" height="${h}" style="display:block"></body></html>`);
try {
  execFileSync("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", ["--headless=new", "--disable-gpu", "--hide-scrollbars", `--user-data-dir=${path.join(work, "profile-" + Date.now())}`,
    `--window-size=${w},${h}`, `--force-device-scale-factor=${scale}`, "--default-background-color=FFFFFFFF", `--screenshot=${path.resolve(png)}`, "file://" + html], { stdio: "ignore" });
} catch (e) { /* Chrome can exit non-zero after writing the file */ }
if (!fs.existsSync(png) || fs.statSync(png).size < 1000) { console.error("no PNG written"); process.exit(1); }
console.log(`${path.basename(png)}: svg ${w}x${h} px, png ${w * scale}x${h * scale} px; at 15.9 cm wide the scale is ${(15.9 / (w / 96 * 2.54)).toFixed(2)}`);
