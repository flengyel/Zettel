# Zettel

This repository contains a self-documenting Zettel template for use with a software implementation of the Zettelkasten Method. The Zettelkasten Method is documented online at [Introduction to the Zettelkasten Method](https://zettelkasten.de/posts/overview/) on the [Zettelkasten.de](https://zettelkasten.de) site and in the [Zettelkasten.de forum](https://forum.zettelkasten.de). Recommended: [Tinderbox Meetup April 23, 2023 Video: On ZettelKasten with Sascha Fast from Zettelkasten.de](https://www.youtube.com/watch?v=I4TXkGjKpTo). 

Licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/legalcode). CC BY-SA 4.0 2022-2023 F Lengyel 

Version 4.0 of the Zettel Template was a simplification by [ChatGPT-4](https://chat.openai.com) of Zettel Template 3.0, which follows Zettel Template 4.0 below.

# # ZKM.4c.0.23.0624 Zettel Template 4.0

[[[ZKID.1.0.22.0225](https://github.com/flengyel/Zettel/wiki/ID-regex-and-alphabetic-index)]] ID Format  
[[0000.0000.0STU]] S-T-U  
[[0000.0000.00YZ]] Y-Z  

 #zettelkasten-method #template #zettel-template

**Note:** This template serves as a guide for creating a Zettel using the Zettelkasten Method. It assumes a software-based implementation. Refer to [Zettelkasten.de](https://zettelkasten.de/posts/overview/) and [Zettelkasten.de forum](https://forum.zettelkasten.de) for detailed explanations of the method.

For software configuration notes, definitions of terms, and more examples, please look at the [Zettel Wiki](https://github.com/flengyel/Zettel/wiki).

## 1. Header

The header consists of four parts:

- **1.1 Optional YAML Frontmatter**: Commands to Zettlr and Pandoc. 
- **1.2 Level 1 (H1) Header**: Contains an immutable ID and a title.
- **1.3 Context Zettel IDs**: IDs of prior Zettels providing context.
- **1.4 Hashtags**: List of relevant keywords.

### 1.1 YAML Frontmatter (optional)

If there are Pandoc-style references in the Zettel body, add the following YAML front matter at the beginning:

```yaml
---
reference-section-title: References
---
```

### 1.2 H1 Header: Immutable ID and Title

Each Zettel should start with an H1 header:

```markdown
# immutableID title
```

The `immutableID` remains unchanged throughout the life of the Zettel, while the `title` can be updated as needed.

### 1.3 Context Zettel IDs

Provide a list of wiki links and titles of Zettels that relate to the current Zettel. For example:

```markdown
[[previousZettelID1]] Title1
[[previousZettelID2]] Title2  
[[previousZettelID3]] Title3
...
```

These IDs contextualize the current Zettel within the larger Zettelkasten.

### 1.4 Hashtags

Include relevant hashtags for the Zettel content:

```markdown
 #yourHashtag1 #yourHashtag2
```

Use specific hashtags that directly pertain to the content of the current Zettel.

## 2. Body

The body should focus on a single concept or idea. Include links to other Zettels or external resources where appropriate. Limit the length of each Zettel to a screenful of text for readability.

## 3. References

If you use Pandoc-style citations in your Zettel, a References section will be automatically created. For this to happen, include the YAML frontmatter mentioned in Section 1.1.

For example:

```markdown
## References
Ahrens, Sönke. 2017. _How to take smart notes: one simple technique to boost writing, learning and thinking: for students, academics and nonfiction book writers_. North Charleston, SC: CreateSpace.
```

---

The previous Zettel Template was simplified by ChatGPT-4, based on the template following.

---

# # ZKM.4.0.23.0609 Zettel template v3.0

[[ZKM.4.0.23.0504]] Zettel template v2.8  
[[ZKM.4a.0.23.0504]] Note on Zettel Template 2.8  
[[ZKID.1.0.22.0305]] ID Format  
[[0000.0000.0STU]] S-T-U  
[[0000.0000.00YZ]] Y-Z  

 #replace #these #hashtags  
  
- Filenames have the format `ID.md` in my implementation, where the ID format is defined in [[ZKID.1.0.22.0305]] ID Format

## 1. Header: in 3 + 1 parts

- An optional YAML frontmatter header with commands to Zettlr and Pandoc;
- a Level 1 (H1) header containing an immutable ID, referred to in this Zettel by `immutableID`, followed by a title, referred to in this Zettel by `title`;
- a list of IDs of prior Zettels providing context for `immutableID` (see 1.c.2 below); and,
- a list of keywords in #hashtag format.

### 1.a YAML frontmatter: optional

\---  
reference-section-title: References
\---

> If there are Pandoc-style references in the Zettel body, add the preceding YAML frontmatter header to the beginning of `immutableID`. References will appear as the last section of the document in Pandoc output.

### 1.b. An immutableID and title at heading level 1

\# `immutableID` `title`

> The value of `immutableID` doesn’t change, although `title` might  change. This syntax relies on enabling the Zettlr `Preferences → Display` setting “If present, use the first heading  level 1 instead of the filename.” This will display the IDs and  titles of Zettel markdown files in the Zettlr file manager pane.  Without this setting, the file manager will only show the Zettlr  filenames, which in my implementation are IDs.

### 1.c.1. CONTEXT Zettel IDs

A list of wikilinks of Zettel IDs such that for each `ID` in the list, `immutableID` either:

- continues `ID`;  
- comments on (or raises a question about) an aspect of `ID`; or,
- begins a new topic;  
- `ID` is the wikilink of an [alphabetic index note](https://github.com/flengyel/Zettel/wiki/ID-regex-and-alphabetic-index).

> The CONTEXT header section is adaptation of Niklas Luhmann’s Folgezettel ID system to digital Zettelkasten. Folgezettel IDs are  spanning tree coordinates for the graph of Zettels of a Zettelkasten.

### 1.c.2. Keywords in \#hashtag format

\#keyword \#example

> Paraphrasing Sascha Fast (Fast, 2018), hashtags should be as specific to `immutableID` as possible.

## 2. Body: the body should have a single focus

- Links \[\[to other Zettels\]\] and external links can go here.
- Footnotes and endnotes become links \[\[to other Zettels\]\] in the body.
- Link the ID `immutableID` of this Zettel within each separate footnote or endnote Zettel.

> Ahrens recommends limiting each Zettel to a screenful of text (a test that this Zettel fails). Arhens identifies five note types under three descriptive categories: fleeting, permanent, and project notes (Ahrens, 2017). See [From Fleeting Notes to Project Notes - zettelkasten.de](https://zettelkasten.de/posts/concepts-sohnke-ahrens-explained/) for the definition of these terms. Ahrens advises Zettel writers to read with pen and paper in hand, to take fleeting notes judiciously, and to reformulate their fleeting notes as Zettels in their own words before committing them as permanent notes to their Zettelkasten (Ahrens, 2017). Since Ahrens omits concrete examples of Zettels, this template attempts to address that omission. Zettels will require rewriting and reorganization before using them in long-form articles and projects—see the Three Dicta of (@Winebrenner 2022). Ahrens describes a bottom-up process for drawing upon the Zettelkasten in larger writing projects (Ahrens, 2017). Niklas Luhmann himself did not follow Ahrens' advice: Hans Georg-Moeller speculates that Luhmann's Zettelkasten contributed to an "unnecessarily convoluted, poorly structured, highly repetitive" writing style lacking a "clear narrative development" (Moeller 2012, chap. 2). For a clear guide to writing style, see Style: Lessons in Clarity and Grace (Williams & Bizup, 2017). Avoid The Elements of Style (Pullum 2010, 2014). Sascha Fast recommends writing for your future self (Fast, 2021). Cory Doctorow states that writing and research are distinct and recommends writing the placeholder "TK" inline instead of stopping to research (Doctorow, 2009).

## 3. References

> Pandoc style references in the body are resolved under the References section (without the "3."), provided the `immutableID` contains a Pandoc citation and the YAML header of 1.a. If the YAML header were present, the references section would appear as follows.

## References

Ahrens, Sönke. 2017. _How to take smart notes: one simple technique to boost writing, learning and thinking: for students, academics and nonfiction book writers_. North Charleston, SC: CreateSpace.

Doctorow, Cory. 2009. “Cory Doctorow: Writing in the Age of Distraction.” January 7, 2009. [http://www.locusmag.com/Features/2009/01/cory-doctorow-writing-in-age-of.html
Doctorow, Cory. 2009. “Cory Doctorow: Writing in the Age of Distraction.” January 7, 2009.](http://www.locusmag.com/Features/2009/01/cory-doctorow-writing-in-age-of.html)

Fast, Sascha. 2018. “The Difference Between Good and Bad Tags.” Blog. _Zettelkasten.de_ (blog). September 24, 2018. [https://zettelkasten.de/posts/object-tags-vs-topic-tags](https://zettelkasten.de/posts/object-tags-vs-topic-tags)

Fast, Sascha. 2021. “Write for Your Future Self.” July 29, 2021. [https://forum.zettelkasten.de/discussion/comment/12480/#Comment_12480](https://forum.zettelkasten.de/discussion/comment/12480/#Comment_12480)

Moeller, Hans-Georg. 2012. _The radical Luhmann_. New York: Columbia University Press.

Pullum, Geoffrey K. 2010. “The Land of the Free and _The Elements of Style_.” _English Today_ 26 (2): 34–44. [https://doi.org/10.1017/S0266078410000076](https://doi.org/10.1017/S0266078410000076)

———. 2014. “Fear and Loathing of the English Passive.” _Language & Communication_ 37 (July): 60–74. [https://doi.org/10.1016/j.langcom.2013.08.009](https://doi.org/10.1016/j.langcom.2013.08.009)

Williams, Joseph M., and Joseph Bizup. 2017. _Style: lessons in clarity and grace_. Twelfth edition. Always learning. Boston Columbus Indianapolis New York San Francisco Amsterdam Cape Town Dubai London Madrid Milan Munich Paris: Pearson.

Winebrenner, Caleb. 2022. “Field Report #4: I spent six months using a Zettelkasten to write my thesis. Here’s what I learned.” _Zettelkasten_ (blog). January 28, 2022. [https://zettelkasten.de/posts/field-report-4-what-i-learned-writing-thesis-with-zettelkasten/](https://zettelkasten.de/posts/field-report-4-what-i-learned-writing-thesis-with-zettelkasten/).
