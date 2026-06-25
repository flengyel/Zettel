# Zettel

This repository documents the conventions I use for a single digital Zettelkasten. This system here works with [Obsidian](https://obsidian.md) and Zotero, but may be adapted to other systems. For software configuration notes, definitions of terms, and more examples, see the [Zettel Wiki](https://github.com/flengyel/Zettel/wiki). The Zettelkasten Method is documented at [Introduction to the Zettelkasten Method](https://zettelkasten.de/posts/overview/) and in the [Zettelkasten.de forum](https://forum.zettelkasten.de). If the terminology of literature notes and permanent notes seems vague or confusing, see [From Fleeting Notes to Project Notes](https://github.com/flengyel/Zettel/wiki/From-Fleeting-Notes-to-Project-Notes). Also see Chris Aldrich's [Note Taking Traditions](https://notemaking.substack.com/).

As of October 2024, I use Obsidian rather than Zettlr. See the [Zettel Wiki](https://github.com/flengyel/Zettel/wiki) for configuration notes and [Guidelines for Maintaining a Digital Zettelkasten](https://github.com/flengyel/Zettel/wiki/Guidelines-for-Maintaining-a-Digital-Zettelkasten) for some of the rules I follow.

## Self-documenting Zettel template

The following self-documenting Zettel template specifies the format of a Zettel. Replace the metavariables `<ID>`, and `<TITLE>`; the angle
brackets do not appear in a completed Zettel.  `<ID>` is the unique, immutable ID of the Zettel and is identical to the filename without the `.md` extension.
We leave the format of `<ID>` unspecified except for uniqueness, immutability, and operating system compatibility. We use a keyword followed by a timestamp,
but our ID formats have changed over time.

```markdown
---

id: <ID>

# `title` consists of `<ID>`, one space, and the H1 text, denoted by <TITLE>.
title: <ID> <TITLE>

# Pandoc uses `reference-section-title` as the heading for a generated
# bibliography when the Zettel contains Pandoc-style citations.
reference-section-title: References
---
# <TITLE>

The Zettel body begins after the H1 heading and ends immediately before the **SEE ALSO** section.
The H1 text is identical to the <TITLE> portion of `title` following `<ID> `, apart from trailing spaces. Titles may change; IDs do not.

## Definitions

### Element types

- **WikiLink:** An internal Markdown link of the form `[[ID]]` or `[[ID|display text]]`.
- **Hashtag:** Optional retrieval metadata, normally placed in **SEE ALSO**.
- **Pandoc citation:** A citation of the form `[@citeKey]`, resolved through a bibliography such as one exported from Zotero. 

### Alphabetic and numeric index notes

To create Index one or more words from the H1 heading by linking from **SEE ALSO** to the corresponding index note:

- `[[0000.0000.0ABC|0000.0000.0ABC A-B-C]]`
- `[[0000.0000.0DEF|0000.0000.0DEF D-E-F]]`
- `[[0000.0000.0GHI|0000.0000.0GHI G-H-I]]`
- `[[0000.0000.0JKL|0000.0000.0JKL J-K-L]]`
- `[[0000.0000.0MNO|0000.0000.0MNO M-N-O]]`
- `[[0000.0000.0PQR|0000.0000.0PQR P-Q-R]]`
- `[[0000.0000.0STU|0000.0000.0STU S-T-U]]`
- `[[0000.0000.0VWX|0000.0000.0VWX V-W-X]]`
- `[[0000.0000.00YZ|0000.0000.00YZ Y-Z]]`
- `[[0000.0000.0009|0000.0000.0009 0-9]]`

`[[0000.0000.0000|0000.0000.0000 INDEX]]` is the top-level index note.

The **SEE ALSO** section contains links other than those in the main body, including index links, related Zettels, continuations of a chain of thought, and optional hashtags.

### References

The **References** section follows **SEE ALSO**. It may be empty. When Pandoc citations are used, Pandoc can generate its contents.

## SEE ALSO

<!-- Add applicable  related Zettels, index links, and optional hashtags here, in the specified order. -->

## References
```

## License

This README and the Zettel Wiki are licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/legalcode), CC BY-SA 4.0, 2022-2026 F. Lengyel. Notes that merely instantiate the template need not credit me. Published copies or derivatives of the template remain subject to CC BY-SA 4.0.

The code is licensed under the GNU General Public License, version 3, 29 June 2007.

## References

- Ahrens, Sönke. 2017. _How to Take Smart Notes_. North Charleston, SC: CreateSpace.
- Doto, Bob. 2024. _A System for Writing_. Old New Traditions.
