import re
import yaml


class ZettelValidator():
    # Initialize stats dictionary
    _stats = dict( )
    _stats['good_zettels'] = 0
    _stats['invalid_yaml_header'] = 0
    _stats['invalid_title_format'] = 0
    _stats['h1_mismatch'] = 0
    _stats['missing_wikilinks'] = 0
    _stats['missing_hashtags'] = 0
    _stats['filename_id_mismatch'] = 0
    _issues = [] 
    _fn = ''


    @property
    def statisics(self):
        return self._stats  

    @property
    def status(self: any) -> int:
        return len(self._issues)
    
    def append(self, key: str, issue: str) -> None:
        self._issues.append(f"{self._fn}: {issue}")
        self._stats[key] += 1
    
    def show_issues(self) -> None:
        print('\n'.join(self._issues))
        
        
    def __init__(self: any) -> None:
        self._issues = []
        self._fn = ''
        for key in self._stats:
            self._stats[key] = 0    
            
    def validate(self, text:str, fn:str='') -> bool:     
        # set the filename of the zettel
        self._fn = fn # set the ID of the zettel
        self._issues = [] # reset the issues list

        # Extract YAML header
        yaml_header_match = re.search(r'^---\n(.*)\n---\n', text, re.DOTALL)
        if not yaml_header_match:
            self.append('invalid_yaml_header', 'Invalid or missing YAML header')
        try:
            yaml_header = yaml_header_match.group(1)
        except AttributeError:
            self.show_issues()
            return False  # give up, invalid YAML header
        
        try:
            header_dict = yaml.safe_load(yaml_header) # parse YAML header
        except yaml.YAMLError:
            self.append('invalid_yaml_header', 'YAML header parsing exception')
            self.show_issues()
            return False  # give up, invalid YAML header 
        
        # Validate YAML header fields
        if 'title' not in header_dict or 'reference-section-title' not in header_dict:
            self.append('invalid_yaml_header', 'YAML header missing title: or reference-section-title:')
        
        title = header_dict.get('title', '')
        
        # Validate title
        title_match = re.fullmatch(r'((\w{1,5}\.)([\w]{1,4}\.)+\d\w{3}) (.+)', title)
        captured_id = ''
        if not title_match:
            self.append('invalid_title_format', 'Invalid title format')
        else:
            captured_id, _, _, _ = title_match.groups()
        
        # Verify that filename matches ID
        if fn and fn != captured_id:
        # Add a new validation error type for filename mismatch
            self.append('filename_id_mismatch', f'Filename ID {captured_id} mismatch')
                
        # Extract content after YAML header
        content = text[yaml_header_match.end():].strip()
    
        # Validate H1 header
        # ignore spaces
        h1_header_match = re.match(r'# ' + re.escape(title), content)
        if not h1_header_match:
            self.append('h1_mismatch', 'H1 header mismatch')
    
        # Extract and validate wikilinks
        wikilinks = re.findall(r'\[\[(.*?)\]\]', content)
        if len(wikilinks) == 0:
            self.append('missing_wikilinks', 'Missing wikilinks')
        
        # Extract and validate hashtags
        hashtags = re.findall(r' (#[\w]+)', content)
        if len(hashtags) == 0:
            self.append('missing_hashtags', 'Missing or non-indented hashtags')
          
        if self.status:
            print('\n'.join(self._issues))
            return False
        
        self._stats['good_zettels'] += 1
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

    print(sample_text)
    zv = ZettelValidator()
    
    sample_text_id = "Math.2.0.21.1220.2213"
    print(f"Validation result: {zv.validate(sample_text, sample_text_id)}") # The ID should be the filename
                                 
    print(f"Validation stats: {zv.statisics}")

    bad_text = '''---
title: Math.2.0.21.1220.4444 Matrix Determinant Lemma
reference-section-title: References
---
# Math.2.0.21.1220.4444 Matrix Determinant Lemma

[[Game.1a.0.21.0613]] The core of a cooperative game  
[[Math.0000.0000]] Mathematics  

 #matrices #linearalgebra'''

    print(bad_text)
    
    print(f"Validation result: {zv.validate(bad_text,sample_text_id)}")  # The ID should be the filename   
    print(f"Validation stats: {zv.statisics}")
