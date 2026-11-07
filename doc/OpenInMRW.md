# Open the current Obsidian note in MRW

Run **Templater: Open in MRW** while reading or editing a note. MRW opens its
current file in Markdown preview and Contents. The command does not insert
text, replace selections, save the note or import its contents.
MRW 0.22.5 or later must be active in the intended VS Code workspace.

## Setup

1. Copy `templates/OpenInMRW.md` into your configured Obsidian templates folder,
   alongside `Timestamp.md`, `NewFileTemplate.md` and `WikilinkTitle.md`.
2. Add it under Templater's **Startup templates**, and enable startup templates
   on this device. This file only registers **Templater: Open in MRW** when
   Obsidian starts; it does not open MRW automatically. Do not add it to
   **Template hotkeys** or use Insert/Create. Registration uses Templater 2.26's
   startup mode and the Obsidian plugin command API.
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

Open the note in Obsidian and run **Templater: Open in MRW**. The action reads
the current filename when invoked. It works in reading view and editing view;
cursor positions, selections and YAML are not processed. No clipboard transfer,
CLI call or per-note link is needed.

Obsidian's normal saving remains responsible for edits. MRW opens the current
saved file and preserves any unsaved VS Code draft instead of replacing it.

The workspace and selected notes folder must match the link. If VS Code routes
it to a different workspace, MRW offers **Copy Link and Open Workspace** in a
separate window; then use **MRW: Open Link from Clipboard** there. The command
does not select a vault or synchronize a separate remote tree automatically.
The relative filename locates a live note, not an immutable source revision.
Moving the note needs no template change: the next invocation uses its current
path. A keyboard shortcut for **Templater: Open in MRW** is optional.

In the configured vault, **Alt+/** is assigned to this command after
checking all three scopes: Windows global shortcuts, VS Code (including
extension bindings), and Obsidian's effective bindings.
**Alt+M** remains **Insert math block**, **Alt+W** remains WikilinkTitle and
**Alt+T** remains Timestamp. **Ctrl+Alt+M** is reserved by MobaXTerm and was
removed from this command. Other machines need their own shortcut check.

## Links in a note

For a link stored in the note, use **MRW: Copy Note Link for Obsidian** and
place the copied link under `## Research`. Change its label to **Open in MRW**,
keeping the address intact. Research holds references and research utilities;
`reference-section-title: References` continues to name Pandoc's generated
bibliography. The Templater command above does not require a stored link.

## Checks

Run `node --test tests/open-in-mrw.test.cjs` from this repository. The checks
execute the startup registration and registered action with a simulated API.
They verify registration without insertion, current-note identity in reading
view, Unicode encoding, rejected insertion routes and configuration failures.
They do not establish an observed desktop round trip.

### Observed checks — 2026-11-07

The four command-registration and action checks pass, as do all 46 existing
Python checks in an isolated environment with PyYAML 6.0.3. The manifest includes
the new files and the previously omitted `prepare_book.py`; the existing
software-inventory snapshot was preserved.

The configured vault's running Templater 2.26.0 registered **Open in MRW** via
its real startup-template path. The user explicitly authorized enabling startup
execution for this single registration template. The old Insert command is
removed; the three earlier template commands and keyboard shortcuts remain.

Invoking the registered action with desktop dispatch captured produced the
current note's MRW address and left editor text and saved bytes unchanged.
The MRW receiving handler separately passed three native VS Code/WSL checks,
including preview/Contents opening and preserving a dirty note. A physical
Obsidian menu click through the operating-system URI router was not observed.
