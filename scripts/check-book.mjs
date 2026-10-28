#!/usr/bin/env node
// Consistency checks for the book sources. Exits non-zero if any check fails.
//
//   node scripts/check-book.mjs
//
// Checks: every chapter in TOC.md exists; each chapter has the required layout;
// math delimiters balance; no control or tab characters; figure markers are well formed,
// numbered in order and drawn; every image and relative link resolves.
import { readFileSync, existsSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { ROOT, listParts, readPart, figureMarkers } from "../lib/book.mjs";

const errors = [];
const err = (file, msg) => errors.push(`${file}: ${msg}`);

const parts = listParts();
const chapters = parts.filter((p) => p.kind === "chapter");

// 1. TOC ↔ files.
const toc = readFileSync(join(ROOT, "TOC.md"), "utf8");
let tocPart = "";
const tocFiles = [];
for (const line of toc.split(/\r?\n/)) {
  const p = /^## Part .*`(part-[^`]+)\/`/.exec(line);
  if (p) tocPart = p[1];
  const c = /^### Chapter (\d+)\..*`(\d+-[^`]+\.md)`/.exec(line);
  if (c) tocFiles.push({ n: Number(c[1]), rel: `${tocPart}/${c[2]}` });
}
for (const { n, rel } of tocFiles) if (!existsSync(join(ROOT, rel))) err("TOC.md", `Chapter ${n} file missing: ${rel}`);
if (tocFiles.length !== chapters.length) err("TOC.md", `${tocFiles.length} chapters in TOC, ${chapters.length} chapter files`);

const last = Math.max(...chapters.map((c) => Number(c.id)));
for (const part of parts) {
  const text = readPart(part);
  const f = part.relPath;

  // 2. Text hygiene.
  if (/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(text)) err(f, "control character (an unescaped \\a, \\b or \\f in LaTeX?)");
  if (/\t/.test(text)) err(f, "tab character (an unescaped \\t in \\times, \\theta or \\tau?)");
  const lines = text.split(/\r?\n/);
  let inFence = false;
  const prose = [];
  for (const l of lines) {
    if (/^\s*```/.test(l)) inFence = !inFence;
    else if (!inFence) prose.push(l);
  }
  const body = prose.join("\n").replace(/<!--[\s\S]*?-->/g, "");
  if ((body.match(/\$\$/g) ?? []).length % 2) err(f, "unbalanced $$");
  if ((body.replace(/\$\$[\s\S]*?\$\$/g, "").replace(/\\\$/g, "").match(/\$/g) ?? []).length % 2) err(f, "unbalanced $");
  if (/\\\(|\\\[/.test(body)) err(f, "uses \\( or \\[ math delimiters; use $ and $$");

  // 3. Layout.
  if (part.kind === "chapter") {
    if (!new RegExp(`^# Chapter ${part.id} — `, "m").test(text)) err(f, `first heading must be "# Chapter ${part.id} — Title"`);
    if (!/^## What remains open/m.test(text)) err(f, 'missing "## What remains open"');
    if (Number(part.id) !== last && !/^\*\*Next:\*\*/m.test(text)) err(f, 'missing "**Next:**" line');
    if (!/Status of the principle/.test(text)) err(f, "no status box");
  } else if (!/^# Part [IVX]+ — /m.test(text)) err(f, 'part opener must start "# Part <Roman> — Title"');

  // 4. Figure markers.
  if (part.kind === "chapter") {
    figureMarkers(part, text).forEach((m, i) => {
      const where = `${f}:${m.line}`;
      if (!m.number || !m.path || !m.kind || !m.caption) return err(where, "malformed FIGURE marker");
      if (m.number !== `${part.id}.${i + 1}`) err(where, `figure ${m.number} out of order (expected ${part.id}.${i + 1})`);
      const nn = String(part.id).padStart(2, "0");
      if (!m.path.startsWith(`figures/ch${nn}/`)) err(where, `figure path should be under figures/ch${nn}/`);
      if (!existsSync(join(ROOT, m.path))) err(where, `figure ${m.number} not drawn: ${m.path}`);
    });
  }

  // 5. Images and relative links.
  for (const m of text.matchAll(/!?\[[^\]]*\]\(([^)\s]+)\)/g)) {
    const target = m[1].split("#")[0];
    if (!target || /^[a-z]+:/i.test(target)) continue;
    if (!existsSync(resolve(dirname(part.file), decodeURI(target)))) err(f, `broken link or image: ${m[1]}`);
  }
}

console.error(`Checked ${parts.length} files (${chapters.length} chapters).`);
if (errors.length) {
  console.error(`${errors.length} problem(s):\n  ${errors.join("\n  ")}`);
  process.exit(1);
}
console.error("All checks passed.");
