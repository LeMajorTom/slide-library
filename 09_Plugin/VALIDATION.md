# Release validation — 0.2.1

Validated on 2026-09-27 with Python 3.9.6, Claude Code 2.1.270, Claude Customize → Skills and the native Claude PowerPoint sidebar on macOS. All test content and portraits are synthetic.

## Automated checks

- 52 tests pass. Coverage includes source-byte preservation, embedded-object inventories, import recovery, scope revocation, citation-preserving recapture, independent curation, content rollback, design references and geometry, image attribution, profile ZIP export, restore and GitHub update metadata.
- New regressions verify that reviewed photo descriptions and tags survive refresh/reimport, invalid metadata is rejected, exported standalone portraits retain filename/hash provenance and unresolved photos are excluded. Additional regressions preserve distinct filenames for identical image bytes and reject missing asset sources before export.
- Package validation checks frontmatter, local documentation links, all twelve command wrappers, ZIP contents, source/package equality and release checksums.

## Actual Claude Code workflow

Claude Code inspected synthetic reference slides and portraits, curated six sourced records and a reviewed three-pattern design, persisted photo associations, finalized the workspace and exported a personal profile. New helper processes reloaded the saved data. Repeated import added no duplicates. Four originals and four retained source snapshots remained byte-identical. Deliberate attempts to promote project-only and note-only facts into reusable records were rejected and rolled back.

The initial command attempt selected an obsolete local helper copy and was stopped. The corrected run used the canonical 0.2.1 source and independently compared the inherited extraction with a fresh 0.2.1 extraction before continuing. Shell permission denials were resolved within the authorized workflow; this was not a clean first attempt.

The previous 0.2.0 release additionally verified actual plugin loading and discovery of all twelve namespaced commands, setup/archive/restore command execution, and the source recapture and scope-revocation fixes.

## Independent Claude Code review

Claude Code ran the full 50-test suite and separately probed metadata persistence through refresh, explicit reimport, scope changes, file renaming and changed image bytes. It found no regression in image associations or source paths. Its two concrete findings were fixed: standalone assets now keep their individual filename even when source bytes are deduplicated, and missing asset extraction metadata is rejected by validation before export. Two new regression tests bring the suite to 52. The docs clarify that slide notes travel with a deck and anonymized material can use source aliases. The release packages were rebuilt after the documentation changes.

A separate focused Claude Code verification reread both fixes, ran all 52 tests and concluded that both reported issues were fixed with no remaining blocker. This verdict covers the two export changes; native PowerPoint is verified separately below.

The strict Claude plugin manifest validator accepts the generated plugin with no errors or warnings.

## Native PowerPoint test

The core 0.2.1 skill and a separately exported personal profile were installed and replaced through Claude's account UI. A fresh PowerPoint chat loaded the profile without the original reference files or earlier conversation. Selecting the corrected profile preserved all four slides and their notes unchanged.

A single explicit build request then filled four rough headings: Agenda, Company overview, Team introduction and Next steps. The request asked for the available profile portraits but did not repeat the stored company facts or call out citations or the email in slide notes.

The saved PPTX passed 17 independent checks: four slides retained, headings preserved, editable native text, correct people and roles, the historical headcount date retained, project email dates and owner used, original notes preserved, source maps present on every slide, source filenames present on factual slides, exactly one team portrait, its bytes identical to the labelled input, six saved profile records, unresolved portrait excluded and included-photo provenance resolvable. A private test sentinel was absent from both slide copy and exported reusable content. Source maps were also read to check the claim-level references.

All four slides were exported locally by PowerPoint to PDF, rendered and inspected. No visible clipping or text/image overlap was found. The result matches the synthetic reference's Arial, teal/navy palette, white background and footer treatment. This validates this fixture, not universal layout quality.

The first profile trial exposed two instruction gaps: profile selection started editing without a build request, and project email facts in notes were overlooked. Both were corrected before the successful fresh-chat retest. That first trial is not counted as a pass. The final build wrote and reread source maps without a later citation prompt. After the independent code review, a regenerated profile was compared with the native-tested snapshot: content, design, source index and portrait bytes were identical; the asset only gained its individual filename, and the instructions gained citation clarification. The full native build was not repeated for that metadata-only refresh.

## Runtime boundaries

A personal profile is a saved snapshot, not a live desktop-folder connection. After changing the library, run update, export and replace the same profile. The PowerPoint add-in can cache its skill list; reload it and start a fresh chat if the installed profile or version is stale. Core upgrades and personal profile refreshes remain separate.

Outlook was excluded at the user's request. No Outlook account, enterprise connector, real client deck or new embedded-object approval scenario was exercised in this release. Embedded-object preservation remains covered by the automated fixtures. Semantic curation and final slide composition still depend on Claude's actual host tools and the supplied references.

Raw Claude transcripts, account details, personal libraries and reference files are not included in this public repository.
