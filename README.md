# Zettel

This repository contains a self-documenting Zettel template for use with a software implementation of the Zettelkasten Method. For software configuration notes, definitions of terms, and more examples, see the [Zettel Wiki](https://github.com/flengyel/Zettel/wiki). The Zettelkasten Method is documented online at [Introduction to the Zettelkasten Method](https://zettelkasten.de/posts/overview/) on the [Zettelkasten.de](https://zettelkasten.de) site and in the [Zettelkasten.de forum](https://forum.zettelkasten.de). If you find the terminology of literature notes and permanent notes vague or confusing, it's not your fault--see [From Fleeting Notes to Project Notes](https://github.com/flengyel/Zettel/wiki/From-Fleeting-Notes-to-Project-Notes). Recommended: [Tinderbox Meetup April 23, 2023 Video: On ZettelKasten with Sascha Fast from Zettelkasten.de](https://www.youtube.com/watch?v=I4TXkGjKpTo). Also, see [Note Taking Traditions](https://notemaking.substack.com/) by Chris Aldrich.

NOTE: As of October 2024 I have switched to Obsidian version 1.6.7 from Zettlr 3.2.2. Zettlr was too slow to work with on my Windows 11 system. See the [Zettel Wiki](https://github.com/flengyel/Zettel/wiki) for updated software configuration notes, which are under construction as I bring them up to date.

This README.md and the Zettek wiki are licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/legalcode). CC BY-SA 4.0 2022-2023 F Lengyel. You don't need to credit me if your notes instantiate the template. If you copy and publish this template or derive a template from this one and publish it, then CC BY-SA 4.0 applies.  

The code is licensed under the GNU GENERAL PUBLIC LICENSE, Version 3, 29 June 2007

```yaml
---
# Version: 2024.10.12.1
# This self-documenting Zettel template specifies the format of 
# a Zettel suitable for a digital Zettelkasten. The Zettel is
# organized as a Markdown file, beginning with this YAML 
# frontmatter followed by self-documenting Markdown sections 
# in the order of presentation. The YAML frontmatter contains
# commands to Zettlr, Pandoc, and Obsidian and includes, 
# at minimum, the following variables: `id:`. `title:` and 
# `reference-section-title:` 

id: ZTEMP.1.0.24.1012

# The value of the `id:` variable is a the unique, immutable ID of the Zettel.  
# Immutable, unique IDs may have different formats, according to personal preference. 
# Timestamps are a popular choice, followed by Folgezettel. 


title: "ZTEMP.1.0.24.0228 H1 header title - Zettel Template"

# The value of the `title:` variable is a quoted string, 
# consisting of a unique, immutable ID, in this case 
# `ZTEMP.1.0.24.0228`, followed by the H1 header title, in this case
# "Zettel Template"

reference-section-title: References

# The `reference-section-title:` variable is a command to Pandoc.
# If Zettel is exported through Pandoc and the Zettel body includes 
# Pandoc-style citations, the `reference-section-title:` variable 
# will cause Pandoc to add a References section with citations to the
# end of the exported document. 
---
```

```markdown
# H1 header title - Zettel Template
```
The Zettel body begins an H1 header. In my system, the H1 header is the value of the `title:` YAML variable minus the unique, immutable ID; however, this choice is optional.
Titles aren't immutable, unlike IDs. The Zettel body ends immediately before the **SEE ALSO** section below.

## Definitions

### Reference Element Types

- WikiLink: A markdown link within Zettels, enclosed in double brackets (e.g., [[UniqueID]] Zettel Title), used to interlink notes.
- Title-only WikiLink: A WikiLink followed immediately by the title, without extra annotations.
- Hashtags: For thematic categorization, typically used in the SEE ALSO section.
- Pandoc citations: References in the form [@citeKey] are linked to a citation database like Zotero.


### Types of Notes in Zettelkasten

- Single-focus Zettels: Focus on one main idea or topic.
- Structure Notes: Outline and connect Single-focus Zettels under broader themes; contain sections with annotated WikiLinks.
- Index Notes: Navigational tools marked by IDs starting with 0000.0000.0; annotated with their title only.

## Revised Zettel Construction Guidelines

ID and Title: Start with a unique ID and descriptive title for each Zettel.  Bob Doto writes that a note title "should be a declarative statement rather than a descriptor" (Doto 2024, 56).

### Main Body:

1. Single-focus Zettels: Focus on one main idea. Annotate WikiLinks when they add context, except for Index Note references. Links should be directly related to the central theme.
2. Structure Notes: Organize and link related Single-focus Zettels under thematic sections, starting each with an annotated WikiLink.
3. Index Notes: Used for navigation with a simple title annotation, listing relevant notes.

### SEE ALSO Section:

- Separates additional links from the main content to maintain focus.
- Contains title-only WikiLinks not directly tied to the Zettel's central theme, including:
- Index Note WikiLinks: For navigation and categorization. See the complete list of index note wikilinks below.
- Distantly Related Zettel Links: Provide additional context or suggest further research.
- Hashtags and Metadata: Aid in organizing and retrieving notes.

### References:

Lists external sources or additional reading. This section is optional if Pandoc citations are used, as Pandoc will generate it.

## SEE ALSO

[[0000.0000.0000]] INDEX  
[[0000.0000.0ABC]] A-B-C  
[[0000.0000.0DEF]] D-E-F  
[[0000.0000.0GHI]] G-H-I  
[[0000.0000.0JKL]] J-K-L  
[[0000.0000.0MNO]] M-N-O  
[[0000.0000.0PQR]] P-Q-R  
[[0000.0000.0STU]] S-T-U  
[[0000.0000.0VWX]] V-W-X  
[[0000.0000.00YZ]] Y-Z  
[[0000.0000.0009]] 0-9  

 #replace #these #hashtags  

## References

- Ahrens, Sönke. 2017. _How to Take Smart Notes_. North Charleston, SC: CreateSpace.
- Doto, Bob. 2024. _A System for Writing_. Old New Traditions.
