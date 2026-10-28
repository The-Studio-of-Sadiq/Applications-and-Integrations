# Applications and Integrations — MCP server

A [Model Context Protocol](https://modelcontextprotocol.io) server that lets an AI client browse, search, cite and typeset this book. It speaks MCP over stdio.

## Setup

```bash
npm install
```

**Claude Code** — the repository ships a project `.mcp.json`, so opening the repo in Claude Code offers the server automatically. To add it by hand:

```bash
claude mcp add applications-integrations -- node /absolute/path/to/Applications-and-Integrations/mcp/server.mjs
```

**Claude Desktop / other clients** — add to the client's MCP config:

```json
{
  "mcpServers": {
    "applications-integrations": { "command": "node", "args": ["/absolute/path/to/Applications-and-Integrations/mcp/server.mjs"] }
  }
}
```

## Tools

| Tool | What it does |
|---|---|
| `list_contents` | Part openers and chapters with ids, titles, files and section headings |
| `read_part` | Markdown of a chapter (`id: "14"`) or part opener (`id: "P3"`), optionally one section (`section: "14.5"` or a title word) |
| `search_book` | Full-text or regex search with chapter, section and line number for every hit |
| `list_figures` | Figures in a chapter (or the whole book) with captions |
| `get_figure` | Returns a figure as an image, by path from `list_figures` |
| `build_pdf` | Builds the whole book or selected parts to PDF and reports any math/image problems |

## Resources and prompts

- Resource template `book://part/{id}` — the Markdown of each chapter or part opener.
- Prompt `explain_section(id, section)` — walks through a section in the book's own method (engineering problem → model → analysis → status of the principle → measurable consequence).

`build_pdf` needs a local Chrome, Edge or Chromium (or `CHROME_PATH`); see [`scripts/build-pdf.mjs`](../scripts/build-pdf.mjs).
