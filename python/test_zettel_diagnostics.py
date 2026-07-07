from __future__ import annotations

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from zettel_diagnostics import (
    FILE_DIAGNOSTICS_FILE,
    ISSUE_COUNTS_FILE,
    ISSUES_FILE,
    SUMMARY_FILE,
    WORD_COUNT_BINS_FILE,
    collect_diagnostics,
    count_words,
    main,
    output_directory_is_inside_supplied_directory,
    word_count_bins,
)


VALID_NOTE = """---
id: Note1
title: Note1 Alpha note
reference-section-title: References
---
# Alpha note

Some body text.

## SEE ALSO

[[0000.0000.0ABC]] INDEX

## References
"""

INVALID_NOTE = """---
id: Note2
title: Note2 Beta note
reference-section-title: References
---
# Beta note

Some body text.

## References
"""


class ZettelDiagnosticsTests(unittest.TestCase):
    def test_count_words_uses_whitespace_delimited_tokens(self) -> None:
        self.assertEqual(count_words("one two\nthree"), 3)
        self.assertEqual(count_words(""), 0)

    def test_word_count_bins_are_deterministic(self) -> None:
        bins = word_count_bins([0, 1, 49, 50, 999, 1000], bin_width=50, overflow_at=100)
        self.assertEqual(bins, [("0-49", 3), ("50-99", 1), ("100+", 2)])

    def test_collects_issue_counts_and_word_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Note1.md").write_text(VALID_NOTE, encoding="utf-8")
            (root / "Note2.md").write_text(INVALID_NOTE, encoding="utf-8")

            report = collect_diagnostics(
                [root],
                [],
                check_index_links=False,
                check_index_inventory=False,
            )

            self.assertEqual(report.files_checked, 2)
            self.assertEqual(report.valid_file_count, 1)
            self.assertEqual(report.invalid_file_count, 1)
            self.assertEqual(report.issue_counts["missing_see_also"], 1)
            self.assertEqual(len(report.word_counts), 2)
            self.assertGreater(report.total_words, 0)

    def test_inventory_issues_are_counted_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Note1.md").write_text(VALID_NOTE, encoding="utf-8")

            report = collect_diagnostics(
                [root],
                [],
                check_index_links=False,
                check_index_inventory=True,
            )

            self.assertGreater(report.inventory_issue_count, 0)
            self.assertGreater(report.issue_counts["missing_index_note"], 0)
            self.assertTrue(report.has_failures)

    def test_output_directory_guard_refuses_input_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "diagnostics"

            self.assertEqual(output_directory_is_inside_supplied_directory(output, [root]), root)
            self.assertIsNone(
                output_directory_is_inside_supplied_directory(Path(directory).parent / "diagnostics", [root])
            )

    def test_main_writes_markdown_and_csv_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            case_root = Path(directory)
            input_dir = case_root / "vault"
            output_dir = case_root / "out"
            input_dir.mkdir()
            (input_dir / "Note1.md").write_text(VALID_NOTE, encoding="utf-8")

            exit_code = main(
                [
                    str(input_dir),
                    "--no-index-links",
                    "--no-index-inventory",
                    "--out-dir",
                    str(output_dir),
                    "--quiet",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / SUMMARY_FILE).is_file())
            self.assertTrue((output_dir / ISSUE_COUNTS_FILE).is_file())
            self.assertTrue((output_dir / ISSUES_FILE).is_file())
            self.assertTrue((output_dir / FILE_DIAGNOSTICS_FILE).is_file())
            self.assertTrue((output_dir / WORD_COUNT_BINS_FILE).is_file())
            self.assertIn("Checked 1 file(s): 1 valid", (output_dir / SUMMARY_FILE).read_text(encoding="utf-8"))

    def test_main_prints_summary_without_writing_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Note1.md").write_text(VALID_NOTE, encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main([str(root), "--no-index-links", "--no-index-inventory"])

            self.assertEqual(exit_code, 0)
            self.assertIn("# Zettel diagnostics summary", stdout.getvalue())
            self.assertFalse((root / SUMMARY_FILE).exists())

    def test_main_refuses_output_inside_input_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Note1.md").write_text(VALID_NOTE, encoding="utf-8")

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = main(
                    [
                        str(root),
                        "--no-index-links",
                        "--no-index-inventory",
                        "--out-dir",
                        str(root / "diagnostics"),
                    ]
                )

            self.assertEqual(exit_code, 2)
            self.assertIn("--out-dir must not be inside", stderr.getvalue())
            self.assertFalse((root / "diagnostics").exists())

    def test_plots_require_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Note1.md").write_text(VALID_NOTE, encoding="utf-8")

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = main([str(root), "--plots"])

            self.assertEqual(exit_code, 2)
            self.assertIn("--plots requires --out-dir", stderr.getvalue())

    def test_zero_exit_allows_diagnostic_runs_to_succeed_despite_issues(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Note2.md").write_text(INVALID_NOTE, encoding="utf-8")

            exit_code = main(
                [
                    str(root),
                    "--no-index-links",
                    "--no-index-inventory",
                    "--zero-exit",
                    "--quiet",
                ]
            )

            self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
