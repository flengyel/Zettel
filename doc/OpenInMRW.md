# Open the current Obsidian note in MRW

`templates/OpenInMRW.md` is a Templater navigation command. Run it while working
in a note to open that note in MRW's Markdown preview and Contents. It inserts
no link, imports no text and does not change the note's filename or metadata.
MRW 0.22.5 or later must be active in the intended VS Code workspace.

## Setup

1. Copy `templates/OpenInMRW.md` into your configured Obsidian templates folder,
   alongside `Timestamp.md`, `NewFileTemplate.md` and `WikilinkTitle.md`.
2. In Templater's **Template hotkeys**, add that template with **Insert** enabled
   and **Create** disabled. This registers **Templater: Insert OpenInMRW** in the
   command palette. A keyboard shortcut is optional.
3. Create `mrw.json` in the vault's configuration directory (normally
   `.obsidian`). For Windows Obsidian and WSL, for example:

   ```json
   {
     "workspace": "vscode-remote://wsl+Debian/home/USER/research/MRW.code-workspace",
     "notes": "/mnt/c/Users/USER/Zettelkasten"
   }
   ```

`workspace` names the saved workspace or opened folder, using its encoded URI.
For local Linux use `file:///home/USER/research`. SSH needs its
`vscode-remote://ssh-remote+HOST/…` address. `notes` is the same absolute vault
root selected by **MRW: Choose Notes Folder…**, on that host. For VS Code
Insiders, add `"scheme": "vscode-insiders"`. Keep machine paths in the local
configuration; do not commit a private `mrw.json` to this repository.

## Use

In Obsidian, open the note and run **Templater: Insert OpenInMRW**. MRW opens
its current saved file. Obsidian's normal saving remains responsible for edits;
MRW preserves an unsaved VS Code draft instead of replacing it. No clipboard
transfer, CLI call or per-note link is required by the command.

Templater's Insert action needs an editor. The command preserves an ordinary
text selection, but refuses multiple cursors and a YAML selection: Templater would interpret returned
front matter as a metadata edit. Clear that selection and run it again.

The workspace and selected notes folder must match the link. If VS Code routes
it to a different workspace, MRW offers **Copy Link and Open Workspace** in a
separate window; then use **MRW: Open Link from Clipboard** there. The command
does not switch workspaces, select a vault or synchronize a separate remote tree
automatically. The relative filename locates a live note, not an immutable
source revision or retained passage. Moving the note needs no template change;
the next invocation uses its current path.

## Checks

Run `node --test tests/open-in-mrw.test.cjs` from this repository. The checks
execute the template with a simulated Templater API and capture URI dispatch.
They verify note identity, Unicode encoding, selected text, configuration errors
and YAML refusal; they do not establish an observed desktop round trip.

### Observed checks — 2026-11-07

The five template checks and all 46 existing Python checks pass. Python checks
used an isolated environment with PyYAML 6.0.3. The manifest now includes the
new template, guide and checks, and the previously omitted `prepare_book.py`.
The existing generated software inventory was preserved.

The command is registered in the configured vault's running Templater 2.26.0,
with Insert enabled and Create disabled. The live Templater parser produced the
current note's MRW URI with its selection returned unchanged; editor text and
saved bytes were unchanged. URI dispatch was captured for this check. The
MRW 0.22.5 receiving handler separately passed native VS Code/WSL checks for
preview/Contents opening and draft preservation. An actual Obsidian menu click
through the desktop URI router was not observed in this check.
