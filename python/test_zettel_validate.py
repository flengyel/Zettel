from pathlib import Path
import tempfile
import unittest

from zettel_validate import (
    INDEX_NOTE_TITLES,
    ZettelValidator,
    index_inventory_issues,
    iter_markdown_files,
    main,
)


VALID_NOTE = """---
id: Tikz202504272354
title: Tikz202504272354 Tikz in Obsidian examples
reference-section-title: References
---
# Tikz in Obsidian examples

Body text.

## SEE ALSO

[[0000.0000.0STU|0000.0000.0STU S-T-U]]

## References
"""


class ZettelValidatorTests(unittest.TestCase):
    def validate(self, text=VALID_NOTE, fn="Tikz202504272354.md", **kwargs):
        validator = ZettelValidator(**kwargs)
        result = validator.validate(text, fn=fn, report=False)
        return validator, result

    def test_current_timestamp_id_passes(self):
        _, result = self.validate()
        self.assertTrue(result)

    def test_legacy_dotted_id_passes(self):
        old_id = "Philo.1a1.0.21.0503"
        text = VALID_NOTE.replace("Tikz202504272354", old_id)
        _, result = self.validate(text, f"{old_id}.md")
        self.assertTrue(result)

    def test_filename_must_equal_yaml_id(self):
        validator, result = self.validate(fn="wrong.md")
        self.assertFalse(result)
        self.assertIn(
            "filename_id_mismatch", {issue.code for issue in validator.issues}
        )

    def test_title_must_begin_with_id_and_one_space(self):
        text = VALID_NOTE.replace(
            "title: Tikz202504272354 Tikz in Obsidian examples",
            "title: Tikz202504272354  Tikz in Obsidian examples",
        )
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn("h1_mismatch", {issue.code for issue in validator.issues})

    def test_h1_must_match_title_remainder(self):
        text = VALID_NOTE.replace(
            "# Tikz in Obsidian examples", "# Different title", 1
        )
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn("h1_mismatch", {issue.code for issue in validator.issues})

    def test_trailing_h1_spaces_are_ignored(self):
        text = VALID_NOTE.replace(
            "# Tikz in Obsidian examples", "# Tikz in Obsidian examples   ", 1
        )
        _, result = self.validate(text)
        self.assertTrue(result)

    def test_missing_index_link_fails(self):
        text = VALID_NOTE.replace(
            "[[0000.0000.0STU|0000.0000.0STU S-T-U]]\n", ""
        )
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn("missing_index_link", {issue.code for issue in validator.issues})

    def test_wrong_index_bucket_fails(self):
        text = VALID_NOTE.replace("0000.0000.0STU", "0000.0000.0PQR")
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn("misindexed_title", {issue.code for issue in validator.issues})

    def test_any_h1_word_may_supply_bucket(self):
        # "examples" begins E, so DEF is also a valid choice.
        text = VALID_NOTE.replace("0000.0000.0STU", "0000.0000.0DEF")
        _, result = self.validate(text)
        self.assertTrue(result)

    def test_links_outside_see_also_do_not_count(self):
        text = VALID_NOTE.replace(
            "Body text.",
            "Body text. [[0000.0000.0STU]]",
        ).replace(
            "[[0000.0000.0STU|0000.0000.0STU S-T-U]]\n",
            "",
        )
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn("missing_index_link", {issue.code for issue in validator.issues})

    def test_index_notes_are_exempt_from_index_link_rule(self):
        note_id = "0000.0000.0ABC"
        text = f"""---
id: {note_id}
title: {note_id} A-B-C
reference-section-title: References
---
# A-B-C

## SEE ALSO

## References
"""
        _, result = self.validate(text, f"{note_id}.md")
        self.assertTrue(result)

    def test_index_note_title_is_fixed(self):
        note_id = "0000.0000.0ABC"
        text = f"""---
id: {note_id}
title: {note_id} Wrong
reference-section-title: References
---
# Wrong

## SEE ALSO

## References
"""
        validator, result = self.validate(text, f"{note_id}.md")
        self.assertFalse(result)
        self.assertIn(
            "index_title_mismatch", {issue.code for issue in validator.issues}
        )

    def test_no_index_links_option(self):
        text = VALID_NOTE.replace(
            "[[0000.0000.0STU|0000.0000.0STU S-T-U]]\n", ""
        )
        _, result = self.validate(text, check_index_links=False)
        self.assertTrue(result)

    def test_heading_in_code_fence_is_ignored(self):
        text = VALID_NOTE.replace(
            "## SEE ALSO\n\n[[0000.0000.0STU|0000.0000.0STU S-T-U]]\n",
            "```markdown\n## SEE ALSO\n[[0000.0000.0STU]]\n```\n",
        )
        validator, result = self.validate(text)
        self.assertFalse(result)
        self.assertIn("missing_see_also", {issue.code for issue in validator.issues})

    def test_root_only_directory_scan_is_default(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "A.md").write_text("x", encoding="utf-8")
            (root / "Projects").mkdir()
            (root / "Projects" / "B.md").write_text("x", encoding="utf-8")
            files = list(iter_markdown_files([root], [], recursive=False))
            self.assertEqual([path.name for path in files], ["A.md"])

    def test_recursive_scan_can_exclude_folders(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "A.md").write_text("x", encoding="utf-8")
            (root / "Templates").mkdir()
            (root / "Templates" / "B.md").write_text("x", encoding="utf-8")
            files = list(
                iter_markdown_files(
                    [root], ["Templates/**"], recursive=True
                )
            )
            self.assertEqual([path.name for path in files], ["A.md"])

    def test_index_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for note_id in INDEX_NOTE_TITLES:
                (root / f"{note_id}.md").write_text("", encoding="utf-8")
            self.assertEqual(index_inventory_issues(root), [])
            (root / "0000.0000.0ABC.md").unlink()
            self.assertEqual(len(index_inventory_issues(root)), 1)

    def test_cli_one_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Tikz202504272354.md"
            path.write_text(VALID_NOTE, encoding="utf-8")
            self.assertEqual(
                main([str(path), "--quiet", "--no-summary"]),
                0,
            )


if __name__ == "__main__":
    unittest.main()
