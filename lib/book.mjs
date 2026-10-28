// Shared index of the book's Markdown sources, used by the PDF builder, the figure scripts and the MCP server.
//
// Layout: one folder per part, `part-N-<slug>/`. Its README.md is the part opener (id "P<N>");
// every `NN-<slug>.md` inside it is chapter NN (id "<NN>" without zero padding).
import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
export const BOOK_TITLE = "Applications and Integrations";
export const BOOK_SUBTITLE = "Book 6 — The Applications & Integrations Core";
export const PDF_NAME = "Applications-and-Integrations";

/** Part folders in order: [{ n, dir, abs }]. */
export function partDirs() {
  return readdirSync(ROOT)
    .map((d) => ({ d, m: /^part-(\d+)-/.exec(d) }))
    .filter(({ d, m }) => m && statSync(join(ROOT, d)).isDirectory())
    .map(({ d, m }) => ({ n: Number(m[1]), dir: d, abs: join(ROOT, d) }))
    .sort((a, b) => a.n - b.n);
}

/**
 * Every book file in reading order: each part opener followed by its chapters.
 * id: "1".."40" for chapters, "P1".."P9" for part openers.
 */
export function listParts() {
  const parts = [];
  for (const { n, abs } of partDirs()) {
    const opener = join(abs, "README.md");
    if (existsSync(opener)) parts.push({ kind: "part", id: `P${n}`, partNo: n, order: n * 1000, file: opener });
    for (const f of readdirSync(abs)) {
      const m = /^(\d+)-.+\.md$/i.exec(f);
      if (m) parts.push({ kind: "chapter", id: String(Number(m[1])), partNo: n, order: n * 1000 + Number(m[1]), file: join(abs, f) });
    }
  }
  parts.sort((a, b) => a.order - b.order);
  for (const p of parts) {
    const text = readFileSync(p.file, "utf8");
    p.title = (/^#\s+(.+)$/m.exec(text)?.[1] ?? p.id).trim();
    p.relPath = p.file.slice(ROOT.length + 1).replace(/\\/g, "/");
  }
  return parts;
}

/** Find a file by id: "5", "05", "chapter 5", "P2", "part 2". */
export function findPart(id) {
  const raw = String(id).trim().toLowerCase();
  const pm = /^(?:part|p)\s*(\d+)$/.exec(raw);
  const norm = pm ? `P${Number(pm[1])}` : String(Number(raw.replace(/^(chapter|ch)\s*/, "")));
  return listParts().find((p) => p.id === norm);
}

export function readPart(part) {
  return readFileSync(part.file, "utf8");
}

/** Split a file into its `## ` sections: [{ number, title, text }]; the first entry is the front matter. */
export function sections(text) {
  const lines = text.split(/\r?\n/);
  const out = [];
  let cur = { number: "", title: "(front matter)", lines: [] };
  for (const line of lines) {
    const m = /^##\s+(?:(\d+(?:\.\d+)*)\s+)?(.+)$/.exec(line);
    if (m) {
      out.push(cur);
      cur = { number: m[1] ?? "", title: m[2].trim(), lines: [] };
    }
    cur.lines.push(line);
  }
  out.push(cur);
  return out
    .filter((s) => s.lines.join("").trim())
    .map((s) => ({ number: s.number, title: s.title, text: s.lines.join("\n").trim() }));
}

/** Image references in a file, resolved to repository-relative paths. */
export function figures(part, text = readPart(part)) {
  const out = [];
  for (const m of text.matchAll(/!\[([^\]]*)\]\(([^)\s]+)\)/g)) {
    const abs = resolve(dirname(part.file), decodeURI(m[2]));
    out.push({ alt: m[1], path: abs.slice(ROOT.length + 1).replace(/\\/g, "/"), exists: existsSync(abs) });
  }
  return out;
}

/** Planned-figure markers: <!-- FIGURE n | path | kind | caption | content --> */
export function figureMarkers(part, text = readPart(part)) {
  const out = [];
  for (const m of text.matchAll(/<!--\s*FIGURE\s+([\s\S]*?)-->/g)) {
    const [number, path, kind, caption, ...rest] = m[1].split("|").map((s) => s.trim());
    const line = text.slice(0, m.index).split("\n").length;
    out.push({ number, path, kind, caption, content: rest.join(" | ").replace(/^Content:\s*/i, ""), line });
  }
  return out;
}
