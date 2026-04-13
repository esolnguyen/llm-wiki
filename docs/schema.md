# Wiki Schema & Agent Operating Manual

This is the schema the LLM agent reads to stay disciplined when maintaining this wiki. Point your agent at this file (or copy it into `CLAUDE.md` / `AGENTS.md` / equivalent) so it follows the same conventions across sessions.

## Domain

**Domain**: General knowledge base (replace this with your specific domain)

## Architecture

```
raw/          # Immutable source documents. The LLM reads but NEVER modifies these.
wiki/         # LLM-generated and LLM-maintained markdown pages. The LLM owns this entirely.
output/       # Generated artifacts (slides, charts, exports). Not part of the wiki proper.
```

### Wiki structure

```
wiki/
├── index.md          # Hierarchical content catalog — the LLM's primary navigation tool
├── log.md            # Chronological operations log
├── overview.md       # High-level overview of the knowledge base (evolves with content)
├── sources/          # One summary page per ingested source (flat)
├── entities/         # Pages for people, organizations, places, products, characters, etc. (flat)
├── concepts/         # Concept pages, organized into topic sub-folders (hierarchical)
│   ├── index.md          # Top-level taxonomy index of all topics
│   ├── <topic>/          # e.g. productivity/, machine_learning/, history/
│   │   ├── index.md          # Topic index — lists child concepts and any sub-topics
│   │   ├── <concept>.md
│   │   └── <subtopic>/       # Optional deeper level when a topic gets crowded
│   │       ├── index.md
│   │       └── <concept>.md
└── synthesis/        # Cross-cutting analysis, comparisons, evolving theses
```

**Concept hierarchy rules**:

- A concept page lives in **one** primary topic folder. Cross-topic relationships are expressed via wikilinks, not duplication.
- Every topic folder has its own `index.md` listing child concepts (and any sub-topics) with one-line summaries and source counts.
- A new top-level topic is added when 2–3 concepts cluster outside any existing branch.
- A sublevel (e.g. `productivity/time-management/`) is added when a topic accumulates ~8+ concepts that cluster naturally.
- Token-cost benefit: when answering a query, read `concepts/index.md` first, then drill into only the relevant topic's `index.md` — never load the whole tree.
- When wikilinking from a nested concept to `sources/` or `entities/`, mind the depth: from `concepts/<topic>/page.md` use `../../sources/...`; from `concepts/<topic>/<subtopic>/page.md` use `../../../sources/...`.

`sources/`, `entities/`, and `synthesis/` stay flat — sources are indexed by date, entities cross topics frequently, and synthesis is cross-cutting by definition.

New subdirectories may be added under `wiki/` if the domain demands it. Document any new categories in this schema and in the index.

## Page conventions

### Frontmatter

Every wiki page MUST have YAML frontmatter:

```yaml
---
title: Page Title
type: source | entity | concept | synthesis
tags: [tag1, tag2]
sources: [raw/filename.md, raw/other.pdf]  # Which raw sources inform this page
depends_on: [wiki/concepts/some_concept.md] # Which wiki pages this page draws from
created: 2026-04-09
updated: 2026-04-09
confidence: high | medium | low | mixed      # Overall confidence in this page's claims
---
```

### Links and citations

- Use Obsidian wikilinks: `[[concepts/attention|Attention]]` for cross-references between wiki pages
- For inline source citations: `[[sources/source_name|Author 2024]]` or `[claim text]([[sources/source_name]])`
- Every non-trivial claim should have an inline citation to a source page
- The source page links back to the raw file, creating a full traceability chain: claim → source page → raw file

### Confidence markers

Use inline markers for claims that need qualification:

- No marker = well-supported by multiple sources or uncontested
- `[single source]` = based on one source only
- `[synthesis]` = LLM's own inference connecting dots between sources, not directly stated in any source
- `[disputed]` = sources disagree on this point (see details on the page)

### Contradiction handling

When sources disagree, record both positions with provenance:

```markdown
## Disputed: [topic]

**Position A**: [claim] — per [[sources/source_a|Author A 2024]]
**Position B**: [claim] — per [[sources/source_b|Author B 2023]]

**Assessment**: [LLM's analysis of the disagreement, if possible]
```

Do NOT silently overwrite earlier claims. Contradictions are valuable information.

### Granularity rules

- A concept or entity gets its own page when it is referenced by **3+ sources** or **3+ other wiki pages**
- Below that threshold, it should be a section on a parent page (a broader concept page, or a source summary)
- If a page grows beyond ~500 lines, consider splitting it into sub-pages
- If a page is under ~30 lines and has no inbound links, consider merging it into a parent page

## Operations

### Ingest

When the user adds a new source to `raw/` and asks to ingest it (or says "ingest", "process", "add this"):

0. **Extract to markdown first (if needed)**. If the source is a PDF, docx, pptx, xlsx, html, epub, image, or other non-text format, run the extraction script before reading:
   ```bash
   .venv/bin/python scripts/extract.py raw/<filename>
   ```
   This produces `raw/<filename>.md` next to the original — e.g. `raw/paper.pdf` → `raw/paper.pdf.md` (the full original filename is kept, with `.md` appended, to prevent collisions). Uses `pymupdf4llm` for PDFs and `markitdown` for other formats. The script is idempotent — it skips extraction if the target `.md` already exists and is newer than the source. If the source is already `.md` or `.txt`, skip this step entirely.

   To extract everything pending in `raw/` at once: `.venv/bin/python scripts/extract.py raw/`

1. **Read the extracted markdown** (e.g. `raw/paper.pdf.md`) in full. For sources with images, read the text first, then view referenced images for additional context. The original binary file (`raw/paper.pdf`) remains the canonical source of truth; the extracted `.md` is a cached intermediate artifact for the LLM's benefit.
2. **Create a source summary page** at `wiki/sources/<slug>.md` with:
   - Frontmatter (title, type: source, tags, sources pointing to the raw file, created/updated dates)
   - A one-paragraph summary
   - Key takeaways as bullet points
   - Notable claims, data points, or arguments
   - Questions or gaps the source raises
   - Links to related entity/concept pages (create or update as needed)
3. **Update or create entity pages** (`wiki/entities/`) for any people, organizations, places, products, or other named entities mentioned significantly. Add the new source's information, update cross-references.
4. **Update or create concept pages** (`wiki/concepts/<topic>/`) for any ideas, methods, theories, or topics discussed substantively. Place each new concept under its primary topic folder, creating the folder + its `index.md` if the topic is new. Update the topic's `index.md` and `wiki/concepts/index.md` when adding pages. Note if the source confirms or contradicts existing content.
5. **Update synthesis pages** (`wiki/synthesis/`) if the new source is relevant to any existing cross-cutting analysis.
6. **Update `wiki/overview.md`** if the new source changes the high-level picture.
7. **Update `wiki/index.md`** — add entries for any new pages, update summaries for modified pages.
8. **Append to `wiki/log.md`** with a structured entry (see log format below).
9. **Report a summary** to the user: what pages were created/updated, any contradictions found, any gaps or follow-up questions suggested.

**Automation level**: Run all steps without waiting for approval between steps. The user will review the results in Obsidian.

**Batch ingest**: If the user asks to ingest multiple sources at once, process them one at a time in sequence, running the full workflow for each. This keeps the wiki consistent at each step.

### Query

When the user asks a question about the wiki's content:

1. **Read `wiki/index.md`** to identify relevant pages
2. **Read the relevant pages** (source summaries, entity pages, concept pages, synthesis pages)
3. **Synthesize an answer** with inline citations to wiki pages and ultimately to sources
4. **Suggest filing** if the answer contains substantial new analysis: "This analysis could be filed as a synthesis page. Want me to save it to `wiki/synthesis/<slug>.md`?"

Answers can take different forms depending on the question:

- A direct markdown response in chat
- A new wiki page (if filed)
- A comparison table
- A Marp slide deck in `output/`
- A chart or visualization in `output/`

### Status

When the user asks "what's been ingested?", "status", "what's new?", or "what hasn't been processed?":

1. **List all files in `raw/`** (excluding `assets/` and `.gitkeep`)
2. **List all source pages in `wiki/sources/`**
3. **Compare**: a raw file is "ingested" if a corresponding source page exists in `wiki/sources/`
4. **Report** in this format:

```
## Ingest Status

### Pending (not yet ingested)
- raw/new_article.pdf
- raw/notes_from_meeting.md

### Ingested
- raw/paper_smith_2024.pdf → [[sources/paper_smith_2024|Smith 2024]]
- raw/blog_post.md → [[sources/blog_post|Blog Post on X]]

### Summary
3 sources total | 1 ingested | 2 pending
```

The matching convention: `raw/foo.pdf` maps to `wiki/sources/foo.md` (same filename stem, `.md` extension). The source page's frontmatter `sources:` field is the canonical link back to the raw file.

**Extraction artifacts**: a non-text raw file may also have an extracted sibling (e.g. `raw/paper.pdf` → `raw/paper.pdf.md`). The extracted `.md` is an intermediate artifact, NOT a wiki source page. When listing raw files for status, treat `raw/paper.pdf` and `raw/paper.pdf.md` as the same logical source — the PDF is canonical, the `.pdf.md` is its cached extraction. Do not double-count them. The easy rule: a file in `raw/` whose name ends in one of `.pdf.md`, `.docx.md`, `.html.md`, etc. is an extraction artifact and should be ignored when counting pending sources.

### Lint

When the user asks to lint, health-check, or review the wiki:

Scan the wiki for:

- **Contradictions**: claims on different pages that disagree without being flagged as disputed
- **Stale pages**: pages whose source dependencies have been superseded by newer sources
- **Orphan pages**: pages with no inbound links from other wiki pages
- **Missing pages**: concepts or entities mentioned on 3+ pages but lacking their own page
- **Missing cross-references**: pages that discuss related topics but don't link to each other
- **Thin pages**: pages with very little content that could be merged
- **Knowledge gaps**: areas where the wiki's coverage is thin and additional sources would help

Report findings as a checklist. Offer to fix each issue automatically. Suggest new sources to investigate.

## Index format

`wiki/index.md` is hierarchical:

```markdown
# Wiki Index

> Last updated: 2026-04-09 | Sources: 0 | Pages: 0

## Overview
- [[overview|Overview]] — High-level summary of the knowledge base

## Sources
<!-- One entry per ingested source, sorted by date -->

## Entities
<!-- One entry per entity page -->

## Concepts
<!-- One entry per concept page -->

## Synthesis
<!-- One entry per synthesis/analysis page -->
```

Each entry format: `- [[path/page_name|Title]] — one-line summary (N sources)`

## Log format

`wiki/log.md` is append-only. Each entry:

```markdown
## [YYYY-MM-DD] operation | Title

- **Operation**: ingest | query | lint | update
- **Source**: (if ingest) raw file path
- **Pages created**: list
- **Pages updated**: list
- **Notes**: brief summary of what changed
```

The consistent `## [date] operation | title` prefix makes the log parseable:
`grep "^## \[" wiki/log.md | tail -10`

## Important rules

1. **NEVER modify files in `raw/`**. Sources are immutable.
2. **ALWAYS update the index and log** after any wiki modification.
3. **ALWAYS include frontmatter** on every wiki page.
4. **ALWAYS cite sources** for non-trivial claims.
5. **NEVER silently overwrite** contradicting information — flag it.
6. **Prefer updating existing pages** over creating new ones, unless granularity rules say otherwise.
7. **Use Obsidian wikilinks** (`[[page]]`) for all internal links — this enables graph view.
8. **Keep the overview current** — it should always reflect the latest state of the wiki.
