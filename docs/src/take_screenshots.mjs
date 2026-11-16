// Dashboard screenshots for docs/DEMO.md (driven by docs/src/demo_screenshots.py, which starts a copy of the database).
// node docs/src/take_screenshots.mjs <dashboard url> <api url> <password> <out dir>   needs puppeteer-core on NODE_PATH and Chrome
import { createRequire } from "node:module";
const puppeteer = createRequire(import.meta.url)("puppeteer-core");   // require() honours NODE_PATH, import does not
import { writeFileSync } from "node:fs";

const [web, api, password, out] = process.argv.slice(2);
const browser = await puppeteer.launch({
  executablePath: process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless: true });
const page = await browser.newPage();
await page.setViewport({ width: 1100, height: 900, deviceScaleFactor: 1.5 });
const shot = async (name, full = true) => { await new Promise((r) => setTimeout(r, 400)); await page.screenshot({ path: `${out}/${name}.png`, fullPage: full }); };
const textOf = (sel) => page.$eval(sel, (e) => e.innerText);

async function signIn(user) {
  await page.goto(web, { waitUntil: "networkidle0" });
  await page.evaluate(() => sessionStorage.clear());
  await page.goto(web, { waitUntil: "networkidle0" });
  await page.waitForSelector("#u");
  await page.type("#u", user);
  await page.type("#p", password);
  await page.click("button.btn");
  await page.waitForSelector('tbody tr[tabindex="0"]', { timeout: 20000 });
}

// Workflow 0: an administrator starts a run on SPEDIA
await signIn("admin");
await page.waitForSelector("#run-dataset");
await page.select("#run-dataset", "spedia_cert");
await shot("14-admin-run-panel", false);
await page.evaluate(() => [...document.querySelectorAll("button.btn")].find((b) => b.innerText === "Start run").click());
await page.waitForFunction(() => /Waiting for the worker|Running/.test(document.body.innerText), { timeout: 20000 });
await shot("15-run-requested", false);
await page.waitForFunction(() => /Finished/.test(document.body.innerText), { timeout: 120000 });
await page.evaluate(() => [...document.querySelectorAll("button.link")].find((b) => b.innerText === "Show details")?.click());
await shot("16-run-finished");
const token = await page.evaluate(() => sessionStorage.getItem("token"));
const report = await (await fetch(`${api}/api/run/report`, { headers: { Authorization: `Bearer ${token}` } })).text();
const rp = await browser.newPage();
await rp.setViewport({ width: 1100, height: 900, deviceScaleFactor: 1.5 });
await rp.setContent(report, { waitUntil: "load" });
await rp.screenshot({ path: `${out}/17-run-report.png`, fullPage: true });
await rp.close();

// Workflow 1: an analyst reviews the top session
await signIn("alice");
await shot("03-flagged-list");
await page.click('tbody tr[tabindex="0"]');   // the flagged list, not the run results table above it
await page.waitForSelector(".scorecard");
await shot("04-session-detail");
const ask = async (q) => {
  const before = await page.$$eval(".chat .msg", (e) => e.length);
  await page.type('input[aria-label="Question"]', q);
  await page.evaluate(() => [...document.querySelectorAll(".chat button.btn")].pop().click());
  await page.waitForFunction((n) => document.querySelectorAll(".chat .msg").length >= n + 2, { timeout: 20000 }, before);   // question and answer
};
await ask("Why was this session flagged?");
await shot("05-assistant-why-flagged");
const reasons = (await textOf("body")).toLowerCase();
const topic = reasons.includes("email") ? "Did they send email outside the company?" : reasons.includes("leak") ? "Did they visit leak sites?" : "Why is the USB use a concern?";
await ask(topic);
await shot("05b-assistant-focused-question");
writeFileSync(`${out}/questions.txt`, `Why was this session flagged?\n${topic}\n`);

// Workflow 2: the same user's history
await page.evaluate(() => document.querySelector("h1 button.link").click());
await page.waitForFunction(() => /session history/.test(document.body.innerText));
await page.waitForSelector("svg");
await shot("06-user-page");
const card = async (title, name) => {
  const h = await page.evaluateHandle((t) => [...document.querySelectorAll(".card h3")].find((e) => e.innerText === t)?.closest(".card"), title);
  await h.asElement().screenshot({ path: `${out}/${name}.png` });
};
await card("Risk over time", "07-risk-timeline");
await card("What is normal for this user", "08-user-tables");
console.log(JSON.stringify({ user: await textOf("h1") }));
await browser.close();
