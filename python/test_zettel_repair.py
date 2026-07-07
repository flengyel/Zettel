"""Tests for zettel_repair.py."""

from __future__ import annotations

import io
from pathlib import Path
import tempfile
import unittest

from zettel_repair import main, plan_repairs
from zettel_validate import ZettelValidator


REPAIRABLE_NOTE = """---
title: Repair202607060001 Repairable note
---
# Repairable note

Body.

## SEE ALSO

[[0000.0000.0PQR]] P-Q-R  
"""

BLOCKED_NOTE = """---
title: Blocked202607070001 Human title
---
# Different H1

Body.

## SEE ALSO

[[rf.2a.0.23.0320]] GNU Radio
"""

UNICODE_VALIDATION_NOTE = """---
title: Unicode202607070001 ASCII title
---
# 雪山 note

Body.

## SEE ALSO

[[0000.0000.0STU]] S-T-U  
"""

H1_COPIED_TITLE_NOTE = """---
id: H1Repair202607070001
title: H1Repair202607070001 Repair copied H1
reference-section-title: References
---
# H1Repair202607070001 Repair copied H1

Body.

## SEE ALSO

[[0000.0000.0PQR]] P-Q-R  

## References
"""

H1_COPIED_TITLE_WITH_ID_MISMATCH_NOTE = """---
id: Other202607070001
title: Other202607070001 Repair copied H1
reference-section-title: References
---
# Other202607070001 Repair copied H1

Body.

## SEE ALSO

[[0000.0000.0PQR]] P-Q-R  

## References
"""


class ZettelRepairTests(unittest.TestCase):
    def write_note(self, root: Path, name: str, text: str) -> Path:
        path = root / name
        path.write_text(text, encoding="utf-8")
        return path

    def assert_valid(self, text: str, path: Path) -> None:
        validator = ZettelValidator()
        self.assertTrue(validator.validate(text, fn=str(path), report=False), validator.issues)

    def test_dry_run_repairs_missing_fields_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_note(root, "Repair202607060001.md", REPAIRABLE_NOTE)

            plan = plan_repairs(path, path.read_text(encoding="utf-8"))
            self.assertEqual(
                [action.code for action in plan.actions],
                ["add_id", "add_reference_section_title", "add_references_section"],
            )
            self.assertFalse(plan.before.valid)
            self.assertTrue(plan.after.valid, plan.after.issues)
            self.assert_valid(plan.repaired_text, path)

            output = io.StringIO()
            status = main([str(path)], stdout=output, stderr=io.StringIO())

            self.assertEqual(status, 1)
            self.assertIn("would apply 3 repair(s)", output.getvalue())
            self.assertEqual(path.read_text(encoding="utf-8"), REPAIRABLE_NOTE)

    def test_write_repairs_missing_fields_when_plan_improves_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_note(root, "Repair202607060001.md", REPAIRABLE_NOTE)

            output = io.StringIO()
            status = main([str(path), "--write"], stdout=output, stderr=io.StringIO())

            self.assertEqual(status, 0)
            self.assertIn("applied 3 repair(s)", output.getvalue())

            repaired = path.read_text(encoding="utf-8")
            self.assertIn("id: Repair202607060001\n", repaired)
            self.assertIn("reference-section-title: References\n", repaired)
            self.assertIn("## References", repaired)
            self.assert_valid(repaired, path)

    def test_whitespace_filename_id_is_not_repaired(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_note(root, "Bad ID.md", REPAIRABLE_NOTE)

            output = io.StringIO()
            status = main([str(path)], stdout=output, stderr=io.StringIO())

            self.assertEqual(status, 1)
            self.assertIn("no safe repair", output.getvalue())
            self.assertEqual(path.read_text(encoding="utf-8"), REPAIRABLE_NOTE)

    def test_write_mode_does_not_write_when_repair_does_not_improve_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_note(root, "Blocked202607070001.md", BLOCKED_NOTE)

            output = io.StringIO()
            status = main([str(path), "--write"], stdout=output, stderr=io.StringIO())

            self.assertEqual(status, 1)
            self.assertEqual(path.read_text(encoding="utf-8"), BLOCKED_NOTE)
            self.assertIn("blocked 3 repair(s)", output.getvalue())
            self.assertIn("validation issues before=2, after=2", output.getvalue())


    def test_repairs_h1_that_copies_full_frontmatter_title(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_note(root, "H1Repair202607070001.md", H1_COPIED_TITLE_NOTE)

            plan = plan_repairs(path, path.read_text(encoding="utf-8"))
            self.assertEqual(
                [action.code for action in plan.actions],
                ["repair_h1_copied_frontmatter_title"],
            )
            self.assertFalse(plan.before.valid)
            self.assertTrue(plan.after.valid, plan.after.issues)
            self.assertIn("# Repair copied H1\n", plan.repaired_text)
            self.assertNotIn("# H1Repair202607070001 Repair copied H1", plan.repaired_text)

            output = io.StringIO()
            status = main([str(path), "--write"], stdout=output, stderr=io.StringIO())

            self.assertEqual(status, 0)
            repaired = path.read_text(encoding="utf-8")
            self.assertIn("# Repair copied H1\n", repaired)
            self.assertNotIn("# H1Repair202607070001 Repair copied H1", repaired)
            self.assertIn("applied 1 repair(s)", output.getvalue())

    def test_h1_repair_requires_filename_and_id_to_match(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_note(
                root,
                "Filename202607070001.md",
                H1_COPIED_TITLE_WITH_ID_MISMATCH_NOTE,
            )

            plan = plan_repairs(path, path.read_text(encoding="utf-8"))
            self.assertEqual(plan.actions, ())
            self.assertEqual(plan.repaired_text, H1_COPIED_TITLE_WITH_ID_MISMATCH_NOTE)

            output = io.StringIO()
            status = main([str(path), "--write"], stdout=output, stderr=io.StringIO())

            self.assertEqual(status, 1)
            self.assertEqual(path.read_text(encoding="utf-8"), H1_COPIED_TITLE_WITH_ID_MISMATCH_NOTE)
            self.assertIn("filename_id_mismatch", output.getvalue())
            self.assertIn("h1_mismatch", output.getvalue())

    def test_output_escapes_characters_unsupported_by_stream_encoding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_note(root, "Unicode202607070001.md", UNICODE_VALIDATION_NOTE)

            raw_output = io.BytesIO()
            output = io.TextIOWrapper(raw_output, encoding="cp1252", errors="strict")
            status = main([str(path), "--no-index-links"], stdout=output, stderr=io.StringIO())
            output.flush()

            rendered = raw_output.getvalue().decode("cp1252")
            self.assertEqual(status, 1)
            self.assertIn("remaining validation issue", rendered)
            self.assertIn("\\u96ea\\u5c71 note", rendered)


if __name__ == "__main__":
    unittest.main()
