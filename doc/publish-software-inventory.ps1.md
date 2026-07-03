# `scripts/publish-software-inventory.ps1`

## Purpose

`publish-software-inventory.ps1` generates the software inventory page, copies it into the local GitHub Wiki clone, commits the Wiki page when it changed, and pushes the Wiki repository unless instructed otherwise.

The script publishes only this Wiki page:

```text
Zettelkasten-software-inventory.md
```

It does not publish or overwrite `Zettelkasten-software-configuration.md`.

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
6. runs the generator to create `generated/Zettelkasten-software-inventory.md`;
7. copies the generated page to the Wiki clone;
8. prints the Wiki diff;
9. stages the Wiki page;
10. skips the commit if there is no staged change;
11. commits the Wiki page if changed;
12. pushes the Wiki repository unless `-NoPush` was supplied.

## Repository boundary

The script commits only the Wiki repository. It does not commit changes in the main repository.

Commit main-repository changes separately when `MANIFEST.software.yaml`, `python/gen_software_components.py`, scripts, documentation, or generated files change.
