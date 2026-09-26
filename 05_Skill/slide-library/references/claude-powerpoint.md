# Claude for PowerPoint runtime and storage

## Runtime

Use tools exposed by the Claude for PowerPoint add-in. Do not call Codex-specific namespaces, assume a local workspace or require the user to install Codex. The skill is an instruction package, not an independent add-in or API service.

On invocation, inspect only the capabilities relevant to this command: access to the current presentation and selected slides, supplied references, slide edits, rendering or screenshots, file tools/code execution and connected storage. Use native slide operations for the open deck. If a visual verification tool is missing, report that the result has not been visually checked; do not invent inspection results.

Claude's `/` picker selects available skills. `setup` and the other terms in commands.md are dispatch instructions interpreted inside this skill, not separately registered global slash commands. Natural-language requests remain valid.

## Storage modes

Choose from capabilities actually available. Do not claim a connector supports writes merely because it can search or read files.

The preferred user experience is one user-selected local folder containing examples, the derived content library and design, and optionally working presentations. A desktop folder is a convenient default suggestion, not a hard-coded path. Follow the folder workflow below when actual authorized file access is available.

1. **Connected store:** If the user has selected an accessible store with appropriate read/write operations, keep a setup index and separate data per setup there. Verify writes by reading them back. Use its version or archive support for updates/removal when available. Changing another organization's shared setup requires authority for that specific target.
2. **Portable package:** If file creation is available but durable storage is not connected, export a named setup package containing a manifest, content records, design profiles, needed assets and reference evidence. The user retains it and supplies it in a future session. Include no organization data in the distributed generic skill. Do not promise that an exported package automatically installs or synchronizes itself. Accept a package via supported file access; if the add-in cannot consume it directly, describe the available import route rather than fabricate support.
3. **Session only:** If neither persistence route is available, keep a temporary setup for the current conversation, clearly label it as temporary and expose whatever export is actually possible. `list` must distinguish temporary from saved setups.

Do not use chat memory as the only authoritative database. Do not write to the installed skill to store evolving company content. Do not rely on hidden slides or speaker notes as an invisible library database. The open deck remains the user's presentation.

## Preferred folder workflow

This storage layout is implemented by scripts/workspace.py when the runtime has authorized file access. It does not itself connect the PowerPoint add-in to the desktop. One folder represents one named setup. Several independent setups can live in separate folders. Adapt existing top-level folder names instead of relocating an existing workspace to enforce this example. Organize the selected setup's incoming material as described in [intake.md](intake.md):

```text
My Slide System/
  00_Throw_In/          Inbox for mixed presentations, photos, logos and other references
  01_Examples/          Automatically organized source originals
  02_Library/           Curated content, portraits, assets and source evidence
  03_Design/            Design rules, profiles, editable templates and slide patterns
  04_Presentations/     Optional rough inputs and generated presentations
  setup.json            Setup identity, relative locations and import state
```

The user drops mixed material into `00_Throw_In`; through `setup` and `update`, the skill automatically sorts originals into `01_Examples` and maintains the library and design. Read [intake.md](intake.md) for classification, evidence-based image associations, optional batch review and recoverable file moves. The user need not sort references by slide type or edit structured data. Source contents remain unchanged even when their paths change through sorting. Store both useful editable reference material and the rules derived from it; font/color extraction alone is not a complete design library. Record provenance and project/reusable scope for content independently of its design value.

On `setup`, resolve the user-selected folder and actual read/write capability once, inspect the supplied examples, then create the derived library and design in that folder. Preserve any existing contents and resolve setup-name collisions. A folder path written in chat is not proof that the runtime can access it. Never silently replace a requested persistent folder with session-only storage.

On `update`, inspect the inbox and indexed source archive, comparing source identities and content fingerprints with the saved import state. Reuse unchanged extraction, reconcile new or changed sources, and retain the prior usable setup until its replacement is saved and checked. A missing source file is not an instruction to delete its derived records; report unavailable evidence. Do not import the generated library, design outputs or presentation output folder as new reference material.

On `build`, use the saved setup and the current rough presentation or chat outline. Do not relearn or change the setup implicitly. A user putting a file into `00_Throw_In` does not trigger processing on its own: updates run when invoked. Do not promise a background folder watcher.

On `delete-setup`, apply commands.md to the derived setup only; do not recursively delete the containing folder with its original examples and presentations. Prefer recoverable archival of the owned derived data.

### Access from Claude in PowerPoint

Claude Desktop/Cowork documents read/write access to connected local folders. This does not establish that a skill running in the PowerPoint sidebar inherits that access. Check the tools actually exposed there. The skill itself cannot grant filesystem permissions or provide a missing file connection.

For the intended seamless PowerPoint workflow, a working connection must provide folder listing, source reads, asset access and verified writes to the selected setup folder. When that connection is unavailable, manage the folder in Desktop/Cowork and use workspace.py export to create a personalized profile skill. Enable the ZIP through Customize > Skills; its content and design can then be used in PowerPoint. Follow [runtime.md](runtime.md). This is a two-step workflow with explicit snapshot refreshes, not a live folder connection. Keep the user's preferred PowerPoint authoring surface; do not silently move the whole workflow to Cowork.

## Setup manifest

A setup can use `setup.json` with `schema_version`, stable `id`, `name`, `status`, `library`, `design_profiles`, `default_design`, `updated_at`, `storage_mode` and `source_references`. Locations are relative within a package or resolved by the connected store. Do not embed machine-specific absolute paths in a portable setup. The optional existing `library.json` and data-model.md describe the library inside a setup.

The active setup selection belongs to the current conversation unless the user requests a durable default. Source ownership is distinct from setup ownership: originals linked into the system are not disposable setup data. Reference snapshots or shared assets are removable only within the selected setup's owned storage and after checking other setup references.

## Documentation checked for this design

- https://support.claude.com/en/articles/12512180-use-skills-in-claude — enabled skills are available in Office add-ins; skill picker and natural-language triggering.
- https://claude.com/docs/office-agents/powerpoint — native slide editing, template awareness, connectors and persistent instruction preferences.
- https://support.claude.com/en/articles/12512198-how-to-create-custom-skills — portable skill instructions, resources and packaging.
- https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork — connected local folder access through Claude Desktop/Cowork; not proof of direct folder access from the PowerPoint sidebar.

These establish the target environment. They do not by themselves establish a writable shared-library backend or automatic self-updating installation. Test the actual storage and add-in behavior before claiming end-to-end deployment.
