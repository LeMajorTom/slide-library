# Executable workspace workflow

Use Python 3.9 or later. Core folder management, sorting, image indexing, HTML review, DOCX/PPTX/text extraction and profile export use the standard library. PDF text extraction uses pypdf when available; otherwise use the host's reader and capture-text. These workspace helpers are local only, with no automatic dependency installer or background watcher. The separate updates.py helper can read public GitHub release metadata when explicitly invoked with --online; see updates.md.

Resolve script paths relative to this skill. Commands below are internal operations performed by Claude; the user types setup, update or build.

## Choose the actual folder

Use the host's folder tools to select the intended desktop location and obtain required access once. Create My Slide System inside it. In Cowork use the real mapped folder: a container's home/Desktop is not the user's desktop. Plugin installation alone does not create folders.

Use native PowerPoint tools for the open deck. If PowerPoint lacks local file/execution tools, manage the folder in Desktop/Cowork and export a profile skill below. Do not invent a local connector.

## Setup and import

Read [reference-safety.md](reference-safety.md). Import preserves the source file bytes and embedded objects. Inspect extract.json's reference_import inventory when present; embedded payloads are not parsed or executed. Do not preprocess reference decks by stripping objects or resaving them. Native-host approval requirements still apply.

    python scripts/workspace.py setup --root "<accessible folder>/My Slide System" --name "My Company"
    python scripts/workspace.py scan --root "<setup folder>"

Setup creates 00_Throw_In, 01_Examples, 02_Library, 03_Design, 04_Presentations, setup.json and START_HERE.md. If the inbox is empty, report a created draft workspace and tell the user where to add files. It has no learned design yet.

Scan reports candidate IDs, fingerprints, paths, format categories and changed/unchanged state. Inspect new slides, images and documents with available readers. Photos is a format fallback, not a semantic judgment. Claude determines logos, icons, portraits and source reuse scope.

Create an import plan keyed by candidate_id:

    {"files": {"<candidate_id>": {
      "category": "Logos", "scope": "reusable", "role": "design",
      "description": "Company logo supplied with the brand guide",
      "tags": ["logo", "dark-background"]
    }}}

Categories are Presentations, Photos, Logos, Icons, Documents, Emails, Needs_Review. Roles are content, design, both. Scope is reusable or project; project scope needs a project name. Default imports are project-scoped to an unassigned context. Mark reusable only after inspecting the material's intended use.

    python scripts/workspace.py import --root "<folder>" --plan "<plan.json>"

Without a plan this safely organizes and extracts with conservative defaults. Passing a plan for an unchanged file explicitly revises its scope/category. A scope change revokes the old scope snapshot for search and evidence reuse while preserving its bytes. Reconcile records that cited it before finalizing or exporting. For mixed client decks, mark individually inspected reusable slides using source.reusable_slides from data-model.md; do not promote the whole deck.

Loose inbox files move into 01_Examples categories. Nested user groups are indexed in place to preserve relative links. Re-running import resumes prepared moves and skips unchanged files. Duplicate occurrences are retained, and destination collisions never overwrite existing files.

Inspect errors, skipped files, missing sources and extraction_status. needs_reader and needs_visual_review mean the file is organized and snapshotted, not understood. Continue independent work while using host readers to resolve unsupported formats.

## Curate source-grounded content

Follow learning.md and data-model.md. Prepare a JSON record or list of records with real source/slide/shape or source/paragraph evidence, then save through:

    python scripts/workspace.py save-records --root "<folder>" --file "<curated-records.json>"

The helper validates quotes, links, scope and identifiers before accepting the batch. It restores prior records if validation fails and keeps previous versions of replaced records. Existing errors in unrelated records remain visible in the returned full-library validation without blocking an otherwise valid batch or design save; finalize and export still require a valid library. Claude still verifies that the quoted evidence supports the interpretation. Use library.py search to retrieve records. Standalone images belong in assets.json rather than fabricated slide-image references.

If a host reader supplies text from an unsupported source, verify it against the file and save a capture:

    {"method": "Host PDF reader; checked against source pages",
     "paragraphs": [{"number": 1, "text": "Actual source text"}]}

    python scripts/workspace.py capture-text --root "<folder>" --source-id "<id>" --file "<capture.json>"

Paragraph numbers become citation anchors. Include page references in the text/method when relevant. The original and previous extraction remain preserved. A recapture that breaks an existing citation is rejected and the prior extract restored; preserve cited paragraph numbers/text or reconcile affected records first. The script checks structure and source integrity; Claude checks transcription accuracy.

## Review and assign images

    python scripts/workspace.py review --root "<folder>"

This creates 02_Library/Image_Review.html and image-review.json. The HTML embeds PNG/JPEG/GIF/WebP images as scaled previews. Other formats require the host's image reader. Show the review with available file tools. Keep its saved number-to-asset mapping until applying the user's answer.

Write a mapping keyed by asset ID:

    {"<asset_id>": {
      "status": "user_confirmed", "label": "Alex Morgan",
      "entity_id": "person-alex-morgan",
      "evidence": "User explicitly mapped review image 2 to Alex Morgan",
      "use": "portrait"
    }}

    python scripts/workspace.py label --root "<folder>" --file "<associations.json>"

Use user_confirmed only for actual user input, source_labeled for unambiguous captions, unresolved/disputed otherwise. Do not identify faces. Source_labeled is not independently verified. Labels retain history. Renamed files retain mappings; changed image bytes become a new unresolved asset. An identity confirmation does not change reuse scope.

Read 02_Library/assets.json during build for descriptions, tags, entity links, intended uses and scope. Ignore retired assets and unresolved/disputed named associations. A photo label does not establish someone's role or credentials.

## Save and validate design

Inspect reference slides and derive the profile using learning.md and data-model.md. The canonical profile is 03_Design/profile.json; template and export_files paths are relative to 03_Design. Place curated editable templates there. Do not use an unmodified client deck as a general template.

Set status to draft while calibrating. Set status to ready and add a truthful visual_review description after inspecting representative output. Then run:

    python scripts/workspace.py save-design --root "<folder>" --file "<profile.json>"
    python scripts/workspace.py validate --root "<folder>"
    python scripts/workspace.py finalize --root "<folder>"

save-design checks basic geometry and evidence integrity, retains the previous version and rejects invalid updates. finalize requires a reviewed design and passing checks. It does not itself inspect slide appearance. A design-only setup is allowed; disclose its empty content library.

## Build and portable handoff

When the folder is reachable, retrieve its records, assets and design directly. Read rough slides or the chat outline and apply composition.md with native editable PowerPoint objects. Claude performs semantic composition and visual review; no script claims to generate the finished deck alone.

If PowerPoint cannot access the folder:

    python scripts/workspace.py export --root "<folder>" --out "<output folder>/my-company-profile.zip"

Export requires a reviewed, valid design. It creates a separate profile skill containing eligible records, evidence excerpts, a sources.json index of cited filenames and fingerprints, clearly associated reusable assets and explicitly declared curated design files. This preserves readable citations without bundling full source text. It excludes raw source archives and project material by default. Add --project "<name>" only for an explicitly requested project export.

Enable the profile ZIP through Customize > Skills > Upload a skill. In PowerPoint select Slide Library and the named profile, then use build. The profile also works independently. It is a snapshot: export and replace it after workspace updates. Do not promise automatic synchronization.

## Manage setups

    python scripts/workspace.py list --root "<user-selected parent folder>"
    python scripts/workspace.py status --root "<setup folder>"
    python scripts/workspace.py archive --root "<setup folder>" --name "My Company"
    python scripts/workspace.py restore --root "<setup folder>" --name "My Company"

list checks the selected folder and immediate children, not the whole computer. use selects the setup in the conversation. delete-setup routes to archive with the exact explicit name. Report archived, with originals and outputs preserved; do not claim permanent deletion.

For optional email context read outlook.md. The plugin has no mail credentials or bundled mail server.
