# Read-only reference learning

Apply this during setup and reference learning in update, including when the reference is the open PowerPoint deck. Setup creates library/design artifacts; it does not edit the reference deck. Inbox sorting may change its path through the verified moves in intake.md, but never its bytes.

## Embedded objects

A PPTX can contain OLE objects, embedded workbooks, add-in data and preview images. An `oleObject*.bin` filename alone establishes neither malware nor safety. Preserve the original package, relationships and embedded parts. Do not activate OLE, run macros, refresh linked objects, follow external data links, or parse embedded binaries to learn a slide's visible content and design.

Use authorized native read operations for the open deck. Where file execution is available, the bundled library.py extractor opens the PPTX ZIP in read mode, reads presentation XML and image assets, and records embedded part names/sizes without parsing their payloads. Its reference_import metadata is an inventory, not a security assessment. Whole-file snapshots still contain the original embedded bytes. Native chart caches are source observations, not refreshed workbook values; an object's preview is not its editable underlying data.

Do not round-trip a reference through a presentation writer or Office Save As merely to analyze it. Do not strip `ppt/embeddings`, delete OLE shapes, flatten objects, remove relationships, or create a sanitized copy to make a warning disappear. Library metadata and derived images belong in separate output paths. Calibration slides belong in a separate generated presentation, never appended to the reference. If only in-place editing is available, leave the reference intact and explain the missing output capability.

## When Claude asks to continue a script

1. Inspect the exact proposed operation and input/output paths if exposed. Distinguish an embedded-object inventory from a script that would modify, delete, convert or overwrite files. The warning text alone does not establish what the pending script does.
2. Do not approve on the user's behalf, recommend unconditional Continue, alter the approval settings or hide the warning. Do not execute a rejected operation by another route.
3. If the proposed script modifies the reference, withdraw that plan. Use a separately permitted read-only analysis operation if available, writing only derived library/design artifacts. If the host requires approval for that operation too, state exactly what it reads and writes and leave approval to the host/user.
4. If no permitted read-only operation is available, pause the affected import. Continue independent work; retain the source and mark its analysis pending. Do not report the reference as learned.

Report actual handling once, for example: “Reference analyzed without changing its bytes. Embedded objects were preserved; their internal contents were not inspected.” Never claim that this disables Claude's security prompts or certifies the file safe. If asked to assess an unknown pending script, obtain its actual code/action details before judging approval safe.

## Existing setups

Version 0.1.1 adds explicit handling instructions and an embedded-part inventory; it does not remove objects or migrate source files. Older source extracts may lack reference_import metadata. Do not infer zero embedded objects from a missing field or delete existing extracts to force reimport. A separate read-only extraction can inventory a source when needed.
