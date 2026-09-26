# Library format, version 1

The helpers use UTF-8 JSON. Content is stored in `02_Library`, separate from the reusable skill; design lives in `03_Design`. The list below describes paths inside the content library. Legacy standalone library.py workflows may use an internal design/ directory, while workspace.py uses the external 03_Design profile.

```
library.json                    name, schema_version, defaults
sources/<source-id>/source.*     retained immutable input
sources/<source-id>/extract.json source metadata, slides or paragraphs
sources/<source-id>/text.md      readable untrusted source evidence
sources/<source-id>/media/       original embedded images (not executables)
records/<record-id>.json         curated person, company, service, case_study, location or contact
assets.json                     standalone assets and saved image associations
```

## Record

```json
{
  "id": "person-cb",
  "kind": "person",
  "label": "C.B.",
  "aliases": [],
  "tags": ["manufacturing", "operational improvement"],
  "scope": "reusable",
  "project": null,
  "status": "source_grounded",
  "source_date": "2026-09-26",
  "facts": [{
    "id": "role", "field": "role", "text": "Senior Consultant",
    "temporal": "as_of_source",
    "evidence": [{"source_id": "source-id", "slide": 46, "shape_id": "3", "quote": "Senior Consultant"}]
  }],
  "assets": [{"role": "portrait", "source_id": "source-id", "slide": 46, "shape_id": "8", "media": "media/image.png", "identity_verified": true}],
  "issues": ["Only initials supplied; full identity is unresolved."]
}
```

Use a stable lowercase ID. Valid status: `source_grounded`, `reviewed`, `needs_review`, `retired`. `reviewed` requires actual user or organizational review, not merely running validation. Facts may have multiple evidence objects. For text/email use `paragraph` instead of `slide`/`shape_id`. Quote is an exact source excerpt modulo whitespace. `field` is semantic (role, expertise, industry, result, company_intro, location, etc.); it is not a mandated universal profile schema.

`temporal` is `evergreen`, `historical`, or `as_of_source`. Source-grounded draft facts can be used with their scope/date but are not official current company statements. Do not create inferred facts such as availability from a historical CV. `scope` is `reusable` or `project`; the latter requires a project name. Reusable records must not cite project-only evidence. For a mixed reference deck, `source.reusable_slides` may list individually inspected slides that contain reusable company material, profiles or anonymous cases within the user's library-building request. Keep the overall source project-scoped. This exception applies only to visible shape evidence on those slides, not private speaker notes or the whole deck. Do not relabel client financials as reusable.

Asset media paths are relative to their source directory. Select photos by the inspected slide/shape. Preserve initials and record unresolved identities. Cross-references should use record IDs rather than duplicate profiles.

## Design profile

`03_Design/profile.json` contains `source_ids`, `template`, `observations` and `patterns`. `template` and optional `export_files` are relative paths inside `03_Design`. Use `status: draft` during curation; after visual inspection set `status: ready` and record a truthful `visual_review` description. Put usable selected values under `rules`:

```json
{
  "schema_version": 1,
  "name": "Brand Light",
  "source_ids": ["source-id"],
  "template": "template.pptx",
  "observations": {"notes": "Measured defaults, with specific source references."},
  "rules": {
    "slide_cm": {"width": 33.866667, "height": 19.05},
    "content": {"x": 1.38, "y": 4.58, "w": 31.106667, "bottom": 17.75},
    "footnotes": {"top": 16.6, "bottom": 17.75, "gap": 0.2},
    "font": "Arial",
    "colors": {"primary": "2F627A"},
    "layouts": {"two_columns": {"widths": [14.95, 14.95], "gap": 1.206667}},
    "exceptions": {"one_line_summary": {"content_y": 3.81}}
  },
  "patterns": [{"id": "team", "intent": "team introduction", "reference": {"source_id": "source-id", "slide": 7}, "capacity": "Select based on legibility", "notes": "Reuse verified portraits and roles."}]
}
```

When footnotes are present, content must end at `footnotes.top - footnotes.gap`; the two regions are not available simultaneously. Profile rules may include additional brand-specific fields. Validation checks dimensions and source existence, not visual quality or semantic correctness.

## Brief

`brief` produces `schema_version`, `input`, `slides` containing `order`, `heading`, `body`, `notes`, `intent_hint`, and `raw`. It deliberately does not choose people or invent a summary. Agent-authored `deck-plan.json` expands each slide with `pattern`, `record_ids`, `fact_ids`, `user_facts`, `content`, `evidence`, `issues` and `status`.
