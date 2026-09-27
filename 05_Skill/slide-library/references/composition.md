# From rough input to finished slides

## Interpret the brief

Read the unfinished open deck with Claude for PowerPoint's native tools. When a file and execution environment are available, `library.py brief` can extract a PPTX or text brief. Read the actual text and relevant notes, not only its detected intent. Semantic interpretation belongs to you; keyword routing is a hint. Preserve user facts verbatim in the private brief even when rewriting them for slides.

Typical inputs and behavior:

| Input | Completion |
| --- | --- |
| “Company overview” | Relevant company overview from this library, fitted to requested scope |
| “Agenda” | Derive from the actual deck sections; exclude the agenda itself, do not add topics |
| “Team introduction: A, B, C” | Resolve those people and verified photos, select task-relevant expertise |
| “Team Supplier Development” | Find matching people; present a proposed expert selection unless assignment is confirmed |
| Facts without formatting | Preserve values and units, choose a table, chart, comparison or simple statement layout |
| Pasted email | Separate context, facts, requests, commitments and dates; summarize only what is relevant |
| “Like slide 14, with these numbers” | Use that composition and explicit new facts, not its old customer results |

An email may be just evidence for one slide. It is not automatically a new deck, a reusable company statement or authority to send mail. Keep uncertain dates, proposed prices and conflicting forecasts qualified. Do not insert sender addresses or signatures unless the requested content needs them.

## Retrieve and plan

Select the library and design profile before retrieval. Use `search --project ...` to access one project plus reusable records. Raw source search requires `--raw` and is for the agent's inspection, never permission to use all results. Read the underlying record and source context before using a claim.

Create a private deck plan with one item per requested slide:

- intent and message;
- explicit user content;
- selected record and fact IDs, evidence links and any verified image association;
- chosen pattern and content density;
- proposed wording and chart/table data;
- omissions, contradictions or genuine blockers.

Prioritize topical relevance, evidence strength and compatible dates. Do not repeat the same generic company paragraph on every slide. Keep project information within its scope; one client's financial figures must not appear in an unrelated sales deck. Never invent an unavailable library match. Ask a bundled short question only when an essential choice remains; otherwise omit optional unsupported detail and keep going.

## Author, then verify

Use Claude for PowerPoint's native tools to complete the working deck within the requested scope. When generating a separate file, save a new PPTX. Apply the selected native template and use its layouts where possible. Use native editable text, charts and tables; supplied photographs/logos remain images. Preserve relationships between values, labels and units. Use the chosen profile and explicit user overrides, not formatting accidents in the rough input.

Keep `deck-plan.json` and a working claim-to-source map alongside build files. Useful source citations belong in speaker notes; review diagnostics do not belong in audience-facing copy. Notes travel with a shared deck. When anonymization or confidentiality requires it, use an approved source alias and retain the full filename mapping in the private workspace. Build an agenda from finalized section names. Resolve slide/page references after final ordering. Fill all requested placeholders; remove unused layout prompts.

Write the source map into each changed slide's speaker notes during this build, preserving existing notes. Map company facts, each person's role/expertise, dates and named images to the relevant source filename plus slide/shape, paragraph or asset association. For an agenda, state which final section titles it derives from; for supplied facts or email, identify the supplied brief/message. A library ID alone is insufficient when its source filename is available. A slide with only user-authored material can cite that material without inventing an external source.

Before reporting completion, read back the notes of every changed slide as well as its visible content. If a source map is missing, add it and check it in the same build; do not leave it for an optional follow-up. When note editing is unavailable, retain the map in an accessible separate artifact and disclose the missing in-deck citations. Do not claim complete source documentation unless the maps were actually saved and checked.

Visually inspect every changed slide with the available rendering or slide-inspection tools. Check text fit, figure labels, image identity/crop, footer and title clearance, content completeness and consistency with the selected reference. Check that required text/charts/tables remain native editable objects. Use package validation when a PPTX file and execution tools are available. A plan or successful file export alone is not a completed presentation; disclose unavailable validation rather than pretending to have performed it.

Explain only material uncertainty at handoff. For a team chosen by expertise, make “proposed team” visible where appropriate; do not claim staffing is booked. Do not turn an old company headcount into a current fact. Leave the source library unchanged by default; update it only when the user asks to learn the new information or has already authorized that update.
