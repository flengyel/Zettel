# Zettel

This repository contains a self-documenting Zettel template for use with a software implementation of the Zettelkasten Method. For software configuration notes, definitions of terms, and more examples, see the [Zettel Wiki](https://github.com/flengyel/Zettel/wiki). The Zettelkasten Method is documented online at [Introduction to the Zettelkasten Method](https://zettelkasten.de/posts/overview/) on the [Zettelkasten.de](https://zettelkasten.de) site and in the [Zettelkasten.de forum](https://forum.zettelkasten.de). If you find the terminology of literature notes and permanent notes vague or confusing, it's not your fault--see [From Fleeting Notes to Project Notes](https://github.com/flengyel/Zettel/wiki/From-Fleeting-Notes-to-Project-Notes). Recommended: [Tinderbox Meetup April 23, 2023 Video: On ZettelKasten with Sascha Fast from Zettelkasten.de](https://www.youtube.com/watch?v=I4TXkGjKpTo). Also, see [Note Taking Traditions](https://notemaking.substack.com/) by Chris Aldrich.

This README.md and the Zettek wiki are licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/legalcode). CC BY-SA 4.0 2022-2023 F Lengyel. You don't need to credit me if your notes instantiate the template. If you copy and publish this template or derive a template from this one and publish it, then CC BY-SA 4.0 applies.  

The code is licensed under the GNU GENERAL PUBLIC LICENSE, Version 3, 29 June 2007

```yaml
---
# Version: 2024.02.28.1
# This self-documenting Zettel template specifies the format of 
# a Zettel suitable for a digital Zettelkasten. The Zettel is
# organized as a Markdown file, beginning with this YAML 
# frontmatter followed by self-documenting Markdown sections 
# in the order of presentation. The YAML frontmatter contains
# commands to Zettlr, Pandoc, and Obsidian and includes, 
# at minimum, the following variables: `title:` and 
# `reference-section-title:` 

title: "ZTEMP.1.0.24.0228 Zettel Template"

# The value of the `title:` variable is a quoted string, 
# consisting of a unique, immutable ID, in this case 
# `ZTEMP.1.0.24.0228`, followed by the Zettel title, in this case
# "Zettel Template" Immutable, unique IDs may have 
# different formats, according to personal preference. 
# Timestamps are a popular choice, followed by Folgezettel. 

reference-section-title: References

# The `reference-section-title:` variable is a command to Pandoc.
# If Zettel is exported through Pandoc and the Zettel body includes 
# Pandoc-style citations, the `reference-section-title:` variable 
# will cause Pandoc to add a References section with citations to the
# end of the exported document. 
---
```

# ZTEMP.1.0.24.0228 Zettel Template

The Zettel body begins an H1 header. In my system, the H1 header duplicates the immutable, unique ID and title with the following syntax; however, this choice is optional.
```markdown
# immutableID title
```
Titles aren't immutable, unlike IDs. The Zettel body ends immediately before the **SEE ALSO** section below.

## Customization notes

_This section guides personalizing your Zettel template. Adjust these elements to suit your note-taking preferences and workflow. For example, while this template places the immutable ID to the left of the title, some users prefer it to the right._

## Definitions

### Reference Element Types

- **WikiLink**: A markdown link used within Zettels to interlink them within the Zettelkasten system. It is enclosed in double square brackets and typically includes a unique identifier followed by the title of the linked Zettel.

- **Title-only WikiLink**: This format includes the WikiLink followed immediately by the title of the linked Zettel without additional annotations or explanations, adhering strictly to the format: `[[UniqueID]] Zettel Title`.
  
- **Hashtags**: Hashtags are for thematic categorization and quick reference within your Zettelkasten. Hashtags typically occur in the SEE ALSO section of a Zettel.

- **Pandoc citations**: Pandoc citations have the form `[@citeKey],` where `citeKey` is a citation Key for a citation maintained within a digital references management system such as Zotero or a manually created and maintained reference database.

### Types of Notes in Zettelkasten

1. **Single-focus Zettels**: Focus on one main idea or topic for clarity and precision. Single-focus Zettels form the core of the Zettelkasten.

2. **Structure Notes**: Outline and connect Single-focus Zettels under broader themes. They contain sections with annotated WikiLinks to individual Zettels.

3. **Index Notes**: Serve as navigational tools within the Zettelkasten, marked by IDs starting with `0000.0000.0` and typically annotated with their title only.

## More on customization

_The list of title-only WikiLinks in the SEE ALSO section is just a starting point. Feel free to modify these links or hashtags to organize your notes better._

## Revised Zettel Construction Guidelines

1. **ID and Title**:
   - Start with a unique ID and clear title for each Zettel to ensure clarity and retrievability.

2. **Main Body**:
   - Prioritize writing Zettels with the author's future self in mind, emphasizing clarity and utility for the author rather than a general reader.
   - **Single-focus Zettels**: Maintain a strict focus on one main idea or topic, crafting content for future clarity and utility. Annotate WikiLinks where they contribute to the topic's context, except for Index Note references. Links within the main body of a Single-focus Zettel should be directly related to the Zettel's central theme or idea and provide immediate, contextual support by offering additional information, evidence, or related viewpoints directly relevant to the Zettel's focus.
   - **Structure Notes**: Organize and link related Single-focus Zettels under thematic sections, starting each section with a relevant annotated WikiLink.
   - **Index Notes**: These are used for navigation with a simple title annotation, listing relevant Single-focus or Structure Notes for easy access.

3. **SEE ALSO Section**:
   - The SEE ALSO section serves as a gateway for expanded exploration and understanding, offering the reader pathways to discover related concepts and themes that might not be central to Zettel's current focus but are valuable for a broader understanding or future research.
   - The separation between the Main Body and the SEE ALSO section helps maintain the focus and clarity of the main content while still providing avenues for further exploration and connectivity within the Zettelkasten.
   - The SEE ALSO section should contain title-only WikiLinks that are not directly tied to the central theme of the Zettel but are still relevant to the broader thematic landscape of the note, including:
     - **Index Note WikiLinks**: Title-only WikiLinks to Index Notes that help with navigation and alphanumeric categorization but are not directly related to the Zettel's main content.
     - **Distantly Related Zettel Links**: Title-only WikiLinks to Zettels that provide additional context and support for the ideas presented or suggest further research but are not essential to understanding the primary focus of the current Zettel.
     - **Hashtags and Metadata**: The SEE ALSO can also include relevant hashtags and metadata that aid in organizing and retrieving Zettels within the Zettelkasten system.

4. **References**:
   - List external sources or additional reading materials to support content validity and facilitate further exploration.

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

- Ahrens, Sönke. 2017. _How to take smart notes_. North Charleston, SC: CreateSpace.
