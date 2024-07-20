import re 
import yaml # type: ignore

class ZettelValidator:
    def __init__(self):
        self._issues = []
        self._fn = ''
        self._stats = {
            'good_zettels': 0,
            'invalid_yaml_header': 0,
            'invalid_title_format': 0,
            'h1_mismatch': 0,
            'missing_see_also': 0,
            'missing_wikilinks': 0,
            'missing_hashtags': 0,
            'filename_id_mismatch': 0,
            'order_issue': 0,
        }
        # Precompile regular expressions
        self._yaml_header_regex = re.compile(r'^---\n(.*)\n---\n', re.DOTALL)
        self._title_regex = re.compile(r'((\w{1,5}\d{13,})|((\w{1,5}\.)(\w{1,4}\.)+\w{4})) (.+)')
        self._see_also_regex = re.compile(r'## SEE ALSO')
        self._wikilink_regex = re.compile(r'\[\[(.*?)\]\]')
        self._hashtag_regex = re.compile(r' (#[\w]+)')

    @property
    def statistics(self) -> dict:
        return self._stats  

    @property
    def status(self) -> int:
        return len(self._issues)
    
    def append_issue(self, key: str, issue: str) -> None:
        self._issues.append(f"{self._fn}: {issue}")
        self._stats[key] += 1
    
    def show_issues(self) -> None:
        print('\n'.join(self._issues))
        
    def validate_yaml_header(self, text: str) -> bool:
        yaml_header_match = self._yaml_header_regex.search(text)
        if not yaml_header_match:
            self.append_issue('invalid_yaml_header', 'Invalid or missing YAML header')
            return False
        yaml_header = yaml_header_match.group(1)
        try:
            header_dict = yaml.safe_load(yaml_header)  # parse YAML header
        except yaml.YAMLError:
            self.append_issue('invalid_yaml_header', 'YAML header parsing exception')
            return False  # give up, invalid YAML header
        if 'title' not in header_dict or 'reference-section-title' not in header_dict:
            self.append_issue('invalid_yaml_header', 'YAML header missing title or reference-section-title')
            return False
        self.title = header_dict.get('title', '')
        return True

    def validate_title_format(self) -> bool:
        title_match = self._title_regex.fullmatch(self.title)
        if not title_match:
            self.append_issue('invalid_title_format', 'Invalid title format')
            return False
        self.captured_id = title_match.group(1)
        return True

    def validate_filename_id_mismatch(self, fn: str) -> bool:
        if fn and fn != self.captured_id:
            self.append_issue('filename_id_mismatch', f'Filename ID {self.captured_id} mismatch')
            return False
        return True

    def validate_content(self, text: str, yaml_header_end: int) -> bool:
        content = text[yaml_header_end:].strip()
        sections = ['h1', 'see_also', 'wikilinks', 'hashtags']
        section_order = []
        
        h1_header_match = re.match(r'# ' + re.escape(self.title), content)
        if h1_header_match:
            section_order.append('h1')
        else:
            self.append_issue('h1_mismatch', 'H1 header mismatch')

        see_also_match = self._see_also_regex.search(content)
        if see_also_match:
            section_order.append('see_also')
        else:
            self.append_issue('missing_see_also', "Missing SEE ALSO subsection")

        wikilinks_match = self._wikilink_regex.search(content)
        if wikilinks_match:
            section_order.append('wikilinks')
        else:
            self.append_issue('missing_wikilinks', 'Missing wikilinks')

        hashtags_match = self._hashtag_regex.search(content)
        if hashtags_match:
            section_order.append('hashtags')
        else:
            self.append_issue('missing_hashtags', 'Missing or non-indented hashtags')

        if section_order != sections:
            self.append_issue('order_issue', 'Sections are not in the required order')

        return not self.status

    def validate(self, text: str, fn: str = '') -> bool:
        self._fn = fn
        self._issues = []
        valid_yaml = self.validate_yaml_header(text)
        valid_title = self.validate_title_format()
        valid_filename = self.validate_filename_id_mismatch(fn)
        yaml_header_match = self._yaml_header_regex.search(text)
        if yaml_header_match:
            valid_content = self.validate_content(text, yaml_header_match.end())
        else:
            valid_content = False

        if valid_yaml and valid_title and valid_filename and valid_content:
            self._stats['good_zettels'] += 1

        self.show_issues()
        return self.status == 0

# Comment out the execution part to prevent running in this environment
if __name__ == "__main__":
    sample_text = '''---
title: Math.2.0.21.1220.2213 Matrix Determinant Lemma
reference-section-title: References
---
# Math.2.0.21.1220.2213 Matrix Determinant Lemma    

Some text.

## SEE ALSO

[[Game.1a.0.21.0613]] The core of a cooperative game  
[[Math.0000.0000]] Mathematics  

 #matrices #linearalgebra'''

#    print(sample_text)
    
    sample_text_id = "Math.2.0.21.1220.2213"

    zv = ZettelValidator()
#    print(f"Validation result: {zv.validate(sample_text, sample_text_id)}")  # The ID should be the filename
#    print(f"Validation stats: {zv.statistics}")

    bad_text = '''---
title: Math.2.0.21.1220.4444 Matrix Determinant Lemma
reference-section-title: References
---
# Math.2.0.21.1220.4444 Matrix Determinant Lemma

More text.

[[Game.1a.0.21.0613]] The core of a cooperative game  
[[Math.0000.0000]] Mathematics  

 #matrices #linearalgebra'''

    print(bad_text)

    print(f"Validation result: {zv.validate(bad_text, sample_text_id)}")  # The ID should be the filename   
    print(f"Validation stats: {zv.statistics}")
