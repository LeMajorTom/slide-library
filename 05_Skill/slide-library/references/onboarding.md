# Guided entry and setup handoff

Read this for a bare skill selection, a request to get started, and the first completed setup. Route an explicit command or clear task directly through commands.md; do not insert a welcome menu, repeat onboarding, or require the user to learn commands before doing that work.

## Choose the entry from actual state

Inspect only the selected/connected folder, supplied package or available installed profile. Do not search the user's computer for libraries. Resolve explicit and active selections using commands.md.

Keep an existing-setup entry to a few short lines. The fuller setup overview belongs at the end of setup/update, not at every greeting. Describe colors and layouts in familiar words rather than dumping measurements or internal metadata.

- **No setup accessible here:** show the short welcome below. Missing access is not proof that no saved library exists. If the user mentions an existing one, offer to select or supply it rather than create a replacement.
- **One accessible ready setup:** name it, identify its saved/exported date and summarize the usable content and design in one or two lines. Offer to build from rough slides or a chat outline, with updating as the secondary option. Selection alone does not edit the deck.
- **Several setups, none selected:** show their names and ask which one to use. Do not blend their content or silently pick the most recent.
- **Draft setup selected:** say what has already been saved and the next unfinished step, such as adding references or reviewing a design. Resume that setup; do not recreate it. An archived setup needs an explicit restore request.
- **Installed profile without local folder access:** use the saved snapshot normally. Show its export date, not a claimed live sync status. Describe the folder/export route only when the user wants to change the library.

## First welcome

Use this English copy as a short conversational menu, adapting it to known context. These are choices in chat, not promised clickable controls or new slash commands.

> Welcome to Slide Library.
>
> Turn rough slides or a short outline into a presentation using your own content and design.
>
> What would you like to do?
>
> **Set up my library** — Add example presentations, photos and documents. I'll organize them and learn your reusable content and design.
>
> **Build a presentation** — Use an existing library to complete rough slides or turn an outline into a deck.
>
> **Update my library** — Add material or revise an existing setup.
>
> You can also describe what you need in your own words.

Accept the option text, a number, or a natural-language answer. Map the choices to setup, build and update. Ask for a folder or references only once setup is chosen and that information is missing. Do not show the twelve-command list unless requested. Honor an explicitly requested interface language.

## Guide the first setup

Use the existing setup and learning workflows; explain only the next step that requires the user. With folder access, suggest `00_Throw_In` for mixed files. Accept supplied references directly when that is the available route. Reuse the user's chosen name and location. An empty workspace is a draft, not a learned library.

After learning, consolidate unresolved photo mappings into the existing numbered image review. Let the user answer once, for example `1 = Alex Morgan; 2 = Berlin office; 3 = leave unassigned`. Persist actual answers. Leave optional unknown photos unassigned by default and continue with clearly associated assets; do not require a reply or an extra "proceed" confirmation to finish the usable setup. When labels cannot be saved in this host, link the review for later instead of collecting an answer you cannot persist. Never infer identity from a face or fill a missing portrait with an unrelated image.

### One editable design preview

As part of the first learned setup, create one representative sample slide by default, unless the user has declined it. This also applies when the first learning happens through update after an empty setup. Reuse an already generated, inspected composition trial if it still matches the learned design. For later updates, regenerate only when the design changed or the user requests it.

- Choose a pattern supported by the references and available content, such as a company overview or team introduction. Use only sourced, in-scope facts and clearly associated images. For a design-only setup, use obvious layout labels such as "Section title" and "Supporting text", never invented company facts.
- Create a separate editable PPTX using the host's available presentation/file tools. In a writable workspace, save a new, non-overwriting file under `04_Presentations`, such as `Setup Preview.pptx`; otherwise return a separately generated attachment. Never insert the sample into the reference deck or modify an unrelated open working deck. Do not change slide counts just to demonstrate the design.
- Apply the actual learned typography, palette, spacing and pattern. Keep claim-to-source notes using composition.md. Render/inspect the created slide and fix fit problems before calling the preview checked. A style description or copied screenshot alone is not an editable preview.
- If separate presentation creation or visual inspection is unavailable, finish the independent library work and state the precise preview limitation. Do not claim a preview exists or was checked, fabricate a visual review, or silently switch to editing the reference. Do not invalidate an already reviewed library solely because this host cannot show its preview.

### Setup overview

Finish with a compact result based on saved files read back or the actual session-only state:

- **Library:** its name and usable content categories/counts. Separate reusable records from project-only or draft material; file counts are not learned-record counts.
- **Design:** the selected style, font/palette and useful slide patterns, with uncertain choices identified.
- **Images:** available associated assets and any unresolved mappings; link the numbered review when it exists.
- **Preview:** link the actual sample and state whether it was visually checked, or say what is pending.
- **Saved / Next:** say where the library lives and the single next action needed to build in PowerPoint.

Use at most six short lines or bullets plus links for this overview, not a full inventory or technical audit. Combine or omit empty lines; do not expose record IDs, schemas, internal paths, geometry, extraction logs or helper-version bookkeeping. Link the actual workspace or deliverables when available. A draft, missing capability or review gap remains visible; do not label the entire setup ready merely because folders were created. No approval of every field is required. Optional refinements can follow after the first usable result.

Use this compact completion shape, filling the placeholders only from observed state. Keep any longer evidence review in the working files, not as extra sections below the overview:

> **[Library name] — [ready / draft / temporary]**
> - **Content:** [usable categories and counts].
> - **Design:** [plain-language style and available patterns].
> - **Images:** [associated count; optional unassigned count and review link].
> - **Preview:** [actual file link and checked status, or precise missing capability].
> - **Saved / Next:** [verified storage state and one next action].

## Make the handoff explicit

Distinguish these states in plain language: **saved in your folder**, **profile ZIP exported**, and **profile available in this PowerPoint chat**. Claim only the furthest state actually verified. If an export or installation was not checked, say "not verified here" rather than asserting that none exists. An exported ZIP is not an installed profile. With direct folder access, build from the saved workspace; otherwise provide the export and guide the existing Customize → Skills replacement route. Verify the loaded profile in a fresh chat before claiming the new content is available there.

After update, summarize changes and any remaining export/replacement step. Say when nothing changed; do not generate a new preview or package just to make a no-op look productive. Core skill upgrades and personal profile updates are separate. Updating the core does not rewrite already exported personal profiles; re-export a profile to include changed standalone profile instructions.
