# Mixed reference intake and automatic sorting

Read this for folder-based `setup` and `update`. The user drops mixed reference material directly into `00_Throw_In`. Recognize, organize and learn from it in the same operation, moving originals into the sorted `01_Examples` archive. The inbox and archive belong to the same user-selected setup folder. Do not require the user to prepare categories or metadata files.

The executable workflow is documented in [runtime.md](runtime.md). workspace.py implements sorting, source snapshots, asset indexing, numbered image review and saved associations. library.py extracts PPTX, DOCX, text and saved EML; PDF text extraction uses an available pypdf reader. Claude supplies semantic image interpretation and content/design curation using the host’s readers. Never claim an unsupported file was understood merely because it was sorted.

## Intake types

| Material | Intended use |
| --- | --- |
| Presentations and templates | Native slide patterns, design rules and source-grounded content |
| Photos | Portraits, locations, products, facilities and other useful slide imagery |
| Logos and icons | Brand assets and reusable graphic elements |
| Documents and PDFs | Profiles, company descriptions, project evidence and brand guidelines |
| Saved emails and text | Dated evidence, briefs and contextual facts |

Inspect formats using available readers. A file extension identifies a candidate type, not its semantic role. Visually inspect images before classifying a logo, icon, portrait or screenshot. Preserve a vector original when available. If a format needs conversion, retain the original and create a separate readable derivative only when supported. Keep unsupported or unreadable material visible as pending; do not report it as learned.

## Inbox and sorted source archive

Create categories as needed, using these English defaults:

```text
My Slide System/
  00_Throw_In/                 Drop mixed new material here
  01_Examples/                 Automatically organized source originals
    Presentations/
    Photos/
    Logos/
    Icons/
    Documents/
    Emails/
    Needs_Review/
```

The user only needs to know `00_Throw_In`; category folders are maintained automatically. Index already sorted material in `01_Examples` too, without creating another copy on every run. Existing user-defined project folders provide context. The runtime indexes nested groups in place to preserve companion files and relative links. Record its processed state so leaving it in the inbox does not cause repeated imports. Report only exceptions that affect use.

Choose the main folder from the file's role and allow multiple tags in the index. A brochure containing photos is still a document; extracted images become derived assets, not a reason to move the brochure into Photos. A portrait with an unknown identity belongs in Photos with an unresolved association. Use Needs_Review for unclear classification or unreadable material.

Sorting means moving source files from `00_Throw_In` into suitable `01_Examples` categories within the selected setup, while preserving their bytes and original filenames where possible. Clear inbox entries only through verified moves, not by deleting source material. This does not authorize modifying source contents or moving unrelated files elsewhere on the computer. Keep source folders separate from generated library, design and presentation outputs.

## Import and move behavior

1. Inventory `00_Throw_In` and check the indexed `01_Examples` archive for changed material. Compare file fingerprints and recorded locations with the import index. Retain original relative paths and any useful project context. Do not traverse links outside the selected setup folder.
2. Inspect new or changed material, determine its category and keep source evidence for any extracted claims. Use stable source IDs, not the current filename alone, for library references.
3. Before moving a file, record its old path, proposed path and fingerprint in a recoverable import log. Retain an immutable source snapshot when extraction requires one. Never replace an existing destination; use a stable disambiguating suffix when names collide.
4. Move only between the authorized inbox and source-archive locations within the selected setup. Check the destination bytes and update source locations and dependent references. Mark each completed move so an interrupted run can resume or undo its own moves without touching unrelated files.
5. Save the library and design updates, verify readable records and assets, and report the useful result and unresolved items. Preserve the previous usable setup if an update is incomplete.

Repeated runs must not keep moving or duplicating unchanged files. A manual rename or move can be reconciled by fingerprint. Recognize exact duplicate bytes without silently deleting either user file. Retain distinct source occurrences and project scopes even when their content is identical. Visually similar images or modified presentations may be useful variants, not duplicates to merge automatically.

## Photos and other standalone assets

For each usable asset, keep a stable ID, source reference, relative location, category, descriptive tags, available dimensions and format, and suitable uses. Store the original separately from optional thumbnails or cropped derivatives. A source-backed asset index belongs in `02_Library`; design profiles may reference its logos and icons without treating them as company facts.

Describe observable content such as “factory exterior” or “portrait on a neutral background.” Do not infer a person's identity, employer, role or credentials from appearance. User-provided captions, explicit filename labels and source context can supply a claimed association; record that evidence and leave it unconfirmed when ambiguous. Do not mark an association verified merely because a filename resembles a person's name. Ask only when a required slide depends on resolving that identity.

### Match images using evidence

Distinguish identifying the visual category from assigning a named person, company, place or product. An unlabeled image may be categorized as a portrait or factory photo without having a named entity attached.

Use these sources of association:

- **Explicit user mapping:** a chat statement such as “Photo 3 is Alex Morgan” or an optional plain-text note naming the file and its subject. Save the association as `user_confirmed` with the user's statement as evidence.
- **Explicit source label:** an unambiguous caption in a CV, presentation or document that links that specific image to a name. Save it as `source_labeled`, not independently verified. Multiple people and names on a slide require a clear image-to-caption relationship; proximity or array order alone is insufficient.
- **Previously mapped file:** exact file identity can reuse an existing association within its valid scope, retaining the original evidence and status. This is file provenance, not facial recognition. Do not establish identity by comparing faces across different photos.
- **Filename or folder context:** `Alex_Morgan_portrait.jpg`, `Berlin_office.jpg`, or a folder containing a CV and several photos supplies a proposed association. An explicit filename is stronger than simply arriving with a CV, but neither should silently override contrary evidence. Keep ambiguous mappings `unresolved`; give the user a compact way to confirm them.

Do not treat files arriving in the same batch as proof of identity. Never use visual resemblance, face recognition, upload order or a fabricated confidence percentage to assign a person. When evidence conflicts, mark the association `disputed` and avoid using that photo for a named profile until resolved. Current explicit user corrections take precedence while preserving the source history.

For unresolved associations, offer one numbered contact sheet or thumbnail list using available preview tools. Include stable short labels, filenames and any text-based proposed association. Let the user answer in one line, for example: “1 = Alex Morgan; 2 = Berlin office; 3 = decorative image.” Offer this once as an optional cleanup step after import; do not block unrelated work or ask separately about every file. If thumbnails cannot be rendered, provide a filename list instead and disclose that limitation.

Persist each association with its asset ID, entity ID if known, status (`user_confirmed`, `source_labeled`, `unresolved` or `disputed`) and evidence. Record its intended use separately, such as named team portrait, location photo, company logo or decorative image. Link to the shared asset record from content and design rather than making disconnected copies. Reuse confirmed mappings in later sessions when the stored setup is accessible; do not repeatedly ask for unchanged mappings.

For a named portrait in a build, use a conflict-free `user_confirmed` or clearly `source_labeled` association. An unresolved image may remain available as a generic visual only when it does not imply a person's identity, employer, location, ownership or endorsement. A decorative factory photo must not be presented as the user's own facility without evidence.

Keep different crops, resolutions and logo variants distinguishable. Do not invent image rights, location names or dates. Extracted slide screenshots are visual references, not editable templates. Link facts learned from documents to source passages and assets learned from images to the original file.

library.py validates images embedded in PPTX shapes. workspace.py separately indexes and validates standalone assets in 02_Library/assets.json; do not fabricate slide or shape references for them.

## Trigger and feedback

Sorting and learning run together when the user invokes `setup` or `update`. Dropping files into a folder alone does not start processing. An always-on folder watcher would require a separate installed component and is outside the current skill draft.

Keep the completion message short and in English, using actual counts, for example: “Imported 2 presentations, 8 photos and 1 logo. Files are organized. Three portraits still need names.” Distinguish organized files, learned content and pending material; moving a file is not the same as understanding it.
