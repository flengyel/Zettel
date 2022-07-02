# Zettel


This repository contains a Zettel template and an abbreviated Zettel template for use with a software implementation of the Zettelkasten Method. The Zettelkasten Method is documented online at [Introduction to the Zettelkasten Method](https://zettelkasten.de/posts/overview/) on the [Zettelkasten.de](https://zettelkasten.de) site and in the [Zettelkasten.de forum](https://forum.zettelkasten.de). The templates are intended to be self-documenting. See the [Zettel wiki](https://github.com/flengyel/Zettel/wiki) for software configuration notes, definitions of terms, and additional info.




This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

---

# 20211119115201 Abbreviated Zettel template v2.5.1

CONTEXT [[20211118010533]] Zettel template v2.5

#replace #these

A Zettel has three parts: a header, a body, and a footer.  The header starts with an optional YAML header and includes a level 1 (H1) header with a timestamp ID and a title; a CONTEXT line that links to a Zettel that this Zettel continues or comments (or raises a question about) on an aspect of that Zettel (if there such a Zettel); and a list of hashtag keywords. This text is part of the body. Footnotes and endnotes become links within the body to other Zettels. That leaves the References section for the footer. The References section below can be omitted, generated with a reference manager such as Zotero and a YAML header [[20211118010533]] Zettel template v2.5; or added by hand, as below. 

-   This Zettel format applies to [Zettlr 2.3.0](https://zettlr.com) + Pandoc 2.18 + MikTeX 21.2-x64 + [Zotero 6.0.9](https://www.zotero.org/support/changelog) + [BetterBibTex 6.7.15](https://retorque.re/zotero-better-bibtex/) under Windows 10 and has not been used with other software.  
-   Filenames have the format `ID.md` in my implementation, where the format of `ID` is defined in [0.1.0.22.0305.1829 ID Format](https://github.com/flengyel/Zettel/wiki/0.1.0.22.0305.1829-ID-Format).
-   See [From Fleeting Notes to Project Notes - zettelkasten.de](https://zettelkasten.de/posts/concepts-sohnke-ahrens-explained/) for definitions of terms in (Ahrens 2017) 


# References

Ahrens, Sönke. 2017. _How to take smart notes: one simple technique to boost writing, learning and thinking: for students, academics and nonfiction book writers_. North Charleston, SC: CreateSpace.


---

# 202202040853 Zettel template v2.5.1

CONTEXT [[20211118010533]] Zettel template v2.5

 #replace #these #hashtags  


-   This Zettel format applies to Zettlr  versions 2.0.3 through 2.2.1 + Pandoc 2.16.1 + MikTeX 21.2-x64 + Zotero 5.0.96.3 + BetterBibTex  5.6.8 under Windows 10.   
-   Filenames have the format `ID.md` in my implementation, where the format of `ID` is defined in [0.1.0.22.0305.1829 ID Format](https://github.com/flengyel/Zettel/wiki/0.1.0.22.0305.1829-ID-Format).

## 1. Header: in 3 + 1 parts

-   An optional YAML frontmatter header with commands to Zettlr and Pandoc;
-   a Level 1 (H1) header containing an immutable ID, referred to in this Zettel by `immutableID`, followed by a title, referred to in this Zettel by `title`;
-   the keyword CONTEXT followed by a list of IDs of prior Zettels providing the immediate context for `immutableID` (see 1.c.2 below); and,
-   a list of keywords in #hashtag format.


### 1.a YAML frontmatter: optional

\---  
reference-section-title: References    
\---

> If there are Pandoc-style references in the Zettel body, add the preceding YAML frontmatter header to the beginning of `immutableID`. References will appear as the last section of the document in Pandoc output. 

###  1.b. An immutableID and title at heading level 1

\# `immutableID` `title`


> The value of `immutableID` doesn’t change, although `title` might  change. This syntax relies on enabling the Zettlr  `Preferences → Display` setting “If present, use the first heading  level 1 instead of the filename.” This will display the IDs and  titles of Zettel markdown files in the Zettlr file manager pane.  Without this setting, the file manager will only show the Zettlr  filenames, which in my implementation are IDs.

###   1.c.1. CONTEXT Zettel IDs

The keyword CONTEXT followed by a list of wikilinks of Zettel IDs such that for each `ID` in the list, `immutableID` either:

-   continues `ID`;  
-   comments on (or raises a question about) an aspect of `ID`; or,
-   begins a new topic and `ID` is the wikilink of an index.
-   No other Zettel ID belongs with CONTEXT.

The keyword CONTEXT applies to Zettel IDs satisfying the above conditions only. Zettels that might provide context for ```immutableID``` in other senses of the term 'context' are excluded. 

> The CONTEXT header section is adaptation of Niklas Luhmann’s Folgezettel ID system to digital Zettelkasten. Folgezettel IDs are  spanning tree coordinates for the graph of Zettels of a Zettelkasten (c.f. [[[20211030133016](https://forum.zettelkasten.de/discussion/comment/13422/#Comment_13422)]]  Folgezettel Formalized). In addition to specifying the location of a Zettel in a distinguished spanning tree, a Folgezettel ID indicates whether that Zettel: continues a  prior Zettel; comments on or raises a question about an aspect of a prior Zettel; or, begins a new topic. If the current Zettel with ID `immutableID` begins a new topic, link to an index with ID [[00000000000000]] (for example). The index Zettel serves as the default context that `immutableID` "continues."


### 1.c.2. Keywords in \#hashtag format

\#keyword \#example

> Paraphrasing Sascha Fast in (Fast 2018), hashtags should be as specific to `immutableID` as possible.

## 2. Body: a self-contained note

-   Links \[\[to other Zettels\]\] and external links can go here.
-   Footnotes and endnotes become links \[\[to other Zettels\]\] in the body.
-   In a footnote or endnote Zettel, the ID `immutableID` is added to CONTEXT.

> Ahrens recommends limiting each Zettel to a screenfull of text (a test that this Zettel fails). Arhens identifies three types of notes: _fleeting_, _permanent_ and _project notes_ (Ahrens 2017). See [From Fleeting Notes to Project Notes - zettelkasten.de](https://zettelkasten.de/posts/concepts-sohnke-ahrens-explained/) for the definition of these terms. Ahrens advises Zettel writers to read with pen and paper in hand, to take fleeting notes judiciously, and to reformulate their fleeting notes as Zettels in their own words before committing them as permanent notes to their Zettelkasten (Ahrens 2017).  Since Ahrens omits concrete examples of Zettels, this template attempts to address that omission. Zettels will require rewriting and reorganization prior to their use in long-form articles and projects&mdash;cf. the Three Dicta of (@Winebrenner 2022). Ahrens describes a bottom-up process for drawing upon the Zettelkasten in larger writing projects (Ahrens 2017). Apparently, Niklas Luhmann himself did not follow Ahrens' advice: Hans Georg-Moeller  speculates that Luhmann’s Zettelkasten contributed to an  “unnecessarily convoluted, poorly structured, highly repetitive” writing style lacking a “clear narrative development” (Moeller 2012, chap. 2). For a clear guide to writing style, see *Style: Lessons  in Clarity and Grace* (Williams and Bizup 2017). Avoid *The Elements of Style* (Pullum 2010, 2014). Sascha Fast recommends writing for your future self (Fast 2021). Cory Doctorow states that writing and  research are distinct, and recommends writing the placeholder "TK" inline instead of stopping to research (Doctorow 2009). 


## 3.  Footer: References


> Pandoc style references in the body are resolved under References, provided the `immutableID` contains a Pandoc citation and the YAML header of 1.a.

# References

Ahrens, Sönke. 2017. _How to take smart notes: one simple technique to boost writing, learning and thinking: for students, academics and nonfiction book writers_. North Charleston, SC: CreateSpace.

Doctorow, Cory. 2009. “Cory Doctorow: Writing in the Age of Distraction.” January 7, 2009. http://www.locusmag.com/Features/2009/01/cory-doctorow-writing-in-age-of.html

Fast, Sascha. 2018. “The Difference Between Good and Bad Tags.” Blog. *Zettelkasten* (blog). September 24, 2018. https://zettelkasten.de/posts/object-tags-vs-topic-tags

Fast, Sascha. 2021. “Write for Your Future Self.” July 29, 2021. https://forum.zettelkasten.de/discussion/comment/12480/#Comment_12480

Moeller, Hans-Georg. 2012. *The radical Luhmann*. New York: Columbia University Press.


Pullum, Geoffrey K. 2010. “The Land of the Free and *The Elements of Style*.” *English Today* 26 (2): 34–44. https://doi.org/10.1017/S0266078410000076

———. 2014. “Fear and Loathing of the English Passive.” *Language & Communication* 37 (July): 60–74. https://doi.org/10.1016/j.langcom.2013.08.009

Williams, Joseph M., and Joseph Bizup. 2017. *Style: lessons in clarity and grace*. Twelfth edition. Always learning. Boston Columbus Indianapolis New York San Francisco Amsterdam Cape Town Dubai London Madrid Milan Munich Paris: Pearson.**

Winebrenner, Caleb. 2022. “Field Report #4: I spent six months using a Zettelkasten to write my thesis. Here’s what I learned.” _Zettelkasten_ (blog). January 28, 2022. https://zettelkasten.de/posts/field-report-4-what-i-learned-writing-thesis-with-zettelkasten/.
