# Zettel

This repository contains a self-documenting Zettel template for use with a software implementation of the Zettelkasten Method. The Zettelkasten Method is documented online at [Introduction to the Zettelkasten Method](https://zettelkasten.de/posts/overview/) on the [Zettelkasten.de](https://zettelkasten.de) site and in the [Zettelkasten.de forum](https://forum.zettelkasten.de). Recommended: [Tinderbox Meetup April 23, 2023 Video: On ZettelKasten with Sascha Fast from Zettelkasten.de](https://www.youtube.com/watch?v=I4TXkGjKpTo). 

Licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/legalcode). CC BY-SA 4.0 2022-2023 F Lengyel 

# # ZKM.4c.0.23.0624 Zettel Template 4.0

[[ZKID.1.0.22.0305]] ID Format  
[[0000.0000.0STU]] S-T-U  
[[0000.0000.00YZ]] Y-Z  

 #zettelkasten-method #template #zettel-template

**Note:** This template serves as a guide for creating a Zettel using the Zettelkasten Method. It assumes a software-based implementation. Refer to [Zettelkasten.de](https://zettelkasten.de/posts/overview/) and [Zettelkasten.de forum](https://forum.zettelkasten.de) for detailed explanations of the method.

For software configuration notes, definitions of terms, and more examples, refer to the [Zettel Wiki](https://github.com/flengyel/Zettel/wiki).

License: [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/legalcode).

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

Provide a list of H1 headers (without the leading hash mark) of Zettels that relate to the current Zettel. For example:

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

If you use Pandoc-style citations in your Zettel, a References section will be automatically created. For this to happen, ensure you included the YAML frontmatter mentioned in Section 1.1.

For example:

```markdown
## References
Ahrens, Sönke. 2017. _How to take smart notes: one simple technique to boost writing, learning and thinking: for students, academics and nonfiction book writers_. North Charleston, SC: CreateSpace.
```
