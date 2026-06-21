# Zettel

This repository documents the conventions I use for a single digital Zettelkasten. This system here works with [Obsidian](https://obsidian.md) and Zotero, but may be adapted to other systems. For software configuration notes, definitions of terms, and more examples, see the [Zettel Wiki](https://github.com/flengyel/Zettel/wiki). The Zettelkasten Method is documented at [Introduction to the Zettelkasten Method](https://zettelkasten.de/posts/overview/) and in the [Zettelkasten.de forum](https://forum.zettelkasten.de). If the terminology of literature notes and permanent notes seems vague or confusing, see [From Fleeting Notes to Project Notes](https://github.com/flengyel/Zettel/wiki/From-Fleeting-Notes-to-Project-Notes). Also see Chris Aldrich's [Note Taking Traditions](https://notemaking.substack.com/).

As of October 2024, I use Obsidian rather than Zettlr. See the [Zettel Wiki](https://github.com/flengyel/Zettel/wiki) for configuration notes and [Guidelines for Maintaining a Digital Zettelkasten](https://github.com/flengyel/Zettel/wiki/Guidelines-for-Maintaining-a-Digital-Zettelkasten) for some of the rules I follow.

## Note identity and displayed title

A Zettel is stored in a Markdown file named:

```text
<ID>.md
```

Here and below, `<ID>` and `<H1>` are metavariables. The angle brackets do not appear in a filename, property value, or heading.

Each note begins with YAML front matter followed by an H1 heading:

```yaml
---
id: <ID>
title: <ID> <H1>
reference-section-title: References
---
# <H1>
```

The following invariants define the convention:

1. The filename without the `.md` extension is identical to the value of `id`.
2. The value of `title` consists of the ID, one space, and the H1 text.
3. The text following the ID in `title` is identical to the H1 text, apart from trailing spaces.
4. The ID is unique and immutable. The H1 and displayed title may change together.

The Obsidian **Front Matter Title** plugin displays the value of the `title` property in the File Explorer. The underlying filename remains the usually uninformative ID.

The Zettelkasten contains several generations of IDs. The current Obsidian template normally constructs an ID by concatenating an alphabetic keyword and a timestamp of the form `YYYYMMDDHHmm`. Older dotted IDs and the special index IDs below remain valid. ID validity therefore cannot be inferred from a single regular-expression pattern.

## Note structure

The body begins after the H1 heading and ends immediately before `## SEE ALSO`.

```markdown
# <H1>

<note body>

## SEE ALSO

<links and optional hashtags>

## References
```

`SEE ALSO` may contain:

- links to notes that continue or support a chain of thought;
- links to related notes;
- links to alphabetic or numeric index notes;
- optional hashtags or other retrieval metadata.

`References` follows `SEE ALSO`. Pandoc-style citations may be used in the body; `reference-section-title: References` tells Pandoc what to call the generated reference section.

## WikiLinks

The target of an internal WikiLink is normally the note ID, which is also the filename stem. Display text may be supplied as an alias. For example:

```markdown
[[Tikz202504272354|Tikz202504272354 Tikz in Obsidian examples]]
```

The target ID is structural; the choice of displayed link text is not.

## Alphabetic and numeric index

The following special notes sort at the beginning of Obsidian's File Explorer:

```text
0000.0000.0000 INDEX
0000.0000.0ABC A-B-C
0000.0000.0DEF D-E-F
0000.0000.0GHI G-H-I
0000.0000.0JKL J-K-L
0000.0000.0MNO M-N-O
0000.0000.0PQR P-Q-R
0000.0000.0STU S-T-U
0000.0000.0VWX V-W-X
0000.0000.00YZ Y-Z
0000.0000.0009 0-9
```

To index an ordinary note, select one or more words from its H1 heading and add a WikiLink in `SEE ALSO` to the corresponding alphabetic index note. Use `0000.0000.0009` for numeric items of interest.

The ordinary note points to the index note. Obsidian's backlinks then make the index self-modifying: notes appear in an index without requiring the index note itself to be edited for every addition.

Example:

```markdown
## SEE ALSO

[[0000.0000.0STU|0000.0000.0STU S-T-U]]
```

This link can index a note whose H1 contains a word such as `Tikz`.

## License

This README and the Zettel Wiki are licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/legalcode), CC BY-SA 4.0, 2022-2026 F. Lengyel. Notes that merely instantiate the template need not credit me. Published copies or derivatives of the template remain subject to CC BY-SA 4.0.

The code is licensed under the GNU General Public License, version 3, 29 June 2007.

## References

- Ahrens, Sönke. 2017. _How to Take Smart Notes_. North Charleston, SC: CreateSpace.
- Doto, Bob. 2024. _A System for Writing_. Old New Traditions.
