#!/usr/bin/env node
// MCP server for "Applications and Integrations" (Book 6 — the Applications & Integrations Core).
//
// Lets an MCP client (Claude Code, Claude Desktop, …) browse, search and cite the book,
// fetch its figures, and build PDFs. Transport: stdio.
//
//   claude mcp add applications-integrations -- node /path/to/Applications-and-Integrations/mcp/server.mjs
import { readFileSync, existsSync } from "node:fs";
import { resolve, extname } from "node:path";
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { ROOT, BOOK_TITLE, listParts, findPart, readPart, sections, figures } from "../lib/book.mjs";

const server = new McpServer({ name: "applications-integrations", version: "1.0.0" });

const text = (s) => ({ content: [{ type: "text", text: s }] });
const fail = (s) => ({ content: [{ type: "text", text: s }], isError: true });
const PART_ID = z.string().describe('Chapter number ("14") or part opener ("P3")');

server.registerTool(
  "list_contents",
  {
    title: "List contents",
    description: `Table of contents of "${BOOK_TITLE}": every part opener and chapter with its id, title, file and section headings.`,
    inputSchema: { with_sections: z.boolean().default(true).describe("Include ## section headings") },
  },
  async ({ with_sections }) => {
    const lines = [];
    for (const p of listParts()) {
      lines.push(`${p.kind === "chapter" ? "  " : ""}[${p.id}] ${p.title}  (${p.relPath})`);
      if (with_sections && p.kind === "chapter") {
        for (const s of sections(readPart(p)).slice(1)) lines.push(`      ${s.number ? s.number + " " : ""}${s.title}`);
      }
    }
    return text(lines.join("\n"));
  },
);

server.registerTool(
  "read_part",
  {
    title: "Read chapter or part opener",
    description:
      "Return the Markdown of a chapter or part opener, or of one section of it. Math is LaTeX ($...$, $$...$$).",
    inputSchema: {
      id: PART_ID,
      section: z
        .string()
        .optional()
        .describe('Optional section number ("14.5") or a word from its title ("MPPT"); omit for the whole file'),
    },
  },
  async ({ id, section }) => {
    const part = findPart(id);
    if (!part) return fail(`No chapter or part "${id}". Use list_contents.`);
    const body = readPart(part);
    if (!section) return text(body);
    const q = section.trim().toLowerCase();
    const hit = sections(body).find((s) => s.number === section.trim() || s.title.toLowerCase().includes(q));
    return hit ? text(hit.text) : fail(`No section "${section}" in ${part.title}.`);
  },
);

server.registerTool(
  "search_book",
  {
    title: "Search the book",
    description:
      "Full-text search across all chapters and part openers. Returns matching lines with their chapter, section and line number.",
    inputSchema: {
      query: z.string().min(1).describe("Text or regular expression to find"),
      regex: z.boolean().default(false).describe("Treat query as a regular expression"),
      parts: z.array(z.string()).optional().describe("Restrict to these chapter/part ids"),
      context: z.number().int().min(0).max(5).default(1).describe("Lines of context around each hit"),
      max_results: z.number().int().min(1).max(200).default(30),
    },
  },
  async ({ query, regex, parts, context, max_results }) => {
    let re;
    try {
      re = new RegExp(regex ? query : query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i");
    } catch (e) {
      return fail(`Bad regular expression: ${e.message}`);
    }
    const scope = parts?.length ? parts.map(findPart).filter(Boolean) : listParts();
    const hits = [];
    for (const p of scope) {
      const lines = readPart(p).split(/\r?\n/);
      let sec = "";
      for (let i = 0; i < lines.length && hits.length < max_results; i++) {
        const h = /^##\s+(.+)$/.exec(lines[i]);
        if (h) sec = h[1];
        if (re.test(lines[i])) {
          const snippet = lines.slice(Math.max(0, i - context), i + context + 1).join("\n");
          hits.push(`── [${p.id}] ${sec || p.title} · ${p.relPath}:${i + 1}\n${snippet}`);
        }
      }
    }
    return text(hits.length ? `${hits.length} result(s)\n\n${hits.join("\n\n")}` : `No matches for "${query}".`);
  },
);

server.registerTool(
  "list_figures",
  {
    title: "List figures",
    description: "List the figures (images) in a chapter, or in the whole book, with captions.",
    inputSchema: { id: PART_ID.optional() },
  },
  async ({ id }) => {
    const scope = id ? [findPart(id)].filter(Boolean) : listParts();
    if (!scope.length) return fail(`No chapter or part "${id}".`);
    const lines = [];
    for (const p of scope) {
      for (const f of figures(p)) lines.push(`[${p.id}] ${f.path}${f.exists ? "" : "  (MISSING)"}\n    ${f.alt}`);
    }
    return text(lines.length ? lines.join("\n") : "No figures.");
  },
);

const MIME = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp" };

server.registerTool(
  "get_figure",
  {
    title: "Get figure",
    description: "Return a figure image by its repository path (as printed by list_figures), e.g. figures/ch14/fig-22-3-string-voltage-window.png.",
    inputSchema: { path: z.string().describe("Repository-relative image path") },
  },
  async ({ path }) => {
    const abs = resolve(ROOT, path);
    const mime = MIME[extname(abs).toLowerCase()];
    if (!abs.startsWith(resolve(ROOT, "figures")) || !mime) return fail("Path must be an image under figures/.");
    if (!existsSync(abs)) return fail(`Not found: ${path}`);
    return { content: [{ type: "image", data: readFileSync(abs).toString("base64"), mimeType: mime }] };
  },
);

server.registerTool(
  "build_pdf",
  {
    title: "Build PDF",
    description:
      "Render the whole book, or selected chapters/part openers, to a PDF (KaTeX math, embedded figures) using a local Chrome/Edge. Returns the output path and any math or image problems found.",
    inputSchema: {
      parts: z.array(z.string()).optional().describe('Ids to include, e.g. ["P3","11","12"]; omit for the whole book'),
      out: z.string().optional().describe("Output .pdf path (default: dist/Applications-and-Integrations.pdf)"),
    },
  },
  async ({ parts, out }) => {
    try {
      // Imported lazily: puppeteer is only needed for this tool.
      const { buildPdf } = await import("../scripts/build-pdf.mjs");
      const r = await buildPdf({ parts, out, log: () => {} });
      const notes = [
        `PDF written: ${r.out}`,
        `Parts: ${r.parts.join(", ")}`,
        r.mathErrors.length ? `Math errors (${r.mathErrors.length}):\n  ${r.mathErrors.join("\n  ")}` : "Math: all expressions rendered.",
        r.missingImages.length ? `Missing images:\n  ${r.missingImages.join("\n  ")}` : "Images: all found.",
      ];
      return text(notes.join("\n"));
    } catch (e) {
      return fail(`PDF build failed: ${e.message}`);
    }
  },
);

server.registerResource(
  "book-part",
  new ResourceTemplate("book://part/{id}", {
    list: async () => ({
      resources: listParts().map((p) => ({ uri: `book://part/${p.id}`, name: p.title, mimeType: "text/markdown" })),
    }),
  }),
  { title: "Book chapter or part opener", description: "Markdown source of one chapter or part opener", mimeType: "text/markdown" },
  async (uri, { id }) => {
    const part = findPart(id);
    if (!part) throw new Error(`No chapter or part "${id}"`);
    return { contents: [{ uri: uri.href, mimeType: "text/markdown", text: readPart(part) }] };
  },
);

server.registerPrompt(
  "explain_section",
  {
    title: "Explain a section",
    description: "Walk through one section of the book: the system, the requirement, the design decision, and how it is verified.",
    argsSchema: { id: PART_ID, section: z.string().describe('Section number, e.g. "14.5"') },
  },
  ({ id, section }) => {
    const part = findPart(id);
    const s = part && sections(readPart(part)).find((x) => x.number === section);
    const body = s ? s.text : `(Section ${section} of ${id} not found; use the read_part tool.)`;
    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text:
              `Explain this section of "${BOOK_TITLE}" following the book's method: start from the system and its requirement, ` +
              `explain the design decision and the budget or calculation behind it, say which results are ` +
              `Fundamental / Derived / Approximate / Empirical, and end with how the design is verified and how it can fail.\n\n${body}`,
          },
        },
      ],
    };
  },
);

await server.connect(new StdioServerTransport());
