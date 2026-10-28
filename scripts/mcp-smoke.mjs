#!/usr/bin/env node
// Start the MCP server over stdio and exercise every read-only tool. Exits non-zero on failure.
//
//   node scripts/mcp-smoke.mjs
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { ROOT } from "../lib/book.mjs";

const client = new Client({ name: "mcp-smoke", version: "1.0.0" });
await client.connect(new StdioClientTransport({ command: process.execPath, args: ["mcp/server.mjs"], cwd: ROOT }));

const fail = (msg) => {
  console.error(`FAIL: ${msg}`);
  process.exitCode = 1;
};
const call = async (name, args) => {
  const r = await client.callTool({ name, arguments: args });
  if (r.isError) fail(`${name}: ${r.content[0].text}`);
  return r.content[0];
};

const tools = (await client.listTools()).tools.map((t) => t.name);
for (const t of ["list_contents", "read_part", "search_book", "list_figures", "get_figure", "build_pdf"]) {
  if (!tools.includes(t)) fail(`tool ${t} not registered`);
}

const toc = (await call("list_contents", { with_sections: false })).text;
if ((toc.match(/^\s+\[\d+\]/gm) ?? []).length !== 40) fail("list_contents does not list 40 chapters");

if (!(await call("read_part", { id: "22", section: "MPPT" })).text.startsWith("## 22.")) fail("read_part section lookup");
if (!(await call("read_part", { id: "P6" })).text.startsWith("# Part VI")) fail("read_part part opener");
if (!/result\(s\)/.test((await call("search_book", { query: "MPPT", max_results: 3 })).text)) fail("search_book");

const figs = (await call("list_figures", {})).text;
if (/MISSING/.test(figs)) fail("list_figures reports missing figures");
const first = /figures\/ch\d+\/\S+\.png/.exec(figs)?.[0];
if ((await call("get_figure", { path: first })).type !== "image") fail("get_figure did not return an image");

const resources = (await client.listResources()).resources;
if (resources.length !== 49) fail(`expected 49 resources, got ${resources.length}`);

await client.close();
console.error(process.exitCode ? "MCP smoke test failed." : `MCP smoke test passed (${tools.length} tools, ${resources.length} resources).`);
