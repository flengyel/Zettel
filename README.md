# Zettel

This repository contains a Markdown note-format specification for my digital Zettelkasten, together with supporting templates, scripts, validators, script documentation, generated documentation, and export files. The note format works with [Obsidian](https://obsidian.md) and [Zotero](https://www.zotero.org/), but may be adapted to other systems.

## Purpose

This repository documents the software, configuration files, scripts, templates, and documentation used with a private digital Zettelkasten vault, using inspectable artifacts.

The repository contains source-controlled artifacts: the Markdown note format, reserved index-note scheme, Obsidian Templater templates, validation scripts, export support files, generated software inventory, and script documentation.

The [Zettel Wiki](https://github.com/flengyel/Zettel/wiki) explains how those artifacts are used: software configuration, indexing conventions, examples, workflow notes, and methodological distinctions.

## Scope

This README specifies the Markdown note format: the self-documenting note template, the `id`/`title`/H1 relationship, reserved index IDs, `SEE ALSO`, `References`, WikiLinks, hashtags, and citations.

## Repository contents

- `README.md` — Markdown note-format specification.
- `doc/` — Markdown documentation for repository scripts and Python tools.
- `generated/` — generated documentation artifacts.
- `pandoc/` and `LaTeX/` — export and typesetting support files.
- `python/` — Python validators, tests, generators, and local diagnostics.
- `scripts/` — bootstrapping and publishing scripts.
- `templates/` — Obsidian Templater templates for note creation and WikiLink title annotation.

The [Zettel Wiki](https://github.com/flengyel/Zettel/wiki) contains operational conventions, definitions, examples, software configuration, generated inventory pages, and methodological notes.

### Background

The Zettelkasten Method is documented at [Introduction to the Zettelkasten Method](https://zettelkasten.de/posts/overview/) and in the [Zettelkasten.de forum](https://forum.zettelkasten.de). If the terminology of literature notes and permanent notes seems vague or confusing, see [From Fleeting Notes to Project Notes](https://github.com/flengyel/Zettel/wiki/From-Fleeting-Notes-to-Project-Notes). Also see Chris Aldrich's [Note Taking Traditions](https://notemaking.substack.com/).

## Self-documenting note specification

The following self-documenting note specification includes explanatory
definitions and index documentation. Ordinary notes use the YAML front matter, the H1 heading, their own body content, and the `## SEE ALSO` and `## References` sections. They do not include the explanatory definitions and index documentation below.

Replace the metavariables `<ID>` and `<TITLE>`; the angle brackets do not appear in a completed note. The metavariable `<ID>` is the unique, immutable ID of the note and is identical to the filename without the `.md` extension. An `<ID>` is a nonempty contiguous string with no whitespace and must be compatible with the target operating system's filename rules. Except for the reserved `<ID>` values below, this document does not prescribe further ID structure.

In this system, current notes use a keyword followed by a timestamp, but ID formats have changed over time.

### YAML Front Matter

Each note begins with YAML front matter: a first line containing three consecutive dashes (`---`), followed by YAML properties, and closed by  
another line containing three consecutive dashes.

The value of the `id:` property is `<ID>`. The value of the `title:` property consists of `<ID>`, one space, and `<TITLE>`.

The `reference-section-title:` property is used by Pandoc as the heading  
for a generated bibliography when the note contains Pandoc-style citations. The value of the `reference-section-title:` property is `References`, as shown below.

```markdown
---
id: <ID>
title: <ID> <TITLE>
reference-section-title: References
---
# <TITLE>

The note body begins with the line after the H1 heading and ends with the line before
the `## SEE ALSO` section below. The H1 heading text is the value of `<TITLE>`, apart
from trailing spaces. Titles may change; IDs do not.

## Definitions

### Element types

- **WikiLink:** A note link of the form `[[ID]]`.
- **Hashtag:** A tag of the form `#tag`.
- **Pandoc citation:** A citation of the form `[@citeKey]`.

### Alphabetic and numeric index notes

The following `<ID>` and `<TITLE>` values are reserved and are used to create an
automatic note index through Obsidian's backlink mechanism. The IDs were chosen to
appear at the beginning of the Obsidian File Explorer panel. For each `<ID> <TITLE>`
pair below, the Zettelkasten should have exactly one note with that `<ID>` and `<TITLE>`:

- `0000.0000.0000 INDEX`
- `0000.0000.0ABC A-B-C`
- `0000.0000.0DEF D-E-F`
- `0000.0000.0GHI G-H-I`
- `0000.0000.0JKL J-K-L`
- `0000.0000.0MNO M-N-O`
- `0000.0000.0PQR P-Q-R`
- `0000.0000.0STU S-T-U`
- `0000.0000.0VWX V-W-X`
- `0000.0000.00YZ Y-Z`
- `0000.0000.0009 0-9`

No other `<ID> <TITLE>` combination belongs to an index note.

Under the `## SEE ALSO` section of a note, index one or more words from 
the H1 heading by adding the corresponding index WikiLink, one index link 
per line. The index-entry line form is documented in the Alphanumeric Index
page of the Zettel Wiki. The `## SEE ALSO` section may include WikiLinks of
related notes other than those appearing in the main body, one or more
alphabetic or numeric index links, and optional hashtags.

The `## References` section is present but may be empty. Here we have 
included a reference on Zettelkasten.

## SEE ALSO

[[0000.0000.00YZ]] Y-Z  

#optional #hashtag

## References

Ahrens, Sönke. 2017. _How to Take Smart Notes_. North Charleston, SC: CreateSpace.
```

## Security

This repository contains executable code, including Obsidian Templater JavaScript, Python, and shell scripts. Standard security precautions apply.

## License

This README and the Zettel Wiki are licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/legalcode), CC BY-SA 4.0, 2022-2026 F. Lengyel. Notes that merely instantiate the template need not credit me. Published copies or derivatives of the template remain subject to CC BY-SA 4.0.

**Notice of License Termination:** Pursuant to Section 6 of the CC BY-SA 4.0, "Your rights under this Public License terminate automatically for failure to comply with this Public License." Upon such termination, all permissions granted under this license cease, and the work remains subject to standard copyright protection.

The code is licensed under the GNU General Public License, version 3, 29 June 2007.
