# Brainstorm: Critiques, Extensions, and Open Questions

> Companion document to [concept.md](concept.md). Use this when evolving the schema or reasoning about the pattern's limits.

## What's strong about the pattern

The core insight — **compilation vs. re-derivation** — is the right framing. RAG re-derives understanding on every query; the wiki compiles it once and keeps it current. This is the same relationship as interpretation vs. compilation in programming languages, and for the same reason, the compiled version wins when you're going to query the same knowledge repeatedly.

The three-layer separation (sources / wiki / schema) is clean. Each layer has a clear owner and clear invariants: sources are immutable, the wiki is LLM-owned, the schema is co-evolved. This prevents the muddled "who wrote this and can I trust it?" problem that plagues most shared knowledge systems.

The maintenance cost argument is the right one to lead with. Wikis die from neglect, not from lack of ambition. Everyone has started a personal wiki; almost no one has maintained one past the initial burst of enthusiasm. The LLM eliminates the maintenance tax that kills every personal knowledge management system.

## Critique 1: The index is a bottleneck that deserves first-class treatment

The document acknowledges the scaling limit ("works surprisingly well at ~100 sources") but treats the transition to real search as an afterthought. In practice, the index is the single point of failure for the entire pattern. It's a hand-maintained routing table that the LLM must scan in full to decide which pages are relevant to a query. At some point you're doing the same thing as RAG — just retrieval over your own summaries instead of raw chunks.

**Suggestion: make the index hierarchical from the start.** A top-level `index.md` points to category indexes (`index-entities.md`, `index-concepts.md`, `index-sources.md`), which point to pages. The LLM navigates the tree rather than scanning a list. This mirrors how real wikis work (Wikipedia's category system) and scales much better. It also makes it easier for the LLM to decide "I need to look at entity pages" vs. "I need concept pages" before loading everything.

A further step: **let pages declare their own routing metadata in frontmatter.** Tags, categories, related pages, upstream dependencies. The index becomes a generated artifact (like a table of contents) rather than a manually curated one. The LLM can regenerate it from page metadata at any time, which makes it self-healing.

## Critique 2: Staleness and consistency are harder than "just lint periodically"

The document mentions lint as a periodic health check, but the real challenge is **transitive updates.** When you ingest a new source that contradicts a claim on Page A, and Page A is cited by Pages B, C, and D, do those downstream pages need updating too? How deep does the cascade go?

The LLM can touch 15 files in one pass — but does it know *which* 15 files to touch? Right now the answer is "scan the index, hope for the best." That works at small scale but becomes unreliable as the wiki grows.

**Suggestion: dependency tracking as a first-class concept.** Each wiki page could include in its frontmatter:

```yaml
---
depends_on:
  sources: [raw/paper_smith_2024.md, raw/article_jones.md]
  pages: [wiki/concept_attention.md, wiki/entity_transformer.md]
last_verified: 2026-04-01
---
```

When a dependency changes (new source ingested, upstream page updated), downstream pages get flagged for review. This is essentially **`make` for your wiki** — a dependency graph that tells the LLM exactly what needs rebuilding when something changes. The lint operation becomes: find pages whose dependencies have changed since `last_verified` and update them.

This also enables a useful diagnostic: "show me all pages that depend on this source" — which tells you the blast radius of discovering that a source was wrong.

## Critique 3: The schema is the actual product

The document describes the schema as "conventions and workflows" — configuration. But in practice the schema is the most critical and hardest piece. It encodes editorial judgment: what deserves its own page vs. a section on an existing page, how detailed summaries should be, what level of cross-referencing is useful vs. noisy, what contradictions are worth flagging vs. ignoring.

A bad schema produces a bad wiki regardless of how good the sources are. Over-granular schemas create hundreds of stub pages with one paragraph each. Under-specified schemas let the LLM make inconsistent decisions about page structure. Schemas that don't distinguish between "established fact" and "one source's opinion" produce wikis that read with false confidence.

**The schema is the product. The wiki is an output.** Someone using this pattern for competitive analysis needs a radically different schema than someone reading a novel. The document would benefit from 2–3 concrete schema sketches showing how different they are across domains.

The schema also has a bootstrapping problem: you can't write a good schema until you've seen what the wiki looks like, but the wiki's quality depends on the schema. This suggests the schema should be explicitly versioned and evolved. **Start with a minimal schema. Ingest 5 sources. Review what the LLM produced. Revise the schema. Re-ingest if necessary.** The first 5 sources are calibration, not production.

## Critique 4: The contradiction model needs a real framework

The document mentions "noting where new data contradicts old claims" without specifying what that looks like in practice. When Source A says X and Source B says not-X, what does the wiki page actually say? This is an editorial choice with major consequences:

| Approach | Behavior | Good for | Bad for |
|---|---|---|---|
| **Last-write-wins** | Newest source's claim replaces the old one | Fast-moving domains, personal notes | Research, anything where provenance matters |
| **Record both with provenance** | "Source A claims X; Source B disputes this" | Research, competitive analysis | Pages get cluttered, hard to get a quick answer |
| **Confidence scoring** | Each claim has a weight based on source count/quality | Large-scale research, due diligence | Overhead, false precision |
| **Separate "claims" and "consensus" sections** | Page has a current-best-understanding section and a detailed claims log | Deep research | Overkill for casual use |

The right choice depends heavily on the domain. The schema should specify which model to use, and the document should at least name these options so users can make an informed choice.

## Extension 1: Versioning as a first-class feature

The document mentions "the wiki is just a git repo" but doesn't explore what that enables. If the LLM commits after each ingest, you get something powerful: **the ability to see how your understanding evolved over time.**

- `git log --oneline` gives you the intellectual history of your research
- `git diff v1..v5 wiki/synthesis.md` shows how your thesis changed across 4 sources
- `git blame wiki/entity_X.md` tells you which source introduced each claim
- You can branch: "what if I follow this interpretation?" and explore without losing the main line

**Suggestion: each ingest should be a git commit** with a structured message:

```
ingest: "Attention Is All You Need" (Vaswani et al., 2017)

Updated: concept_attention.md, concept_transformer.md, entity_vaswani.md
Created: concept_self_attention.md
Sources: 12 total (+1)
```

This makes `git log` a readable narrative of the wiki's evolution. For research wikis especially, this history is itself a valuable artifact — it shows how your thinking developed, which sources were inflection points, and when specific ideas entered your understanding.

## Extension 2: Multi-agent and collaborative patterns

The document assumes one person, one LLM, one wiki. But the pattern naturally extends:

**Multiple agents, one wiki.** A research team where each person's LLM ingests different sources into a shared wiki. Git merge conflicts become *knowledge conflicts* — genuinely interesting to resolve. "My sources say X, yours say Y, let's look at both." This could work with a shared repo and conventional branching: each person works on a branch, merges go through review (by the human or the LLM).

**Agent specialization.** Instead of one LLM doing everything, split the roles:

- An **ingest agent** optimized for careful reading and extraction
- A **lint agent** optimized for finding inconsistencies and gaps
- A **query agent** optimized for synthesizing answers from wiki pages
- A **schema agent** that periodically reviews the schema and suggests improvements

Different system prompts, possibly different models (a cheaper model for routine ingests, a more capable model for synthesis and lint).

**Wiki-to-wiki references.** Your personal health wiki cross-references your nutrition wiki. A company's product wiki links to the competitive analysis wiki. Federated knowledge bases with typed relationships between them.

## Extension 3: Query-driven structure evolution

The document mentions that good answers can be filed back as wiki pages. But there's a deeper pattern: **queries reveal structural gaps.**

If you keep asking questions that require the LLM to read 8 pages and synthesize them, that's a signal that a synthesis page is missing. The LLM could track this: "You've asked three questions this week that required cross-referencing the same five pages. Should I create a synthesis page covering their intersection?"

Similarly, if queries consistently touch a page but only use one section of it, that section might deserve its own page. And if a page is never touched by any query, it might be an orphan that's not pulling its weight.

This turns the wiki into an **adaptive structure** — it reorganizes itself based on how it's actually used, not just how sources happen to be organized. The schema could include a rule like: "If a set of pages is co-accessed in 3+ queries, suggest a synthesis page."

## Extension 4: Epistemic hygiene as a design principle

The wiki is an opinionated synthesis written by an LLM. If the LLM misunderstands a source, that misunderstanding gets compiled into the wiki and then informs all future synthesis. Compounding advantage becomes compounding error.

**Every claim in the wiki should be traceable to a source.** Not just "this page was informed by these 5 sources" but "this specific sentence comes from Source A, paragraph 3." This is the difference between a wiki you can trust and one you can't.

Mitigations:

- **Source citations on every non-trivial claim.** Not just a references section at the bottom — inline citations like `[[raw/paper.md#section|Smith 2024]]` so you can drill down.
- **Confidence markers.** A lightweight convention: claims supported by multiple sources get no marker. Claims from a single source get a marker like `[single source]`. Claims that are the LLM's own inference (connecting dots between sources) get `[synthesis]`. This lets the reader calibrate trust.
- **"Drill down" links.** Every summary or synthesis should link to the raw source so the reader can verify. The wiki is a map, not the territory — but the territory should always be one click away.
- **Periodic human spot-checks.** Especially for high-dependency pages (pages that many other pages cite). If a hub page has an error, it propagates everywhere.

## Extension 5: The cold start problem

The first 5 sources are the hardest because the wiki has no structure yet. The LLM is creating the skeleton and the content simultaneously, which means early architectural decisions (what categories exist, what granularity to use, what pages to create) get locked in and are expensive to change later.

**Suggestion: explicit bootstrapping phase.** The schema could include a "bootstrap" workflow:

1. Ingest the first 3–5 sources with a lightweight schema (just summaries, no cross-referencing yet)
2. Review the summaries with the human
3. Together, identify the emerging categories, key entities, and main themes
4. Write the full schema based on what you've seen
5. Re-process the initial sources with the full schema

This avoids premature structure. You don't decide "this wiki needs entity pages, concept pages, and comparison pages" before you've seen what the sources actually contain. The structure emerges from the content.

## Anti-patterns to name

**The stub wiki.** The schema is too granular — every proper noun gets its own page, resulting in hundreds of pages with one paragraph each. The wiki has breadth but no depth. Fix: set a minimum page size in the schema; if something doesn't warrant a full page, it's a section on a parent page.

**The monolith wiki.** The opposite — everything goes on a few giant pages. Cross-referencing is impossible because there's nothing to cross-reference to. Fix: set a maximum page size in the schema; if a page grows past it, split it.

**The echo chamber wiki.** The LLM summarizes but doesn't synthesize. Each source gets a faithful summary, but there's no page that says "here's what all 20 sources collectively tell us." The wiki is a filing cabinet, not a knowledge base. Fix: the schema should mandate synthesis pages that are updated on every ingest.

**The false confidence wiki.** Single-source claims are stated as facts. The LLM's own inferences are presented with the same authority as well-established findings. The reader can't tell what's solid and what's speculative. Fix: provenance and confidence markers (see epistemic hygiene above).

**The stale wiki.** Early pages are never revisited. Source 1's summary still reflects the wiki's understanding from before sources 2–30 were ingested. Fix: dependency tracking and periodic lint, with explicit attention to oldest pages.

## Open questions

1. **What's the right page granularity?** Too few pages and you lose the ability to cross-reference. Too many and the wiki becomes a maze. Is there a heuristic? ("One page per concept that gets referenced from 3+ other places"?)

2. **How should the wiki handle uncertainty and speculation?** Research often involves tentative hypotheses that aren't yet supported by sources. Should these live in the wiki? In a separate "hypotheses" section? Outside the wiki entirely?

3. **What's the right relationship between the wiki and chat history?** Right now, valuable insights from the conversation are manually filed into the wiki. Could this be automatic? Should the LLM propose "this exchange should become a wiki page" when it detects something worth keeping?

4. **How do you handle source quality?** A peer-reviewed paper and a blog post are both "sources," but they shouldn't carry equal weight. Should the schema include source quality tiers? Should claims from lower-quality sources be marked?

5. **What happens when you change your mind about the schema?** If you realize after 50 sources that your page categories are wrong, do you re-process everything? Can you migrate incrementally? How much of the wiki survives a schema change?

6. **Is there a natural size limit?** At what point does the wiki become too large for this pattern to work — even with search tools? Is there a "wiki of wikis" pattern for truly large knowledge bases?

7. **Can the wiki be shared as a standalone artifact?** If you build a comprehensive wiki on a topic, can someone else read it without knowing the pattern? Or is it too tied to the LLM's conventions and the schema's assumptions?

8. **How does this interact with existing tools?** Obsidian is the assumed viewer, but what about Notion, Logseq, Dendron? What about non-markdown formats? The pattern is format-agnostic in theory — is it in practice?

9. **What's the minimum viable schema?** If someone wants to try this pattern with zero setup, what's the simplest schema that produces a useful wiki? Three rules? Five? What are the absolute essentials?

10. **Could the wiki generate its own "curriculum"?** Given the state of the wiki, what should you read next? What questions haven't been asked yet? What areas are thin and need more sources? The wiki as a research advisor, not just a research artifact.
