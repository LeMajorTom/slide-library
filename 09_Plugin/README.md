# Slide Library

An English-language Claude plugin for learning a personal content library and design from reference material, then completing rough slides in PowerPoint.

## Install

Use **dist/slide-library-@VERSION@.zip** for the plugin. In Claude, open **Customize → Plugins** and use the custom plugin upload option. Enable the plugin. The release builder substitutes the version in this guide when packaging.

For the documented PowerPoint skill route, use **dist/slide-library-skill-@VERSION@.zip** under **Customize → Skills → + Create skill → Upload a skill**, then enable it. Enable code execution and file creation if required by the account. Both packages contain the same core skill; choose one installation route per surface to avoid duplicate skills.

Claude for PowerPoint must already be installed and signed in to the same Claude account. Type / in its sidebar to select Slide Library, then use the commands below. Plugin command wrappers are namespaced in Claude Code; they are not independent global /setup commands in PowerPoint.

## First setup

1. In Claude Desktop/Cowork, select the desktop location where Claude may create your workspace.
2. Select Slide Library and ask: **setup My Company — create My Slide System in this folder**.
3. The helper creates the workspace below. It does not create it merely because the plugin was installed.
4. Drop reference presentations, photos, logos, documents or saved emails into **00_Throw_In**.
5. Ask **update**. Claude inspects the files, uses the helper to sort/import them, and curates content and design.
6. If needed, name unresolved pictures using the numbered image review.

    My Slide System/
      00_Throw_In/
      01_Examples/
      02_Library/
      03_Design/
      04_Presentations/
      setup.json

The helper requires Python 3.9+. No additional package is needed for core operations. PDF text extraction can use an existing pypdf installation; other formats may need Claude's document/image tools. Unsupported files remain visible for review.

## Use in PowerPoint

Open rough slides or supply a short outline, select Slide Library and use **build**. Claude retrieves content and applies the selected design using native PowerPoint tools.

Local folder permissions do not automatically carry into PowerPoint. If that surface cannot access your workspace, ask Claude in Desktop/Cowork:

**export — save this setup as a profile skill for PowerPoint.**

Enable the resulting profile ZIP under Customize → Skills. In PowerPoint select that profile and Slide Library, then use build. A profile is a saved snapshot, not a live connection. Export a new version after updating the folder. Raw source archives and project material are excluded by default.

To verify persistence, start a **new** PowerPoint chat after installation, select the profile, and ask **use My Company**. Claude should read the saved profile's identity, export date, records and design, without learning the references again. Then use **build**. After a library update, export and replace the same profile through its **Replace** control in Customize → Skills; verify the new export date in a fresh chat. Core skill updates and personal profile updates are separate. If a newly installed or replaced skill is missing or stale in PowerPoint, reload the Claude add-in from its add-in options, then start a fresh chat and verify the profile export date or core version again.

## Embedded-object warnings during setup

Reference learning preserves the original presentation and its embedded objects. Version 0.1.1 explicitly instructs Claude to avoid reference cleanup/resaving and inventories embedded package parts without parsing their contents. The helper already used read-only extraction in version 0.1.0. This update clarifies Claude's orchestration; it does not certify a source file safe or disable the host's approval prompts.

If Claude asks to continue a script and lists oleObject*.bin files, the list alone does not show what the pending script will do. Inspect that operation before approving. Setup should read the reference and write separate library/design artifacts, without deleting objects or overwriting the presentation. If the host blocks the read, leave that import pending instead of bypassing the restriction. Updating the skill does not require deleting an existing setup.

## Commands

| Command | Result |
| --- | --- |
| setup | Create a workspace and learn supplied references |
| update | Sort and learn new/changed material |
| build | Complete rough slides or an outline |
| list | Show accessible setups |
| use My Company | Select a setup/design for this conversation |
| export | Export a ready setup as a personal profile skill |
| delete-setup My Company | Archive the named setup; preserve files |
| restore My Company | Restore an archived setup as a draft for review |
| version | Show the active core skill version |
| check-updates | Check GitHub Releases or compare a supplied release file/ZIP |
| upgrade | Check a new skill ZIP and guide manual installation |
| help | Show commands and starting examples |

Image classification and factual curation are performed by Claude. The helper does not identify faces or invent names. Explicit user mappings and source captions are retained as evidence.

For a quick photo assignment, include a short caption file such as **Photo captions.txt** with **portrait-A.png = Alex Morgan**. Claude checks that explicit source label and links the image to the matching profile. An ambiguous filename or an unlabeled photo remains unresolved; the numbered image review lets you resolve it once. Unresolved and disputed photos are excluded from the exported named-person assets. Original filenames and fingerprints accompany included photos for traceable citations.

## Updates with a personal Claude account

The release builder automatically runs tests, creates both ZIPs, checks their contents, and writes release.json with versions and checksums. The skill's check-updates command reads the latest GitHub release for the repository in version.json when authorized network access is available. It can also compare a supplied release.json or standalone skill ZIP without installing or executing it. An inaccessible repository, missing release or network error is reported as a failed check. Configuring a repository address alone does not publish anything.

For an upgrade, supply the new skill ZIP and ask upgrade. Upload the checked package through Customize > Skills using the actual update/upload option available there. If Claude creates a second entry, verify and enable the new core skill and disable the old one. In a fresh PowerPoint sidebar conversation, select Slide Library and ask version to verify what is loaded. Your saved workspace and separate personal profile skill stay in place; do not delete or recreate the setup.

The installation click remains manual. These commands do not make a local release automatically appear in Claude, provide a background update service or synchronize personal profile contents. Public GitHub releases need no credentials. A private repository needs an authorized host connection or manually downloaded release files; the skill stores no GitHub token.

## Optional Outlook

Use an existing authorized Microsoft 365 connection configured for read-only access. The standard connector supports work accounts and may require administrator approval. This package contains no mail credentials, mail server, send tools or background mailbox import. Saved EML files and pasted text also work.

## What was validated

Local tests cover sorting, name collisions, duplicate preservation, interrupted move recovery, path boundaries, image assignment evidence, changed images, source extraction, content rollback, design geometry and references, archival, restoration and profile exports. The builder validates the skill files, archive contents and release checksums. Claude Code validation is a separate release check, not an implicit part of packaging.

Actual upload to your Claude account, account-specific folder permissions and native PowerPoint editing must be exercised in that environment. No local library, design or company material is bundled.

## Build from source

The canonical skill source is ../05_Skill/slide-library. Set the release version and notes in its version.json, then run:

    python3 build_plugin.py

The build runs the tests first and package validation afterward. It writes versioned ZIPs, a versioned release manifest and the current release.json. Prior versioned ZIPs are retained. The build script replaces only its generated slide-library folder and its release outputs. It never modifies a user's desktop, Claude settings or library. Nothing is published or installed by this command.

In the standalone GitHub repository, pushing a matching vMAJOR.MINOR.PATCH tag triggers the release workflow. GitHub Actions runs the build and publishes the checked ZIPs and manifest together. Main-branch and pull-request pushes only validate. Keep personal examples, workspaces and profile exports outside this repository.

Official installation references:
- https://support.claude.com/en/articles/13837440-use-plugins-in-claude
- https://support.claude.com/en/articles/12512180-use-skills-in-claude
- https://claude.com/docs/office-agents/powerpoint
