# `scripts/publish-software-inventory.cmd`

## Purpose

`publish-software-inventory.cmd` is the Windows command-wrapper for `scripts/publish-software-inventory.ps1`.

It exists so the publishing workflow can be run from `cmd.exe`, PowerShell, or a Windows shell without typing the full PowerShell invocation.

## Routine procedure

From PowerShell in the main repository root, activate the repository's Python virtual environment:

```powershell
.\.venv\Scripts\Activate
```

Generate the software inventory and preview the Wiki diff without committing or pushing:

```powershell
.\scripts\publish-software-inventory.cmd -DiffOnly
```

After inspecting the diff, generate the inventory again, commit any substantive Wiki change, and push it:

```powershell
.\scripts\publish-software-inventory.cmd
```

## Usage

Run from the main repository root:

```cmd
scripts\publish-software-inventory.cmd
```

Preview the Wiki diff without committing or pushing:

```cmd
scripts\publish-software-inventory.cmd -DiffOnly
```

Commit the Wiki page without pushing:

```cmd
scripts\publish-software-inventory.cmd -NoPush
```

Pass a different Wiki clone path:

```cmd
scripts\publish-software-inventory.cmd -WikiDir C:\Users\fleng\vscode\Zettel.wiki
```

## Behavior

The wrapper runs:

```cmd
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0publish-software-inventory.ps1" %*
```

All arguments are forwarded to the PowerShell script.

The wrapper exits with the PowerShell script's exit code.

## Boundary

This wrapper contains no publishing logic of its own. The generation, copy, diff, commit, and push behavior is defined in `scripts/publish-software-inventory.ps1`.
