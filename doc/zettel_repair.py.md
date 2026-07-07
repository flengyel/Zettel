# Zettel repair tool

`python/zettel_repair.py` applies selected structural repairs to completed Markdown Zettels.

The tool uses `python/zettel_validate.py` to validate each note before and after a repair plan. Dry run is the default. Files are modified only when `--write` is supplied and the repair plan reduces the validation issue count.

## What it repairs

The current repair set is deliberately narrow:

1. Add a missing `id:` property from the filename stem when the filename stem is a valid ID with no whitespace.
2. Add a missing `reference-section-title: References` property.
3. Repair an H1 that copied the complete front-matter `title:` value, but only when the filename stem and YAML `id:` already agree.
4. Append an empty `## References` section when that section is missing.

The repair tool does not infer note content, move sections, rewrite duplicate headings, guess missing index links, repair mismatched filename/front-matter IDs, or resolve malformed YAML.

## Exit status

- `0` when no repairs are pending and all checked files are valid after the repair plan.
- `1` when a dry run found repairable files, a write-mode repair was blocked, or validation failures remain after the repair plan.
- `2` for invocation, path, read, or write errors.

## Dry run one note

Run from the repository root:

```powershell
python .\python\zettel_repair.py "$env:USERPROFILE\Zettelkasten\rf.2b.0.23.0323.md"
```

The command reports the repair plan, validates the proposed repaired text, and does not write the file.

## Repair one note

```powershell
python .\python\zettel_repair.py "$env:USERPROFILE\Zettelkasten\rf.2b.0.23.0323.md" --write
```

Write mode applies a repair plan only when the plan reduces the validation issue count. A file may remain invalid after a partial repair; the after-validation output reports the remaining issues.

## Check the Zettelkasten root

```powershell
python .\python\zettel_repair.py "$env:USERPROFILE\Zettelkasten"
```

A directory is not searched recursively by default.

## Check recursively

```powershell
python .\python\zettel_repair.py "$env:USERPROFILE\Zettelkasten" --recursive `
  --exclude "Templates/**" `
  --exclude "Periodic-Notes/**" `
  --exclude "Projects/**"
```

## Temporarily omit index checks

```powershell
python .\python\zettel_repair.py "$env:USERPROFILE\Zettelkasten" --no-index-links
```

This is useful when repairing front matter before addressing index-link failures.

## Run tests

```powershell
python .\python\test_zettel_repair.py
python -m unittest discover -s python -p "test*.py"
```
