import re
import yaml

# Initialize stats dictionary
validation_stats = {
    'invalid_yaml_header': 0,
    'invalid_title_format': 0,
    'h1_mismatch': 0,
    'missing_wikilinks': 0,
    'missing_hashtags': 0,
    'filename_id_mismatch': 0
}

def zettel_validate(text, filename_without_extension=''):
    global validation_stats
    
    issues=[]
    
    # Extract YAML header
    yaml_header_match = re.search(r'---\n(.*?)\n---', text, re.DOTALL)
    if not yaml_header_match:
        issues.append(f"{filename_without_extension}: Invalid or missing YAML header")
        validation_stats['invalid_yaml_header'] += 1
    try:
        yaml_header = yaml_header_match.group(1)
    except  AttributeError:
        print('\n'.join(issues))
        return False
    
    try:
        header_dict = yaml.safe_load(yaml_header)
    except yaml.YAMLError:
        issues.append(f"{filename_without_extension}: YAML header parsing exception")
        validation_stats['invalid_yaml_header'] += 1
        print('\n'.join(issues))
        return False
        
    # Validate YAML header fields
    if 'title' not in header_dict or 'reference-section-title' not in header_dict:
        issues.append(f"{filename_without_extension}: YAML header missing title: or reference-section-title:")
        validation_stats['invalid_yaml_header'] += 1
        
    title = header_dict.get('title', '')
    ref_section_title = header_dict.get('reference-section-title', '')
       
    # Validate title
    title_match = re.fullmatch(r'((\w{1,4}\.){2,}\d\w{3}) (.+)', title)
    if not title_match:
        issues.append(f"{filename_without_extension}: Invalid title format")
        validation_stats['invalid_title_format'] += 1
    else:
        captured_id, _, captured_title = title_match.groups()
        
        # Verify that filename matches ID
        if filename_without_extension:
            if filename_without_extension != captured_id:
                # Add a new validation error type for filename mismatch
                issues.append(f"{filename_without_extension}: Filename ID mismatch")
                validation_stats['filename_id_mismatch'] += 1
           
    # Extract content after YAML header
    content = text[yaml_header_match.end():].strip()
    
    # Validate H1 header
    h1_header_match = re.match(r'# ' + re.escape(title) + r'\n', content)
    if not h1_header_match:
        issues.append(f"{filename_without_extension}: H1 header YAML ID mismatch")
        validation_stats['h1_mismatch'] += 1
    
    # Extract and validate wikilinks
    wikilinks = re.findall(r'\[\[(.*?)\]\]', content)
    if len(wikilinks) == 0:
        issues.append(f"{filename_without_extension}: Missing wikilinks")
        validation_stats['missing_wikilinks'] += 1
    
    # Extract and validate hashtags
    hashtags = re.findall(r' (#[\w]+)', content)
    if len(hashtags) == 0:
        issues.append(f"{filename_without_extension}: Missing or improperly indented hashtags")
        validation_stats['missing_hashtags'] += 1
    
    if len(issues) > 0:
        print('\n'.join(issues))
        return False
    return True

if __name__=="__main__":
    sample_text = '''---
title: Math.2.0.21.1220.2213 Matrix Determinant Lemma
reference-section-title: References
---
# Math.2.0.21.1220.2213 Matrix Determinant Lemma

[[Game.1a.0.21.0613]] The core of a cooperative game
[[Math.0000.0000]] Mathematics

 #matrices #linearalgebra'''

    result = zettel_validate(sample_text)
    print(f"Validation result: {result}")
    print(f"Validation stats: {validation_stats}")
