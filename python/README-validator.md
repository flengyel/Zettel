# Zettel validator

This version validates the current Obsidian conventions rather than the old ID format documented in the repository README.

## What it checks

For each completed Zettel:

1. The file is named `ID.md`.
2. YAML `id` equals `ID`.
3. YAML `title` equals `ID` followed by one space and the H1 text.
4. The H1 is the first nonblank body line and is unique.
5. `## SEE ALSO` and `## References` exist in that order.
6. An ordinary note has, in `SEE ALSO`, at least one link to an alphabetic index note corresponding to the initial letter or digit of at least one H1 word.
7. Special index notes have their fixed IDs and titles and are exempt from rule 6.

ID syntax itself is not restricted. Timestamp IDs, dotted legacy IDs, and special index IDs may coexist.

## Install

In PowerShell:

```powershell
py -m pip install pyyaml
```

## Check one note

```powershell
py .\zettel_validate.py "C:\Users\fleng\OneDrive\Documents\Zettelkasten\Tikz202504272354.md"
```

## Check the Zettelkasten root

```powershell
py .\zettel_validate.py "C:\Users\fleng\OneDrive\Documents\Zettelkasten"
```

A directory is **not searched recursively by default**. This checks the root Zettels without treating `Periodic-Notes`, `Projects`, or `Templates` as Zettels.

## Check recursively

```powershell
py .\zettel_validate.py "C:\Users\fleng\OneDrive\Documents\Zettelkasten" --recursive `
  --exclude "Templates/**" `
  --exclude "Periodic-Notes/**" `
  --exclude "Projects/**"
```

## Temporarily omit index checks

```powershell
py .\zettel_validate.py "C:\Users\fleng\OneDrive\Documents\Zettelkasten" --no-index-links --no-index-inventory
```

This is useful for first checking only the filename/front-matter/H1 redundancy.
