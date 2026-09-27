# Release validation — 0.3.0

Validated on 2026-09-27. This release adds guided entry, a setup overview, a separate first-setup design preview workflow and clearer profile handoff instructions. It does not change the workspace schema or the slide-editing backend.

## Automated checks

- All 52 existing helper and release tests pass. They cover source preservation, import/recovery, scoped evidence, photo associations, duplicate-image filenames, missing asset sources, export, archive/restore and update metadata.
- The package builder validates frontmatter, local reference links, all twelve command wrappers, source/package equality, archive integrity and checksums. The new onboarding reference is included in both distributions.
- The skill-creator quick validator and strict Claude plugin manifest validator pass. PyYAML was installed only in a temporary validation environment; the plugin gained no runtime dependency.
- Helper changes are limited to the generated START_HERE guide and standalone profile instructions. No wording-matching unit tests were added as a substitute for behavior testing.

## Claude Code behavior checks

Read-only Claude Code sessions used the generated plugin and isolated synthetic profile/workspace fixtures. They had no PowerPoint editing tools, file-write tools, network connectors or mailbox access.

- **First use:** an empty directory produced the three English choices: Set up my library, Build a presentation, Update my library. No setup, preview or installation was claimed as completed.
- **Saved profile:** selecting the exported profile loaded its real name, export date, six reusable records, associated portrait and design, then invited rough slides or an outline without repeating the first-use menu.
- **Explicit build:** a direct two-slide request bypassed the welcome menu. With no editing tools it disclosed the limitation and produced a content draft; it did not claim an edited PPTX or saved slide notes. An initial overly technical response led to a narrower plain-language fallback; the repeated case omitted coordinates and font specifications.
- **Setup without preview tools:** the saved draft, content/design coverage and unresolved image were read. The response kept preview creation, visual checking and finalization pending rather than inventing them. Optional unresolved images are to remain unassigned without blocking usable work.

The first attempted first-use test shared a directory with the saved draft fixture. It correctly followed the existing-setup branch, so it was not counted as a no-library test; that case was repeated in an empty directory. Early overly detailed setup replies also motivated a six-line overview limit, optional image-review handoff and an explicit distinction between an unverified export and a nonexistent export.

The normal setup command was also exercised against the existing draft. It resumed that identity, used the five-part overview and kept the unresolved photo optional. Read-only setup responses still sometimes added explanatory detail beyond the requested compact format; their predictions about finalization or source fingerprints are not treated as executed validation. Actual helper validation is covered by the automated suite, not by these prose responses.

## Account installation

The final 0.3.0 standalone skill ZIP replaced the existing core skill through Claude Customize → Skills. The enabled state, new onboarding resource and version.json product version 0.3.0 were verified in the account UI. This confirms installation; it does not prove the new preview workflow has run in PowerPoint.

## Runtime limits and previous evidence

These behavior checks validate routing and truthful capability handling, not the visual quality of a newly generated setup preview. No new native PowerPoint composition trial was performed for 0.3.0. The separate editable preview is created by Claude only when the active host exposes suitable presentation/file tools, and visual checking still needs rendering or inspection tools. A source screenshot or a prose style description is not accepted as an editable preview.

The [0.2.1 native PowerPoint validation](https://github.com/LeMajorTom/slide-library/blob/v0.2.1/09_Plugin/VALIDATION.md) remains the recorded end-to-end evidence for saved-profile composition, portrait insertion, project email facts and per-slide source maps. It is not presented as a fresh 0.3.0 preview test.

Personal profiles remain snapshots. Existing profiles need re-export/replacement to pick up new standalone profile instructions. A core upgrade does not modify private libraries, install profiles, or provide live synchronization. Outlook remains excluded from this work.

Raw transcripts, account identifiers, test portraits and personal workspaces are not published in the repository.
