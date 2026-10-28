#!/usr/bin/env node
// Place each drawn figure into its chapter, directly below its <!-- FIGURE ... --> marker.
//
//   node scripts/insert-figures.mjs          # insert every figure whose PNG exists
//   node scripts/insert-figures.mjs --check  # only report what would change
//
// The marker stays as the figure's specification (FIGURES.md is generated from it);
// the image line and italic caption follow it. Running it again is a no-op.
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { ROOT, listParts } from "../lib/book.mjs";

const check = process.argv.includes("--check");
const MARKER = /^(<!--\s*FIGURE\s+([\s\S]*?)-->)[ \t]*\r?\n/gm;
let inserted = 0;
const missing = [];

for (const ch of listParts().filter((p) => p.kind === "chapter")) {
  const text = readFileSync(ch.file, "utf8");
  const next = text.replace(MARKER, (whole, marker, body, offset) => {
    const [number, path, , caption] = body.split("|").map((s) => s.trim());
    const rest = text.slice(offset + whole.length).replace(/^\s*/, "");
    if (rest.startsWith(`![Figure ${number} `)) return whole; // already placed
    if (!existsSync(join(ROOT, path))) {
      missing.push(`${ch.relPath}: Figure ${number} (${path})`);
      return whole;
    }
    inserted++;
    const alt = caption.replace(/\$[^$]*\$/g, "").replace(/[[\]]/g, "").replace(/\s+/g, " ").trim().replace(/\.$/, "");
    const cap = caption.replace(/\s*\.?$/, ".");
    return `${marker}\n\n![Figure ${number} — ${alt}](../${encodeURI(path)})\n\n*Figure ${number} — ${cap}*\n`;
  });
  if (next !== text && !check) writeFileSync(ch.file, next);
}

console.error(`${check ? "Would insert" : "Inserted"} ${inserted} figure(s).`);
if (missing.length) console.error(`${missing.length} figure(s) not drawn yet:\n  ${missing.join("\n  ")}`);
