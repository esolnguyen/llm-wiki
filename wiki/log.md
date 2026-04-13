# Wiki Log

<!-- Append-only chronological log of all wiki operations. -->
<!-- Each entry uses the format: ## [YYYY-MM-DD] operation | Title -->
<!-- Parseable with: grep "^## \[" wiki/log.md | tail -10 -->

## [2026-04-09] init | Wiki initialized

- **Operation**: init
- **Pages created**: index.md, log.md, overview.md
- **Notes**: Initial scaffolding. No sources ingested yet.

## [2026-04-09] ingest | The Pomodoro Technique: A Brief Overview

- **Operation**: ingest
- **Source**: raw/sample_pomodoro_technique.md
- **Pages created**: sources/sample_pomodoro_technique.md, entities/francesco_cirillo.md, concepts/pomodoro_technique.md, concepts/time_boxing.md, concepts/deep_work.md, concepts/cognitive_load.md
- **Pages updated**: index.md, overview.md
- **Notes**: First ingest. Dummy source demonstrating the full workflow. Created 1 entity (Cirillo), 1 full concept page (Pomodoro Technique), and 3 concept stubs (time-boxing, deep work, cognitive load) that need dedicated sources. Several `[single source]` markers flagged for claims not yet cross-validated. Overview updated to describe current state and suggest next sources.

## [2026-04-12] restructure | Concepts moved into topic hierarchy

- **Operation**: update
- **Pages created**: concepts/index.md, concepts/productivity/index.md
- **Pages moved**: concepts/{pomodoro_technique,time_boxing,deep_work,cognitive_load}.md → concepts/productivity/
- **Pages updated**: index.md, overview.md, sources/sample_pomodoro_technique.md, entities/francesco_cirillo.md, CLAUDE.md
- **Notes**: Replaced flat `concepts/` with a topic-folder hierarchy (Option A from planning discussion). Each topic folder has an `index.md`; top-level `concepts/index.md` lists topics. Schema in CLAUDE.md updated with hierarchy rules and link-depth guidance. Motivation: keep retrieval token cost proportional to the topic touched, not the whole wiki.

## [2026-04-13] lint | Redundancy cleanup

- **Operation**: update
- **Pages deleted**: concepts/productivity/cognitive_load.md, concepts/productivity/deep_work.md, concepts/productivity/time_boxing.md, entities/francesco_cirillo.md
- **Pages updated**: concepts/productivity/pomodoro_technique.md, concepts/productivity/index.md, concepts/index.md, sources/sample_pomodoro_technique.md, index.md, overview.md
- **Notes**: Removed three concept stubs and the Cirillo entity page — none met the 3+ sources/pages granularity rule. Their incidental content is now folded into `pomodoro_technique.md` (as a "Related concepts (no dedicated sources yet)" section and inline mentions). Tightened the source page to record only what *this source uniquely contributes*, eliminating duplicated mechanics/benefits/criticisms already canonical on the concept page. Indexes and overview updated to reflect the new shape: 1 source, 1 concept page, 0 entities.
