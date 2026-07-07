# `scripts/publish-software-inventory.ps1`

## Purpose

`publish-software-inventory.ps1` generates the software inventory page, copies it into the local GitHub Wiki clone, commits the Wiki page when it changed, and pushes the Wiki repository unless instructed otherwise.

The script publishes only this Wiki page:

```text
Zettelkasten-software-inventory.md
```

It does not publish or overwrite `Zettelkasten-software-configuration.md`.


## Windows 11 command prerequisites

The publishing command assumes a Windows 11 workstation with these command-line prerequisites:

| Component | Required for |
|---|---|
| Windows PowerShell 5.1 or PowerShell 7 | running `scripts/publish-software-inventory.ps1` |
| `cmd.exe` | running `scripts/publish-software-inventory.cmd` |
| Python 3.10+ with PyYAML | running `python/gen_software_components.py`, `python/zettel_validate.py`, `python/zettel_repair.py`, and Python unit tests |
| Git for Windows | repository status, diff, commit, push, and Wiki publishing commands |
| Local `Zettel.wiki` Git clone | publishing `Zettelkasten-software-inventory.md` to the Wiki clone |
| GNU Make for Windows | optional `Makefile` targets such as `make generate`, `make publish-wiki`, and `make publish-all` |

Pandoc, MiKTeX, and WinEdt are export-workflow tools. They are listed in the generated inventory under `Export software` with version probes; they are not publisher prerequisites.

Matplotlib is needed only when `python/zettel_diagnostics.py` is run with `--plots`. Seaborn is no longer required for repository diagnostic scripts.

## Usage

Run from the main repository root:

```powershell
.\scripts\publish-software-inventory.ps1
```

Preview the Wiki diff without committing or pushing:

```powershell
.\scripts\publish-software-inventory.ps1 -DiffOnly
```

Commit the Wiki page without pushing:

```powershell
.\scripts\publish-software-inventory.ps1 -NoPush
```

Use a different Wiki clone path:

```powershell
.\scripts\publish-software-inventory.ps1 -WikiDir C:\Users\fleng\vscode\Zettel.wiki
```

Use a different Python launcher:

```powershell
.\scripts\publish-software-inventory.ps1 -Python py
```

## Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `-Python` | `python` | Python executable or launcher used to run `python/gen_software_components.py`. |
| `-WikiDir` | `..\Zettel.wiki` | Local clone of the GitHub Wiki repository. Relative paths are resolved from the main repository root. |
| `-WikiCommitMessage` | `Update software inventory page` | Commit message for the Wiki repository. |
| `-DiffOnly` | off | Generate and copy the page, show the Wiki diff, then stop. |
| `-NoPush` | off | Commit the Wiki page but do not push the Wiki repository. |

## Workflow

The script:

1. resolves the main repository root from the script location;
2. resolves the Wiki repository path;
3. checks that `MANIFEST.software.yaml` exists;
4. checks that `python/gen_software_components.py` exists;
5. verifies that both the main repository and Wiki directory are Git work trees;
6. records the pre-run generated and Wiki inventory file contents, when those files already exist;
7. runs the generator to create `generated/Zettelkasten-software-inventory.md`;
8. restores the pre-run generated inventory when the only generated difference is one `Last checked:` line;
9. copies the generated page to the Wiki clone;
10. restores the pre-run Wiki inventory when the copy changed only one `Last checked:` line;
11. prints the Wiki diff;
12. stages the Wiki page;
13. skips the commit if there is no staged change;
14. commits the Wiki page if changed;
15. pushes the Wiki repository unless `-NoPush` was supplied.


## Timestamp-only generated changes

The software inventory contains a `Last checked:` line. The publisher suppresses a run when that timestamp is the only changed line:

- the generated page is restored from its pre-run bytes when only `Last checked:` changed;
- the Wiki page is restored from its pre-run bytes when copying the generated page changed only `Last checked:`;
- no `git restore` command is used.

Real inventory changes are preserved and published normally.

## Repository boundary

The script commits only the Wiki repository. It does not commit changes in the main repository.

Commit main-repository changes separately when `MANIFEST.software.yaml`, `python/gen_software_components.py`, scripts, documentation, or generated files change.
