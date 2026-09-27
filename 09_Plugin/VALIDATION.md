# Release validation — 0.2.0

Validated on 2026-09-27 with Python 3.9.6 and Claude Code 2.1.270.

## Automated checks

- 48 tests pass. Coverage includes source-byte preservation, embedded-object inventories, import recovery, scope revocation, citation-preserving recapture, independent curation, content rollback, design references and geometry, image attribution, profile ZIP export, restore and GitHub update metadata.
- The full helper workflow saves sourced content, searches it, saves a synthetic design fixture, exports an inspectable profile ZIP, archives the setup and restores it. The synthetic design fixture is not evidence of a visual PowerPoint review.
- Package validation checks frontmatter, local documentation links, all twelve command wrappers, ZIP contents, source/package equality and release checksums.

## Claude Code checks

- `claude plugin validate 09_Plugin/slide-library --strict --json` accepts the plugin manifest with no errors or warnings.
- Claude Code loaded the generated plugin through `--plugin-dir`; all twelve namespaced commands and the core skill were discovered.
- In a separate synthetic folder, Claude executed setup, status, archive, restore and final status with the bundled helpers. The final setup was valid, empty and draft, with no invented design or visual review.
- A repeated command test preserved the explicitly requested display name independently of the folder name. No permission denials occurred in that repeated test.
- An independent Claude Code review read the implementation and ran the suite. Its material findings concerned text recapture invalidating citations and scope changes retaining old permissions. Both were fixed with regression tests. The reported recovery, duplicate-marker, reserved export-path and legacy validation issues were also addressed.
- A separate Claude Code verification re-read those fixes, ran all 48 tests and concluded: "All six fixes hold. No blocker found." This verdict covers the reviewed helpers and regressions, with the runtime limits below.

## Runtime boundary

No live PowerPoint sidebar editing, account installation, slide rendering or Outlook connection was exercised in this environment. These checks validate the plugin loading and local library workflow, not native Office integration or the visual quality of generated slides. Semantic curation and visual review still require Claude's actual host tools and the user's references.

Validation uses synthetic material. Raw Claude transcripts, account details, personal libraries and reference files are not included in this repository.
