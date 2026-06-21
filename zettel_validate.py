"""Validate Markdown notes produced by the Obsidian Zettel template.

The validator enforces the template's structural contract. It deliberately
places no requirements on WikiLinks, hashtags, note length, or section content.

PyYAML is required::

    python -m pip install pyyaml

Examples::

    python zettel_validate.py path/to/note.md
    python zettel_validate.py path/to/vault --exclude 'Templates/**'
    python zettel_validate.py path/to/vault --require-template-id
"""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
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
_TEMPLATE_ID_RE = re.compile(r"^(.+?)(\d{12})$")


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
class Heading:
    """An ATX-style Markdown heading outside a fenced code block."""

    level: int
    text: str
    line: int


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
    """Validate completed Zettels and accumulate validation statistics.

    ``validate`` preserves the original public calling convention: it accepts
    note text and an optional filename/ID, and returns ``True`` exactly when
    the note is valid. ``issues`` describes the most recently checked note;
    ``statistics`` is cumulative for the lifetime of the validator.

    By default, legacy IDs are accepted. Set ``require_template_id=True`` to
    require the current ``alpha-keyword + YYYYMMDDHHmm`` form.
    """

    REQUIRED_FRONT_MATTER_KEYS = ("id", "title", "reference-section-title")

    _STATISTIC_KEYS = (
        "files_checked",
        "good_zettels",
        "invalid_zettels",
        "invalid_yaml_header",
        "invalid_yaml",
        "missing_frontmatter_key",
        "invalid_id",
        "invalid_template_id",
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
        "read_error",
    )

    def __init__(self, *, require_template_id: bool = False) -> None:
        self.require_template_id = require_template_id
        self._issues: list[ValidationIssue] = []
        self._filename = ""
        self._stats: Counter[str] = Counter()
        self.reset_statistics()

    @property
    def issues(self) -> tuple[ValidationIssue, ...]:
        """Failures for the most recently validated note."""

        return tuple(self._issues)

    @property
    def statistics(self) -> dict[str, int]:
        """Cumulative counts for all notes checked by this object."""

        return dict(self._stats)

    @property
    def status(self) -> int:
        """Number of failures for the most recently validated note."""

        return len(self._issues)

    def reset_statistics(self) -> None:
        """Reset cumulative counters without changing configuration."""

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
        """Record a failure and increment its cumulative count."""

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
        """Print failures for the most recently validated note."""

        for issue in self._issues:
            print(issue, file=stream)

    @staticmethod
    def _filename_stem(filename: str) -> str:
        """Return an ID from either ``ID``, ``ID.md``, or a path.

        ``Path.stem`` is intentionally avoided when no ``.md`` suffix is
        present because legacy IDs may contain periods.
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
        """Return YAML text, body lines, and the body's first 1-based line."""

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

        return value.strip()

    def _validate_template_id(self, note_id: str) -> None:
        match = _TEMPLATE_ID_RE.fullmatch(note_id)
        if match is None:
            self.append_issue(
                "invalid_template_id",
                "The ID must be an alpha keyword followed by a 12-digit "
                "YYYYMMDDHHmm timestamp.",
            )
            return

        timestamp = match.group(2)
        try:
            datetime.strptime(timestamp, "%Y%m%d%H%M")
        except ValueError:
            self.append_issue(
                "invalid_template_id",
                f"The ID suffix {timestamp!r} is not a valid YYYYMMDDHHmm timestamp.",
            )

    @staticmethod
    def _visible_body_lines(
        body_lines: Sequence[str], body_start_line: int
    ) -> Iterator[tuple[int, str]]:
        """Yield body lines outside fenced code blocks."""

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
                yield line_number, line

    @staticmethod
    def _headings(visible_lines: Sequence[tuple[int, str]]) -> list[Heading]:
        headings: list[Heading] = []
        for line_number, line in visible_lines:
            match = _ATX_HEADING_RE.match(line)
            if match:
                headings.append(
                    Heading(
                        level=len(match.group(1)),
                        text=match.group(2).strip(),
                        line=line_number,
                    )
                )
        return headings

    def _validate_body(
        self,
        body_lines: list[str],
        body_start_line: int,
        human_title: str | None,
        reference_title: str | None,
    ) -> None:
        visible_lines = list(self._visible_body_lines(body_lines, body_start_line))
        headings = self._headings(visible_lines)

        first_nonblank_line = next(
            (
                line_number
                for line_number, line in visible_lines
                if line.strip()
            ),
            None,
        )

        h1_headings = [heading for heading in headings if heading.level == 1]
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
            if human_title is not None and first_h1.text != human_title:
                self.append_issue(
                    "h1_mismatch",
                    f"H1 {first_h1.text!r} does not match title text {human_title!r}.",
                    line=first_h1.line,
                )
            if len(h1_headings) > 1:
                self.append_issue(
                    "duplicate_h1",
                    "More than one H1 heading was found.",
                    line=h1_headings[1].line,
                )

        see_also = [
            heading
            for heading in headings
            if heading.level == 2 and heading.text == "SEE ALSO"
        ]
        if not see_also:
            self.append_issue("missing_see_also", "Missing '## SEE ALSO' section.")
        elif len(see_also) > 1:
            self.append_issue(
                "duplicate_see_also",
                "More than one '## SEE ALSO' section was found.",
                line=see_also[1].line,
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

        if see_also and references and see_also[0].line > references[0].line:
            self.append_issue(
                "order_issue",
                f"'## SEE ALSO' must precede '## {reference_title}'.",
                line=see_also[0].line,
            )

    def validate(
        self,
        text: str,
        fn: str = "",
        *,
        report: bool = True,
    ) -> bool:
        """Validate one completed Zettel.

        Parameters
        ----------
        text:
            Entire Markdown file contents.
        fn:
            Note ID, filename, or full path. If supplied, its filename stem
            must equal the front-matter ``id``.
        report:
            Print failures. This defaults to ``True`` for compatibility with
            the original validator.
        """

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
        full_title = self._front_matter_string(
            front_matter, "title", "invalid_title"
        )
        reference_title = self._front_matter_string(
            front_matter,
            "reference-section-title",
            "invalid_reference_section_title",
        )

        if note_id is not None and self.require_template_id:
            self._validate_template_id(note_id)

        if fn and note_id is not None:
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
                    "The front-matter 'title' must begin with the ID "
                    "followed by one space.",
                )
            else:
                human_title = full_title[len(title_prefix) :].strip()
                if not human_title:
                    self.append_issue(
                        "invalid_title",
                        "The front-matter 'title' must contain text after the ID.",
                    )

        self._validate_body(
            body_lines,
            body_start_line,
            human_title,
            reference_title,
        )
        return self._finish(report=report)

    def validate_file(self, path: Path | str, *, report: bool = True) -> bool:
        """Read and validate one UTF-8 Markdown file."""

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
    paths: Sequence[Path], exclusions: Sequence[str]
) -> Iterator[Path]:
    """Yield Markdown files from files and recursively searched directories."""

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
            for candidate in sorted(path.rglob("*.md")):
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


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate completed Markdown Zettels created from the "
        "Obsidian template."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Markdown files or directories; directories are searched recursively",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="exclude a relative path or filename matching GLOB; may be repeated",
    )
    parser.add_argument(
        "--require-template-id",
        action="store_true",
        help="require alpha-keyword + YYYYMMDDHHmm IDs",
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

    files = list(iter_markdown_files(args.paths, args.exclude))
    if not files:
        print("zettel_validate.py: no Markdown files found", file=sys.stderr)
        return 2

    validator = ZettelValidator(require_template_id=args.require_template_id)
    invalid_count = 0

    for path in files:
        if not validator.validate_file(path, report=not args.quiet):
            invalid_count += 1

    if not args.no_summary:
        valid_count = len(files) - invalid_count
        print(
            f"Checked {len(files)} file(s): "
            f"{valid_count} valid, {invalid_count} invalid."
        )

    return 1 if invalid_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
