# Learn and maintain a library

## Intake and extraction

Follow [reference-safety.md](reference-safety.md) for every reference import. Learning is read-only with respect to the presentation, including its embedded objects. Create any composition trial in a separate generated deck.

For a mixed examples folder, read [intake.md](intake.md) first. Accept photos, logos, icons and documents alongside slide decks, organize incoming files, and build source-backed asset associations using the runtime's actual readers. The optional Python helper's supported formats are narrower than this intended workflow.

Distinguish reference-design decks from content sources and rough user input. A deck can serve both roles only when intended. In Claude for PowerPoint, use the native read tools first. Where file execution is available, optionally import source decks with `library.py ingest`; import customer-specific decks with `--scope project --project <stable-name>`. The source snapshot stores original files, slides in presentation order, hidden flags, object text, notes, tables, chart caches, image links, masters, layouts and theme observations. The original remains unchanged.

The extractor records positions local to shape groups. For visual placement resolve group transforms and inherited placeholder styles using the original PPTX and rendering tools. Explicit font counts are observations, not effective-font counts. Text-only extraction misses text baked into images; inspect the rendered reference and read relevant image content. The helper does not parse binary `.ppt` or `.msg`; request/export a supported copy only when needed.

Inspect all candidate reusable slides and representative design families at readable size. Prefer existing renders if they match the source; otherwise use Claude's available slide rendering or inspection tools. Find master defaults, recurring compositions and deliberate exceptions. Do not turn every imported master, draft annotation or font outlier into a brand rule. Count native chart and chartEx parts separately from think-cell metadata. Notes and handout themes are not necessarily unused themes.

## Curate reusable content

Read [data-model.md](data-model.md). Create separate records for people, company overview, services, locations, case studies and contacts. Build the index automatically by saving records under `records/`; search reads these files directly.

- **Person:** exact name or initials, role, skills, industries, languages, experience, achievements and source date. Group fields by the actual person, not by XML text order. Associate a photo from explicit user labeling or supporting source context after inspecting the slide or standalone asset; do not identify people from appearance. Same initials alone do not establish identity. Keep ambiguous associations unresolved as described in intake.md. Team-card, expert-slide and CV copy can be composed from the same record.
- **Company:** identity, short introduction, capabilities, geographic coverage, working approach and dated metrics. Separate evergreen descriptions from numbers and staffing counts. Store short/long variants only when they materially help; do not repeat facts in disconnected copies.
- **Case study:** client descriptor, situation, intervention, result and units. Keep client anonymity from the source; notes that disclose the underlying client are not permission to name it. Limit reuse to an anonymous description when that is the source's visible presentation.
- **Source notes/emails:** distinguish editorial requests, factual evidence, proposed actions and actual decisions. Do not import “@name”, “Headline”, “xxx”, review questions or raw correspondence into reusable marketing copy.

Each fact must carry a quote from the cited object or paragraph. A grounded paraphrase or translation is allowed; validation checks the quote exists, while you check that it supports the claim. `source_grounded` means traceable to the supplied material, not independently verified or approved by the company. Mark draft-origin facts accordingly. Keep an unresolved alias or contradictory claim visible in record issues rather than guessing.

## Derive the design system

Create the workspace’s `03_Design/profile.json` with source IDs, template path, visual references, observations and generation rules. Paths inside that profile are relative to `03_Design`. Save and validate it using workspace.py as described in runtime.md. Keep these separate:

1. **Observed:** source geometry, palette, font hierarchy, master features, recurring layouts, title style, image crops, table/chart patterns and anomalies, with source/slide anchors.
2. **Rules:** selected defaults, semantic colors, supported layout variants, editable-object requirements and density limits. Label normalizations as design decisions, not source facts.
3. **Patterns:** semantic recipes such as company overview, team, CV, agenda, comparison, case study, facts, chart/commentary and roadmap. Each records an inspected example, intended content, capacity and handling of overflow. There is no fixed universal palette or minimum font size; derive those from this brand.

For a supplied native master, keep a local immutable copy and prefer its layouts. For references with conflicting styles, follow the user's chosen reference or the dominant consistent family. Treat uncommon but deliberate slides as variants. Use a named profile per design direction instead of averaging unrelated brands.

Before calling a profile ready, check column widths plus gutters against available width; reserve footnotes before laying out content; distinguish one-line and two-line title spaces; ensure translated text fits. Document a specific overflow response: trim repetition, choose a less dense pattern, or split only when the requested slide count permits. Do not silently shrink all text.

## Updates

Source IDs are content- and scope-based. Identical reimports should not create another source. A changed deck is a new snapshot, linked through `supersedes` only after establishing the relationship. Reconcile affected facts and pictures, preserving user-written corrections. A new statement about current staff does not automatically replace historical case-study staffing. Store a brief source date for freshness; file modification time alone is not a factual effective date.

Run library validation after curating. It validates references, quotes, scope, asset links and basic geometric constraints. Resolve errors, inspect important warnings, then summarize useful coverage and remaining ambiguities. Finish with a real composition trial when the workflow has materially changed.
