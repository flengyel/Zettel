# Zettel

This repository documents the conventions I use for a single digital Zettelkasten. This system here works with [Obsidian](https://obsidian.md) and Zotero, but 
may be adapted to other systems. For software configuration notes, definitions of terms, and more examples, see the [Zettel Wiki](https://github.com/flengyel/Zettel/wiki). 
The Zettelkasten Method is documented at [Introduction to the Zettelkasten Method](https://zettelkasten.de/posts/overview/) and in the [Zettelkasten.de forum](https://forum.zettelkasten.de). If the terminology of literature notes and permanent notes seems vague or confusing, see [From Fleeting Notes to Project Notes](https://github.com/flengyel/Zettel/wiki/From-Fleeting-Notes-to-Project-Notes). Also see Chris Aldrich's [Note Taking Traditions](https://notemaking.substack.com/).

As of October 2024, I stopped using Zettlr and began using Obsidian. See the [Zettel Wiki](https://github.com/flengyel/Zettel/wiki) for configuration notes and [Guidelines for Maintaining a Digital Zettelkasten](https://github.com/flengyel/Zettel/wiki/Guidelines-for-Maintaining-a-Digital-Zettelkasten) for some of the rules I follow.

## Self-documenting Zettel template

The following self-documenting note specification includes explanatory definitions and index documentation. 
Your notes will use only YAML front matter, the H1 header, the `## SEE ALSO`, and `## References` sections, with your own content. 

Replace the metavariables `<ID>`, and `<TITLE>`; the angle brackets do not appear in a completed Zettel.  
The metabvariable `<ID>` is the unique, immutable ID of the Zettel and is identical to the filename without 
the `.md` extension. We leave the format of `<ID>` unspecified except for uniqueness, immutability, and operating system 
compatibility, with the exception of the reserved `<ID>` values below. 

In our system, we use a keyword followed by a timestamp, but our ID formats have changed over time. 

### YAML Front Matter

Each note begins with YAML front matter beginning on the first line of the document and ending with lines 
containing three consecutive dashes (`---`), as shown immediately below. The value of the `id:` property 
is `<ID>`. The value of the `title:` variable consists of `<ID>`, one space, and `<TITLE>`.  
The `reference-section-title:` property is used by Pandoc 
to generate bibliography when the Zettel contains Pandoc-style citations. The value of the 
`reference-section-title:` property is `References`, as shown below.

```markdown
---
id: <ID>
title: <ID> <TITLE>
reference-section-title: References
---
# <TITLE>

The Zettel body begins after the H1 heading and ends immediately before the **SEE ALSO** section below.
The H1 text is identical to the <TITLE> portion of `title` following `<ID> `, apart from trailing spaces.
Titles may change; IDs do not.

## Definitions

### Element types

- **WikiLink:** An internal Markdown link of the form `[[ID]]` or `[[ID|display text]]`.
- **Hashtag:** Optional retrieval metadata, normally placed in **SEE ALSO**.
- **Pandoc citation:** A citation of the form `[@citeKey]`, resolved through a bibliography  
such as one exported from Zotero. 

### Alphabetic and numeric index notes

The following `<ID>` and `<TITLE>` values are reserved and are used to create an
automatic Zettel index through Obsidian's backlink mechanism. The IDs were chosen to
appear at the begining of the Obsidan File Explorer panel. For each `<ID> <TITLE>`
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

No other `<ID> <TITLE>` combination is an index note.

Under the `## SEE ALSO` section of a note, index one or more words from the H1 heading by adding
the corresponding index Wikilink. For example, this Zettel template has the WikiLink
`[[0000.0000.00YZ]]` under the `## SEE ALSO` section. The `## SEE ALSO` subsection may include
WIkiLinks of related notes other than those appearing in the main body, one or more alphanumeric
index links, and optional hashtags. 

The `## References` section is optional. Here we have included two references on Zettelkasten.

## SEE ALSO

[[0000.0000.00YZ]]

 #optional #hashtag

## References
- Ahrens, Sönke. 2017. _How to Take Smart Notes_. North Charleston, SC: CreateSpace.
- Doto, Bob. 2024. _A System for Writing_. Old New Traditions.
```

## License

This README and the Zettel Wiki are licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/legalcode), CC BY-SA 4.0, 2022-2026 F. Lengyel. Notes that merely instantiate the template need not credit me. Published copies or derivatives of the template remain subject to CC BY-SA 4.0.

The code is licensed under the GNU General Public License, version 3, 29 June 2007.


