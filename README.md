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
# H1 header title - Zettel Template

```markdown
# H1 header title - Zettel Template
```
The Zettel body begins with the H1 header and ends immediately before the **SEE ALSO** section below.
. In my system, the H1 header is the value of the `title:` YAML variable minus the unique, immutable ID; however, this choice is optional.
Titles aren't immutable, unlike IDs.  Bob Doto writes that a note title "should be a declarative statement rather than a descriptor" (Doto 2024, 56).

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


---

## Guidelines for Maintaining a Digital Zettelkasten

1. **Edit Old Notes Before Importing Them**
   * Rewrite or edit old notes to match your understanding before adding them to your Zettelkasten.
   * There is no pressure to document everything; e.g., I only take notes on amateur radio if I plan to splurge on a rig, recall obscure commands, etc.

2. **Choose and Stick with a Consistent Note Format**
   * Establish a standard note format early to avoid reformatting notes later.
   * Update older entries to conform to this standardized format to ensure software compatibility with, e.g., Obsidian, The Archive, Zettlr, etc.

3. **Organize Projects and Tasks**
   * Pick one specific keyword or tag for project notes, such as "Log," "CLOG" (Bob Doto's abbreviation for "catalog" or "creative log"), or create your own  [@doto2024].
   * Track non-project tasks in periodic notes (daily, weekly, etc.).
   * Store periodic notes in a dedicated subdirectory to minimize clutter.

4. **Write Outside Your Zettelkasten**
   * Ahrens writes, "... there is no reason not to work as if nothing else counts than writing" [@ahrensHowTakeSmart2022, pp. 34-35].
      * Ahrens writes "work," not "live," though some fanatical writers live like this.
   * Ahrens' maxim has some consequences: 
      * Writing is more important than your Zettelkasten.
      * Draft your notes outside of the Zettelkasten system. This is not a hard-and-fast rule, though I tend to work like this.
      * Daily or other periodic notes and project notes are an exception.
      
5. **Rewrite and add notes as your understanding changes**
   * Expect to relearn your subject, which means revisiting, rewriting, or adding notes. See [Learn and relearn your field](https://terrytao.wordpress.com/career-advice/learn-and-relearn-your-field/).
   * Add a note if revising one note changes the existing note linking.

6. **Efficient Reference Management with Zotero and Better BibTex**
   * Use Zotero with the Better BibTex plugin to manage references and generate consistent citation keys.
   * Rename PDFs using these citation keys for organized and easily retrievable files.
   * Use the Zotero Connector extension to save web pages with a consistent citation format.
   * Create and rename PDFs of web pages using the Better BibTex citation key.
   * Attach the renamed PDFs to citations in Zotero.

7. **Physical Setup Considerations**
   * Use a smaller secondary monitor to work with your Zettelkasten.
   * A smaller monitor forces you to be brief.
   * Copying content requires effort, which acts as a natural filter.
   * The physical setup creates beneficial friction.
