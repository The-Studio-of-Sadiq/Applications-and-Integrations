# Security Policy

This repository is mostly a book. The parts that run code are:

- the **MCP server** (`mcp/server.mjs`), which reads the book's Markdown and figure files on the local machine and serves them to MCP clients over stdio; its `get_figure` tool only serves images under `figures/`, and `build_pdf` writes a PDF to a path the client chooses;
- the **PDF build** (`scripts/build-pdf.mjs`), which renders Markdown to HTML and prints it with a local headless Chrome/Edge;
- the **figure scripts** (`figures/scripts/`) and the build/check scripts (`scripts/`);
- the **GitHub Actions workflows** (`.github/workflows/`).

## Supported versions

Only the latest commit on `main` and the latest release are supported.

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Use GitHub's private vulnerability reporting (**Security → Report a vulnerability**) or email **princekhan7748@gmail.com** with:

- what the problem is and which component it affects;
- steps to reproduce, or a proof of concept;
- the impact you expect.

You should get a reply within a week. Once a fix is ready we will credit you, if you wish, in the release notes.

## Not vulnerabilities

The communication chapters describe modulation, coding and link budgets as engineering theory. An error in that theory is welcome as an **Erratum** issue, not a security report.
