# Zettel

This repository contains a Zettel template for a software implementation of the Zettelkasten Method. The Zettelkasten Method is documented online at [Introduction to the Zettelkasten Method](https://zettelkasten.de/posts/overview/) on the [Zettelkasten.de](https://zettelkasten.de) site and in the [Zettelkasten.de forum](https://forum.zettelkasten.de). The template is intended to be self documenting. Further documentation and sample Zettels may be added to the repository in the future.

As of November 18, 2021, the template was developed for Zettlr 2.0.3 + Pandoc 2.16.1 + MikTeX 21.2-x64 + Zotero 5.0.96.3 + BetterBibTex  5.6.8 under Windows 10; it has not been tested with other software. 

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

For convenience, the evaluated Markdown template is provided within this README.md below. The unevaluated Markdown template 20211118010533.md is also provided within this repository.

---

# 20211118010533 Zettel template v2.1

 #zettel #zettelkasten #ruleofthrees #folgezettel #replace #these 

**CONTEXT** \[\[20211115172141\]\] Zettel format: revised

Revision v2.1 following remarks by (Simpson 2021), with additional citations.

-   This Zettel format only applies to Zettlr 2.0.3 + Pandoc 2.16.1 + MikTeX 21.2-x64 + Zotero 5.0.96.3 + BetterBibTex  5.6.8 under Windows 10 and has not been tested with other software.  
-   Filenames have the format `timestamp.md` in my implementation.

## 1. Header: in 3 + 1 parts

-   An optional YAML frontmatter header with commands to Zettlr and Pandoc;
-   a Level 1 (H1) header containing an immutable ID, referred to in this Zettel by `immutableID`, followed by a title, referred to in this Zettel by `title`;
-   a list of keywords in #hashtag format; and,
-   the keyword **CONTEXT** followed by a list of IDs of prior Zettels providing the immediate context for `immutableID`; see 1.c.2 below.

> The meta-variables ‘`immutableID`’ and ‘`title`’ are indexicals in the meta-language. The preceding sentence is in the  meta-meta-language since it quotes meta-linguistic terms. The  header of this Zettel is in the object language. For the utility  of keeping the object language, meta-language and  meta-meta-language separate, see (Chakraborty and Dutta 2019).

### 1.a YAML frontmatter: optional

\-\-\-  
reference-section-title: References<br /> 
\-\-\-

> If there are Pandoc-style references in the Zettel body, add the preceding YAML frontmatter header to the beginning of `immutableID`. References will appear as the last section of the document in Pandoc output. 

###  1.b. An immutableID and title at heading level 1

\# `immutableID` `title`

\[\[20210424174054\]\] Zettlr title format \#+ImmutableID+Title,

> The value of `immutableID` doesn’t change, although `title` might  change. This syntax relies on enabling the Zettlr  `Preferences → Display` setting “If present, use the first heading  level 1 instead of the filename.” This will display the IDs and  titles of Zettel markdown files in the Zettlr file manager pane.  Without this setting, the file manager will only show the Zettlr  filenames, which in my implementation are IDs.


### 1.c.1. Keywords in \#hashtag format

\#keyword \#example

> Paraphrasing Sascha Fast in (Fast 2018), hashtags should be as specific to `immutableID` as possible.

###   1.c.2. CONTEXT Zettel IDs

The keyword **CONTEXT** followed by a comma-separated list of  Zettel IDs such that for each `ID` in the list, `immutableID` either:

-   continues `ID`;  
-   comments on (or raises a question about) an aspect of `ID`; or,
-   is continued by `ID`.
-   No other Zettel ID belongs with **CONTEXT**,

The keyword **CONTEXT** applies to Zettel IDs satisfying the above conditions only,  including those that might provide context for ```immutableID``` in other senses of the term 'context'. 

> The **CONTEXT** header section is adaptation of Niklas Luhman’s Folgezettel ID system to digital Zettelkasten. Folgezettel IDs are  [spanning tree coordinates](https://forum.zettelkasten.de/discussion/comment/13422/#Comment_13422) for the graph of Zettels of a Zettelkasten. In addition to specifying the location of a Zettel in a distinguished spanning tree, a Folgezettel ID indicates whether that Zettel: continues a  prior Zettel; comments on or raises a question about an aspect of a prior Zettel; or, begins a new topic.This last case is not covered under **CONTEXT**. Under consideration: an additional keyword **PROTEXT** for IDs for which ```immutableID``` provides the **CONTEXT**. 


## 2. Body: an atomic note

-   Some authors recommend limiting the body to a single “unit of thought.”
-   Links \[\[to other Zettels\]\] and external links can go here.
-   Footnotes and endnotes become links \[\[to other Zettels\]\] in the body.
-   In a footnote or endnote Zettel, the ID `immutableID` is added to **CONTEXT**.

> To my knowledge, there is no standard “unit of thought” maintained at the [National Institute of Standards and Technology](https://www.nist.gov/); the [Bureau international des poids et mesures](https://www.bipm.org/en/home); or elsewhere.  What a “unit of thought” could mean is time-, context- and writer-dependent. Perhaps an appropriate “unit of thought” is the schema of  Cognitive Load Theory (CLT) (Plass, Moreno, and Brünken 2010).  Zettels that follow instructional design principles from CLT should: manage intrinsic cognitive load; stimulate germane cognitive load; and, minimize extraneous cognitive load (Clark,  Nguyen, and Sweller 2006). Ahrens encourages Zettel writers to use  their own words (Ahrens 2017). Arhens leaves no room for direct  quotation in Zettels, even in “Literature Notes.” Literature and  Permanent Notes considered harmful: see the comments of @ctietze,  @sfast, and @MartinBB in reply to (anonymous 2021). Hans Georg-Moeller  speculates that Luhmann’s Zettelkasten contributed to an  “unnecessarily convoluted, poorly structured, highly repetitive” writing style lacking a “clear narrative development” (Moeller 2012, chap. 2). An antidote to unclear writing is *Style: Lessons  in Clarity and Grace* (Williams and Bizup 2017). Avoid *The Elements of Style* (Pullum 2010, 2014). Sascha Fast recommends writing for your future self (Fast 2021). Cory Doctorow maintains that writing and  research are distinct, and recommends writing the placeholder TK inline instead of stopping to research (Doctorow 2009). At this  point, Zettel writing could use a checklist (Gawande 2010).


## 3.  Footer: References

\[\[20210803113219\]\] Zotero: citing BetterBibTeX references in Zettlr

> Pandoc style references in the body are resolved under References, provided the `immutableID` contains a Pandoc citation and the YAML header of 1.a.

# References

Ahrens, Sönke. 2017. *How to take smart notes: one simple technique to boost writing, learning and thinking - for students, academics and nonfiction book writers*. https://www.overdrive.com/search?q=B41A3269-BC2A-4497-8C71-0A3F1FA3C694.

anonymous. 2021. “Literature Notes, Where Do They Go Once They Become Permanent Notes?” *Zettelkasten Forum* (blog). March 26, 2021. https://forum.zettelkasten.de/discussion/1749/literature-notes-where-do-they-go-once-they-become-permanent-notes

Chakraborty, Mihir K., and Soma Dutta. 2019. *Theory of graded consequence: a general framework for logics of uncertainty*. Logic in Asia: Studia Logica Library. Singapore: Springer.

Clark, Ruth Colvin, Frank Nguyen, and John Sweller. 2006. *Efficiency in learning: evidence-based guidelines to manage cognitive load*. Essential resources for training and HR professionals. San Francisco, CA: Pfeiffer, a Wiley imprint.

Doctorow, Cory. 2009. “Cory Doctorow: Writing in the Age of Distraction.” January 7, 2009. http://www.locusmag.com/Features/2009/01/cory-doctorow-writing-in-age-of.html

Fast, Sascha. 2018. “The Difference Between Good and Bad Tags.” Blog. *Zettelkasten* (blog). September 24, 2018. https://zettelkasten.de/posts/object-tags-vs-topic-tags

Fast, Sascha. 2021. “Write for Your Future Self.” July 29, 2021. https://forum.zettelkasten.de/discussion/comment/12480/#Comment_12480

Gawande, Atul. 2010. *The checklist manifesto: how to get things right*. New York, N.Y: Metropolitan Books.

Moeller, Hans-Georg. 2012. *The radical Luhmann*. New York: Columbia University Press.

Plass, Jan L., Roxana Moreno, and Roland Brünken, eds. 2010. *Cognitive load theory*. 1. publ. Cambridge: Cambridge University Press.

Pullum, Geoffrey K. 2010. “The Land of the Free and *The Elements of Style*.” *English Today* 26 (2): 34–44. https://doi.org/10.1017/S0266078410000076

———. 2014. “Fear and Loathing of the English Passive.” *Language & Communication* 37 (July): 60–74. https://doi.org/10.1016/j.langcom.2013.08.009

Simpson, Will. 2021. “Comment 13603 on Zettel Format.” Blog. *Zettelkasten Forum* (blog). November 15, 2021. https://forum.zettelkasten.de/discussion/comment/13603/#Comment_13603

Williams, Joseph M., and Joseph Bizup. 2017. *Style: lessons in clarity and grace*. Twelfth edition. Always learning. Boston Columbus Indianapolis New York San Francisco Amsterdam Cape Town Dubai London Madrid Milan Munich Paris: Pearson.
