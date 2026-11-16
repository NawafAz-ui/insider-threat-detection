// Page load in a real browser for the integrated test (IT9): time to the sign-in form, and from "Sign in" to the flagged list.
// node scripts/page_load.mjs <dashboard url> <user> <password>   needs puppeteer-core on NODE_PATH and Chrome (CHROME to override)
import { createRequire } from "node:module";
const puppeteer = createRequire(import.meta.url)("puppeteer-core");   // require() honours NODE_PATH, import does not

const [url, user, password] = process.argv.slice(2);
const browser = await puppeteer.launch({
  executablePath: process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless: true });
try {
  const page = await browser.newPage();
  let t = performance.now();
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#u", { timeout: 15000 });
  const loginPageMs = performance.now() - t;
  await page.type("#u", user);
  await page.type("#p", password);
  t = performance.now();
  await page.click("button.btn");
  await page.waitForSelector("tbody tr", { timeout: 15000 });
  console.log(JSON.stringify({ login_page_ms: Math.round(loginPageMs), flagged_list_ms: Math.round(performance.now() - t) }));
} finally {
  await browser.close();
}
