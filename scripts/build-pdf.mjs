#!/usr/bin/env node
// Build the book (or selected chapters) into a single PDF.
//
//   node scripts/build-pdf.mjs                      # whole book -> dist/Applications-and-Integrations.pdf
//   node scripts/build-pdf.mjs --parts P4,10,11     # selected part openers/chapters
//   node scripts/build-pdf.mjs --out my.pdf --html  # also keep the intermediate HTML
//
// Markdown is rendered with markdown-it, math with KaTeX (server side), and the
// page is printed to PDF by a locally installed Chrome/Edge/Chromium through
// puppeteer-core. Set CHROME_PATH to point at a specific browser binary.
import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync } from "node:fs";
import { dirname, resolve, join } from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import MarkdownIt from "markdown-it";
import texmath from "markdown-it-texmath";
import katex from "katex";
import puppeteer from "puppeteer-core";
import { ROOT, BOOK_TITLE, BOOK_SUBTITLE, PDF_NAME, listParts, findPart, readPart } from "../lib/book.mjs";

const require = createRequire(import.meta.url);
// Inline KaTeX's stylesheet, pointing its font URLs at the installed font files.
const KATEX_CSS_PATH = require.resolve("katex/dist/katex.min.css");
const KATEX_CSS = readFileSync(KATEX_CSS_PATH, "utf8").replace(
  /url\((fonts\/[^)]+)\)/g,
  (_, f) => `url(${pathToFileURL(join(dirname(KATEX_CSS_PATH), f)).href})`,
);

const BROWSER_CANDIDATES = {
  win32: [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
  ],
  darwin: [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
  ],
  linux: [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/microsoft-edge",
  ],
};

export function findBrowser() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const hit = (BROWSER_CANDIDATES[process.platform] ?? []).find((p) => existsSync(p));
  if (!hit) throw new Error("No Chrome/Edge/Chromium found. Set CHROME_PATH to a Chromium-based browser binary.");
  return hit;
}

const slug = (s) =>
  s.toLowerCase().normalize("NFKD").replace(/[^\w\s.-]/g, "").trim().replace(/[\s.]+/g, "-");

function makeRenderer(part, mathErrors) {
  const md = new MarkdownIt({ html: true, linkify: true, typographer: false });
  md.use(texmath, {
    engine: katex,
    delimiters: "dollars",
    katexOptions: { throwOnError: false, strict: "ignore", output: "html" },
  });

  // Unique heading ids, prefixed by part so anchors never collide across chapters.
  md.renderer.rules.heading_open = (tokens, i, opts, env, self) => {
    const title = tokens[i + 1].children.map((t) => t.content).join("");
    tokens[i].attrSet("id", `p${part.id}-${slug(title)}`);
    return self.renderToken(tokens, i, opts);
  };

  // Resolve image paths relative to the source Markdown file.
  const defaultImage = md.renderer.rules.image;
  md.renderer.rules.image = (tokens, i, opts, env, self) => {
    const src = tokens[i].attrGet("src");
    if (src && !/^[a-z]+:/i.test(src)) {
      tokens[i].attrSet("src", pathToFileURL(resolve(dirname(part.file), decodeURI(src))).href);
    }
    return defaultImage(tokens, i, opts, env, self);
  };

  return (text) => {
    const html = md.render(text);
    for (const m of html.matchAll(/class="katex-error"[^>]*title="([^"]*)"/g)) {
      mathErrors.push(`${part.relPath}: ${m[1].replace(/&#x27;/g, "'").slice(0, 160)}`);
    }
    return html;
  };
}

const CSS = `
@page { size: A4; margin: 22mm 18mm 22mm 18mm; }
html { font-size: 10.5pt; }
body { font-family: "Charter", "Georgia", "Cambria", serif; color: #1d1d1d; line-height: 1.5; }
h1, h2, h3, h4 { font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; color: #12355b; line-height: 1.25; break-after: avoid; }
h1 { font-size: 22pt; margin: 0 0 6mm; border-bottom: 2px solid #0b6e4f; padding-bottom: 3mm; }
section.partpage { padding-top: 55mm; }
section.partpage h1 { font-size: 28pt; color: #0b6e4f; border-bottom: 3px solid #0b6e4f; }
h2 { font-size: 14pt; margin-top: 8mm; }
h3 { font-size: 11.5pt; margin-top: 6mm; }
section.part { break-before: page; }
p, li { text-align: justify; hyphens: auto; }
hr { border: none; border-top: 1px solid #ccd; margin: 6mm 0; }
blockquote { margin: 4mm 0; padding: 2mm 4mm; background: #f2f6fb; border-left: 3px solid #12355b; break-inside: avoid; }
blockquote p { margin: 1mm 0; }
blockquote p > strong:first-child { display: block; }
table { border-collapse: collapse; margin: 4mm auto; font-size: 9.5pt; break-inside: avoid; }
th, td { border: 1px solid #c8cfd8; padding: 1.5mm 2.5mm; vertical-align: top; text-align: left; }
th { background: #e8eef5; }
img { display: block; max-width: 100%; max-height: 120mm; margin: 4mm auto 1mm; break-inside: avoid; }
p:has(> img) { break-after: avoid; margin-bottom: 0; }
p:has(> img) + p:has(> em:only-child) { break-before: avoid; break-inside: avoid; }
p:has(> img) + p > em:only-child { display: block; text-align: center; font-size: 9pt; color: #444; }
code { font-family: Consolas, "DejaVu Sans Mono", monospace; font-size: 9pt; background: #f4f4f4; padding: 0 1mm; }
pre { background: #f4f4f4; padding: 3mm; overflow-x: hidden; white-space: pre-wrap; font-size: 8.5pt; break-inside: avoid; }
eq { display: inline; }
eqn { display: block; overflow-x: auto; overflow-y: hidden; margin: 3mm 0; break-inside: avoid; }
.katex { font-size: 1.05em; }
.katex-display { margin: 0; }
.katex-error { color: #b00020; }
.cover { height: 240mm; display: flex; flex-direction: column; justify-content: center; text-align: center; }
.cover h1 { border: none; font-size: 30pt; }
.cover .sub { font-size: 13pt; color: #444; font-style: italic; }
.toc h2 { margin-top: 0; }
.toc ol { list-style: none; padding: 0; }
.toc li { margin: 1.6mm 0; text-align: left; }
.toc li.toc-part { margin-top: 4mm; font-weight: bold; font-family: "Segoe UI", Arial, sans-serif; }
.toc li.toc-chapter { padding-left: 6mm; }
.toc a { color: #12355b; text-decoration: none; }
a { color: #1a4f8b; }
`;

/**
 * Build a PDF. Returns { out, parts, pages?, mathErrors, missingImages }.
 * @param {{ parts?: string[], out?: string, keepHtml?: boolean, log?: (s: string) => void }} opts
 */
export async function buildPdf({ parts: ids, out, keepHtml = false, log = console.error } = {}) {
  const all = listParts();
  const parts = ids?.length
    ? ids.map((id) => findPart(id) ?? (() => { throw new Error(`Unknown part "${id}"`); })())
    : all;
  out = resolve(out ?? join(ROOT, "dist", parts.length === all.length ? `${PDF_NAME}.pdf` : `${PDF_NAME}-excerpt.pdf`));
  mkdirSync(dirname(out), { recursive: true });

  const mathErrors = [];
  const missingImages = [];
  const bodies = parts.map((part) => {
    const text = readPart(part);
    for (const m of text.matchAll(/!\[[^\]]*\]\(([^)\s]+)\)/g)) {
      if (!/^[a-z]+:/i.test(m[1]) && !existsSync(resolve(dirname(part.file), decodeURI(m[1])))) {
        missingImages.push(`${part.relPath}: ${m[1]}`);
      }
    }
    const h1 = slug(part.title);
    return { part, anchor: `p${part.id}-${h1}`, html: makeRenderer(part, mathErrors)(text) };
  });

  const toc = bodies
    .map((b) => `<li class="toc-${b.part.kind}"><a href="#${b.anchor}">${b.part.title}</a></li>`)
    .join("\n");
  const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>${BOOK_TITLE}</title>
<style>${KATEX_CSS}</style>
<style>${CSS}</style></head>
<body>
<div class="cover"><h1>${BOOK_TITLE}</h1>
<p class="sub">${BOOK_SUBTITLE}</p>
<p class="sub">From requirement to working system: design method, instrumentation and data acquisition, embedded and IoT systems, robotics and drones, industrial automation, solar, battery, EV and microgrid systems, communications, signal processing and biomedical instrumentation, engineering software and digital twins, and complete engineering projects.</p>
<p>The Studio of Sadiq · Golam Kuadir Khan Prince</p></div>
<section class="part toc"><h2>Contents</h2><ol>${toc}</ol></section>
${bodies.map((b) => `<section class="part${b.part.kind === "part" ? " partpage" : ""}">\n${b.html}\n</section>`).join("\n")}
</body></html>`;

  const htmlPath = out.replace(/\.pdf$/i, "") + ".html";
  writeFileSync(htmlPath, html);
  log(`Rendered ${parts.length} part(s) to HTML; printing PDF…`);

  const browser = await puppeteer.launch({
    executablePath: findBrowser(),
    headless: true,
    args: ["--allow-file-access-from-files", "--no-sandbox"],
  });
  try {
    const page = await browser.newPage();
    await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "networkidle0", timeout: 300_000 });
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({
      path: out,
      format: "A4",
      printBackground: true,
      preferCSSPageSize: true,
      outline: true,
      tagged: true,
      displayHeaderFooter: true,
      headerTemplate: `<div style="font-size:7pt;width:100%;text-align:center;color:#888;font-family:sans-serif">${BOOK_TITLE}</div>`,
      footerTemplate: `<div style="font-size:8pt;width:100%;text-align:center;color:#555;font-family:sans-serif"><span class="pageNumber"></span> / <span class="totalPages"></span></div>`,
      timeout: 600_000,
    });
  } finally {
    await browser.close();
    if (!keepHtml) rmSync(htmlPath, { force: true });
  }
  log(`Wrote ${out}`);
  if (mathErrors.length) log(`${mathErrors.length} math expression(s) failed to render:\n  ${mathErrors.join("\n  ")}`);
  if (missingImages.length) log(`${missingImages.length} missing image(s):\n  ${missingImages.join("\n  ")}`);
  return { out, parts: parts.map((p) => p.id), mathErrors, missingImages };
}

function parseArgs(argv) {
  const opts = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--parts" || a === "-p") opts.parts = argv[++i].split(",").map((s) => s.trim()).filter(Boolean);
    else if (a === "--out" || a === "-o") opts.out = argv[++i];
    else if (a === "--html") opts.keepHtml = true;
    else if (a === "--help" || a === "-h") {
      console.log("Usage: node scripts/build-pdf.mjs [--parts P1,1,2] [--out file.pdf] [--html]");
      process.exit(0);
    } else throw new Error(`Unknown argument ${a}`);
  }
  return opts;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  buildPdf(parseArgs(process.argv.slice(2))).catch((e) => {
    console.error(e.message);
    process.exit(1);
  });
}
