# Slide Library for Claude in PowerPoint

Build a personal content library and design from reference slides, photos and documents. Use it to turn a rough PowerPoint or chat outline into a source-grounded presentation.

## Install

Open this repository's **Releases**, choose the latest version and download **slide-library-skill-VERSION.zip**. In Claude, open **Customize → Skills → + Create skill → Upload a skill**, upload the ZIP and enable it. In the PowerPoint sidebar, select Slide Library and use `version` to verify the loaded release.

The release also includes a full Claude plugin ZIP, release metadata and SHA-256 checksums. Use the standalone **skill** ZIP for the Skills upload route. Uploading it as an attachment in the PowerPoint chat does not install it.

## Personal workflow

1. Use `setup` in Claude Desktop/Cowork with access to your chosen folder.
2. Drop reference slides, photos, logos, documents and emails into `00_Throw_In`.
3. Use `update` to organize and learn the new material.
4. In PowerPoint, use `build` with rough slides or a short outline.

When PowerPoint cannot access the local folder, use `export` to save your ready setup as a separate personal profile skill. Keep that profile and your workspace private. Use `delete-setup` to archive a named setup and `restore` to reactivate it without deleting files. A restored setup is a draft until its content and design have been checked again.

Reference learning preserves the source presentation and embedded objects. The skill does not activate OLE objects or disable Claude's approval prompts. A setup becomes ready only after Claude has reviewed the references and a rendered composition trial; passing storage checks alone is insufficient.

See [installation and workflow details](09_Plugin/README.md).

The [0.2.1 validation report](09_Plugin/VALIDATION.md) records the automated checks, actual Claude Code checks and native PowerPoint tests.

## Scope

This is a skill/plugin for Claude, not a standalone Office add-in. Its Python helpers organize, validate, search and export the library. Claude interprets references and composes editable slides with the tools available in PowerPoint. Installing the skill does not create a desktop folder or grant file access; `setup` creates the folder in a location the user has authorized.

The helper reads PPTX/POTX, DOCX, text, Markdown and saved EML files. PDF text extraction uses an existing optional pypdf installation. Other formats remain available for review with the host's readers. Photos are assigned from user labels or source captions, never face recognition. Embedded portraits require a recorded explanation of the identity association before export.

## Updates

`check-updates` checks the repository configured in the installed skill's version.json. `upgrade` provides the latest version-specific skill ZIP and guides the manual upload. A public repository allows checks without GitHub credentials. Private repositories need an authorized host connection or manually supplied release files. No tokens are embedded in the skill. Network restrictions in the host still apply.

Your personal library and design stay separate from core skill updates. Checks run when invoked; this is not an always-on updater. The final installation in a personal Claude account remains manual.

## Development and releases

This standalone repository contains the general skill, synthetic tests and release tooling. It contains no customer reference decks, company library, photos or email archives.

After publication, develop in this standalone repository. The source lives in `05_Skill/slide-library`; `09_Plugin/slide-library` and `09_Plugin/dist` are generated and ignored by Git.

To release:

1. Update `05_Skill/slide-library/version.json` with the next stable version and release notes. Keep the workspace schema unchanged unless implementing a documented migration.
2. Run `python3 09_Plugin/build_plugin.py`. This runs tests and checks the ZIPs and release manifest.
3. Commit and push the source changes. Create and push the matching `vMAJOR.MINOR.PATCH` tag.

GitHub Actions rebuilds and tests the tag, uploads all assets to a draft release and then publishes it. A tag/version or repository mismatch stops publishing. Existing releases are not overwritten. The update checker uses the latest published release's `release.json`; package links point to a specific version. Installation ZIPs are release assets, not GitHub's automatically generated source-code ZIPs.

The main-branch and pull-request workflow validates changes without publishing. The tag workflow needs GitHub Actions enabled and its standard repository contents-write permission. It uses the automatic GITHUB_TOKEN; no personal access token is required.
