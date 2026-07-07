#!/usr/bin/env python3
r"""Generate read-only diagnostics for Markdown Zettels.

The script validates Markdown notes with ``zettel_validate.py`` and can write
inspectable report artifacts: Markdown summary, CSV data, and optional PNG
plots. It never modifies vault files and rejects an output directory inside a
supplied input directory.

Examples (PowerShell)::

    py .\python\zettel_diagnostics.py C:\Users\fleng\Zettelkasten `
        --no-index-links --out-dir .\diagnostics

    py .\python\zettel_diagnostics.py C:\Users\fleng\Zettelkasten `
        --no-index-links --no-index-inventory --out-dir .\diagnostics --plots

Matplotlib is imported only when ``--plots`` is supplied.
"""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterable, Sequence
import csv
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
import sys
from typing import TextIO

from zettel_validate import (
    ZettelValidator,
    index_inventory_issues,
    iter_markdown_files,
)


SUMMARY_FILE = "zettel-diagnostics-summary.md"
ISSUE_COUNTS_FILE = "zettel-diagnostics-issue-counts.csv"
ISSUES_FILE = "zettel-diagnostics-issues.csv"
FILE_DIAGNOSTICS_FILE = "zettel-diagnostics-file-diagnostics.csv"
WORD_COUNT_BINS_FILE = "zettel-diagnostics-word-count-bins.csv"
ISSUE_PLOT_FILE = "zettel-diagnostics-issue-counts.png"
WORD_PLOT_FILE = "zettel-diagnostics-word-counts.png"


@dataclass(frozen=True, slots=True)
class IssueRecord:
    """A validation or index-inventory issue rendered for CSV output."""

    path: str
    line: int | None
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class WordCountRecord:
    """Word-count and validity facts for one Markdown file."""

    path: str
    words: int
    valid: bool
    issue_count: int


@dataclass(frozen=True, slots=True)
class DiagnosticReport:
    """Complete read-only diagnostic facts before serialization."""

    files_checked: int
    valid_file_count: int
    invalid_file_count: int
    inventory_issue_count: int
    issues: tuple[IssueRecord, ...]
    word_counts: tuple[WordCountRecord, ...]

    @property
    def issue_counts(self) -> Counter[str]:
        return Counter(issue.code for issue in self.issues)

    @property
    def total_words(self) -> int:
        return sum(record.words for record in self.word_counts)

    @property
    def has_failures(self) -> bool:
        return bool(self.invalid_file_count or self.inventory_issue_count)


def _safe_for_stream(value: object, stream: TextIO) -> str:
    text = str(value)
    encoding = getattr(stream, "encoding", None)
    if not encoding:
        return text

    try:
        text.encode(encoding)
    except UnicodeEncodeError:
        return text.encode(encoding, errors="backslashreplace").decode(encoding)
    except LookupError:
        return text.encode("ascii", errors="backslashreplace").decode("ascii")
    return text


def safe_print(value: object = "", *, stream: TextIO | None = None) -> None:
    if stream is None:
        stream = sys.stdout
    print(_safe_for_stream(value, stream), file=stream)


def count_words(text: str) -> int:
    """Count whitespace-delimited tokens, matching the legacy graph scripts."""

    return len(text.split())


def choose_relative_base(paths: Sequence[Path]) -> Path | None:
    directories = [path.expanduser().resolve() for path in paths if path.expanduser().is_dir()]
    return directories[0] if len(directories) == 1 else None


def display_path(path: Path, relative_base: Path | None) -> str:
    if relative_base is not None:
        try:
            return path.resolve().relative_to(relative_base).as_posix()
        except ValueError:
            pass
    return str(path)


def output_directory_is_inside_supplied_directory(
    output_dir: Path,
    supplied_paths: Sequence[Path],
) -> Path | None:
    """Return the supplied directory that would contain output_dir, if any."""

    resolved_output = output_dir.expanduser().resolve(strict=False)
    for supplied in supplied_paths:
        expanded = supplied.expanduser()
        if not expanded.is_dir():
            continue
        resolved_supplied = expanded.resolve(strict=False)
        if resolved_output == resolved_supplied:
            return expanded
        try:
            resolved_output.relative_to(resolved_supplied)
        except ValueError:
            continue
        return expanded
    return None


def collect_diagnostics(
    paths: Sequence[Path],
    exclusions: Sequence[str],
    *,
    recursive: bool = False,
    check_index_links: bool = True,
    check_index_inventory: bool = True,
) -> DiagnosticReport:
    """Validate files and collect word counts without modifying inputs."""

    expanded_paths = [path.expanduser() for path in paths]
    files = list(iter_markdown_files(expanded_paths, exclusions, recursive=recursive))
    relative_base = choose_relative_base(expanded_paths)
    validator = ZettelValidator(check_index_links=check_index_links)
    issues: list[IssueRecord] = []
    word_counts: list[WordCountRecord] = []
    invalid_files = 0

    for path in files:
        shown_path = display_path(path, relative_base)
        try:
            text = path.read_text(encoding="utf-8")
            words = count_words(text)
            valid = validator.validate(text, fn=str(path), report=False)
        except (OSError, UnicodeError):
            words = 0
            valid = validator.validate_file(path, report=False)

        file_issues = tuple(validator.issues)
        issues.extend(
            IssueRecord(
                path=shown_path,
                line=issue.line,
                code=issue.code,
                message=issue.message,
            )
            for issue in file_issues
        )
        word_counts.append(
            WordCountRecord(
                path=shown_path,
                words=words,
                valid=valid,
                issue_count=len(file_issues),
            )
        )
        if not valid:
            invalid_files += 1

    inventory_issue_count = 0
    if check_index_inventory:
        for directory in [path for path in expanded_paths if path.is_dir()]:
            for issue in index_inventory_issues(directory):
                inventory_issue_count += 1
                issues.append(
                    IssueRecord(
                        path=issue.filename,
                        line=issue.line,
                        code=issue.code,
                        message=issue.message,
                    )
                )

    return DiagnosticReport(
        files_checked=len(files),
        valid_file_count=len(files) - invalid_files,
        invalid_file_count=invalid_files,
        inventory_issue_count=inventory_issue_count,
        issues=tuple(issues),
        word_counts=tuple(word_counts),
    )


def word_count_summary(records: Sequence[WordCountRecord]) -> dict[str, str]:
    counts = [record.words for record in records]
    if not counts:
        return {
            "total_words": "0",
            "average_words": "0",
            "median_words": "0",
            "minimum_words": "0",
            "maximum_words": "0",
        }

    return {
        "total_words": str(sum(counts)),
        "average_words": f"{mean(counts):.2f}",
        "median_words": f"{median(counts):.2f}",
        "minimum_words": str(min(counts)),
        "maximum_words": str(max(counts)),
    }


def word_count_bins(
    word_counts: Sequence[int],
    *,
    bin_width: int,
    overflow_at: int,
) -> list[tuple[str, int]]:
    """Return deterministic word-count bins."""

    bins: list[tuple[str, int]] = []
    for left in range(0, overflow_at, bin_width):
        right = min(left + bin_width - 1, overflow_at - 1)
        count = sum(1 for words in word_counts if left <= words <= right)
        bins.append((f"{left}-{right}", count))
    overflow_count = sum(1 for words in word_counts if words >= overflow_at)
    bins.append((f"{overflow_at}+", overflow_count))
    return bins


def sorted_issue_counts(counts: Counter[str]) -> list[tuple[str, int]]:
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def render_markdown_summary(
    report: DiagnosticReport,
    *,
    paths: Sequence[Path],
    recursive: bool,
    exclusions: Sequence[str],
    check_index_links: bool,
    check_index_inventory: bool,
    top_issues: int,
) -> str:
    lines: list[str] = [
        "# Zettel diagnostics summary",
        "",
        "## Inputs",
        "",
        "| Setting | Value |",
        "|---|---|",
        f"| Paths | {', '.join(str(path) for path in paths)} |",
        f"| Recursive | {str(recursive).lower()} |",
        f"| Exclusions | {', '.join(exclusions) if exclusions else '(none)'} |",
        f"| Index-link checks | {str(check_index_links).lower()} |",
        f"| Index-inventory checks | {str(check_index_inventory).lower()} |",
        "",
        "## Validation summary",
        "",
        f"Checked {report.files_checked} file(s): {report.valid_file_count} valid, "
        f"{report.invalid_file_count} invalid; {report.inventory_issue_count} "
        "index-inventory failure(s).",
        "",
        "## Issue category counts",
        "",
    ]

    issue_counts = sorted_issue_counts(report.issue_counts)
    if issue_counts:
        lines.append("| Count | Issue code |")
        lines.append("|---:|---|")
        for code, count in issue_counts[:top_issues]:
            lines.append(f"| {count} | `{code}` |")
    else:
        lines.append("No validation or index-inventory issues were found.")
    lines.append("")

    summary = word_count_summary(report.word_counts)
    lines.extend(
        [
            "## Word-count summary",
            "",
            "| Statistic | Value |",
            "|---|---:|",
            f"| Total words | {summary['total_words']} |",
            f"| Average words per file | {summary['average_words']} |",
            f"| Median words per file | {summary['median_words']} |",
            f"| Minimum words in a file | {summary['minimum_words']} |",
            f"| Maximum words in a file | {summary['maximum_words']} |",
            "",
            "## Artifact boundary",
            "",
            "This diagnostic run is read-only with respect to the supplied vault paths. "
            "It may write report artifacts only to the requested output directory.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def write_csv_rows(path: Path, fieldnames: Sequence[str], rows: Iterable[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_reports(
    report: DiagnosticReport,
    output_dir: Path,
    *,
    paths: Sequence[Path] = (),
    recursive: bool = False,
    exclusions: Sequence[str] = (),
    check_index_links: bool = True,
    check_index_inventory: bool = True,
    top_issues: int = 40,
    bin_width: int = 50,
    overflow_at: int = 1000,
    plots: bool = False,
) -> list[Path]:
    """Write inspectable Markdown, CSV, and optional PNG artifacts."""

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    summary_path = output_dir / SUMMARY_FILE
    summary_path.write_text(
        render_markdown_summary(
            report,
            paths=paths,
            recursive=recursive,
            exclusions=exclusions,
            check_index_links=check_index_links,
            check_index_inventory=check_index_inventory,
            top_issues=top_issues,
        ),
        encoding="utf-8",
        newline="\n",
    )
    written.append(summary_path)

    issue_counts_path = output_dir / ISSUE_COUNTS_FILE
    write_csv_rows(
        issue_counts_path,
        ("issue_code", "count"),
        (
            {"issue_code": code, "count": count}
            for code, count in sorted_issue_counts(report.issue_counts)
        ),
    )
    written.append(issue_counts_path)

    issues_path = output_dir / ISSUES_FILE
    write_csv_rows(
        issues_path,
        ("path", "line", "issue_code", "message"),
        (
            {
                "path": issue.path,
                "line": issue.line if issue.line is not None else "",
                "issue_code": issue.code,
                "message": issue.message,
            }
            for issue in report.issues
        ),
    )
    written.append(issues_path)

    file_diagnostics_path = output_dir / FILE_DIAGNOSTICS_FILE
    write_csv_rows(
        file_diagnostics_path,
        ("path", "words", "valid", "issue_count"),
        (
            {
                "path": record.path,
                "words": record.words,
                "valid": str(record.valid).lower(),
                "issue_count": record.issue_count,
            }
            for record in report.word_counts
        ),
    )
    written.append(file_diagnostics_path)

    bins_path = output_dir / WORD_COUNT_BINS_FILE
    write_csv_rows(
        bins_path,
        ("bin", "count"),
        (
            {"bin": label, "count": count}
            for label, count in word_count_bins(
                [record.words for record in report.word_counts],
                bin_width=bin_width,
                overflow_at=overflow_at,
            )
        ),
    )
    written.append(bins_path)

    if plots:
        written.extend(
            write_plots(report, output_dir, bin_width=bin_width, overflow_at=overflow_at)
        )

    return written


def write_plots(
    report: DiagnosticReport,
    output_dir: Path,
    *,
    bin_width: int,
    overflow_at: int,
) -> list[Path]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("--plots requires matplotlib in the active Python environment") from exc

    written: list[Path] = []

    issue_counts = sorted_issue_counts(report.issue_counts)
    if issue_counts:
        labels = [code for code, _count in issue_counts]
        values = [count for _code, count in issue_counts]
    else:
        labels = ["no_issues"]
        values = [0]

    figure = plt.figure(figsize=(10, 6))
    axis = figure.add_subplot(1, 1, 1)
    axis.bar(labels, values)
    axis.set_title("Zettel validation issue counts")
    axis.set_xlabel("Issue code")
    axis.set_ylabel("Count")
    axis.tick_params(axis="x", rotation=75)
    figure.tight_layout()
    issue_plot_path = output_dir / ISSUE_PLOT_FILE
    figure.savefig(issue_plot_path)
    plt.close(figure)
    written.append(issue_plot_path)

    bins = word_count_bins(
        [record.words for record in report.word_counts],
        bin_width=bin_width,
        overflow_at=overflow_at,
    )
    if bins:
        labels = [label for label, _count in bins]
        values = [count for _label, count in bins]
        figure = plt.figure(figsize=(10, 6))
        axis = figure.add_subplot(1, 1, 1)
        axis.bar(labels, values)
        axis.set_title("Zettel word-count distribution")
        axis.set_xlabel("Words per file")
        axis.set_ylabel("File count")
        axis.tick_params(axis="x", rotation=75)
        figure.tight_layout()
        word_plot_path = output_dir / WORD_PLOT_FILE
        figure.savefig(word_plot_path)
        plt.close(figure)
        written.append(word_plot_path)

    return written


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create read-only validation and word-count diagnostics for Markdown Zettels."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Markdown files or directories; directories mean their root only unless --recursive is supplied",
    )
    parser.add_argument("--recursive", action="store_true", help="search directories recursively")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="exclude a relative path or filename matching GLOB; may be repeated",
    )
    parser.add_argument(
        "--no-index-links",
        action="store_true",
        help="do not require or check alphabetic-index links in SEE ALSO",
    )
    parser.add_argument(
        "--no-index-inventory",
        action="store_true",
        help="when a directory is supplied, do not require all special index files in its root",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        help="directory for Markdown, CSV, and optional PNG artifacts; omitted means print summary only",
    )
    parser.add_argument(
        "--plots",
        action="store_true",
        help="write PNG plots with matplotlib; requires matplotlib in the active Python environment",
    )
    parser.add_argument("--word-bin-size", type=int, default=50, help="word-count bin size")
    parser.add_argument(
        "--word-bin-max",
        type=int,
        default=1000,
        help="left endpoint for the final open-ended word-count bin",
    )
    parser.add_argument(
        "--top-issues",
        type=int,
        default=40,
        help="maximum issue-code rows to include in the Markdown summary",
    )
    parser.add_argument(
        "--zero-exit",
        action="store_true",
        help="return exit code 0 after writing diagnostics even when validation issues are found",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress non-error console output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    if args.word_bin_size <= 0:
        safe_print("zettel_diagnostics.py: --word-bin-size must be positive", stream=sys.stderr)
        return 2
    if args.word_bin_max <= 0:
        safe_print("zettel_diagnostics.py: --word-bin-max must be positive", stream=sys.stderr)
        return 2
    if args.top_issues <= 0:
        safe_print("zettel_diagnostics.py: --top-issues must be positive", stream=sys.stderr)
        return 2
    if args.plots and args.out_dir is None:
        safe_print("zettel_diagnostics.py: --plots requires --out-dir", stream=sys.stderr)
        return 2

    supplied_paths = [path.expanduser() for path in args.paths]
    nonexistent = [path for path in supplied_paths if not path.exists()]
    if nonexistent:
        for path in nonexistent:
            safe_print(f"zettel_diagnostics.py: path not found: {path}", stream=sys.stderr)
        return 2

    if args.out_dir is not None:
        contained_by = output_directory_is_inside_supplied_directory(args.out_dir, supplied_paths)
        if contained_by is not None:
            safe_print(
                "zettel_diagnostics.py: --out-dir must not be inside supplied input directory "
                f"{contained_by}",
                stream=sys.stderr,
            )
            return 2

    report = collect_diagnostics(
        supplied_paths,
        args.exclude,
        recursive=args.recursive,
        check_index_links=not args.no_index_links,
        check_index_inventory=not args.no_index_inventory,
    )
    if report.files_checked == 0:
        safe_print("zettel_diagnostics.py: no Markdown files found", stream=sys.stderr)
        return 2

    if args.out_dir is not None:
        try:
            written = write_reports(
                report,
                args.out_dir.expanduser(),
                paths=supplied_paths,
                recursive=args.recursive,
                exclusions=args.exclude,
                check_index_links=not args.no_index_links,
                check_index_inventory=not args.no_index_inventory,
                top_issues=args.top_issues,
                bin_width=args.word_bin_size,
                overflow_at=args.word_bin_max,
                plots=args.plots,
            )
        except (OSError, UnicodeError, RuntimeError) as exc:
            safe_print(f"zettel_diagnostics.py: could not write diagnostics: {exc}", stream=sys.stderr)
            return 2
        if not args.quiet:
            for path in written:
                safe_print(f"wrote {path}")
    elif not args.quiet:
        safe_print(
            render_markdown_summary(
                report,
                paths=supplied_paths,
                recursive=args.recursive,
                exclusions=args.exclude,
                check_index_links=not args.no_index_links,
                check_index_inventory=not args.no_index_inventory,
                top_issues=args.top_issues,
            )
        )

    if args.zero_exit:
        return 0
    return 1 if report.has_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
