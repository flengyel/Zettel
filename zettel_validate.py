r"""Validate Markdown Zettels in an Obsidian vault.

The validator implements the conventions described by the vault owner:

* the filename is ``ID.md``;
* YAML ``id`` is exactly ``ID``;
* YAML ``title`` is exactly ``ID`` + one space + the H1 text;
* trailing spaces in the H1/title text are ignored;
* ``## SEE ALSO`` precedes ``## References`` (or the heading named by
  ``reference-section-title``);
* every ordinary Zettel links, from ``SEE ALSO``, to at least one alphabetic
  index note appropriate to at least one word in its H1;
* the special index notes are exempt from that last rule.

ID syntax is deliberately opaque.  Current timestamp IDs, legacy dotted IDs,
and the special index IDs can coexist.  Equality among filename, YAML ``id``,
and the prefix of YAML ``title`` is what is enforced.

PyYAML is required::

    py -m pip install pyyaml

Examples (PowerShell)::

    # Check one note
    py .\zettel_validate.py 'C:\path\to\vault\Tikz202504272354.md'

    # Check only Markdown files in the vault root (the default for a directory)
    py .\zettel_validate.py 'C:\path\to\vault'

    # Include subdirectories as well
    py .\zettel_validate.py 'C:\path\to\vault' --recursive \
        --exclude 'Templates/**' --exclude 'Periodic-Notes/**' \
        --exclude 'Projects/**'

Exit status is 0 when everything checked is valid, 1 when validation failures
are found, and 2 for invocation/path errors.
"""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePath
import re
import sys
from typing import Any, TextIO

import yaml
from yaml.constructor import ConstructorError


_FRONT_MATTER_DELIMITER = "---"
_ATX_HEADING_RE = re.compile(
    r"^[ \t]{0,3}(#{1,6})[ \t]+(.+?)(?:[ \t]+#+[ \t]*)?$"
)
_FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
_WIKILINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")
_TITLE_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'’][A-Za-z0-9]+)*")

# These notes live in the vault root.  Front Matter Title displays the complete
# YAML title, but the actual filenames remain ID.md.
INDEX_NOTE_TITLES: dict[str, str] = {
    "0000.0000.0000": "INDEX",
    "0000.0000.0ABC": "A-B-C",
    "0000.0000.0DEF": "D-E-F",
    "0000.0000.0GHI": "G-H-I",
    "0000.0000.0JKL": "J-K-L",
    "0000.0000.0MNO": "M-N-O",
    "0000.0000.0PQR": "P-Q-R",
    "0000.0000.0STU": "S-T-U",
    "0000.0000.0VWX": "V-W-X",
    "0000.0000.00YZ": "Y-Z",
    "0000.0000.0009": "0-9",
}

INDEX_BUCKETS: dict[str, frozenset[str]] = {
    "0000.0000.0ABC": frozenset("ABC"),
    "0000.0000.0DEF": frozenset("DEF"),
    "0000.0000.0GHI": frozenset("GHI"),
    "0000.0000.0JKL": frozenset("JKL"),
    "0000.0000.0MNO": frozenset("MNO"),
    "0000.0000.0PQR": frozenset("PQR"),
    "0000.0000.0STU": frozenset("STU"),
    "0000.0000.0VWX": frozenset("VWX"),
    "0000.0000.00YZ": frozenset("YZ"),
    "0000.0000.0009": frozenset("0123456789"),
}

_CHAR_TO_INDEX_ID: dict[str, str] = {
    character: note_id
    for note_id, characters in INDEX_BUCKETS.items()
    for character in characters
}


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}

    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable key",
                key_node.start_mark,
            ) from exc

        if duplicate:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )

        mapping[key] = loader.construct_object(value_node, deep=deep)

    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


@dataclass(frozen=True, slots=True)
class VisibleLine:
    """A Markdown body line outside a fenced code block."""

    number: int
    text: str


@dataclass(frozen=True, slots=True)
class Heading:
    """An ATX-style Markdown heading outside a fenced code block."""

    level: int
    text: str
    line: int
    visible_index: int


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One validation failure."""

    code: str
    message: str
    filename: str = ""
    line: int | None = None

    def __str__(self) -> str:
        location = self.filename or "<text>"
        if self.line is not None:
            location = f"{location}:{self.line}"
        return f"{location}: [{self.code}] {self.message}"


class ZettelValidator:
    """Validate one Zettel at a time and accumulate statistics.

    ``validate(text, fn=...)`` retains the public interface used by the old
    scripts.  ID format is not classified or restricted.
    """

    _STATISTIC_KEYS = (
        "files_checked",
        "good_zettels",
        "invalid_zettels",
        "invalid_yaml_header",
        "invalid_yaml",
        "missing_frontmatter_key",
        "invalid_id",
        "invalid_title",
        "invalid_reference_section_title",
        "filename_id_mismatch",
        "title_id_mismatch",
        "missing_h1",
        "h1_not_first",
        "h1_mismatch",
        "duplicate_h1",
        "missing_see_also",
        "duplicate_see_also",
        "missing_references",
        "duplicate_references",
        "order_issue",
        "index_title_mismatch",
        "missing_index_link",
        "misindexed_title",
        "no_indexable_title_word",
        "read_error",
    )

    def __init__(self, *, check_index_links: bool = True) -> None:
        self.check_index_links = check_index_links
        self._issues: list[ValidationIssue] = []
        self._filename = ""
        self._stats: Counter[str] = Counter()
        self.reset_statistics()

    @property
    def issues(self) -> tuple[ValidationIssue, ...]:
        return tuple(self._issues)

    @property
    def statistics(self) -> dict[str, int]:
        return dict(self._stats)

    @property
    def status(self) -> int:
        return len(self._issues)

    def reset_statistics(self) -> None:
        self._stats.clear()
        for key in self._STATISTIC_KEYS:
            self._stats[key] = 0

    def append_issue(
        self,
        code: str,
        message: str,
        *,
        line: int | None = None,
    ) -> None:
        self._issues.append(
            ValidationIssue(
                code=code,
                message=message,
                filename=self._filename,
                line=line,
            )
        )
        self._stats[code] += 1

    def show_issues(self, stream: TextIO = sys.stdout) -> None:
        for issue in self._issues:
            print(issue, file=stream)

    @staticmethod
    def _filename_stem(filename: str) -> str:
        """Return the ID from ``ID``, ``ID.md``, or a full path.

        ``Path.stem`` cannot be used for legacy IDs containing periods when a
        bare ID rather than a filename is supplied.
        """

        name = Path(filename).name
        return name[:-3] if name.lower().endswith(".md") else name

    def _finish(self, *, report: bool) -> bool:
        valid = not self._issues
        if valid:
            self._stats["good_zettels"] += 1
        else:
            self._stats["invalid_zettels"] += 1
            if report:
                self.show_issues()
        return valid

    def _split_front_matter(
        self, text: str
    ) -> tuple[str, list[str], int] | None:
        normalized = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized.split("\n")

        if not lines or lines[0].strip() != _FRONT_MATTER_DELIMITER:
            self.append_issue(
                "invalid_yaml_header",
                "The file must begin with a YAML front-matter delimiter (---).",
                line=1,
            )
            return None

        closing_index: int | None = None
        for index in range(1, len(lines)):
            if lines[index].strip() == _FRONT_MATTER_DELIMITER:
                closing_index = index
                break

        if closing_index is None:
            self.append_issue(
                "invalid_yaml_header",
                "The YAML front matter has no closing delimiter (---).",
                line=1,
            )
            return None

        yaml_text = "\n".join(lines[1:closing_index])
        body_lines = lines[closing_index + 1 :]
        body_start_line = closing_index + 2
        return yaml_text, body_lines, body_start_line

    def _load_front_matter(self, yaml_text: str) -> Mapping[str, Any] | None:
        try:
            parsed = yaml.load(yaml_text, Loader=_UniqueKeyLoader)
        except yaml.YAMLError as exc:
            problem = getattr(exc, "problem", None)
            if not problem:
                problem = str(exc).splitlines()[0] if str(exc) else "YAML parsing failed"
            mark = getattr(exc, "problem_mark", None)
            line = mark.line + 2 if mark is not None else None
            self.append_issue(
                "invalid_yaml",
                f"YAML front matter could not be parsed: {problem}.",
                line=line,
            )
            return None

        if not isinstance(parsed, Mapping):
            self.append_issue(
                "invalid_yaml",
                "YAML front matter must be a mapping of field names to values.",
                line=2,
            )
            return None

        return parsed

    def _front_matter_string(
        self,
        front_matter: Mapping[str, Any],
        key: str,
        invalid_code: str,
    ) -> str | None:
        if key not in front_matter:
            self.append_issue(
                "missing_frontmatter_key",
                f"YAML front matter is missing {key!r}.",
            )
            return None

        value = front_matter[key]
        if not isinstance(value, str) or not value.strip():
            self.append_issue(
                invalid_code,
                f"The front-matter field {key!r} must be a nonempty string.",
            )
            return None

        # Leading whitespace is meaningful in the title text; trailing
        # whitespace is not, according to the stated convention.
        return value.rstrip()

    @staticmethod
    def _visible_body_lines(
        body_lines: Sequence[str], body_start_line: int
    ) -> list[VisibleLine]:
        visible: list[VisibleLine] = []
        fence_character: str | None = None
        fence_length = 0

        for offset, line in enumerate(body_lines):
            line_number = body_start_line + offset
            fence_match = _FENCE_RE.match(line)
            if fence_match:
                marker = fence_match.group(1)
                if fence_character is None:
                    fence_character = marker[0]
                    fence_length = len(marker)
                elif marker[0] == fence_character and len(marker) >= fence_length:
                    fence_character = None
                    fence_length = 0
                continue

            if fence_character is None:
                visible.append(VisibleLine(line_number, line))

        return visible

    @staticmethod
    def _headings(visible_lines: Sequence[VisibleLine]) -> list[Heading]:
        headings: list[Heading] = []
        for visible_index, visible_line in enumerate(visible_lines):
            match = _ATX_HEADING_RE.match(visible_line.text)
            if match:
                headings.append(
                    Heading(
                        level=len(match.group(1)),
                        text=match.group(2).rstrip(),
                        line=visible_line.number,
                        visible_index=visible_index,
                    )
                )
        return headings

    @staticmethod
    def _wikilink_target(raw_link: str) -> str:
        target = raw_link.split("|", 1)[0].strip()
        target = target.split("#", 1)[0].strip()
        target = target.split("^", 1)[0].strip()
        if target.lower().endswith(".md"):
            target = target[:-3]
        return target

    @classmethod
    def _wikilinks_in_section(
        cls,
        visible_lines: Sequence[VisibleLine],
        section_heading: Heading,
    ) -> list[tuple[str, int]]:
        links: list[tuple[str, int]] = []

        for visible_line in visible_lines[section_heading.visible_index + 1 :]:
            heading_match = _ATX_HEADING_RE.match(visible_line.text)
            if heading_match and len(heading_match.group(1)) <= section_heading.level:
                break

            for match in _WIKILINK_RE.finditer(visible_line.text):
                links.append((cls._wikilink_target(match.group(1)), visible_line.number))

        return links

    @staticmethod
    def _expected_index_ids(human_title: str) -> set[str]:
        expected: set[str] = set()
        for match in _TITLE_WORD_RE.finditer(human_title):
            initial = match.group(0)[0].upper()
            index_id = _CHAR_TO_INDEX_ID.get(initial)
            if index_id is not None:
                expected.add(index_id)
        return expected

    def _validate_index_link(
        self,
        note_id: str,
        human_title: str,
        visible_lines: Sequence[VisibleLine],
        see_also: Heading,
    ) -> None:
        if note_id in INDEX_NOTE_TITLES:
            return

        section_links = self._wikilinks_in_section(visible_lines, see_also)
        linked_index_ids = {
            target for target, _ in section_links if target in INDEX_BUCKETS
        }

        if not linked_index_ids:
            self.append_issue(
                "missing_index_link",
                "The SEE ALSO section must link to at least one alphabetic "
                "index note.",
                line=see_also.line,
            )
            return

        expected_index_ids = self._expected_index_ids(human_title)
        if not expected_index_ids:
            self.append_issue(
                "no_indexable_title_word",
                "The H1 contains no word beginning with an ASCII letter or digit, "
                "so its index bucket cannot be checked.",
                line=see_also.line,
            )
            return

        if linked_index_ids.isdisjoint(expected_index_ids):
            linked = ", ".join(sorted(linked_index_ids))
            expected = ", ".join(sorted(expected_index_ids))
            self.append_issue(
                "misindexed_title",
                f"Index link(s) {linked} do not index any word in the H1. "
                f"Expected at least one of: {expected}.",
                line=see_also.line,
            )

    def _validate_body(
        self,
        body_lines: list[str],
        body_start_line: int,
        note_id: str | None,
        human_title: str | None,
        reference_title: str | None,
    ) -> None:
        visible_lines = self._visible_body_lines(body_lines, body_start_line)
        headings = self._headings(visible_lines)

        first_nonblank_line = next(
            (line.number for line in visible_lines if line.text.strip()),
            None,
        )

        h1_headings = [heading for heading in headings if heading.level == 1]
        first_h1: Heading | None = None
        if not h1_headings:
            self.append_issue("missing_h1", "Missing H1 title after front matter.")
        else:
            first_h1 = h1_headings[0]
            if first_nonblank_line != first_h1.line:
                self.append_issue(
                    "h1_not_first",
                    "The H1 title must be the first nonblank line after front matter.",
                    line=first_h1.line,
                )
            if human_title is not None and first_h1.text.rstrip() != human_title.rstrip():
                self.append_issue(
                    "h1_mismatch",
                    f"H1 {first_h1.text!r} does not match title text "
                    f"{human_title!r}.",
                    line=first_h1.line,
                )
            if len(h1_headings) > 1:
                self.append_issue(
                    "duplicate_h1",
                    "More than one H1 heading was found.",
                    line=h1_headings[1].line,
                )

        see_also_headings = [
            heading
            for heading in headings
            if heading.level == 2 and heading.text == "SEE ALSO"
        ]
        first_see_also: Heading | None = None
        if not see_also_headings:
            self.append_issue("missing_see_also", "Missing '## SEE ALSO' section.")
        else:
            first_see_also = see_also_headings[0]
            if len(see_also_headings) > 1:
                self.append_issue(
                    "duplicate_see_also",
                    "More than one '## SEE ALSO' section was found.",
                    line=see_also_headings[1].line,
                )

        references: list[Heading] = []
        if reference_title is not None:
            references = [
                heading
                for heading in headings
                if heading.level == 2 and heading.text == reference_title
            ]
            if not references:
                self.append_issue(
                    "missing_references",
                    f"Missing '## {reference_title}' section.",
                )
            elif len(references) > 1:
                self.append_issue(
                    "duplicate_references",
                    f"More than one '## {reference_title}' section was found.",
                    line=references[1].line,
                )

        if first_see_also is not None and references:
            if first_see_also.line > references[0].line:
                self.append_issue(
                    "order_issue",
                    f"'## SEE ALSO' must precede '## {reference_title}'.",
                    line=first_see_also.line,
                )

        if (
            self.check_index_links
            and note_id is not None
            and human_title is not None
            and first_see_also is not None
        ):
            self._validate_index_link(
                note_id,
                human_title,
                visible_lines,
                first_see_also,
            )

    def validate(
        self,
        text: str,
        fn: str = "",
        *,
        report: bool = True,
    ) -> bool:
        """Validate one completed Zettel."""

        self._issues = []
        self._filename = Path(fn).name if fn else ""
        self._stats["files_checked"] += 1

        split = self._split_front_matter(text)
        if split is None:
            return self._finish(report=report)

        yaml_text, body_lines, body_start_line = split
        front_matter = self._load_front_matter(yaml_text)
        if front_matter is None:
            return self._finish(report=report)

        note_id = self._front_matter_string(front_matter, "id", "invalid_id")
        full_title = self._front_matter_string(front_matter, "title", "invalid_title")
        reference_title = self._front_matter_string(
            front_matter,
            "reference-section-title",
            "invalid_reference_section_title",
        )

        if note_id is not None:
            if any(character in note_id for character in ("/", "\\", "\0")):
                self.append_issue(
                    "invalid_id",
                    "The ID cannot contain a path separator or NUL character.",
                )

            if fn:
                filename_id = self._filename_stem(fn)
                if filename_id != note_id:
                    self.append_issue(
                        "filename_id_mismatch",
                        f"Filename ID {filename_id!r} does not match "
                        f"front-matter ID {note_id!r}.",
                    )

        human_title: str | None = None
        if note_id is not None and full_title is not None:
            title_prefix = f"{note_id} "
            if not full_title.startswith(title_prefix):
                self.append_issue(
                    "title_id_mismatch",
                    "The front-matter 'title' must begin with the ID followed "
                    "by exactly one space.",
                )
            else:
                human_title = full_title[len(title_prefix) :].rstrip()
                if not human_title:
                    self.append_issue(
                        "invalid_title",
                        "The front-matter 'title' must contain text after the ID.",
                    )

        if note_id is not None and human_title is not None:
            expected_index_title = INDEX_NOTE_TITLES.get(note_id)
            if expected_index_title is not None and human_title != expected_index_title:
                self.append_issue(
                    "index_title_mismatch",
                    f"Index note {note_id!r} must have title text "
                    f"{expected_index_title!r}, not {human_title!r}.",
                )

        self._validate_body(
            body_lines,
            body_start_line,
            note_id,
            human_title,
            reference_title,
        )
        return self._finish(report=report)

    def validate_file(self, path: Path | str, *, report: bool = True) -> bool:
        note_path = Path(path)
        try:
            text = note_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self._issues = []
            self._filename = str(note_path)
            self._stats["files_checked"] += 1
            self.append_issue("read_error", f"Could not read file: {exc}")
            return self._finish(report=report)

        return self.validate(text, fn=str(note_path), report=report)


def _matches_exclusion(path: Path, root: Path, patterns: Sequence[str]) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        relative = path

    candidates = (PurePath(path.name), PurePath(relative.as_posix()))
    return any(
        candidate.match(pattern)
        for pattern in patterns
        for candidate in candidates
    )


def iter_markdown_files(
    paths: Sequence[Path],
    exclusions: Sequence[str],
    *,
    recursive: bool,
) -> Iterator[Path]:
    """Yield Markdown files.

    A directory means only its root by default.  ``recursive=True`` includes
    subdirectories.  Hidden directories are skipped.
    """

    seen: set[Path] = set()

    for supplied_path in paths:
        path = supplied_path.expanduser()
        if path.is_file():
            resolved = path.resolve()
            if path.suffix.lower() == ".md" and resolved not in seen:
                seen.add(resolved)
                yield path
            continue

        if path.is_dir():
            candidates = path.rglob("*.md") if recursive else path.glob("*.md")
            for candidate in sorted(candidates):
                relative_parts = candidate.relative_to(path).parts
                if any(part.startswith(".") for part in relative_parts):
                    continue
                if _matches_exclusion(candidate, path, exclusions):
                    continue
                resolved = candidate.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    yield candidate
            continue

        print(f"zettel_validate.py: path not found: {path}", file=sys.stderr)


def index_inventory_issues(vault_root: Path) -> list[ValidationIssue]:
    """Check that all special index files exist in the vault root."""

    issues: list[ValidationIssue] = []
    for note_id, title in INDEX_NOTE_TITLES.items():
        expected_path = vault_root / f"{note_id}.md"
        if not expected_path.is_file():
            issues.append(
                ValidationIssue(
                    code="missing_index_note",
                    message=f"Missing special index note {note_id!r} ({title}).",
                    filename=str(vault_root),
                )
            )
    return issues


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate completed Markdown Zettels in an Obsidian vault."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Markdown files or directories; directories mean their root only "
        "unless --recursive is supplied",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="search supplied directories recursively",
    )
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
        help="when a directory is supplied, do not require all special index "
        "files in its root",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress individual failures and print only the summary",
    )
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="suppress the final summary",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_argument_parser()
    args = parser.parse_args(argv)

    supplied_directories = [
        path.expanduser() for path in args.paths if path.expanduser().is_dir()
    ]
    nonexistent = [
        path.expanduser() for path in args.paths if not path.expanduser().exists()
    ]
    if nonexistent:
        for path in nonexistent:
            print(f"zettel_validate.py: path not found: {path}", file=sys.stderr)
        return 2

    files = list(
        iter_markdown_files(
            args.paths,
            args.exclude,
            recursive=args.recursive,
        )
    )
    if not files:
        print("zettel_validate.py: no Markdown files found", file=sys.stderr)
        return 2

    validator = ZettelValidator(check_index_links=not args.no_index_links)
    invalid_count = 0

    for path in files:
        if not validator.validate_file(path, report=not args.quiet):
            invalid_count += 1

    inventory_issues: list[ValidationIssue] = []
    if not args.no_index_inventory:
        for directory in supplied_directories:
            inventory_issues.extend(index_inventory_issues(directory))

    if inventory_issues and not args.quiet:
        for issue in inventory_issues:
            print(issue)

    if not args.no_summary:
        valid_count = len(files) - invalid_count
        inventory_suffix = (
            f"; {len(inventory_issues)} index-inventory failure(s)"
            if inventory_issues
            else ""
        )
        print(
            f"Checked {len(files)} file(s): "
            f"{valid_count} valid, {invalid_count} invalid{inventory_suffix}."
        )

    return 1 if invalid_count or inventory_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
