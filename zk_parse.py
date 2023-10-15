import re
import yaml

def zettel_validate(text):
    # Extract YAML header
    yaml_header_match = re.search(r'---\n(.*?)\n---', text, re.DOTALL)
    if not yaml_header_match:
        return "No YAML header found."
    
    yaml_header = yaml_header_match.group(1)
    header_dict = yaml.safe_load(yaml_header)
    
    # Validate YAML header fields
    if 'title' not in header_dict or 'reference-section-title' not in header_dict:
        return "Invalid YAML header."
    
    title = header_dict['title']
    ref_section_title = header_dict['reference-section-title']
    
    # Validate title
    title_match = re.fullmatch(r'(\w{1,4}\.){2,}\d\w{3} .+', title)
    if not title_match:
        return "Invalid title format."
    
    # Extract content after YAML header
    content = text[yaml_header_match.end():].strip()
    
    # Validate H1 header
    h1_header_match = re.match(r'# ' + re.escape(title) + r'\n', content)
    if not h1_header_match:
        return "H1 header doesn't match title."
    
    # Extract and validate wikilinks
    wikilinks = re.findall(r'\[\[(.*?)\]\]', content)
    if len(wikilinks) == 0:
        return "No wikilinks found."
    
    # Extract and validate hashtags
    hashtags = re.findall(r' (#[\w]+)', content)
    if len(hashtags) == 0:
        return "No hashtags found."
    
    return {
        "header": header_dict,
        "title": title,
        "ref_section_title": ref_section_title,
        "wikilinks": wikilinks,
        "hashtags": hashtags
    }

sample_text = '''---
title: Math.2.0.21.1220.2213 Matrix Determinant Lemma
reference-section-title: References
---
# Math.2.0.21.1220.2213 Matrix Determinant Lemma

[[Game.1a.0.21.0613]] The core of a cooperative game
[[Math.0000.0000]] Mathematics

 #matrices #linearalgebra'''

result = zettel_validate(sample_text)
print(result)
