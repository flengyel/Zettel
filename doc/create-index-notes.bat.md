# `scripts/create-index-notes.bat`

## Purpose

`create-index-notes.bat` bootstraps the reserved alphanumeric index notes for a Zettelkasten vault.

It creates only the reserved index-note files. It does not create ordinary notes, validate ordinary note IDs, or impose an ordinary note ID scheme.

## Usage

From the repository root:

```cmd
scripts\create-index-notes.bat
```

or with an explicit target directory:

```cmd
scripts\create-index-notes.bat "%USERPROFILE%\Zettelkasten"
```

If no target directory is supplied, the script writes to the current directory.

## Behavior

The script:

- creates the target directory when it does not exist;
- stops if the target path exists but is not a directory;
- creates missing reserved index-note files;
- skips existing files;
- never overwrites existing notes;
- exits with a nonzero status if directory creation or file writing fails.

## Reserved files

The script creates these files when absent:

| File | Title |
|---|---|
| `0000.0000.0000.md` | `0000.0000.0000 INDEX` |
| `0000.0000.0ABC.md` | `0000.0000.0ABC A-B-C` |
| `0000.0000.0DEF.md` | `0000.0000.0DEF D-E-F` |
| `0000.0000.0GHI.md` | `0000.0000.0GHI G-H-I` |
| `0000.0000.0JKL.md` | `0000.0000.0JKL J-K-L` |
| `0000.0000.0MNO.md` | `0000.0000.0MNO M-N-O` |
| `0000.0000.0PQR.md` | `0000.0000.0PQR P-Q-R` |
| `0000.0000.0STU.md` | `0000.0000.0STU S-T-U` |
| `0000.0000.0VWX.md` | `0000.0000.0VWX V-W-X` |
| `0000.0000.00YZ.md` | `0000.0000.00YZ Y-Z` |
| `0000.0000.0009.md` | `0000.0000.0009 0-9` |

## Generated note structure

Each generated note has YAML front matter, an H1 heading, a `## SEE ALSO` section, and a `## References` section.

The master index note has this title and heading:

```yaml
id: 0000.0000.0000
title: 0000.0000.0000 INDEX
reference-section-title: References
```

```markdown
# INDEX
```

Each subordinate index note has its own title and H1 heading, for example:

```yaml
id: 0000.0000.0ABC
title: 0000.0000.0ABC A-B-C
reference-section-title: References
```

```markdown
# A-B-C
```

## SEE ALSO links

The master `INDEX` note links to every subordinate index note under `SEE ALSO`.

Each subordinate index note links back to the master `INDEX` note under `SEE ALSO`.

The script writes index links in this form:

```text
[[<ID>]] <TITLE>
```

The title is plain text outside the WikiLink. The generated link target is the reserved index ID.

Example:

```text
[[0000.0000.0ABC]] A-B-C
```

## Non-overwrite rule

The script checks each output filename before writing it. If the file already exists, the script prints a skip message and leaves the file unchanged.

This allows the script to be run against an existing vault to create only missing reserved index notes.
