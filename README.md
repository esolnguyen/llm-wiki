# LLM Wiki: A Second Brain Maintained by an LLM

A personal knowledge base that compiles, rather than re-derives, understanding over time.

You drop sources into `raw/`. The LLM reads them, writes summary pages, updates entity and concept pages, flags contradictions, and keeps the whole wiki cross-referenced. You browse the result in Obsidian. The LLM does the bookkeeping; you do the curating and the asking.

This repo is an instance of that pattern. The wiki is just markdown files under `wiki/`, so you get git history, graph view, and search for free.

## Repository layout

```
raw/          # Immutable source documents (PDFs, articles, notes). LLM reads, never writes.
wiki/         # LLM-generated markdown pages. Sources, entities, concepts, synthesis, index, log.
output/       # Generated artifacts (slide decks, charts, exports). Not part of the wiki proper.
scripts/      # Helper scripts (e.g. extract.py for PDF → markdown).
docs/         # Project documentation (this folder).
```

## Quick start

1. Install dependencies: `python -m venv .venv && .venv/bin/pip install -r requirements.txt`
2. Drop a source into `raw/` (PDF, markdown, html, docx, etc.)
3. Open the project in Claude Code (or your LLM agent of choice) and say "ingest this"
4. Browse the result in Obsidian pointed at the repo root

For non-text sources, the agent will run `scripts/extract.py` first to produce a cached `.md` sibling.

## Documentation

- **[docs/concept.md](docs/concept.md)**: The pattern: why compile instead of re-derive, three-layer architecture (raw / wiki / schema), operations (ingest / query / lint).
- **[docs/schema.md](docs/schema.md)**: Wiki structure, page conventions, frontmatter, citations, contradiction handling, and the concrete workflows this project follows. This is the schema the LLM agent reads to stay disciplined.
- **[docs/brainstorm.md](docs/brainstorm.md)**: Critiques, extensions, anti-patterns, and open questions about the pattern. Useful when evolving the schema.
- **[PLAN.md](PLAN.md)**: Phased roadmap: foundation, growth, mobile, query API, chat interface.

## How to use this with an LLM agent

Point your agent at `docs/schema.md`. That document tells it how the wiki is structured and which workflows to run for ingest, query, status, and lint. The schema is the agent's operating manual; the wiki is the output.

## Credit

The pattern is adapted from the "LLM Wiki" idea file by Geoffrey Litt. See [docs/concept.md](docs/concept.md) for the full description.
