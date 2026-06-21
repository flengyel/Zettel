from pathlib import Path
import tempfile
import unittest

from zettel_validate import ZettelValidator, main


VALID_NOTE = """---
id: ZK202606211234
title: ZK202606211234 A title
reference-section-title: References
---
# A title

Body text. Links and hashtags are optional.

```markdown
## SEE ALSO
```

## SEE ALSO

## References
"""


class ZettelValidatorTests(unittest.TestCase):
    def validate(self, text=VALID_NOTE, fn="ZK202606211234.md", **kwargs):
        validator = ZettelValidator(**kwargs)
        result = validator.validate(text, fn=fn, report=False)
        return validator, result

    def test_valid_template_note(self):
        validator, result = self.validate()
        self.assertTrue(result)
        self.assertEqual(validator.issues, ())

    def test_strict_template_id_accepts_current_format(self):
        _, result = self.validate(require_template_id=True)
        self.assertTrue(result)

    def test_legacy_dotted_id_is_allowed_by_default(self):
        text = VALID_NOTE.replace("ZK202606211234", "Math.2.0.21.1220.2213")
        _, result = self.validate(text, "Math.2.0.21.1220.2213.md")
        self.assertTrue(result)

    def test_strict_template_id_rejects_legacy_id(self):
        text = VALID_NOTE.replace("ZK202606211234", "Math.2.0.21.1220.2213")
        validator, result = self.validate(
            text,
            "Math.2.0.21.1220.2213.md",
            require_template_id=True,
        )
        self.assertFalse(result)
        self.assertIn(
            "invalid_template_id", {issue.code for issue in validator.issues}
        )

    def test_links_and_hashtags_are_not_required(self):
        text = VALID_NOTE.replace(
            "Body text. Links and hashtags are optional.\n", ""
        )
        _, result = self.validate(text)
        self.assertTrue(result)

    def test_filename_must_match_id(self):
        validator, result = self.validate(fn="wrong.md")
        self.assertFalse(result)
        self.assertIn(
            "filename_id_mismatch", {issue.code for issue in validator.issues}
        )

    def test_title_must_begin_with_id(self):
        text = VALID_NOTE.replace(
            "title: ZK202606211234 A title",
            "title: A title",
        )
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn(
            "title_id_mismatch", {issue.code for issue in validator.issues}
        )

    def test_h1_must_match_human_title(self):
        text = VALID_NOTE.replace("# A title", "# A different title", 1)
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn("h1_mismatch", {issue.code for issue in validator.issues})

    def test_see_also_must_precede_references(self):
        text = VALID_NOTE.replace(
            "## SEE ALSO\n\n## References",
            "## References\n\n## SEE ALSO",
        )
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn("order_issue", {issue.code for issue in validator.issues})

    def test_heading_inside_code_fence_is_ignored(self):
        text = VALID_NOTE.replace(
            "\n## SEE ALSO\n\n## References\n", "\n## References\n"
        )
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn(
            "missing_see_also", {issue.code for issue in validator.issues}
        )

    def test_crlf_input(self):
        text = VALID_NOTE.replace("\n", "\r\n")
        _, result = self.validate(text)
        self.assertTrue(result)

    def test_duplicate_yaml_keys_are_rejected(self):
        text = VALID_NOTE.replace(
            "id: ZK202606211234",
            "id: ZK202606211234\nid: Other202606211234",
        )
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn("invalid_yaml", {issue.code for issue in validator.issues})

    def test_quoted_title_may_contain_colon(self):
        text = VALID_NOTE.replace(
            "title: ZK202606211234 A title",
            'title: "ZK202606211234 A title: with punctuation"',
        ).replace("# A title", "# A title: with punctuation", 1)
        _, result = self.validate(text)
        self.assertTrue(result)

    def test_unquoted_colon_is_reported_as_invalid_yaml(self):
        text = VALID_NOTE.replace(
            "title: ZK202606211234 A title",
            "title: ZK202606211234 A title: with punctuation",
        ).replace("# A title", "# A title: with punctuation", 1)
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn("invalid_yaml", {issue.code for issue in validator.issues})

    def test_cli_exit_status(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ZK202606211234.md"
            path.write_text(VALID_NOTE, encoding="utf-8")
            self.assertEqual(main([str(path), "--quiet", "--no-summary"]), 0)


if __name__ == "__main__":
    unittest.main()
